import json
import matplotlib.pyplot as plt
import networkx as nx
import os
import pickle
from pythonds.basic import Queue
import webbrowser as wb
from generate_baseball_graph import read_csv_file, make_graph


def map_player_to_id(people, appearances):
    '''
    Maps a list of dictionaries representing baseball players to a dictionary
    that associates each player's full name with a list of tuples containing
    their player ID and birth year.

    Parameters
    ----------
    people: list
        A list of players

    appearances: list
        A list of player appearances

    Returns
    -------
    player_name_to_id: dict
        A dictionary that maps each player's full name to a list of tuples. Each tuple
      contains the player's ID and birth year

    '''
    player_name_to_id = {}
    for person in people:
        has_appearance = False
        for appearance in appearances:
            if appearance['playerID'] == person['playerID']:
                has_appearance = True
                break
        if not has_appearance:
            continue
        player_name = person['nameFirst'].strip() + ' ' + \
            person['nameLast'].strip()
        if player_name not in player_name_to_id:
            player_name_to_id[player_name] = []
        player_name_to_id[player_name].append(
            (person['playerID'], person['birthYear']))
    return player_name_to_id


def map_playerid_to_name(people):
    '''
    Maps a list of dictionaries representing playerID's to a dictionary that associates
    each playerID to a player's first name and last name.

    Parameters
    ----------
    people: list
        A list of players

    Returns
    -------
    playerid_to_name: dict
        A dictionary that maps playerID's to player names
    '''
    playerid_to_name = {}
    for person in people:
        playerid_to_name[person['playerID']] = person['nameFirst'].strip(
        ) + ' ' + person['nameLast'].strip()
    return playerid_to_name


def map_teamid_to_name(teams):
    '''
    Maps a list of dictionaries representing teamID's to a dictionary that associates
    each teamID to the full team name.

    Parameters
    ----------
    teams: list
        A list of teams

    Returns
    -------
    teamid_to_name: dict
        A dictionary that maps teamID's to full team names

    '''
    teamid_to_name = {}
    for team in teams:
        teamid_to_name[team['teamID']] = team['name']
    return teamid_to_name


def bfs(gr, start):
    '''
    Performs breadth first search and modifies
    Graph object in place.

    Parameters
    ----------
    gr: Graph
      Graph object representation of players (playerID) and the teams (teamID) they played for

    start: Vertex
      Starting vertex for breadth first search
    '''

    gr.nodes[start]['distance'] = 0
    gr.nodes[start]['pred'] = None
    vertQueue = Queue()
    vertQueue.enqueue(start)
    while (vertQueue.size() > 0):
        currentVert = vertQueue.dequeue()
        for nbr in gr.neighbors(currentVert):
            if gr.nodes[nbr]['color'] == 'white':
                gr.nodes[nbr]['color'] = 'gray'
                gr.nodes[nbr]['distance'] = gr.nodes[currentVert]['distance'] + 1
                gr.nodes[nbr]['pred'] = currentVert
                vertQueue.enqueue(nbr)
        gr.nodes[currentVert]['color'] = 'black'


def traverse(gr, y):
    '''
    Performs traversal from y to previously defined start position (x).

    Parameters
    ----------
    gr: Graph
        Graph object representation of players (playerID) and the teams (teamID) they played for
    y: Vertex
        End vertex

    Returns
    -------
    path: list
        List of nodes representing the path between x and y
    '''
    path = []
    x = y
    while gr.nodes[x]['pred']:
        path.append(x)
        x = gr.nodes[x]['pred']
    path.append(x)
    return path


def format_path(path, playerid_to_name, teamid_to_name):
    '''
    Format final path of player ids and team ids to player names and the full team name they played for.

    Parameters
    ----------
    path: list
        Player to team path to be formatted
    playerid_to_name: dict
        Mapping of playerID to player first name and last name
    teamid_to_name: dict
        Mapping of teamID to full team name

    Returns
    -------
    new_path: list
        Formatted player to team path
    '''
    new_path = []
    for i in range(len(path)):
        if i % 2 == 0:
            player_name = playerid_to_name[path[i]]
            new_path.append(player_name)
        else:
            team_name = f"{teamid_to_name[path[i][0]]}, {path[i][1]}"
            new_path.append(team_name)
    return new_path


def get_user_input(prompt):
    '''
    Prompts user for input.

    Parameters
    ----------
    prompt: str
        Prompt to ask user for input

    Returns
    -------
    input prompt: str
        Input from user
    '''
    return input(prompt)


