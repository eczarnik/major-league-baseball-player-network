import csv
import os
import pickle
from pythonds import Graph, Vertex
from pythonds.basic import Queue
import pprint as pp

def read_csv_file(filepath):
    '''
    Opens and reads lines in a csv file and saves the lines to a new list.

    Parameters
    ----------
    filepath: str
        Name of the filepath
    '''
    data = []
    with open(filepath, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    return data

def map_player_to_id(people):
    '''
    Maps a list of dictionaries representing baseball players to a dictionary
    that associates each player's full name with a list of tuples containing
    their player ID and birth year.

    Parameters
    ----------
    people: list
        A list of player statistics

    Returns
    -------
    player_name_to_id: dict
        A dictionary that maps each player's full name to a list of tuples. Each tuple
      contains the player's ID and birth year

    '''
    player_name_to_id = {}
    for person in people:
        player_name = person['nameFirst'].strip() + ' ' + person['nameLast'].strip()
        if player_name not in player_name_to_id:
            player_name_to_id[player_name] = []
        player_name_to_id[player_name].append((person['playerID'], person['birthYear']))
    return player_name_to_id

def make_graph(appearances):
    '''
    """
    Builds an undirected graph of players and teams based on the given list of
    appearances, where each appearance is a dictionary with keys 'playerID' and
    'teamID'. The resulting graph has a vertex for each unique player and team
    ID, and an edge between a player and a team if the player appeared for that
    team, and vice versa.

    Parameters
    ----------
    appearances: list
        A list of dictionaries representing player appearances,
        where each dictionary has keys 'playerID' and 'teamID'

    Returns
    -------
    gr: Graph
        An undirected graph representing the player and team relationships
        based on the given appearances. The graph is implemented using the
        Graph class from the graph.py module
    '''
    gr = Graph() # initialize empty graph
    for item in appearances:
        gr.addEdge(item['playerID'], item['teamID'])
        gr.addEdge(item['teamID'], item['playerID'])
        gr.getVertex(item['playerID']).setColor('white')
        gr.getVertex(item['teamID']).setColor('white')
    return gr


def bfs(gr: Graph, start: Vertex):
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
    start.setDistance(0)
    start.setPred(None)
    vertQueue = Queue()
    vertQueue.enqueue(start)
    while (vertQueue.size() > 0):
        currentVert = vertQueue.dequeue()
        for nbr in currentVert.getConnections():
            if (nbr.getColor() == 'white'):
                nbr.setColor('gray')
                nbr.setDistance(currentVert.getDistance() + 1)
                nbr.setPred(currentVert)
                vertQueue.enqueue(nbr)
        currentVert.setColor('black')

def traverse(y):
    '''
    Performs traversal from y to previously defined start position (x).

    Parameters
    ----------
    y: Vertex
        End vertex

    Returns
    -------
    path: list
        List of nodes representing the path between x and y
    '''
    path = []
    x = y
    while (x.getPred()):
        path.append(x.getId())
        x = x.getPred()
    path.append(x.getId())
    return path

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

def main():
    '''
    Driver function for program.
    '''

    appearances = read_csv_file('Appearances.csv')
    people = read_csv_file('People.csv')
    teams = read_csv_file('Teams.csv')

    #  map players to their playerID
    if os.path.exists('players_and_id'):
        with open('players_and_id', 'rb') as f:
            players_and_id = pickle.load(f) # loading the cached players_and_id mapped data
    else:
        players_and_id = map_player_to_id(people)
        with open('players_and_id', 'wb') as f:
            pickle.dump(players_and_id, f) # caching the players_and_id mapping data

    gr = make_graph(appearances)

    # initial prompt for user input
    start_prompt = "Enter the first and last name of a player in the following format: '<Firstname> <Lastname>', or 'exit' to quit: "
    start_input = get_user_input(start_prompt)
    while start_input not in players_and_id.keys() and start_input != 'exit':
        print('Invalid player name.')
        start_input = get_user_input(start_prompt)
    if start_input == 'exit':
        print('Bye')
        exit(0)

    # build bfs graph; the graph will be built off of the starting input player name provided by the user
    # first we need to grab the start_input's (player's) playerID because the network is built off of playerID entries
    if len(players_and_id[start_input]) > 1: # are there duplicate players with the same name?
        print(f'More than one {start_input} has been found.')
        idx = 1
        for item in players_and_id[start_input]:
            print(f'{idx}: {start_input} born in {item[1]}') # print all the duplicate player names and their birth years
            idx += 1
        birth_year_input = get_user_input(f'Please select the birth year for the {start_input} you want: ') # user selects which player they want based on birth year
        while int(birth_year_input) < 1 or int(birth_year_input) > (idx - 1):
            birth_year_input = get_user_input(f'Please select the birth year for the {start_input} you want: ')
        player_id = players_and_id[start_input][int(birth_year_input) - 1][0]
    elif len(players_and_id[start_input]) == 1: # if no duplicate players
        player_id = players_and_id[start_input][0][0] # use the playerid to build the graph
    start_vertex = gr.getVertex(player_id)
    bfs(gr, start_vertex)

    # get second player name from user
    end_prompt = "Enter the first and last name of another player in the following format: '<Firstname> <Lastname>', or 'exit' to quit: "
    end_input = get_user_input(end_prompt)
    while end_input not in players_and_id.keys() and end_input != 'exit':
        print('Invalid player name.')
        end_input = get_user_input(end_prompt)
    if end_input == 'exit':
        print('Bye')
        exit(0)

    # input loop
    while end_input != 'exit':
        if end_input in players_and_id.keys():
            player_id = players_and_id[end_input][0][0]
        end_vertex = gr.getVertex(player_id)
        path = traverse(end_vertex)
        print(path)
        end_input = get_user_input(end_prompt)
        while end_input not in players_and_id.keys() and end_input != 'exit':
            print('Invalid player name.')
            end_input = get_user_input(end_prompt)
    print('Bye')

if __name__ == "__main__":
    main()