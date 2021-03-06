# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow.compat.v2 as tf
import tensorflow.keras as tfk
tf.enable_v2_behavior()
from keras.layers import Activation, Dense, Input
from keras.models import Sequential, Model
from keras import backend as K

def iqnet_model(in_num, out_num, coding=256):
    e_in = tfk.Input(shape=(in_num, ), name='encoder_in')
    e = tfk.layers.Dense(1024, activation='elu', name='encoder_h1')(e_in)
    e = tfk.layers.Dense(512, activation='elu', name='encoder_h2')(e)
    e = tfk.layers.Dense(coding, activation='elu', name='encoder_h3')(e)
    coding_out = tfk.layers.Dense(coding, activation='elu', name='encoder_out')(e)
    encoder = tfk.Model(e_in, coding_out, name='Encoder')

    coding_in = tfk.Input(shape=(coding, ), name='decoder_in')
    d = tfk.layers.Dense(512, activation='elu', name='decoder_h1')(coding_in)
    d = tfk.layers.Dense(1024, activation='elu', name='decoder_h2')(d)
    d = tfk.layers.Dense(2048, activation='elu', name='decoder_h3')(d)
    d_out = tfk.layers.Dense(out_num, activation='sigmoid', name='decoder_out')(d)
    decoder = tfk.Model(coding_in, d_out, name='Decoder')

    spec_in = tfk.Input(shape=(in_num,), name='spec_in')
    spec_coding = encoder(spec_in)
    cont_out = decoder(spec_coding)
    iqnet = tfk.Model(spec_in, cont_out, name='iQNet')
    return iqnet, encoder, decoder

def save_iqnet_weights(model=None, name='hst+sdss'):
    # name : hst or hst+sdss
    cp_folder = './_model_weights/' + name + '_weights/'
    for i in range(len(model.get_weights())):
        if i%2 == 0:
            weight_name = 'layer_{}_weight'.format(int(i/2 + 1))
            print('Saving..' + weight_name)
            np.savez(cp_folder+weight_name, model.get_weights()[i])
        else:
            bias_name = 'layer_{}_bias'.format(int((i+1)/2))
            print('Saving..' + bias_name)
            np.savez(cp_folder+bias_name, model.get_weights()[i])
    return 0

def load_iqnet_weights(model=None, name='hst+sdss'):
    # name : hst or hst+sdss
    cp_folder = './_model_weights/' + name + '_weights/'
    model_weights = []
    for i in range(16):
        if i%2 == 0:
            weight_name = 'layer_{}_weight.npz'.format(int(i/2 + 1))
            print('Loading.. ' + weight_name)
            w = np.load(cp_folder + weight_name)
            model_weights.append(w['arr_0'])
            w.close()
        else:
            bias_name = 'layer_{}_bias.npz'.format(int((i+1)/2))
            print('Loading.. ' + bias_name)
            b = np.load(cp_folder + bias_name)
            model_weights.append(b['arr_0'])
            b.close()
    model.set_weights(model_weights)
    return 0