def get_playerid_from_playername(players_and_id, player_name):
    '''
    Given a dictionary containing players and their ids, and a player name, returns the player id.

    Parameters
    ----------
    players_and_id: dict
        A dictionary containing players and their ids. Keys are player names and values are a list of
        tuples, where each tuple contains the player id and birth year
    player_name: str
        The name of the player to search for

    Returns
    -------
    player_id: str
       The id of the player
    '''

    # check if there are multiple players with the same name (e.g., Bob Allen)
    if len(players_and_id[player_name]) > 1:
        print(f'More than one {player_name} has been found.')
        idx = 1
        for item in players_and_id[player_name]:
            # print all the duplicate player names and their birth years
            print(f'{idx}: {player_name} born in {item[1]}')
            idx += 1
        # user selects which player they want based on birth year
        birth_year_input = get_user_input(
            f'Please select the birth year for the {player_name} you want: ')
        while int(birth_year_input) < 1 or int(birth_year_input) > (idx - 1):
            birth_year_input = get_user_input(
                f'Please select the birth year for the {player_name} you want: ')
        player_id = players_and_id[player_name][int(birth_year_input) - 1][0]
    # if no duplicate players, use the playerid to build the graph
    elif len(players_and_id[player_name]) == 1:
        player_id = players_and_id[player_name][0][0]
    return player_id


def main():
    '''
    Driver function for program.
    '''

    appearances = read_csv_file('data/Appearances.csv')
    people = read_csv_file('data/People.csv')
    teams = read_csv_file('data/Teams.csv')

    #  map players to their playerID
    if os.path.exists('players_and_id'):
        with open('players_and_id', 'rb') as f:
            players_and_id = pickle.load(f)
    else:
        players_and_id = map_player_to_id(people)
        with open('players_and_id', 'wb') as f:
            pickle.dump(players_and_id, f)

    player_names = map_playerid_to_name(people)
    team_names = map_teamid_to_name(teams)

    # cache graph
    if os.path.exists('baseball_graph.json'):
        with open('baseball_graph.json', 'r') as f:
            res = json.load(f)
            gr = nx.node_link.node_link_graph(res)
    else:
        gr = make_graph(appearances)
        res = nx.node_link.node_link_data(gr)
        with open('baseball_graph.json', 'w') as f:
            json.dump(res, f)

    # initial prompt for user input
    start_prompt = "Enter the first and last name of a player in the following format: '<Firstname> <Lastname>', or 'exit' to quit: "
    start_input = get_user_input(start_prompt)
    while start_input not in players_and_id.keys() and start_input != 'exit':
        print('Invalid player name.')
        start_input = get_user_input(start_prompt)
    if start_input == 'exit':
        print('Bye')
        exit(0)

    # build bfs graph; the graph will be built off of the starting input
    # player name provided by the user
    start_vertex = get_playerid_from_playername(players_and_id, start_input)
    bfs(gr, start_vertex)

    # display subset of graph to show teams and players that starting player
    # played with (first-degree connections only)
    subgraph = nx.graphviews.subgraph_view(
        gr, lambda node: gr.nodes[node]['distance'] < 3)
    nx.drawing.draw(subgraph, with_labels=True)
    plt.show()

    # second player input loop
    end_prompt = "Enter the first and last name of another player in the following format: '<Firstname> <Lastname>', or 'exit' to quit: "
    end_input = get_user_input(end_prompt)
    while end_input != 'exit':
        if end_input in players_and_id.keys():
            end_vertex = get_playerid_from_playername(
                players_and_id, end_input)
            path = traverse(gr, end_vertex)

            # create a subgraph that includes the path and its first-degree
            # connections
            nodes_to_include = set(path)
            for node in path:
                nodes_to_include.update(list(gr.neighbors(node)))
            subgraph = gr.subgraph(nodes_to_include)
            # set the color of nodes in the path to hotpink and all other nodes
            # to dodger blue
            node_colors = [
                'hotpink' if node in path else 'dodgerblue' for node in subgraph.nodes]
            # compute the positions of the nodes using the kamada kawai
            # algorithm
            pos = nx.kamada_kawai_layout(subgraph)

            # plot the subgraph with the path and its nodes highlighted
            nx.draw_networkx_nodes(subgraph, pos, node_color=node_colors)
            nx.draw_networkx_edges(subgraph, pos)
            nx.draw_networkx_edges(subgraph, pos, edgelist=[(
                path[i], path[i + 1]) for i in range(len(path) - 1)], edge_color='r', width=3)
            nx.draw_networkx_labels(subgraph, pos)
            plt.axis('off')
            plt.show()

            # display path between player one and player two
            print(format_path(path, player_names, team_names))

            # baseball-reference.com player bios IO loop
            for i in range(len(path)):
                if i % 2 == 0:
                    print(f'{i//2 + 1}. {player_names[path[i]]}')
            bio_input = get_user_input(
                f'Please select the number of a player you would like more information, or \'N\' to continue: ')
            while not str.isdigit(bio_input) and bio_input != 'N':
                bio_input = get_user_input(
                    f'Please select the number of a player you would like more information, or \'N\' to continue: ')
            if bio_input != 'N':
                # player id from path
                bio_input = path[(int(bio_input) - 1) * 2]
                wb.open(
                    f'https://www.baseball-reference.com/players/{bio_input[0]}/{bio_input}.shtml')
        else:
            print('Invalid player name.')
        end_input = get_user_input(end_prompt)
    print('Good Bye!')


if __name__ == "__main__":
    main()
