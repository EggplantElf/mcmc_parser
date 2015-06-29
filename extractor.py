from math import exp


# try hash kernel someday
class Extractor:
    def __init__(self, model):
        self.func = model.map_feat

    def all_exp_scores(self, sent):
        exp_scores = {}
        for d in sent[1:]:
            exp_scores[d] = {}
            for h in sent:
                if h is not d:
                    exp_scores[d][h] = exp(self.local_score(h, d))
        return exp_scores

    # use in training, later
    def all_weights(self, sent):
        arc_weights = {}
        for d in sent[1:]:
            arc_weights[d] = {}
            for h in sent:
                if h is not d:
                    arc_weights[d][h] = self.weights(h, d)
        return arc_weights

    # use lookup cache, fine for now
    def tree_score(self, weights):
        # return sum(self.local_score(h, d) for (d, h) in tree.head_map.items())
        return sum(w.s for w in weights)

    def tree_local_weights(self, tree):
        return sum([self.local_weights(h, d) for (d, h) in tree.head_map.items()], [])


    def local_score(self, h, d):
        return sum(w.s for w in self.iter_local(h, d, self.func))

    def local_weights(self, h, d):
        return list(self.iter_local(h, d, self.func))


    def iter_local(self, h, d, func):
        yield func('hfm_dfm:%s_%s' % (h.form, d.form))
        yield func('hps_dps:%s_%s' % (h.pos, d.pos))
        yield func('hps_dlm:%s_%s' % (h.pos, d.form))
        yield func('hfm_dps:%s_%s' % (h.form, d.pos))


    def iter_global(self, tree, func):
        yield func('GLOBAL')
