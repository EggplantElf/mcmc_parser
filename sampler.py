from __future__ import division
from random import random, choice, sample
from tree import *
from math import exp


class Sampler:

    def __init__(self, model, extractor, temp, c):
        self.model = model
        self.extractor = extractor
        self.init_temp = temp
        self.temp = temp
        self.c = c

    def cool(self):
        self.temp *= self.c

    def random_head(self, sent, u, exp_scores):
        if exp_scores is not None:
            candidates = exp_scores[u]
        else:
            candidates = {}
            for h in sent:
                if h is not u:
                    candidates[h] = exp(self.extractor.local_score(h, u))

        exp_sum = sum(candidates.values())
        num = random() * exp_sum
        for h in candidates:
            num -= candidates[h]
            if num < 0:
                return h
        return h



    def random_tree(self, sent, exp_scores = None):
        self.temp = self.init_temp
        # wilson's algorithm
        head_map = {d: None for d in sent[1:]}
        in_tree = {d: False for d in sent}
        in_tree[sent[0]] = True
        for i in sent[1:]:
            u = i
            while not in_tree[u]:
                head_map[u] = self.random_head(sent, u, exp_scores)
                u = head_map[u]
            u = i
            while not in_tree[u]:
                in_tree[u] = True
                u = head_map[u]

        tree = Tree(sent, head_map)
        return tree
        # return tree.get_weights(self.model)
        

    # note "new" as label to demo the change
    def propose(self, sent, seed, exp_scores = None, num = 2):
        change = set(sample(sent[1:], min(len(sent[1:]), num)))
        head_map = {d: None for d in sent[1:]}
        in_tree = {d: False for d in sent}
        in_tree[sent[0]] = True
        for i in sent[1:]:
            u = i
            while not in_tree[u]:
                if u in change:
                    head_map[u] = self.random_head(sent, u, exp_scores)
                else:
                    head_map[u] = seed.head_map[u]
                u = head_map[u]
            u = i
            while not in_tree[u]:
                in_tree[u] = True
                u = head_map[u]

        tree = Tree(sent, head_map)
        # self.cool()
        # tree.get_score(self.model)
        # return tree.get_weights(self.model)
        return tree

    # def trans_prob(self, seed, tree, ss, ts, all_exp_scores):
    #     diff_ratio = exp(ss - ts) # diff global score
    #     for (d, th) in tree.head_map.items():
    #         sh = seed.head_map[d]
    #         if th is not sh:
    #             diff_ratio *= all_exp_scores[d][th] / all_exp_scores[d][sh] # diff local score
    #     return diff_ratio # accept ratio: diff (global - local) score 

    def trans_prob(self, sgs, tgs):
        return exp(tgs - sgs)


class GibbsSampler(Sampler):
    def __init__(self, model):
        self.model = model

    def trans_prob(self):
        return 1