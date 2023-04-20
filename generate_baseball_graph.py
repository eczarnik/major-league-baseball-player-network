import csv
import json
import networkx as nx


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
    gr = nx.Graph() # initialize empty graph
    for item in appearances:
        team_node = (item['teamID'], item['yearID'])
        gr.add_edge(item['playerID'], team_node)
        gr.add_edge(team_node, item['playerID'])
        nx.set_node_attributes(gr, {item['playerID']: {'color': 'white', 'distance': float('inf'), 'pred': None}, team_node: {'color': 'white', 'distance': float('inf'), 'pred': None}}) # set the nodes to white
    return gr

if __name__ == '__main__':
    appearances = read_csv_file('data/Appearances.csv')

    gr = make_graph(appearances)
    res = nx.node_link.node_link_data(gr)
    with open('baseball_graph.json', 'w') as f:
        json.dump(res, f)