"""Makes prediction using given model and data
"""

import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import sys
import pickle
import pandas as pd
import numpy as np

model = sys.argv[1]  # name fo the model
date = sys.argv[2]  # timestamp
type = sys.argv[3]  # type of prediction
is_hash = sys.argv[4]  # False if hash was not provided

# load model
with open("flaskr/V/Models/" + model + "/model", 'rb') as fd:
    model = pickle.load(fd)

# loading data
if is_hash == '0':
    # case when hash was not provided
    # reading data
    data = pd.read_csv("flaskr/tmp/" + date + ".csv", delimiter=',', header=0)
else:
    # case when hash was not provided
    # reading hash
    hash = sys.argv[5]
    # reading target column name
    target = sys.argv[6]

    # reading data
    data = pd.read_csv("flaskr/V/Datasets/" + hash, delimiter=',', header=0)
    # dropping target column
    data = data.drop(columns=target)

# making prediction
if type == 'prob':
    pred = model.predict_proba(data)
elif type == 'exact':
    pred = model.predict(data)

# saving result
with open("flaskr/tmp/" + date + ".txt", "wb") as fd:
    np.savetxt(fd, pred, delimiter=',')
