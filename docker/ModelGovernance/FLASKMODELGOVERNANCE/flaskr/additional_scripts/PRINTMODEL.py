"""Prints model.
"""

import pickle
import sys

# model name
model = sys.argv[1]

# loading model
with open("flaskr/V/Models/" + model + "/model", "rb") as fp:
    md = pickle.load(fp)

    print(md)
