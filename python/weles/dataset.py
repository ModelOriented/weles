"""@package docstring
The module with functions related to datasets in the **weles**
"""

import sys
import requests
import pickle
import os
import pandas as pd
import platform
import re
from io import StringIO
from datetime import datetime
from getpass import getpass

def upload(data, data_name, data_desc):
	"""Upload data to **weles**.

	Parameters
	----------
	data : array-like/string
		data to upload or path to this data
	data_name : string
		name of the dataset that will be visible in the weles base
	data_desc : string
		desciprtion of the data

	Returns
	-------
	string
		information if uploading data was successful

	Examples
	--------
	datasets.upload(iris, 'iris', 'Example dataset')
		-> user: 'example_user'
		-> password:
	"""

	user_name = input('user: ')
	password = getpass('password: ')

	if not isinstance(data, (str, pd.DataFrame)):
		raise ValueError("data must be a string or a data frame")
	if not isinstance(data_name, str):
		raise ValueError("data_name must be a string")
	if not isinstance(data_desc, str):
		raise ValueError("data_desc must be a string")
	if not isinstance(user_name, str):
		raise ValueError("user_name must be a string")
	if not isinstance(password, str):
		raise ValueError("password must be a string")

	# url to post
	url = 'http://192.168.137.64/datasets/post'

	# timestamp for temporary files
	timestamp = str(datetime.now().timestamp())

	# uploading data
	info = {'user_name': user_name, 'password': password, 'data_name': data_name, 'data_desc': data_desc}

	if type(data) == str:
		# case when data is a path

		data = pd.read_csv(data)
		info['data'] = data.to_csv(index=False)

		# request
		r = requests.post(url, data=info)
	else:
		# case when data is an object

		# conversion to pandas data frame
		data = pd.DataFrame(data)

		info['data'] = data.to_csv(index=False)

		# request
		r = requests.post(url, data = info)

	return r.text

def head(dataset_id, n=5):
	"""View the head of the dataset.

	Parameters
	----------
	dataset_id : string
		hash of the dataset
	n : int
		number of rows to show

	Returns
	-------
	pandas.DataFrame
		pandas DataFrame with top n rows

	Examples
	--------
	datasets.head('aaaaaaaaaaaaaaaaaaaaaaa')

	datasets.head(models.info('example_model')['data']['dataset_id'])

	datasets.head('aaaaaaaaaaaaaaaaaaaaaaa', n=10)
	"""

	if not isinstance(dataset_id, str):
		raise ValueError("dataset_id must be a string")
	if not len(dataset_id) == 64:
		raise ValueError("dataset_id must be 64 character long")
	if not isinstance(n, int):
		raise ValueError("n must be an integer")

	r = requests.get('http://192.168.137.64/datasets/' + dataset_id + '/head', data = {'n': n})

	return pd.read_csv(StringIO(r.text))

def get(dataset_id):
	"""Get dataset from the **weles** as dataframe.

	Parameters
	----------
	dataset_id : string
		hash of the dataset

	Returns
	-------
	pandas.DataFrame
		pandas Data Frame containing the requested dataset

	Examples
	--------
	datasets.get('aaaaaaaaaaaaaaaaaaaaaaa')

	datasets.get(models.info('example_model')['data']['dataset_id'])
	"""

	if not isinstance(dataset_id, str):
		raise ValueError("dataset_id must be a string")
	if not len(dataset_id) == 64:
		raise ValueError("dataset_id must be 64 character long")

	r = requests.get('http://192.168.137.64/datasets/' + dataset_id)

	return pd.read_csv(StringIO(r.text))

def info(dataset_id):
	"""Get all metadata about dataset

	Parameters
	----------
	dataset_id : string
		hash of the dataset

	Returns
	-------
	dict
		dictionary contating all metadata about the dataset

	Examples
	--------
	datasets.info('aaaaaaaaaaaaaaaaaaaaaaaa')
	"""

	if not isinstance(dataset_id, str):
		raise ValueError("dataset_id must be a string")
	if not len(dataset_id) == 64:
		raise ValueError("dataset_id must be 64 character long")

	r = requests.get('http://192.168.137.64/datasets/' + dataset_id + '/info')
	r = r.json()
	r['columns'] = pd.DataFrame(r['columns'])
	r['aliases'] = pd.DataFrame(r['aliases'])

	return r
