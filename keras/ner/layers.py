import numpy as np

from keras import backend as K
from keras.layers.core import Layer
from keras.layers import Reshape

def Input(shape):
    """Return no-op layer that can be used as an input layer."""
    return Reshape(shape, input_shape=shape)

class FixedEmbedding(Layer):
    """Embedding with fixed weights.

    Modified from keras/layers/embeddings.py in Keras (http://keras.io).

    WARNING: this is experimental and not fully tested, use at your
    own risk.
    """
    input_ndim = 2

    def __init__(self, input_dim, output_dim, weights, input_length=None,
                 mask_zero=False, dropout=0., **kwargs):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.input_length = input_length
        self.mask_zero = mask_zero
        self.dropout = dropout

        if (not isinstance(weights, list) or len(weights) != 1 or
            weights[0].shape != (input_dim, output_dim)):
            raise ValueError('weights must be a list with single element'
                             ' with shape (input_dim, output_dim).')
        self.initial_weights = weights

        kwargs['input_shape'] = (self.input_dim,)
        super(FixedEmbedding, self).__init__(**kwargs)

    def build(self):
        self.input = K.placeholder(shape=(self.input_shape[0],
                                          self.input_length),
                                   dtype='int32')
        self.W = K.variable(self.initial_weights[0])
        self.trainable_weights = []
        self.regularizers = []

    def get_output_mask(self, train=None):
        X = self.get_input(train)
        if not self.mask_zero:
            return None
        else:
            return K.not_equal(X, 0)

    @property
    def output_shape(self):
        return (self.input_shape[0], self.input_length, self.output_dim)

    def get_output(self, train=False):
        X = self.get_input(train)
        if self.dropout:
            raise NotImplementedError()     # TODO
        out = K.gather(self.W, X)
        return out

    def get_config(self):
        config = {"name": self.__class__.__name__,
                  "input_dim": self.input_dim,
                  "output_dim": self.output_dim,
                  "input_length": self.input_length,
                  "mask_zero": self.mask_zero,
                  "dropout": self.dropout}
        base_config = super(FixedEmbedding, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))
