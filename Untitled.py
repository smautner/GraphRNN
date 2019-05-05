# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# from IPython.core.display import display, HTML
# display(HTML("<style>.container { width:100% !important; }</style>"))


# ok the plan is this:
# 1. read fasta 
# 2. NN
# 3. fold
# return nx graph

import os
from Bio import SeqIO
import subprocess as sp
from ShaKer.rna_tools import util
import re
def readfasta(name="RF00162.fa"):
    result = []
    for record in SeqIO.parse("toolsdata/%s" % name, "fasta"):
        result.append(record.seq._data)
    return result

def write_fasta(sequences, filename='asdasd'):
    fasta = ''
    for i, s in enumerate(sequences):
        if len(s) > 5:
            seq = s
            seq = '\n'.join(textwrap(seq, width=60))
            fasta += '>HACK%d\n%s\n\n' % (i, seq)
    with open(filename, 'w') as f:
        f.write(fasta)

def textwrap(seq,width=10):
    res=[]
    while len(seq) > width:
        res.append(seq[:width])
        seq=seq[width:]
    res.append(seq)
    return res

def extract_aligned_seed(header, out):
    text = out.strip().split('\n')
    seed = ''
    for line in text:
        if header in line:
            seed += line.strip().split()[1]
    return seed


def convert_seq_to_fasta_str(seq_pair):
    header, seq = normalize_seq(seq_pair)
    return '>%s\n%s\n' % (header, seq)

def make_seq_struct(seq, struct):
    clean_seq = ''
    clean_struct = ''
    for seq_char, struct_char in zip(seq, struct):
        if seq_char == '-' and struct_char == '.':
            pass
        else:
            clean_seq += seq_char
            clean_struct += struct_char
    return clean_seq, clean_struct


def extract_struct_energy(out):
    text = out.strip().split('\n')
    struct = text[1].strip().split()[0]
    energy = text[1].strip().split()[1:]
    energy = ' '.join(energy).replace('(', '').replace(')', '')
    energy = energy.split('=')[0]
    energy = float(energy)
    return struct, energy

def normalize_seq(seq_pair):
    header, seq = seq_pair
    header = header.split('\n')[0]
    header = header.split('_')[0]
    return (header, seq)


def normalize_seqs(seqs):
    for seq in seqs:
        yield normalize_seq(seq)




from sklearn.neighbors import NearestNeighbors
from eden import sequence as eseq
class NNF:
    def fit (self, sequences): 
        self.sequences = sequences
        self.NN = NearestNeighbors(n_neighbors=4).fit(eseq.vectorize(sequences))
    
    def predict(self,seq):
        seqvec = eseq.vectorize([seq])
        dist, neighs = self.NN.kneighbors(seqvec)
        return [self.sequences[i] for i in neighs[0]  ]


    
    def getstruct(self,seq):
        seqs = self.predict(seq)
        return self.callfold(('999',seq),[(str(i),s) for i,s in enumerate(seqs)])

    def callfold(self,seq,neighs):    
        str_out = convert_seq_to_fasta_str(seq)
        for neigh in neighs:
            str_out += convert_seq_to_fasta_str(neigh)
        cmd = 'echo "%s" | muscle -clwstrict -quiet' % (str_out)
        out = sp.run(cmd,shell=True,stdout=sp.PIPE).stdout.decode("utf-8")
        #print ("MUSCLE:",out)
        seed = extract_aligned_seed(seq[0], out)
        cmd = 'echo "%s" | RNAalifold --noPS 2>/dev/null' % (out)
        out = sp.run(cmd,shell=True,stdout=sp.PIPE).stdout.decode("utf-8")
        #print ("RNAALI:",out)
        #print ("seed:",seed)
        struct, energy = extract_struct_energy(out)
        clean_seq, struct = make_seq_struct(seed, struct)
        return struct

    
    def getgraph(self,seq):
        struct = self.getstruct(seq)
        if len(seq)!=len(struct):
            print ("skipping seq, bad stru")
        return util.sequence_dotbracket_to_graph(seq,struct)
    
def get_all_graphs(fasta='RF00162.fa', maxgr=0):
    seqs = readfasta(fasta)
    mod = NNF()
    mod.fit(seqs)
    if maxgr: 
        seqs=seqs[:maxgr]
    return [mod.getgraph(seq) for seq in seqs]





'''
import utils
graphs = utils.load_graph_list('graphs/GraphRNN_RNN_RNA1_4_128_train_0.dat')
for i in range(0, 192, 16):
    utils.draw_graph_list(graphs[i:i+16], 4, 4, fname="picDGMG2_%d" % i)
'''
