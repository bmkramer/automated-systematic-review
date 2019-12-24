# Copyright 2019 The ASReview Authors. All Rights Reserved.
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

from asreview.models.sklearn_models import SVCModel, NBModel, RFModel
from asreview.models.lstm_base import LSTMBaseModel
from asreview.models.lstm_pool import LSTMPoolModel


def get_model_class(model):
    "Get class of model from string."
    models = {
        "svm": SVCModel,
        "nb": NBModel,
        "lstm_base": LSTMBaseModel,
        "lstm_pool": LSTMPoolModel,
        "rf": RFModel,
    }
    return models.get(model, None)
