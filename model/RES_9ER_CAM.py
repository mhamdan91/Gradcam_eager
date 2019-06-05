# Acknoledgement and Creditation
# This model is adapted from the tf.tensorflow.contrib.eager.python.examples.resnet50.
# Only a set of selected layers from the Original ResNet50 model are implemented
# The model definition is compatible with TensorFlow's eager execution.
# The output of this model is a single logit
# ==============================================================================
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools

import tensorflow as tf


layers = tf.keras.layers


class _IdentityBlock(tf.keras.Model):
  """_IdentityBlock is the block that has no conv layer at shortcut.

  Args:
    kernel_size: the kernel size of middle conv layer at main path
    filters: list of integers, the filters of 3 conv layer at main path
    stage: integer, current stage label, used for generating layer names
    block: 'a','b'..., current block label, used for generating layer names
    data_format: data_format for the input ('channels_first' or
      'channels_last').
  """

  def __init__(self, kernel_size, filters, stage, block, data_format):
    super(_IdentityBlock, self).__init__(name='')				# super refers to the parent class (identityBlock with method __init__
    filters1, filters2, filters3 = filters

    conv_name_base = 'res' + str(stage) + block + '_branch'

    self.conv2a = layers.Conv2D(filters1, (1, 1), name=conv_name_base + '2a', data_format=data_format)

    self.conv2b = layers.Conv2D(filters2, kernel_size, padding='same', data_format=data_format, name=conv_name_base + '2b')

    self.conv2c = layers.Conv2D( filters3, (1, 1), name=conv_name_base + '2c', data_format=data_format)


  def call(self, input_tensor, training=False,conv_out = True, mask=None):
    x = self.conv2a(input_tensor)

    x = tf.nn.elu(x)

    x = self.conv2b(x)

    x = tf.nn.elu(x)

    x = self.conv2c(x)

    x += input_tensor
    if conv_out:
      return tf.nn.elu(x), x
    else:
      return tf.nn.elu(x)


class _ConvBlock(tf.keras.Model):

  def __init__(self, kernel_size, filters, stage, block, data_format, strides=(2, 2)):
    super(_ConvBlock, self).__init__(name='')
    filters1, filters2, filters3 = filters

    conv_name_base = 'res' + str(stage) + block + '_branch'

    self.conv2a = layers.Conv2D(filters1, (1, 1), strides=strides, name=conv_name_base + '2a', data_format=data_format)

    self.conv2b = layers.Conv2D(filters2, kernel_size, padding='same', name=conv_name_base + '2b', data_format=data_format)

    self.conv2c = layers.Conv2D(filters3, (1, 1), name=conv_name_base + '2c', data_format=data_format)

    self.conv_shortcut = layers.Conv2D(filters3, (1, 1), strides=strides, name=conv_name_base + '1', data_format=data_format)

  def call(self, input_tensor, training=False, conv_out= True, mask=None):
    x = self.conv2a(input_tensor)

    x = tf.nn.elu(x)

    x = self.conv2b(x)

    x = tf.nn.elu(x)

    x = self.conv2c(x)

    shortcut = self.conv_shortcut(input_tensor)


    x += shortcut

    return tf.nn.elu(x)


# pylint: disable=not-callable
class Res9ER(tf.keras.Model):

  def __init__(self, data_format, name='', trainable=True, include_top=True, pooling=None, classes=1):    # modified
    super(Res9ER, self).__init__(name=name)

    valid_channel_values = ('channels_first', 'channels_last')
    if data_format not in valid_channel_values:
      raise ValueError('Unknown data_format: %s. Valid values: %s' % (data_format, valid_channel_values))
    self.include_top = include_top

    def conv_block(filters, stage, block, strides=(2, 2)):
      return _ConvBlock(3, filters, stage=stage, block=block, data_format=data_format, strides=strides)

    def id_block(filters, stage, block):
      return _IdentityBlock(3, filters, stage=stage, block=block, data_format=data_format)

    self.conv1 = layers.Conv2D(32, (7, 7), strides=(2, 2), data_format=data_format, padding='same', name='conv1')
    self.max_pool = layers.MaxPooling2D((3, 3), strides=(2, 2), data_format=data_format)

    self.l2a = conv_block([32, 32, 128], stage=2, block='a', strides=(1, 1))
    self.l2b = id_block([32, 32, 128], stage=2, block='b')

    self.avg_pool = layers.AveragePooling2D((23, 35), strides=(23, 35), data_format=data_format)  # modified for 5th

    if self.include_top:
      self.flatten = layers.Flatten()
      self.regressor = layers.Dense(classes, activation="elu", name='elu_FC')    # modified

    else:
      reduction_indices = [1, 2] if data_format == 'channels_last' else [2, 3]
      reduction_indices = tf.constant(reduction_indices)
      if pooling == 'avg':
        self.global_pooling = functools.partial(
            tf.reduce_mean,
            reduction_indices=reduction_indices,
            keepdims=False)
      elif pooling == 'max':
        self.global_pooling = functools.partial(
            tf.reduce_max, reduction_indices=reduction_indices, keepdims=False)
      else:
        self.global_pooling = None

  def call(self, inputs, training=True, conv_out=True, mask=None):
    x = self.conv1(inputs)

    x = tf.nn.elu(x)

    x = self.max_pool(x)

    x = self.l2a(x, training=training)

    x, x22 = self.l2b(x, training=training, conv_out=True)

    cam = x

    x = self.avg_pool(x)

    if self.include_top:
      if conv_out:
        return self.regressor(self.flatten(x)), cam
      else:
        return self.regressor(self.flatten(x))
    elif self.global_pooling:
      x = self.global_pooling(x)
      return tf.nn.elu(x)
    else:
      return x
