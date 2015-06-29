from model import *
from parser import *
from sampler import *
from tree import *

# TODO
# MIRA or PA
# finish features
# pics of time and head error with T
# pics of # of ranked trees


def demo(train_file, test_file):
    model = Model()
    parser = Parser(model, 1, 1)
    instances = list(read_sentence(train_file))
    parser.learn(instances)

    for sent in read_sentence(test_file):
        parser.decode_show(sent)




if __name__ == '__main__':
    demo('../data/english/train/wsj_train.first-5k.conll06', 'demo.conll06')