import sys
import math

from logging import warn

import numpy as np

from keras.models import Graph
from keras.layers import Activation, Dropout, TimeDistributedDense
from keras.layers import Embedding
from keras.layers import LSTM, GRU
from keras.optimizers import Adagrad, Adam
from keras.regularizers import l2
from keras.preprocessing.sequence import pad_sequences

import input_data
import common
import viterbi

# Settings

class BasicConfig(object):
    window = 0
    max_vocab_size = 200000    # None
    max_train_examples = None
    max_develtest_examples = 100000    # for faster develtest
    examples_as_indices = True    # must be True
    learn_embeddings = False
    batch_size = 64 # 32
    num_steps = 40   # RNN steps
    epochs = 10
    rnn_size = 500
    rnn_activation = 'relu'    # 'sigmoid'
    rnn_inner_activation = 'hard_sigmoid'
    rnn_bidirectional = True
    rnn_dropout_W = 0.0 # 0.5    # dropout for input gates
    rnn_dropout_U = 0.0 # 0.5    # dropout for recurrent connections
    rnn_l2_lambda_W = 1e-04 # 0 # 1e-05
    rnn_l2_lambda_U = 1e-04 # 0 # 1e-05
    after_rnn_dropout = 0.5 # 0.5    # dropout after RNN layer
    learning_rate = 0.001
    loss = 'categorical_crossentropy' # 'mse'

config = BasicConfig()

RNN = GRU    # alternative: LSTM
optimizer = Adam(config.learning_rate)

# Data

data_dir = sys.argv[1] if len(sys.argv) >= 2 else 'data/ner/BC2GM'
w2v_file = sys.argv[2] if len(sys.argv) >= 3 else None

data = input_data.read_data_sets(data_dir, w2v_file, config=config)

embedding = common.word_to_vector_to_matrix(config.word_to_vector)

if (config.max_train_examples is not None and
    len(data.train.examples) > config.max_train_examples):
    warn('cropping train data from %d to %d' % (len(data.train.examples),
                                                config.max_train_examples))
    data.train._examples = data.train._examples[:config.max_train_examples]
    data.train._labels = data.train._labels[:config.max_train_examples]

# Model

model = Graph()

# Input and optional embedding layer
if config.learn_embeddings:
    input_shape=(config.num_steps,)
    model.add_input(input_shape=input_shape, name='input', dtype=int)
    model.add_node(Embedding(embedding.shape[0], embedding.shape[1],
                             input_length=config.num_steps,
                             weights=[embedding]),
                   input='input', name='embedding')
    prev = 'embedding'
else:
    input_shape=(config.num_steps, embedding.shape[1])
    model.add_input(input_shape=input_shape, name='input')
    prev = 'input'

# RNN and dropout
def rnn_layer(size, config, **kwargs):
    return RNN(size,
               activation=config.rnn_activation,
               inner_activation=config.rnn_inner_activation,
               return_sequences=True,
               # W/U dropout and reg need a newer keras
               dropout_W=config.rnn_dropout_W,
               dropout_U=config.rnn_dropout_U,
               W_regularizer=l2(config.rnn_l2_lambda_W),
               U_regularizer=l2(config.rnn_l2_lambda_U),
               **kwargs)

if not config.rnn_bidirectional:
    model.add_node(rnn_layer(config.rnn_size, config), input=prev, name='rnn')
    model.add_node(Dropout(config.after_rnn_dropout), input='rnn',
                   name='dropout')
else:
    # BRNN following https://github.com/fchollet/keras/blob/master/examples/imdb_bidirectional_lstm.py. Alternative approach: https://github.com/EderSantana/seya/blob/master/seya/layers/recurrent.py#L17-L48
    model.add_node(rnn_layer(config.rnn_size/2, config),
                   input=prev, name='forward')
    model.add_node(rnn_layer(config.rnn_size/2, config, go_backwards=True),
                   input=prev, name='backward')
    model.add_node(Dropout(config.after_rnn_dropout),
                   inputs=['forward', 'backward'], name='dropout')

# Output
model.add_node(TimeDistributedDense(data.output_size), input='dropout',
               name='tddense')
model.add_node(Activation('softmax'), input='tddense', name='softmax')
model.add_output(input='softmax', name='output')

model.compile(optimizer=optimizer, loss={ 'output': config.loss })

def make_sequences(a, size=config.num_steps):
    """Reshape (d1, d2, ...) array into (d1/size, size, d2, ...).

    Pad with zeros if d1 % size is non-zero.
    """
    if a.shape[0] % size != 0:
        pad_size = size - (a.shape[0] % size)
        warn('make_sequences: padding with %d zeros' % pad_size)
        pad = np.zeros((pad_size,) + a.shape[1:], dtype=a.dtype)
        a = np.concatenate((a, pad))
    return np.reshape(a, (a.shape[0]/size, size) + a.shape[1:])

def prepare_dataset(dataset):
    """Format DataSet for RNN, return (examples, labels)."""
    examples = make_sequences(dataset.examples)
    labels = make_sequences(dataset.labels)
    # take out "window" dim, should be size 1
    examples = examples.reshape(examples.shape[:2])
    return examples, labels

def predictions(model, examples):
    pred = list(model.predict({'input': examples },
                              batch_size=config.batch_size)['output'])
    return np.argmax(np.asarray(pred), axis=2).flatten()

def evaluate(model, examples, gold, label=None):
    output = list(model.predict({'input': examples },
                                batch_size=config.batch_size)['output'])
    pred = np.argmax(np.asarray(output), axis=2).flatten()
    vpred = viterbi.viterbi(np.concatenate(output), *viterbi_probabilities)
    return (common.classification_summary(gold, pred) + '\n' +
            'w/viterbi ' + common.classification_summary(gold, vpred))
    
train_examples, train_labels = prepare_dataset(data.train)
devel_examples, devel_labels = prepare_dataset(data.devel)

if not config.learn_embeddings:
    # no Embedding layer in model, embed here
    train_examples = embedding[train_examples]
    devel_examples = embedding[devel_examples]

train_gold = common.one_hot_to_dense(data.train.labels)
devel_gold = common.one_hot_to_dense(data.devel.labels)

viterbi_probabilities = viterbi.estimate_probabilities(train_gold)

# Make (possibly) smaller devtest versions
def crop_data(examples, labels, maximum=config.max_develtest_examples):
    max_batches = int(math.ceil(1.*maximum/config.batch_size))
    if examples.shape[0] < max_batches:
        return examples, labels
    else:
        warn('crop_data: cropping %d to %d' % (examples.shape[0], max_batches))
        return examples[:max_batches], labels[:max_batches*config.batch_size]

train_examples_s, train_gold_s = crop_data(train_examples, train_gold)
devel_examples_s, devel_gold_s = crop_data(devel_examples, devel_gold)

for epoch in range(1, config.epochs+1):
    model.fit({'input': train_examples, 'output': train_labels },
              batch_size=config.batch_size, nb_epoch=1)
    print epoch, 'train', evaluate(model, train_examples_s, train_gold_s)
    print epoch, 'devel', evaluate(model, devel_examples_s, devel_gold_s)

print 'FINAL train', evaluate(model, train_examples, train_gold)
print 'FINAL devel', evaluate(model, devel_examples, devel_gold)

with open('predictions.txt', 'wt') as out:
    pred = predictions(model, devel_examples)
    pred = pred[:len(data.devel.examples)]    # cut possible zero-padding
    common.write_gold_and_prediction(data.devel, pred, config, out)
