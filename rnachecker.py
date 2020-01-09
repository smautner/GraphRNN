import pickle 
from collections import Counter
import networkx as nx
import utils
import eden.display as ed
graphs  = pickle.load(open('graphs/GraphRNN_RNN_RNA2_4_128_pred_3000_1.dat','rb'))



def check_graph(graph): 
    c=Counter([graph.degree(x) for x in graph.nodes()])
    if c.get(1,1) <= 2 and max(c.keys()) <= 3 and nx.is_connected(graph):
        return True
    return False



print (len(graphs))
graphs = list(filter(check_graph, graphs))

print (len(graphs))
for i, g in enumerate(graphs): 
    ed.draw_graph(g,file_name=f"asd{i}.png",vertex_label=None,vertex_size=100)



