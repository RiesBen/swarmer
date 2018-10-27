import numpy as np
from shapely.geometry import LineString
import matplotlib.pyplot as plt
import networkx as nx

def get_point_or_idx(input):
    sites = np.array([
            [2.2, 1.6], #[2.3,1.6],
            [2.6, 0.6], #[2.7,0.5],
            [3.4, 1.4], #[3.7,1.5],
            [2.4, 3.4], #[2.5,3.4],
            [0.6, 2.2], #[0.5,2.1],
            [1.4, 3.2], #[1.4,3.2],
            [1.0, 1.6], #[0.8,1.6],
            [3.6, 0.6], #[3.7,0.5],
            [3.2, 3.2], #[3.3,3.1],
            ])
    if type(input) is int:
        return sites[input - 1]
    else:
        return np.argmax(np.all(np.isclose(sites, input),1))+1
#print(get_point_or_idx([3.2,3.2]))
#print(get_point_or_idx(3))

def do(input_list):
    buildings = np.array([[2.0, 2.8, 0], [1.5, 1.0, 0], [3.15, 0.7, 0], [3.0, 2.0, 0]])
        # 9 sites, 3 buildings
    sites = np.array([
            [2.2, 1.6], #[2.3,1.6],
            [2.6, 0.6], #[2.7,0.5],
            [3.4, 1.4], #[3.7,1.5],
            [2.4, 3.4], #[2.5,3.4],
            [0.6, 2.2], #[0.5,2.1],
            [1.4, 3.2], #[1.4,3.2],
            [1.0, 1.6], #[0.8,1.6],
            [3.6, 0.6], #[3.7,0.5],
            [3.2, 3.2], #[3.3,3.1],
            ])

    def init_graph():
        offset = 0.5 #meter
        G=nx.Graph()
        colors = []
        sizes = []
        labels = {}

        """
        #building
        for i in range(len(buildings)):
            name = "B" + str(i)
            G.add_node(name)
            G.node[name]['pos'] = buildings[i][:2]
            colors.append("green")
            sizes.append(1)
            labels[name] = name
        """

        #points around building
        for i in range(len(buildings)):
            bl = str(i) + "_bl"
            G.add_node(bl)
            x,y = buildings[i][0] - offset, buildings[i][1] - offset
            G.node[bl]['pos'] = np.array([x,y])
            colors.append("green")
            sizes.append(10)

            br = str(i) + "_br"
            G.add_node(br)
            x,y = buildings[i][0] - offset, buildings[i][1] + offset
            G.node[br]['pos'] = np.array([x,y])
            colors.append("green")
            sizes.append(10)

            ul = str(i) + "_ul"
            G.add_node(ul)
            x,y = buildings[i][0] + offset, buildings[i][1] - offset
            G.node[ul]['pos'] = np.array([x,y])
            colors.append("green")
            sizes.append(10)

            ur = str(i) + "_ur"
            G.add_node(ur)
            x,y = buildings[i][0] + offset, buildings[i][1] + offset
            G.node[ur]['pos'] = np.array([x,y])
            colors.append("green")
            sizes.append(10)

            for e in [(bl,br), (bl,ul), (ul,ur),(ur, br)] :
                G.add_edge(*e, weight = 0.8)
            labels[bl] = ""
            labels[ul] = ""
            labels[br] = ""
            labels[ur] = ""

        for i in range(len(sites)):
            G.add_node(i+1)
            G.node[i+1]['pos'] = np.array(sites[i])
            colors.append("red")
            sizes.append(70)
            labels[i+1] = str(i+1)
        return (G,(colors,sizes,labels))



    def node_distance(node1, node2):
        out = np.linalg.norm(node1['pos'] - node2['pos'])
        return round(out, 2)

    #node_distance(G.node['0_ur'], G.node['0_ul'])
    def intersect(p1,p2):
        l1 = LineString(p1)
        l2 = LineString(p2)
        return l1.intersects(l2)


    def plot_graph(G, colors, sizes, labels):

        pos=nx.get_node_attributes(G,'pos')

        edge_labels = nx.get_edge_attributes(G,'weight')
        nx.draw_networkx(G, pos,node_color = colors, node_size = sizes, labels = labels, font_size = 8)
    #    nx.draw_networkx_edge_labels(G, pos, edge_labels = edge_labels, font_size = 8)
        plt.axis('equal')
        axes = plt.gca()
        axes.set_xlim([0,4])
        axes.set_ylim([0,4])
        plt.show()


    ################ to run################################
    import copy
    G,args = init_graph() #gets the graph
    BUILDING_BOUNDARIES = copy.deepcopy(G.edges()) #IMPORTANT
    colors,sizes, labels = args

    #print((intersect(([2.2,1.6],[2.6,.6]), ([1.6, 2.4],[1.6,3.2]))))
    #print((intersect(([2.2,-2.2],[3.3,-3.3]), ([2.2,2.2],[3.3,3.3]))))
    #raise Error
    # only adds edges from this point
    #print(BUILDING_BOUNDARIES)
    def allowed_path(node1, node2, graph):
        tolerance = 0.01
        line1 = [graph.node[node1]['pos'] , graph.node[node2]['pos']]
        for i in BUILDING_BOUNDARIES:
            assert type(i[0]) is str
            #if type(i[0]) is not str or type(i[1]) is not str:
            #    continue
            #print("bound" ,i)
            x_upper = max(graph.node[i[0]]['pos'][0], graph.node[i[1]]['pos'][0])
            x_lower = min(graph.node[i[0]]['pos'][0], graph.node[i[1]]['pos'][0])
            y_upper = max(graph.node[i[0]]['pos'][1], graph.node[i[1]]['pos'][1])
            y_lower = min(graph.node[i[0]]['pos'][1], graph.node[i[1]]['pos'][1])
            line2 = [[x_lower + tolerance , y_lower + tolerance ], [x_upper - tolerance, y_upper - tolerance ]]
            if intersect(line1, line2):
                #print(node1, node2, i, line1, line2)
                return False
        #print("I am here")
        return True

    def connect_all_allowed_paths(G):
        #print(allowed_path(1,2,G))
        for i in range(1, len(sites) + 1):
            for j in range(i+1 , len(sites) + 1):
                if allowed_path(i,j, G):
                    G.add_edge(i, j, weight = node_distance(G.node[i] , G.node[j]))
            for j in range(len(buildings)):
                name = "{}_ul".format(j)
                if allowed_path(i,name, G):
                    G.add_edge(i, name , weight = node_distance(G.node[i] , G.node[name]))
                name = "{}_ur".format(j)
                if allowed_path(i,name, G):
                    G.add_edge(i, name , weight = node_distance(G.node[i] , G.node[name]))
                name = "{}_bl".format(j)
                if allowed_path(i,name, G):
                    G.add_edge(i, name , weight = node_distance(G.node[i] , G.node[name]))
                name = "{}_br".format(j)
                if allowed_path(i,name, G):
                    G.add_edge(i, name , weight = node_distance(G.node[i] , G.node[name]))

    connect_all_allowed_paths(G)


    def get_paths(source, target, graph):
        assert target in G.nodes and source in G.nodes
        dj = nx.dijkstra_path(G,source, target)
        return [G.node[i]['pos'] for i in dj]

    output = []
    for i in input_list:
        output.append([np.argmax(np.all(np.isclose(sites, i[0]),1))+1,
                       np.argmax(np.all(np.isclose(sites, i[1]),1))+1])

    return [get_paths(source, target,G) for source,target in output]
    #plot_graph(G, colors, sizes, labels)

