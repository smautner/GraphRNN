import pickle 
from collections import Counter
import networkx as nx
import utils
import eden.display as ed
graphs  = pickle.load(open('graphs/GraphRNN_RNN_RNA2_4_128_pred_3000_1.dat','rb'))


def cyclecheck(graph):
    cycles = nx.cycle_basis(graph)
    for nodelist in cycles: 
        # we only filter for a single problematic case, where there is a hairpin with a not-connected exit
        degrees = [ graph.degree(n) for n in nodelist ]
        c = Counter(degrees)
        # we expect degree in [2,3] , 2 needs to appear n times, 3 exactly twice 
        if len(c) == 2 and 2 in c and c.get(3,1)==2:
            a,b = [ n for n,d in zip(nodelist,degrees) if d == 3 ]
            if not graph.has_edge(a,b):
                #print('removing',nodelist,degrees)
                return False
    return True


def check_graph(graph): 
    c=Counter([graph.degree(x) for x in graph.nodes()])
    if c.get(1,1) <= 2 and max(c.keys()) <= 3 and nx.is_connected(graph):
        if cyclecheck(graph):
            return True
    return False



print ('ehere are this many graphs: ',len(graphs))
graphs2 = list(filter(check_graph, graphs))
print("how many pass the filter:")
print ('all filters:', len(graphs2), len(graphs2)/1024)

def check_end(graph): 
    c=Counter([graph.degree(x) for x in graph.nodes()])
    if c.get(1,1) <= 2:
        return True
    return False


def check_degree(graph): 
    c=Counter([graph.degree(x) for x in graph.nodes()])
    if max(c.keys()) <= 3:
            return True
    return False


def check_con(graph): 
    c=Counter([graph.degree(x) for x in graph.nodes()])
    if nx.is_connected(graph):
            return True
    return False


def check_cys(graph): 
    if cyclecheck(graph):
            return True
    return False


for x,z in zip([check_end, check_degree, check_con, check_cys],['2x deg1','maxdegree','connected','cycles']): 
    
    l  = len(list(filter(x, graphs)))
    print(z ,l, l/1024)


#for i, g in enumerate(graphs): 
#    ed.draw_graph(g,file_name=f"asd{i}.png",vertex_label=None,vertex_size=100)



