import numpy as np
from shapely.geometry import LineString
import matplotlib.pyplot as plt
import networkx as nx
import os
import pickle
import get_graph as gg

os.chdir(os.getcwd())

G= nx.read_gpickle('our_map.mp')
args = pickle.load(open('args.mp','rb'))

colors,sizes,labels = args


def make_pairs(path):
    l = list()
    for i in range(0,len(path)-1):
        pair = list()
        pair.append(path[i])
        pair.append(path[i+1])
        l.append(tuple(pair))
        pair=list()
        pair.append(path[i+1])
        pair.append(path[i])
        l.append(tuple(pair))
    return l


def graph_colors(G,x,y):
    dj = nx.dijkstra_path(G,x,y)
    pairs = make_pairs(dj)
    colors = list()
    for edge in G.edges:
        if edge in pairs:
            colors.append('red')
            continue
        colors.append('black')
    return (dj, colors)

def plot_with_colors(G, colors, size, labels, x, y):
    dj, edge_colors = graph_colors(G, x, y)
    gg.plot_graph(G,colors,size,labels,edge_colors)

x1 = 1
x2 = 6

#dj, edge_colors = graph_colors(G,x1,x2)

plot_with_colors(G, colors, sizes,labels, x1, x2)


