"""@package docstring
The module related to models in the **weles**
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
from tqdm import tqdm
import time

def upload(model, model_name, model_desc, target, tags, train_dataset, train_dataset_name=None, dataset_desc=None, requirements_file=None):
	"""Function uploads scikit-learn or keras model, the training set and all needed metadata to the **weles** base.

	Parameters
	----------
	model : scikit-learn or keras model or string
		model object or path to the model pickle
	model_name : string
		name of the model that will be visible in the **weles**
	model_desc : string
		description of the model
	tags : list
		list of tags
	train_dataset : pandas.DataFrame or string
		pandas.DataFrame or path to csv file (must contain '/') or hash of already uploaded data, structure X|Y is required
	train_dataset_name : string
		name of the dataset that will be visible in the **weles**
	dataset_desc : string
		description of the dataset
	requirements_file : string
		path to python style requirements file, can be easily obtained by running: "pip freeze > requirements.txt" at your command line
	user_name : string
		your user name
	password : string 
		your password

	Returns
	-------
	string
		id of the uploading

	Examples
	--------
	models.upload(model, 'Example_model', 'This is the example model', 'Species', ['example', 'easy'], iris, 'iris', 'Example dataset', 'req')
		-> user: Example user
		-> password:

	models.upload(model, 'Example_model', 'This is the example model', 'Species', ['example', 'easy'], 'aaaaaaaaaaaaaa', 'iris', 'Example dataset', 'req')
		-> user: Example user
		-> password:

	models.upload(model, 'Example_model', 'This is the example model', 'Species', ['example', 'easy'], 'aaaaaaaaaaaaaa', None, None, 'req')
		-> user: Example user
		-> password:
	"""

	user_name = input('user: ')
	password = getpass('password: ')

	if not isinstance(model_name, str):
		raise ValueError("model_name must be a string")
	if not isinstance(model_desc, str):
		raise ValueError("model_desc must be a string")
	if not isinstance(target, str):
		raise ValueError("target must be a string")
	if not isinstance(tags, list):
		raise ValueError("tags must be a list")
	if not isinstance(train_dataset, (str, pd.DataFrame)):
		raise ValueError("train_dataset must be a string or pandas data frame")
	if train_dataset_name is not None and not isinstance(train_dataset_name, str):
		raise ValueError("train_dataset_name must be a string")
	if dataset_desc is not None and not isinstance(dataset_desc, str):
		raise ValueError("dataset_desc must be a string")
	if requirements_file is not None and not isinstance(requirements_file, str):
		raise ValueError("requirements_file must be a string")
	if not isinstance(user_name, str):
		raise ValueError("user_name must be a string")
	if not isinstance(password, str):
		raise ValueError("password must be a string")

	timestamp = str(datetime.now().timestamp())

	if re.search('^[a-z0-9A-Z_]+$', model_name) is None:
		return "Your model name contains non alphanumerical signs."

	# url to post
	url = 'http://192.168.137.64/models/post'

	# collecting system info
	info = {'system': platform.system(),
			'system_release': platform.release(),
			'distribution': platform.linux_distribution()[0],
			'distribution_version': platform.linux_distribution()[1],
			'language': 'python',
			'language_version': platform.python_version(),
			'architecture': platform.architecture()[0],
			'processor': platform.machine()}

	info['model_name'] = model_name

	info['target'] = target


	# init of flag if train_dataset is a hash
	info['is_train_dataset_hash'] = 0

	# uploading model
	if type(model) == str:
		# case when model is a path
		files = {'model': open(model, 'rb')}
	else:
		# case when model is an object

		files = {'model': pickle.dumps(model)}

	# creating regexp to findout if the train_dataset is a path or id
	reg = re.compile("/")

	info['is_train_name'] = 1

	# uploading train dataset
	if type(train_dataset) == str and reg.search(train_dataset) is None:
		# case when train_dataset is a hash of already uploaded dataset

		info['train_dataset'] = train_dataset
		info['is_train_dataset_hash'] = 1

		if train_dataset_name is not None and dataset_desc is None:
			raise ValueError('If your dataset name is specified, you need to pass dataset_desc')
		if train_dataset_name is None and dataset_desc is not None:
			raise ValueError('If your dataset description is specified, you need to pass its name')

		if train_dataset_name is None:
			info['is_train_name'] = 0

	elif type(train_dataset) == str:
		# case when train_dataset is a path to dataset

		train_dataset = pd.read_csv(train_dataset)
		info['train_dataset'] = train_dataset.to_csv(index=False)

	else:
		# case when train_dataset is a matrix

		# conversion to pandas data frame
		train_dataset = pd.DataFrame(train_dataset)

		# uploading dataset
		info['train_dataset'] = train_dataset.to_csv(index=False)

	if type(model_desc) == str and reg.search(model_desc) is not None:
		info['model_desc'] = open(model_desc, 'rb').read()
	elif type(model_desc) == str:
		info['model_desc'] = model_desc

	if info['is_train_name'] == 1:
		info['train_data_name'] = train_dataset_name

		if type(dataset_desc) == str and reg.search(dataset_desc) is not None:
			info['dataset_desc'] = open(dataset_desc, 'rb').read()
		elif type(dataset_desc) == str:
			info['dataset_desc'] = dataset_desc

	# uploading requirements file
	files['requirements'] = open(requirements_file, 'rb')

	# setting session info flag
	info['is_sessionInfo'] = 0

	# user_name
	info['user_name'] = user_name

	# password
	info['password'] = password

	# tags
	info['tags'] = tags

	# creating request
	r = requests.post(url, files = files, data = info)

	return r.json()

def status(task_id, interactive = True):
	"""Get the information about the progress of the uploading model

	Parameters
	----------
	task_id : string
		task id, it is always returned by the models.upload function
	interactive : bool, optional
		display progress bar if true

	Returns
	-------
	dict
		dictionary with metadata about uploading model

	Examples
	--------
	models.status('aaaaaaaaaaaaaaaaaaaaaa')

	models.status('aaaaaaaaaaaaaaaaaaaaaa', interactive=False)

	models.status('aaaaaaaaaaaaaaaaaaaaaa')['model_existed']

	models.status('aaaaaaaaaaaaaaaaaaaaaa')['added_alias_for_data']
	"""

	# url
	url = 'http://192.168.137.64/models/status/' + task_id

	# getting metadata
	r = requests.get(url).json()

	# display progressbar
	if interactive:
		with tqdm(total = r['total']) as bar:
			bar.update(r['current'])
			bar.set_description(r['status'])
			prev = r['current']
			while r['state'] != 'SUCCESS':
				time.sleep(3)
				r = requests.get(url).json()
				bar.update(r['current'] - prev)
				bar.set_description(r['status'])
				prev = r['current']

	return r

def predict(model_name, X, pred_type = 'exact', prepare_columns = True):
	"""
	Function uses model in the database to make a prediction on X.

	Parameters
	----------
	model_name : string
		name of the model in the base that you want to use
	X : pandas.DataFrame/string
		pandas data frame or path to csv file (must containt '/') or hash of already uploaded dataset, must have column names if prepare_columns is set to False
	pred_type : string
		type of the prediction: exact/prob
	prepare_columns : boolean
		if true and if X is an object then take column names from model in the database

	Returns
	-------
	pandas.DataFrame
		Returns a pandas data frame with made predictions.

	Examples
	--------
	models.predict('example_model', iris.drop(column='Species'))

	models.predict('example_model', data, prepare_columns=False)
	"""

	if not isinstance(model_name, str):
		raise ValueError("model_name must be a string")
	if not isinstance(X, (str, pd.DataFrame)):
		raise ValueError("X must be a string or pandas.DataFrame")
	if not isinstance(pred_type, str):
		raise ValueError("pred_type must be a string")
	if not isinstance(prepare_columns, bool):
		raise ValueError("prepare_columns must be a bool")

	timestamp = str(datetime.now().timestamp())

	# url
	url = 'http://192.168.137.64/models/' + model_name + '/predict/' + pred_type

	# regexp to find out if X is a path
	reg = re.compile("/")

	# uploading data
	if type(X) == str and reg.search(X) is None:
		# case when X is a hash
		body = {'is_hash': 1}
		body['hash'] = X

		# request
		r = requests.get(url, data = body)
	elif type(X) == str:
		# case when X is a path

		body = {'is_hash': 0}
		X = pd.read_csv(X)
		body['data'] = X.to_csv(index=False)

		# request
		r = requests.get(url, data=body)
	else:
		# case when X is an object

		# conversion to pandas data frame
		X = pd.DataFrame(X)

		if prepare_columns:
			model_info = info(model_name)
			columns = model_info['columns']
			target = model_info['model']['target']
			columns = columns.sort_values('id')
			columns = columns.loc[columns['name'] != target, 'name']
			X.columns = columns

		body = {'is_hash': 0, 'data': X.to_csv(index=False)}

		# request
		r = requests.get(url, data = body)

	return pd.read_csv(StringIO(r.text), header=None)

def info(model_name):
	"""
	Get the information about model.

	Parameters
	----------
	model_name : string
		name of the model in the **weles** base

	Returns
	-------
	dict
		dictionary with fields: model, data, columns and audits containing all metadata about the model

	Examples
	--------
	models.info('example_model')

	models.info('example_model')['columns]'

	models.info('example_model')['data']['dataset_id']
	"""

	if not isinstance(model_name, str):
		raise ValueError("model_name must be a string")

	r = requests.get('http://192.168.137.64/models/' + model_name + '/info')
	r = r.json()
	r['audits'] = pd.DataFrame(r['audits'])
	r['columns'] = pd.DataFrame(r['columns'])
	r['aliases'] = pd.DataFrame(r['aliases'])

	return r

def search(language=None, language_version=None, row=None, column=None, missing=None, classes=None, owner=None, tags=None, regex=None):
	"""Search weles base for models with specific restrictions. If all parameters are set to None, then returns all models' name in weles.

	Parameters
	------
	language : string
		search only for models written in given language
	language_version : string
		string describing what version of language are in you interest
		examples:
			language_version = '>3.5.0;', language_version = '=3.6.0;', lanugage_version = '>3.3.3;<3.6.6;'
	row : string
		string describing how many rows should have training dataset
		examples:
			row = '<101;', row = '>120;', row = '>100;<200;', row = '=2222;'
	column : string
		string describing how many columns should have training dataset
		examples:
			column = '<101;', column = '>120;', column = '>100;<200;', column = '=22;'
	missing : string
		string descibing how many missing values should have training dataset
		examples:
			missing = '=0;', missing = '>120;', missing = '<10001;', missing = '>100;<200;'
	classes : string
		string descibing how many classes should have training dataset
		examples:
			classes = '=2;', classes = '<3;', classes = '>2;', classes = '>2;<11;'
	owner : string
		owner's user name
	tags : list
		list of tags, all should be strings
	regex : string
		regex for models' names

	Returns
	-------
	list
		Returns a list of models' names that satisfies given restrictions

	Examples
	--------
	models.search(language='r', column='>10;<20;', row='<2600;', tags=['iris', 'example'])

	models.search(owner='Example user')

	models.search(regex='^abc.*xxx$')
	"""

	if language is not None and not isinstance(language, str):
		raise ValueError("language must be a string")
	if language_version is not None and not isinstance(language_version, str):
		raise ValueError("language_version must be a string")
	if row is not None and not isinstance(row, str):
		raise ValueError("row must be a string")
	if column is not None and not isinstance(column, str):
		raise ValueError("column must be a string")
	if missing is not None and not isinstance(missing, str):
		raise ValueError("missing must be a string")
	if classes is not None and not isinstance(classes, str):
		raise ValueError("classes must be a string")
	if owner is not None and not isinstance(owner, str):
		raise ValueError("owner must be a string")
	if tags is not None and not isinstance(tags, list):
		raise ValueError("tags must be a list")
	if regex is not None and not isinstance(regex, str):
		raise ValueError("regex must be a string")

	data = {'language': language, 'language_version': language_version, 'row': row, 'column': column, 'missing': missing, 'classes': classes, 'owner': owner, 'tags': tags, 'regex': regex}
	r = requests.get('http://192.168.137.64/models/search', data=data)
	return r.json()['models']

def audit(model_name, measure, data, target, data_name=None, data_desc=None):
	"""Audit the model

	Parameters
	----------
	model_name : string
		name of the model in the **weles** base to make an audit of
	measure : string
		name of the measure used on model, must be one of supported
	data : array-like/string
		data frame to make an audit on or hash of already uploaded data in the **weles** or path to the dataset
	target : string
		name of the column in the dataset that should be used as the target
	data_name : string
		optional, name of the dataset that will be visible in the **weles**, unnecessary if data is a hash
	data_desc : string
		optional, description of the dataset, unnecessary if data is a hash

	Returns
	-------
	string/float
		return the result of the audit or information if something went wrong

	Examples
	--------
	models.audit('example_model', 'acc', iris, 'Species', 'iris', 'example dataset')
		-> user: 'example_user'
		-> password:

	models.audit('example_model', 'mae', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'target')
		-> user: 'example_user'
		-> password:
	"""

	user = input('user: ')
	password = getpass('password: ')

	if not isinstance(model_name, str):
		raise ValueError("model_name must be a string")
	if not isinstance(measure, str):
		raise ValueError("measure must be a string")
	if not isinstance(user, str):
		raise ValueError("user must be a string")
	if not isinstance(password, str):
		raise ValueError("password must be a string")
	if not isinstance(data, (pd.DataFrame, str)):
		raise ValueError("data must be a string or pd.DataFrame")
	if not isinstance(target, str):
		raise ValueError("target must be a string")
	if data_name is not None and not isinstance(data_name, str):
		raise ValueError("data_name must be a str")
	if data_desc is not None and not isinstance(data_desc, str):
		raise ValueError("data_name must be a str")

	info = {'model_name': model_name, 'measure': measure, 'user': user, 'password': password, 'target': target}

	timestamp = str(datetime.now().timestamp())
	del_data = False

	# regexp to find out if data is a path
	reg = re.compile("/")

	info['is_data_name'] = 1
	# uploading data
	if type(data) == str and reg.search(data) is None:
		# case when data is a hash
		info['is_hash'] = 1
		info['hash'] = data

		if data_name is not None and data_desc is None:
			raise ValueError('If your dataset name is specified, you need to pass dataset_desc')
		if data_name is None and data_desc is not None:
			raise ValueError('If your dataset description is specified, you need to pass its name')

		if data_name is None:
			info['is_data_name'] = 0

	elif type(data) == str:
		# case when data is a path
		info['is_hash'] = 0

		data = pd.read_csv(data)
		info['data'] = data.to_csv(index=False)
	else:
		# case when data is an object

		info['is_hash'] = 0

		# conversion to pandas data frame
		data = pd.DataFrame(data)

		info['data'] = data.to_csv(index=False)

	if info['is_data_name'] == 1:

		info['data_name'] = data_name
		if type(data_desc) == str and reg.search(data_desc) is not None:
			info['data_desc'] = open(data_desc, 'rb').read()
		elif type(data_desc) == str:
			info['data_desc'] = data_desc

	r = requests.post('http://192.168.137.64/models/audit', data=info)

	return r.json()

def requirements(model):
	"""Get the list of package requirements

	Parameters
	----------
	model : string
		name of the model

	Returns
	-------
	dict
		listed requirements

	Examples
	--------
	models.requirements('example_model')
	"""

	if not isinstance(model, str):
		raise ValueError("model must be a string")

	r = requests.get('http://192.168.137.64/models/' + model + '/requirements')
	return r.json()
