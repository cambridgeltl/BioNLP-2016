#!/usr/bin/env python

import sys
import numpy as np

from os import path
from logging import info, warn

from keras.models import Sequential
from keras.layers import Embedding, Reshape, Dense, Activation, Dropout
from keras.layers import Merge, Flatten
from keras.regularizers import l2
from keras.optimizers import Adagrad, Adam
from layers import Input, FixedEmbedding

import input_data
import common
import settings

# Settings

class Defaults(object):
    window = 2
    max_vocab_size = 200000    # None
    max_train_examples = None
    max_develtest_examples = 100000    # for faster develtest
    examples_as_indices = True
    learn_embeddings = False
    hidden_sizes = [300]
    hidden_activation = 'hard_sigmoid' # 'relu'
    l2_lambda = 1e-5 # 1e-4
    dropout = 0.5
    batch_size = 50
    epochs = 10
    learning_rate = 0.001
    loss = 'categorical_crossentropy' # 'mse'

config = settings.from_cli(['datadir', 'wordvecs'], Defaults)
optimizer = Adam(config.learning_rate)

data_name = path.basename(config.datadir.rstrip('/'))
common.setup_logging(data_name)
settings.log_with(config, info)

# Data

data = input_data.read_data_sets(config.datadir, config.wordvecs, config)
embedding = common.word_to_vector_to_matrix(config.word_to_vector)

if config.max_train_examples and len(data.train) > config.max_train_examples:
    warn('cropping train data from %d to %d' % (len(data.train),
                                                config.max_train_examples))
    data.train.crop(config.max_train_examples)

# Model

model = Sequential()

# Separate embedded-words and word-features sequences
embedded = Sequential()
EmbeddingLayer = Embedding if config.learn_embeddings else FixedEmbedding
embedded.add(EmbeddingLayer(embedding.shape[0], embedding.shape[1],
                            input_length=data.input_size, weights=[embedding]))
features = Sequential()
features.add(Input(data.feature_shape))

model.add(Merge([embedded, features], mode='concat', concat_axis=2))
model.add(Flatten())

# Fully connected layers
for size in config.hidden_sizes:
    model.add(Dense(size, W_regularizer=l2(config.l2_lambda)))
    model.add(Activation(config.hidden_activation))
model.add(Dense(data.output_size))
model.add(Activation('softmax'))

model.compile(optimizer=optimizer, loss=config.loss)

def predictions(model, inputs):
    output = list(model.predict(inputs, batch_size=config.batch_size))
    return np.argmax(np.asarray(output), axis=1)

def evaluate(model, dataset, config):
    pred = predictions(model, dataset.inputs)
    gold = np.argmax(dataset.labels, axis=1)
    return common.per_type_summary(gold, pred, config)

def eval_report(prefix, model, dataset, config, log=info):
    summary = evaluate(model, dataset, config)
    for s in summary.split('\n'):
        log(prefix + ' ' + s)

small_train = data.train.subsample(config.max_develtest_examples)
small_devel = data.devel.subsample(config.max_develtest_examples)

for epoch in range(1, config.epochs+1):
    model.fit(data.train.inputs, data.train.labels,
              batch_size=config.batch_size, nb_epoch=1)
    eval_report('Ep %d train' % epoch, model, small_train, config)
    eval_report('Ep %d devel' % epoch, model, small_devel, config)
    data.train.shuffle()

eval_report('FINAL train', model, data.train, config)
eval_report('FINAL devel', model, data.devel, config)

pred = predictions(model, data.devel.inputs)
common.save_gold_and_prediction(data.devel, pred, config, data_name)
