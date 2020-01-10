# Copyright 2020 The ASReview Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import scipy
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.wrappers.scikit_learn import KerasClassifier
from tensorflow.keras import regularizers

from asreview.models.lstm_base import _get_optimizer
from asreview.models.base import BaseModel
from asreview.utils import _set_class_weight


class DenseNNModel(BaseModel):
    "Dense neural network model"
    name = "nn-2-layer"

    def __init__(self, dense_width=128, optimizer='rmsprop',
                 learn_rate=1.0, regularization=0.01, verbose=0,
                 epochs=35, batch_size=32, shuffle=False, class_weight=30.0):
        super(DenseNNModel, self).__init__()
        self.dense_width = dense_width
        self.optimizer = optimizer
        self.learn_rate = learn_rate
        self.regularization = regularization
        self.verbose = verbose
        self.epochs = epochs
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.class_weight = _set_class_weight(class_weight)

        self._model = None
        self.input_dim = None

    def fit(self, X, y):
        if scipy.sparse.issparse(X):
            X = X.toarray()
        if self._model is None or X.shape[1] != self.input_dim:
            self.input_dim = X.shape[1]
            keras_model = create_dense_nn_model(
                self.input_dim, self.dense_width, self.optimizer,
                self.learn_rate, self.regularization, self.verbose)
            self._model = KerasClassifier(keras_model, verbose=self.verbose)

        self._model.fit(X, y, batch_size=self.batch_size, epochs=self.epochs,
                        shuffle=self.shuffle, verbose=self.verbose)

    def full_hyper_space(self):
        from hyperopt import hp
        hyper_choices = {
            "mdl_optimizer": ["sgd", "rmsprop", "adagrad", "adam", "nadam"]
        }
        hyper_space = {
            "mdl_vector_size": hp.quniform("mdl_vector_size", 16, 128, 16),
            "mdl_dense_width": hp.quniform("mdl_dense_width", 2, 100, 1),
            "mdl_epochs": hp.quniform("mdl_epochs", 20, 60, 1),
            "mdl_optimizer": hp.choice("mdl_optimizer",
                                       hyper_choices["mdl_optimizer"]),
            "mdl_learn_rate_mult": hp.lognormal("mdl_learn_rate_mult", 0, 1),
            "mdl_class_weight_inc": hp.lognormal("mdl_class_weight_inc", 3, 1),
            "mdl_regularization": hp.lognormal("mdl_regularization", -4, 2),
        }
        return hyper_space, hyper_choices


def create_dense_nn_model(vector_size=40,
                          dense_width=128,
                          optimizer='rmsprop',
                          learn_rate_mult=1.0,
                          regularization=0.01,
                          verbose=1):
    """Return callable lstm model.

    Arguments
    ---------

    Returns
    -------
    callable:
        A function that return the Keras Sklearn model when
        called.

    """
    def model_wrapper():
        model = Sequential()

        model.add(
            Dense(
                dense_width,
                input_dim=vector_size,
                kernel_regularizer=regularizers.l2(regularization),
                activity_regularizer=regularizers.l1(regularization),
                activation='relu',
            )
        )

        # add Dense layer with relu activation
        model.add(
            Dense(
                dense_width,
                kernel_regularizer=regularizers.l2(regularization),
                activity_regularizer=regularizers.l1(regularization),
                activation='relu',
            )
        )

        # add Dense layer
        model.add(
            Dense(
                1,
                activation='sigmoid'
            )
        )

        optimizer_fn = _get_optimizer(optimizer, learn_rate_mult)

        # Compile model
        model.compile(
            loss='binary_crossentropy',
            optimizer=optimizer_fn, metrics=['acc'])

        if verbose >= 1:
            model.summary()

        return model
    return model_wrapper
