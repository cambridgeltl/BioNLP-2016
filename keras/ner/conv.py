#!/usr/bin/env python

import sys
import numpy as np

from os import path
from logging import info, warn

from keras.models import Graph
from keras.layers import Embedding, Reshape, Dense, Activation, Flatten, Dropout
from keras.layers import Merge, Flatten, Convolution2D
from keras.regularizers import l2
from keras.optimizers import Adam
from layers import Input, FixedEmbedding

import input_data
import common
import settings

# Settings

class Defaults(object):
    window = 3
    max_vocab_size = 200000    # None for no limit
    max_train_examples = None
    max_develtest_examples = 100000    # for faster develtest
    learn_embeddings = False
    filter_sizes = [3,4]
    filter_num = 100
    hidden_size = 100
    batch_size = 100
    drop_prob = 0.5
    l2_lambda = 0.001
    epochs = 10
    learning_rate = 0.001
    loss = 'categorical_crossentropy'
    verbosity = 1    # 0=quiet, 1=progress bar, 2=one line per epoch
    iobes = False     # Map tags to IOBES on input

config = settings.from_cli(['datadir', 'wordvecs'], Defaults)
optimizer = Adam(config.learning_rate)

data_name = path.basename(config.datadir.rstrip('/'))
common.setup_logging(data_name)
settings.log_with(config, info)

# Data

data = input_data.read_data_sets(config.datadir, config.wordvecs, config)
embedding = common.word_to_vector_to_matrix(config.word_to_vector)

if (config.max_train_examples and len(data.train) > config.max_train_examples):
    warn('cropping train data from %d to %d' % (len(data.train),
                                                config.max_train_examples))
    data.train.crop(config.max_train_examples)

# Model

model = Graph()

# Separate word (index) and word-features inputs
model.add_input(name='input-w', input_shape=(data.input_size,), dtype=int)
EmbeddingLayer = Embedding if config.learn_embeddings else FixedEmbedding
model.add_node(EmbeddingLayer(embedding.shape[0], embedding.shape[1],
                              input_length=data.input_size,
                              weights=[embedding]),
               name='embedding', input='input-w')
model.add_input(name='input-f', input_shape=data.feature_shape,
                dtype='float')

# Combine and reshape for convolution
cshape = (data.input_size, embedding.shape[1] + data.feature_shape[1])
model.add_node(Reshape((1, cshape[0], cshape[1]), input_shape=cshape),
               merge_mode='concat', concat_axis=2,
               name='reshape', inputs=['embedding', 'input-f'])

# Convolutions
conv_outputs = []
for i, filter_size in enumerate(config.filter_sizes, start=1):
    model.add_node(Convolution2D(config.filter_num, filter_size, cshape[1]),
                   name='convolution-%d' % i, input='reshape')
    model.add_node(Activation('relu'),
                   name='activation-%d' % i, input='convolution-%d' % i)
    model.add_node(Flatten(),
                   name='flatten-%d' % i, input='activation-%d' % i)
    conv_outputs.append('flatten-%d' % i)

# Fully connected layer and output
if len(conv_outputs) == 1:
    # Keras rejects "inputs" list with length 1
    input_arg = { 'input': conv_outputs[0] }
else:
    input_arg = { 'inputs': conv_outputs }
model.add_node(Dense(config.hidden_size, activation='relu',
                     W_regularizer=l2(config.l2_lambda)),
               name='dense-1', **input_arg)
model.add_node(Dropout(config.drop_prob),
               name='dropout', input='dense-1')
model.add_node(Dense(data.output_size,
                     W_regularizer=l2(config.l2_lambda)),
               name='dense-out', input='dropout')
model.add_node(Activation('softmax'), name='softmax', input='dense-out')
model.add_output(name='output', input='softmax')

def predictions(model, examples):
    output = list(model.predict({ 'input-w': examples[0],
                                  'input-f': examples[1] },
                                batch_size=config.batch_size)['output'])
    return np.argmax(np.asarray(output), axis=1)

def evaluate(model, dataset, config):
    pred = predictions(model, dataset.inputs)
    gold = np.argmax(dataset.labels, axis=1)
    return common.per_type_summary(gold, pred, config)

def eval_report(prefix, model, dataset, config, log=info):
    summary = evaluate(model, dataset, config)
    for s in summary.split('\n'):
        log(prefix + ' ' + s)

model.compile(optimizer=optimizer, loss={ 'output': config.loss })

small_train = data.train.subsample(config.max_develtest_examples)
small_devel = data.devel.subsample(config.max_develtest_examples)

for epoch in range(1, config.epochs+1):
    model.fit({ 'input-w': data.train.inputs[0],
                'input-f': data.train.inputs[1],
                'output': data.train.labels },
              batch_size=config.batch_size, nb_epoch=1,
              verbose=config.verbosity)
    eval_report('Ep %d train' % epoch, model, small_train, config)
    eval_report('Ep %d devel' % epoch, model, small_devel, config)
    data.train.shuffle()

eval_report('FINAL train', model, data.train, config)
eval_report('FINAL devel', model, data.devel, config)

pred = predictions(model, data.devel.inputs)
common.save_gold_and_prediction(data.devel, pred, config, data_name)
