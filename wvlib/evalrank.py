#!/usr/bin/env python

"""Evaluate word representation by similarity ranking to reference."""

import sys
import codecs

import numpy
import wvlib
from scipy.spatial import distance
from os.path import basename, splitext
from scipy.stats import spearmanr
from _collections import defaultdict

DEFAULT_ENCODING = 'UTF-8'

class FormatError(Exception):
    pass
from math import*
from decimal import Decimal

def nth_root(value, n_root):

    root_value = 1/float(n_root)
    return round (Decimal(value) ** Decimal(root_value),3)

def minkowski_distance(x,y,p_value):
    return nth_root(sum(pow(abs(a-b),p_value) for a,b in zip(x, y)),p_value)

def argparser():
    try:
        import argparse
    except ImportError:
        import compat.argparse as argparse

    ap=argparse.ArgumentParser()
    ap.add_argument('-r', '--max-rank', metavar='INT', default=None, 
                    type=int, help='only consider r most frequent words')
    ap.add_argument('-q', '--quiet', default=False, action='store_true')
    ap.add_argument('vectors', help='word vectors')
    ap.add_argument('references', metavar='FILE', nargs='+',
                    help='reference similarities')
    return ap

def cosine(v1, v2):
    return numpy.dot(v1/numpy.linalg.norm(v1), v2/numpy.linalg.norm(v2))

def dot(v1, v2):
    return numpy.dot(v1, v2)


def evaluate(wv, reference):
    """Evaluate wv against reference, return (rho, count) where rwo is
    Spearman's rho and count is the number of reference word pairs
    that could be evaluated against.
    """

    gold, predicted = [], []

    
    #dict1=defaultdict(list)
    for words, sim in sorted(reference, key=lambda ws: ws[1]):
        try:
            v1, v2 = wv[words[0]], wv[words[1]]
            #print words[0],words[1] ,"\t",v1[0],"\t",v2[0]
        except KeyError:
            continue
        
        gold.append((words, sim))
        #print len(variance)
                
        predicted.append((words, cosine(v1, v2))) # this function have problem when v1 v2 are very similar
        

#         for i in range(1):           
#             
#             newSim=1/distance.minkowski(v1,v2,3)           
#             dict1["minkowski"].append((words, newSim))
#             
#             newSim=1/distance.chebyshev(v1,v2)           
#             dict1["chebyshev"].append((words, newSim))
#             
#             newSim=1/distance.canberra(v1,v2)           
#             dict1["canberra"].append((words, newSim))
#             
#             newSim=1/distance.braycurtis(v1,v2)           
#             dict1["braycurtis"].append((words, newSim))
#             
#             newSim=1/distance.cityblock(v1,v2)           
#             dict1["cityblock"].append((words, newSim))
#                         
#             newSim=(1-distance.correlation(v1,v2))/2           
#             dict1["correlation"].append((words, newSim))
#             
#             newSim=1/distance.cosine(v1,v2)           
#             dict1["cosine"].append((words, newSim))
#             
#             newSim=1/distance.hamming(v1,v2)           
#             dict1["hamming"].append((words, newSim))
#             
#             newSim=1/distance.euclidean(v1,v2)         
#             dict1["Euclidean"].append((words, newSim))  
        
        
#         print words, newSim, 1- cosine(v1, v2)\
#          , distance.minkowski(v1,v2,3),distance.chebyshev(v1,v2) , distance.canberra(v1,v2),\
#          distance.braycurtis(v1,v2),distance.cityblock(v1,v2),(1-distance.correlation(v1,v2))/2,\
#          distance.cosine(v1,v2),distance.hamming(v1,v2),distance.euclidean(v1,v2)
        #print words[0],words[1],cosine(v1, v2)    
    #print "intersection between updated word vector and Mayo: ", counter
    simlist = lambda ws: [s for w,s in ws]
#     for key,value in dict1.items():
#         rho1, p = spearmanr(simlist(gold), simlist(value))
#         print key,rho1
    #print gold,predicted    
    rho, p = spearmanr(simlist(gold), simlist(predicted))
    
    return (rho, len(gold))

def evaluateTest(wv, reference,wordList):
    """Evaluate wv against reference, return (rho, count) where rwo is
    Spearman's rho and count is the number of reference word pairs
    that could be evaluated against.
    """
    count=0
    counter=0
    gold, predicted = [], []
    a = numpy.array(wv.values())
    variance = numpy.var(a,axis=0)
    
    for words, sim in sorted(reference, key=lambda ws: ws[1]):
        try:
            v1, v2 = wv[words[0]], wv[words[1]]
            #print words[0],words[1] ,"\t",v1[0],"\t",v2[0]
        except KeyError:
            count+=1
            continue
        
        gold.append((words, sim))
        #print len(variance)
        weight=[0.5,0.5]
        newSim=(cosine(v1, v2)) * weight[0] +  1/distance.seuclidean(v1,v2,variance) * weight[1] 
        predicted.append((words, cosine(v1, v2))) # this function have problem when v1 v2 are very similar
        
        

