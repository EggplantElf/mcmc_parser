


class Token:
    __slots__ = ['conll', 'tid', 'form', 'lemma', 'pos', 'mor', 'hid', 'head', 'label']

    def __init__(self, line, conll, train):
        self.conll = conll
        if conll == 'CoNLL06':
            entries = line.split()
            self.tid = int(entries[0])
            self.form = entries[1]
            self.lemma = entries[2]
            self.pos = entries[3]
            self.mor = entries[5]
            if train:
                self.hid = int(entries[6])
                self.label = entries[7]
            else:
                self.hid = -1
                self.label = '_'
        else:
            pass

    def to_str(self):
        if self.conll == 'CoNLL06':
            return '%d\t%s\t%s\t%s\t_\t%s\t%d\t%s\t_\t_' %\
                (self.tid, self.form, self.lemma, self.pos, self.mor, self.hid, self.label)
        else:
            return 'Wrong Format'


class Root(Token):
    def __init__(self):
        self.tid = 0
        self.form = 'ROOT'
        self.lemma = 'ROOT'
        self.pos = 'ROOT'
        self.mor = 'ROOT'

class Sentence(list):
    def __init__(self):
        self.append(Root())
        self.arcs = []

    def add_token(self, token):
        self.append(token)

    def add_heads(self):
        for d in self[1:]:
            h = self[d.hid]
            d.head = h
            self.arcs.append((d, h))

    def to_str(self):
        return '\n'.join(t.to_str() for t in self[1:]) + '\n\n'


    def get_gold_tree(self):
        return Tree(self, dict(self.arcs))

# Tree shouldn't change any token in it, can only read the info 
class Tree:
    def __init__(self, sent, head_map):
        self.sent = sent
        self.head_map = head_map

    # for demo only! 
    # changed the head of the original tokens!
    def to_str(self): 
        for d in self.sent[1:]:
            d.hid = self.head_map[d].tid
        return self.sent.to_str()


    # def get_global_weights(self, extractor):
    #     self.weights = extractor.   
    #     return self

    def error(self, gold):
        return sum(1 for d in self.head_map if self.head_map[d] is not gold.head_map[d])

    def get_score(self):
        self.score = sum(w.s for w in self.weights)
        return self

    def change_head(self, h, d):
        pass



def read_sentence(filename, conll = 'CoNLL06', train = True):
    print 'reading sentences ...'
    sentence = Sentence()
    for line in open(filename):
        line = line.rstrip()
        if line:
            sentence.add_token(Token(line, conll, train))
        elif len(sentence) != 1:
            if train:
                sentence.add_heads()
            yield sentence
            sentence = Sentence()

