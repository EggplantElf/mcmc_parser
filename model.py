import gzip, cPickle
from itertools import imap
from collections import defaultdict
# from sentence import *

class Model:
    def __init__(self, modelfile = None):
        if modelfile:
            self.load(modelfile)
        else:
            self.weights = defaultdict(Weight)
            self.q = 0

    def save(self, modelfile):
        stream = gzip.open(modelfile,'wb')
        cPickle.dump(self.weights,stream,-1)
        stream.close()

    def load(self, modelfile):
        stream = gzip.open(modelfile,'rb')
        self.weights = cPickle.load(stream)
        stream.close()

    def show(self):
        print 'show model'
        for w in self.weights:
            print w, self.weights[w]


    def map_feat(self, feat):
        # return self.weights.get(feat, Weight(0))
        return self.weights[feat]


    def update(self, gold_weights, pred_weights, t = 0.1):
        # print 'update'
        for w in gold_weights:
            w.sadd(t)
            w.dadd(t * self.q)
        for w in pred_weights:
            w.sadd(-t)
            w.dadd(-t * self.q)
        # print gold_weights, pred_weights

    def qadd(self):
        self.q += 1

    def average(self):
        q = self.q
        for w in self.weights.values():
            w.sadd(- w.d / q)

# wrapper for easier update
class Weight:
    def __init__(self, s = 0):
        self.s = s
        self.d = 0

    def __repr__(self):
        return str(self.s)

    def sadd(self, i):
        self.s += i

    def dadd(self, i):
        self.d += i


        