#         for i in range(1):
#             newSim=(cosine(v1, v2)) * weight[0] +  1/distance.seuclidean(v1,v2,variance) * weight[1] 
#             dict1["newSim"].append((words, newSim))
# 
#               
#             newSim=1/distance.seuclidean(v1,v2,variance)            
#             dict1["seuclidean"].append((words, newSim))            
#             
#             newSim=1/distance.minkowski(v1,v2,3)           
#             dict1["minkowski"].append((words, newSim))
#             
#             newSim=1/distance.chebyshev(v1,v2)           
#             dict1["chebyshev"].append((words, newSim))
#             
#             newSim=1/distance.canberra(v1,v2)           
#             dict1["canberra"].append((words, newSim))
#             
#             newSim=1/distance.braycurtis(v1,v2)           
#             dict1["braycurtis"].append((words, newSim))
#             
#             newSim=1/distance.cityblock(v1,v2)           
#             dict1["cityblock"].append((words, newSim))
#                         
#             newSim=(1-distance.correlation(v1,v2))/2           
#             dict1["correlation"].append((words, newSim))
#             
#             newSim=1/distance.cosine(v1,v2)           
#             dict1["cosine"].append((words, newSim))
#             
#             newSim=1/distance.hamming(v1,v2)           
#             dict1["hamming"].append((words, newSim))
            
#             newSim=1/distance.euclidean(v1,v2)         
#             dict1["Euclidean"].append((words, newSim))  
        
        
#         print words, newSim, distance.seuclidean(v1,v2,variance), cosine(v1, v2)\
#          , distance.minkowski(v1,v2,3),distance.chebyshev(v1,v2) , distance.canberra(v1,v2),\
#          distance.braycurtis(v1,v2),distance.cityblock(v1,v2),(1-distance.correlation(v1,v2))/2,\
#          distance.cosine(v1,v2),distance.hamming(v1,v2),distance.euclidean(v1,v2)
        #print words[0],words[1],cosine(v1, v2)
#         if words[0].strip() in wordList.keys(): # words[0]= word in eva, wordList = word retrofitted
#             #print " intersection between keys:",words[0]
#             counter+=1
#             targetList=wordList[words[0].strip()]
#             if words[1] in targetList:
#                 print words[0],words[1],targetList
            #print words[0],"\t","\t".join(str(e) for e in wordList[words[0]])
    print "intersection between updated word vector and Eva.Set: ", counter
    simlist = lambda ws: [s for w,s in ws]
#     for word,sim in gold:
#         print word,sim
#     for key,value in dict1.items():
#         rho1, p = spearmanr(simlist(gold), simlist(value))
#         print key,rho1
        
    rho, p = spearmanr(simlist(gold), simlist(predicted))
    print "Eva.item not found in WordVector:",count
    return (rho, len(gold))

def evaluate1Word(wv, reference):
    """Evaluate wv against reference, return (rho, count) where rwo is
    Spearman's rho and count is the number of reference word pairs
    that could be evaluated against.
    """
    count=0
    gold, predicted = [], []
    for words, sim in sorted(reference, key=lambda ws: ws[1]):
        if " " not in words[0] and " " not in words[1]:
            #print words[0],words[1]
            try:
                v1, v2 = wv[words[0]], wv[words[1]]
            except KeyError:
                count+=1
                continue
            #print words
            gold.append((words, sim))
            predicted.append((words, cosine(v1, v2)))

    simlist = lambda ws: [s for w,s in ws]
    rho, p = spearmanr(simlist(gold), simlist(predicted))
    print "Word not found in WordVector",count
    return (rho, len(gold))    

def read_reference(name, encoding=DEFAULT_ENCODING):
    """Return similarity ranking data as list of ((w1, w2), sim) tuples."""
    data = []
    with codecs.open(name, 'rU', encoding=encoding) as f:
        for line in f:
            # try tab-separated first, fall back to any space
            fields = line.strip().split('\t')
            if len(fields) != 3:
                fields = line.strip().split()
            if len(fields) != 3:
                raise FormatError(line)
            try:
                data.append(((fields[0], fields[1]), float(fields[2])))
            except ValueError:
                raise FormatError(line)
    return data

def read_referenceSingleWords(name, encoding=DEFAULT_ENCODING):
    """Return similarity ranking data as list of ((w1, w2), sim) tuples."""
    data = []
    with codecs.open(name, 'rU', encoding=encoding) as f:
        for line in f:
            # try tab-separated first, fall back to any space
            fields = line.strip().split('\t')
            if len(fields) != 3:
                fields = line.strip().split()
            if len(fields) != 3:
                raise FormatError(line)
            
            try:
                if " " not in fields[0] and " " not in fields[1]: 
                    data.append(((fields[0], fields[1]), float(fields[2])))
            except ValueError:
                raise FormatError(line)
    return data

def baseroot(name):
    return splitext(basename(name))[0]

def main(argv=None):
    if argv is None:
        argv = sys.argv

    options = argparser().parse_args(argv[1:])

    if options.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    try:
        wv = wvlib.load(options.vectors, max_rank=options.max_rank)
        wv = wv.normalize()
    except Exception, e:
        print >> sys.stderr, 'Error: %s' % str(e)
        return 1
    print options.references    
    references = [(r, read_reference(r)) for r in options.references]

    print '%20s\trho\tmissed\ttotal\tratio' % 'dataset'
    for name, ref in references:
        rho, count = evaluate(wv, ref)
        total, miss = len(ref), len(ref) - count
        print '%20s\t%.4f\t%d\t%d\t(%.2f%%)' % \
            (baseroot(name), rho, miss, total, 100.*miss/total)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
