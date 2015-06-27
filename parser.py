from random import random
from sampler import Sampler
from extractor import Extractor

class Parser:
    def __init__(self, model, temp, c):
        self.model = model
        self.extractor = Extractor(model)
        self.sampler = Sampler(model, self.extractor, temp, c) # model may be  redundant


    def decode(self, sent, num = 30):

        o = open('samples.conll06', 'w')

        seed = self.sampler.random_tree(sent)
        sw = self.extractor.tree_local_weights(seed) # should be global
        ss = self.extractor.tree_score(sw)

        optimal = seed
        ow = self.extractor.tree_local_weights(seed)
        os = self.extractor.tree_score(ow)

        for i in xrange(num): # or converge
            tree = self.sampler.propose(sent, seed)
            tw = self.extractor.tree_local_weights(tree)
            ts = self.extractor.tree_score(tw)

            if ts > os:
                optimal, os = tree, ts
            if ts > ss:
            #     or random() < sampler.trans_prob(seed, tree):
                seed, ss = tree, ts

            o.write(tree.to_str())
        o.close()
        return optimal






    def learn(self, instances, epochs = 10, num = 10):
        model = self.model
        sampler = self.sampler
        extractor = self.extractor
        for e in xrange(epochs):
            for sent in instances:
                gold = sent.get_gold_tree()
                gw = extractor.tree_local_weights(gold) # should be global

                seed = sampler.random_tree(sent)
                sw = extractor.tree_local_weights(seed) # should be global
                se = seed.error(gold)


                for i in xrange(num):
                    tree = sampler.propose(sent, seed)
                    tw = extractor.tree_local_weights(tree) # should be global
                    te = tree.error(gold)

                    gs = extractor.tree_score(gw)
                    ts = extractor.tree_score(tw)
                    ss = extractor.tree_score(sw)

                    
                    # C1
                    if gs - ts < te * 5:
                        model.update(gw, tw)

                    # C2
                    if te < se: # tree > seed
                        if ts - ss < (se - te) * 5:
                            model.update(tw, sw)
                    else: # tree <= seed
                        if ss - ts < (te - se) * 5:
                            model.update(sw, tw)

                    # accept or reject, should be probablistic, deterministic for now
                    if te < se:
                        seed, sw, se = tree, tw, te

                    model.qadd()
        model.average()
        model.show()


    def decode_stats(self, sent, num = 300):
        all_score = extractor.all_score(sent)


        seed = self.sampler.random_tree(sent)
        sw = self.extractor.tree_local_weights(seed) # should be global
        ss = self.extractor.tree_score(sw)

        optimal = seed
        ow = self.extractor.tree_local_weights(seed)
        os = self.extractor.tree_score(ow)

        for i in xrange(num): # or converge
            tree = self.sampler.propose(sent, seed)
            tw = self.extractor.tree_local_weights(tree)
            ts = self.extractor.tree_score(tw)

            if ts > os:
                optimal, os = tree, ts
            if ts > ss:
            #     or random() < sampler.trans_prob(seed, tree):
                seed, ss = tree, ts

        return optimal


