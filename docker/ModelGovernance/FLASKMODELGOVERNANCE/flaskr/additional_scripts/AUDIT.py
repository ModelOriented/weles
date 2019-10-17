"""Auditing model
"""

import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import sys
import pickle
import pandas as pd
import numpy as np

# name of the model
model = sys.argv[1]
# data hash
hash = sys.argv[2]
# target column name
target = sys.argv[3]
# measure
measure = sys.argv[4]
# timestamp
date = sys.argv[5]

# load model
with open("flaskr/V/Models/" + model + "/model", 'rb') as fd:
    model = pickle.load(fd)

# loading data

data = pd.read_csv("flaskr/V/Datasets/" + hash, delimiter=',', header=0)
y = data[target]
X = data.drop(columns=target)

# making prediction
pred = model.predict(X)

if measure == 'acc':
    result = np.mean(pred == y)
elif measure == 'mae':
    result = np.mean(np.sum(np.abs(pred - y)))
elif measure == 'mse':
    result = np.mean(np.sum((pred - y) ** 2))

# saving result
with open("flaskr/tmp/" + date + ".txt", "w") as fd:
    fd.write(str(result))
