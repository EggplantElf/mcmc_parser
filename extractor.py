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

    def tree_global_weights(self, tree):
        return list(self.iter_global(tree, self.func))

    def local_score(self, h, d):
        return sum(w.s for w in self.iter_local(h, d, self.func))

    def local_weights(self, h, d):
        return list(self.iter_local(h, d, self.func))

    # first order features
    def iter_local(self, h, d, func):
        yield func('fo:hfm_dfm:%s_%s' % (h.form, d.form))
        yield func('fo:hps_dps:%s_%s' % (h.pos, d.pos))
        yield func('fo:hps_dlm:%s_%s' % (h.pos, d.form))
        yield func('fo:hfm_dps:%s_%s' % (h.form, d.pos))

    # other features except first-order
    def iter_global(self, tree, func):
        # second and third order features
        for (d, h) in tree.head_map.items():
            hps, hfm = h.form_pos()
            dps, dfm = d.form_pos()
            s = d.rsib
            

            # sconsecutive sibling
            if s and tree.head_map[s] is h:
                sps, sfm = s.form_pos()
                yield func('cs:hps_dps_sps:%s_%s_%s' % (hps, dps, sps))
                yield func('cs:dfm_sfm:%s_%s' % (dfm, sfm))
                yield func('cs:dps_sps:%s_%s' % (dps, sps))
                yield func('cs:dps_sfm:%s_%s' % (dps, sfm))
                yield func('cs:dfm_sps:%s_%s' % (dfm, sps))

            # grandparent
            if h in tree.head_map:
                g = tree.head_map[h]
                gps, gfm = g.form_pos()
                yield func('gp:gps_hps_dps:%s_%s_%s' % (gps, hps, dps))
                yield func('gp:gfm_hfm_dfm:%s_%s_%s' % (gfm, hfm, dfm))
                # yield func('gp:gfm_dfm:%s_%s' % (gfm, dfm))
                # yield func('gp:dps_sps:%s_%s' % (dps, sps))
                # yield func('gp:dps_dfm:%s_%s' % (dps, dfm))
                # yield func('gp:gfm_sps:%s_%s' % (gfm, sps))

        # real global features
        # right branch
        last = tree.sent[-1]
        while last.pos == 'P':
            last = tree.head_map[last]
        pl = 0
        while last in tree.head_map:
            last = tree.head_map[last]
            pl += 1
        yield func('rb:%d' % (pl / len(tree.sent) * 10) )# bin of 10

        # 


