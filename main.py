from model import *
from parser import *
from sampler import *
from tree import *

def demo(input_file):
    model = Model()
    parser = Parser(model, 1, 1)
    instances = list(read_sentence(input_file))
    parser.learn(instances)

    for sent in read_sentence(input_file):
        parser.decode(sent)




if __name__ == '__main__':
    demo('demo.conll06')