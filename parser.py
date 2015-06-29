from random import random
from sampler import Sampler
from extractor import Extractor
from collections import defaultdict

class Parser:
    def __init__(self, model, temp, c):
        self.model = model
        self.extractor = Extractor(model)
        self.sampler = Sampler(model, self.extractor, temp, c) # model may be  redundant


    def decode(self, sent, num = 30):
        trees = defaultdict(int)
        exp_scores = self.extractor.all_exp_scores(sent)
        seed = self.sampler.random_tree(sent, exp_scores)
        optimal = seed
        slw = self.extractor.tree_local_weights(seed)
        sls = self.extractor.tree_score(slw)
        sgw = self.extractor.tree_global_weights(seed)
        sgs = self.extractor.tree_score(sgw)
        ss = sls + sgs

        for i in xrange(num): # or converge
            tree = self.sampler.propose(sent, seed, exp_scores)
            tlw = self.extractor.tree_local_weights(tree)
            tls = self.extractor.tree_score(tlw)
            tgw = self.extractor.tree_global_weights(tree)
            tgs = self.extractor.tree_score(tgw)
            ts = tls + tgs
            if ts > ss or random() < self.sampler.trans_prob(sgs, tgs):
                seed, ss = tree, ts
        return optimal


    def learn(self, instances, epochs = 10, num = 10):
        model = self.model
        sampler = self.sampler
        extractor = self.extractor
        for e in xrange(epochs):
            print 'iteration: %d' % e
            for i, sent in enumerate(instances):
                if i % 100 == 0:
                    print i
                gold = sent.get_gold_tree()
                gw = extractor.tree_local_weights(gold) + extractor.tree_global_weights(gold)

                seed = sampler.random_tree(sent)
                sw = extractor.tree_local_weights(seed) + extractor.tree_global_weights(seed)
                se = seed.error(gold)

                for i in xrange(num):
                    tree = sampler.propose(sent, seed)
                    tw = extractor.tree_local_weights(tree) + extractor.tree_global_weights(tree)
                    te = tree.error(gold)

                    gs = self.extractor.tree_score(gw)
                    ts = self.extractor.tree_score(tw)
                    ss = self.extractor.tree_score(sw)

                    
                    # C1
                    if gs - ts < te:
                        model.update(gw, tw)

                    # C2
                    if te < se: # tree > seed
                        if ts - ss < (se - te):
                            model.update(tw, sw) # se - te) margin
                    else: # tree <= seed
                        if ss - ts < (te - se):
                            model.update(sw, tw)

                    # accept or reject, should be probablistic, deterministic for now
                    if te < se:
                        seed, sw, se = tree, tw, te

                    model.qadd()
        model.average()
        # model.show()


    def decode_show(self, sent, num = 30000):

        o = open('samples.conll06', 'w')

        statistics = {d: {h: 0 for h in sent if h is not d} for d in sent[1:]}
        trees = defaultdict(int)

        exp_scores = self.extractor.all_exp_scores(sent)
        seed = self.sampler.random_tree(sent, exp_scores)
        optimal = seed
        slw = self.extractor.tree_local_weights(seed)
        sls = self.extractor.tree_score(slw)
        sgw = self.extractor.tree_global_weights(seed)
        sgs = self.extractor.tree_score(sgw)
        ss = sls + sgs

        for i in xrange(num): # or converge
            tree = self.sampler.propose(sent, seed, exp_scores)
            tlw = self.extractor.tree_local_weights(tree)
            tls = self.extractor.tree_score(tlw)
            tgw = self.extractor.tree_global_weights(tree)
            tgs = self.extractor.tree_score(tgw)
            ts = tls + tgs
            if ts > ss or random() < self.sampler.trans_prob(sgs, tgs):
                seed, ss = tree, ts

            for (d, h) in seed.head_map.items():
                statistics[d][h] += 1
            trees[self.tree_key(seed)] += 1
        # print statistics
        print 'trees:', len(trees)
        for k, v in sorted(trees.items(), key = lambda x: x[1], reverse = True):
            print k, '\t', v
        for d in statistics:
            for h in statistics[d]:
                print d, h, exp_scores[d][h], statistics[d][h]
            o.write(tree.to_str())
        o.close()

        return optimal


    def change_head_stats(self, sent, num = 500):
        exp_scores = self.extractor.all_exp_scores(sent)
        statistics = {d: {h: 0 for h in sent if h is not d} for d in sent[1:]}
        trees = defaultdict(int)

        seed = self.sampler.random_tree(sent, exp_scores)
        sw = self.extractor.tree_local_weights(seed) # should be global
        ss = self.extractor.tree_score(sw)

        for i in xrange(num): # or converge
            tree = self.sampler.propose(sent, seed, exp_scores)
            tw = self.extractor.tree_local_weights(tree)
            ts = self.extractor.tree_score(tw)

            if ts > ss or random() < self.sampler.trans_prob(seed, tree, ss, ts, exp_scores):
                seed, ss = tree, ts

            for (d, h) in seed.head_map.items():
                statistics[d][h] += 1
            trees[self.tree_key(seed)] += 1


        print 'trees:', len(trees)
        for k, v in sorted(trees.items(), key = lambda x: x[1], reverse = True):
            print k, '\t', v

        for d in statistics:
            for h in statistics[d]:
                print d, h, exp_scores[d][h], statistics[d][h]

        # return optimal



    def random_tree_stats(self, sent, num = 100000):
        exp_scores = self.extractor.all_exp_scores(sent)
        trees = defaultdict(int)

        for i in xrange(num): # or converge
            tree = self.sampler.random_tree(sent, exp_scores)
            trees[self.tree_key(tree)] += 1
        print 'trees:', len(trees)
        for k, v in sorted(trees.items(), key = lambda x: x[1], reverse = True):
            print k, '\t', v


    def tree_key(self, tree):
        return ','.join(['%s<-%s' % (d, h) for (d, h) in sorted(tree.head_map.items())])        





