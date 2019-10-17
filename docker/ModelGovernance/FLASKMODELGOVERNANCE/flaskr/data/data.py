import pandas as pd
import os
import hashlib
from datetime import datetime
from flaskr.database import database
import re
from io import StringIO


def hash_dataset(dataset):
    """Creates hash from dataset.

    Parameters
    ----------
    dataset : string
        dataset in csv format

    Returns
    -------
    string
        hash of the dataset
    """

    m = hashlib.sha256()

    m.update(bytes(dataset, 'utf-8'))

    return m.hexdigest()


def save_data(dataset, dataset_name, dataset_desc, owner, is_hash=False):
    """Function saves dataset if has not existed yet.

    Parameters
    ----------
    dataset : string
        dataset in csv format
    dataset_name : string
        name of the dataset
    dataset_desc : string
        description of the dataset
    owner : string
        user name

    Returns
    -------
    string
        Return hash of this dataset or None if dataset would have been None.
    bool
        Flag if dataset already existed
    """

    if dataset == None:
        return None

    # timestamp
    timestamp = datetime.now()

    # hashing dataset
    if is_hash == False:
        data_hash = hash_dataset(dataset)
    else:
        data_hash = dataset

    if os.path.exists("flaskr/V/Datasets/" + data_hash):
        # case when dataset already exists

        alias = database.insert_alias(data_hash, dataset_name, dataset_desc, owner, timestamp)

        exists = True
    else:
        # case when dataset has not existed yet
        if is_hash:
            return data_hash, False, False
        # collecting info about dataset

        # reading data
        dataset = pd.read_csv(StringIO(dataset))
        # number of rows
        number_of_rows = dataset.shape[0]
        # number of columns
        number_of_columns = dataset.shape[1]
        # all missing values
        missing_all = dataset.isna().sum().sum()
        # number of unique values in each column
        unique = list(dataset.nunique())
        # missing values in each column
        missing_col = list(dataset.isna().sum())

        columns = dataset.columns

        # saving dataset
        dataset.to_csv('flaskr/V/Datasets/' + data_hash, index=False)

        # insert metadata into dataset
        database.add_dataset(data_hash, number_of_rows, number_of_columns, columns, unique, missing_col, owner,
                             missing_all, timestamp)

        alias = database.insert_alias(data_hash, dataset_name, dataset_desc, owner, timestamp)

        exists = False

    return data_hash, exists, alias


def head(dataset_id, n):
    """Head of the data

    Parameters
    ----------
    dataset_id : string
        hash of the dataset
    n : int
        number of rows to return

    Returns
    -------
    pandas.DataFrame
        top n rows of the data
    """
    dataset = pd.read_csv("flaskr/V/Datasets/" + dataset_id)
    return dataset.head(n)
