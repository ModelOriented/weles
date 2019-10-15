#! /usr/bin/python3

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, current_app, request

from datetime import datetime
import pickle

import os

from io import StringIO

import subprocess

import hashlib

import json
import pandas as pd

from flaskr.requirement import requirement
from flaskr.environment import environment
from flaskr.database import database
from flaskr.models import models, model_python, model_r
from flaskr.user import user
from . import celery

bp = Blueprint('models', __name__, url_prefix='/models')


@bp.route('/<model>', methods=('GET',))
def print_model(model):
    """Allows printing model in its environment.

    Parameters
    ----------
    model : string
        name of the model in the Model Base

    Returns
    -------
    string
        Printed model in virtual environment
    """

    # getting model's language and its varsion from database
    lang = database.get_lang(model)

    return models.print_model(model, lang[0], lang[1])


@bp.route('/post', methods=('GET', 'POST'))
def post_model():
    """Receives the model with requirements, system info, train dataset.

    Parameters
    ----------
    user_name : string
        user name
    password : string
        user's password
    model : FileStorage
        model in FileStorage wrapper
    requirements : FileStorage, optional
        requirements file in FileStorage wrapper
    sessionInfo : FileStorage, optional
        R's session info in FileStorage wrapper
    is_train_dataset_hash : string
        '0', if train dataset is not a hash, '1' otherwise
    train_dataset : string
        train dataset in csv format or hash of already uploaded
    train_dataset_name : string, optional
        name of the dataset, needed only when is_train_dataset_hash == '0'
    tags : MultiDict
        MultiDict of model's tags
    dataset_desc : string
        description of the dataset
    model_desc : string
        description of the model
    system : string
        system on which model was created
    system_release : string
        system's release
    distribution : string
        system's distribution
    distribution_vesrsion : string
        distribution's version
    language : string
        model's language
    language_version : string
        language's version
    architecture : string
        architecture of the computer where model was created
    processor : string
        computer's processor
    is_sessionInfo : string
        0, if sessionInfo was provided, 1 otherwise

    Returns
    -------
    Information if adding model was successful
    """

    # timestamp
    t = datetime.now()

    # language version and system
    info = dict(request.form)

    response = user.login(info['user_name'], info['password'])

    if response == False:
        return 'Wrong user or wrong password'

    # session info
    if info['is_sessionInfo'] == '1':
        sessionInfo = request.files['sessionInfo']
    else:
        sessionInfo = None

    # file storage for model
    model = request.files['model']

    # file storage for requirements
    requirements = request.files['requirements']

    # train dataset
    train_data = info['train_dataset']

    if info['is_train_name'] == '0':
        info['train_data_name'] = None
        info['dataset_desc'] = None

    # getting list of tags
    info['tags'] = request.form.getlist('tags')

    return models.post_model(model=model, train_data=train_data, requirements=requirements, sessionInfo=sessionInfo,
                             timestamp=t, **info)


@bp.route('/status/<task_id>', methods=('GET',))
def status(task_id):
    """Endpoint for status of uploading

    Parameters
    ----------
    task_id : string
        id of the task

    Returns
    -------
    dict
        dictionary with metadata about uploading
    """

    # get the result
    task = models.post_model_task.AsyncResult(task_id)

    if task.state == 'PENDING':
        # case when task has not starterd yet

        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'PENDING'
        }
    elif task.state == 'CREATING ENVIRONMENT' and task.info.get('language') == 'r':
        # case when R model is uploaded and environment is being created

        # reading package name that is now being installed
        t = task.info.get('timestamp')
        info = pd.read_csv("flaskr/tmp/status_" + t + ".txt", header=None)

        response = {
            'state': task.state,
            'current': int(info.iloc[0, 0]),
            'total': task.info.get('total'),
            'status': info.iloc[0, 1]
        }
    elif task.state == 'CREATING ENVIRONMENT' and task.info.get('language') == 'python':
        # case when python model is uploaded and environment is being created

        response = {
            'state': task.state,
            'current': task.info.get('current'),
            'total': task.info.get('total'),
            'status': 'UPLOADING',
            'info': task.info
        }
    elif task.state == 'UPLOADING':
        # remaining part of uploading

        response = {
            'state': task.state,
            'current': task.info.get('current'),
            'total': task.info.get('total'),
            'status': 'UPLOADING',
            'info': task.info
        }
    elif task.state == 'SUCCESS':
        # successfuly ended uploading

        response = {
            'state': 'SUCCESS',
            'current': task.info.get('total'),
            'total': task.info.get('total'),
            'status': 'SUCCESS',
            'info': {
                'model_existed': task.info.get('model_existed'),
                'training_data_hash': task.info.get('training_data_hash'),
                'training_data_existed': task.info.get('training_data_existed'),
                'added_alias_for_data': task.info.get('added_alias_for_data')
            }
        }
    else:
        # failure of uploading

        response = {
            'state': task.state,
            'status': 'UPLOAD FAILED'
        }

    return response


@bp.route('/<model>/explain', methods=('GET',))
def explain(model):
    """
    Return explainer for model. Only for scikit-learn models.
    """

    # creating hash of requirements
    with current_app.open_resource("V/Models/" + model + "/requirements.txt") as fd:
        m = requirement.create_hash_of_requirements(fd.read())

    # model path
    model = "flaskr/V/Models/" + model + "/model"

    # running script "explain.r" in virtual environment
    x = subprocess.run(
        ["Rscript", "flaskr/explain.r", model, "flaskr/VENV/python/ENV-" + m.hexdigest(), "flaskr/X", "flaskr/Y"],
        stdout=subprocess.PIPE)

    return x.stdout


@bp.route('/<model>/explain/<func>', methods=('GET',))
def explain_func(model, func):
    """
    Returns fields of the explainer. Only for scikit-learn models.
    """

    # creating hash of requirements
    with current_app.open_resource("V/Models/" + model + "/requirements.txt") as fd:
        m = requirement.create_hash_of_requirements(fd.read())

    # path to model
    model = "flaskr/V/Models/" + model + "/model"

    # running script "explain.r" in virtual environment
    x = subprocess.run(
        ["Rscript", "flaskr/explain.r", model, "flaskr/VENV/python/ENV-" + m.hexdigest(), "flaskr/X", "flaskr/Y", func],
        stdout=subprocess.PIPE)

    return x.stdout


@bp.route('/<model>/predict/<type>', methods=('GET', 'POST'))
def predict_model(model, type):
    """Endpoint for function runs model with given data in its virtual environment. Returns prediction.

    Parameters
    ----------
    model : string
        name of the model to make a prediction with
    type : string
        type of the prediction
    data : string
        data for prediction in csv format
    is_hash : string
        '0', if there is not hash of the already uploaded dataset, '1' otherwise
    hash : string, optional
        hash of the already uploaded dataset

    Returns
    -------
    string
        result as a csv
    """

    # date in timestamp to use for the names of temporary files
    date = str(datetime.now().timestamp())

    # received data

    # flag describing if hash was given
    info = dict(request.form)

    is_hash = int(info['is_hash'])

    if is_hash == 1:
        # case when hash was provided

        # reading hash
        hash = info['hash']
        target = database.get_target(model)
    else:
        # case when hash was not provided

        data = info['data']

        # saving data to temporary file
        with open('flaskr/tmp/' + date + '.csv', 'w') as fd:
            fd.write(data)

        hash = None
        target = None

    # getting model's language
    lang, lang_version = database.get_lang(model)

    # calling function for making prediction
    models.predict(model, lang, lang_version, date, type, is_hash, hash, target)

    if not is_hash == 1:
        # case when hash was not provided
        # removing temporary data file
        os.remove("flaskr/tmp/" + date + ".csv")

    # reading result
    with open("flaskr/tmp/" + date + ".txt", 'r') as fd:
        result = fd.read()

    # removing temporary result file
    os.remove("flaskr/tmp/" + date + ".txt")

    return result


@bp.route('/<model>/info', methods=('GET',))
def model_info(model):
    """Endpoint for metadata of the model

    Parameters
    ----------
    model : string
        name of the model

    Returns
    -------
    dict
        dictionary with all metadata of the model
    """

    # getting metadata
    info = database.model_info(model)

    # constructing field with model info
    model_info = {
        'model_name': info['model'][0],
        'hash': info['model'][1],
        'timestamp': info['model'][2],
        'system': info['model'][3],
        'system_release': info['model'][4],
        'distribution': info['model'][5],
        'distribution_version': info['model'][6],
        'language': info['model'][7],
        'language_version': info['model'][8],
        'architecture': info['model'][9],
        'processor': info['model'][10],
        'model_description': info['model'][11],
        'target': info['model'][12],
        'owner': info['model'][13]
    }

    # data info
    data = info['data']

    # constructing field with data metadata
    data_info = {
        'dataset_id': data[0],
        'number_of_rows': data[1],
        'number_of_columns': data[2],
        'timestamp': data[3],
        'missing': data[4],
        'owner': data[5]
    }

    # columns info
    columns = info['columns']

    # constructing field with columns metadata
    columns_info = pd.DataFrame(columns, columns=['id', 'name', 'unique', 'missing']).to_dict()

    # audits info
    audits = info['audits']

    # aliases info
    aliases = pd.DataFrame(info['aliases'], columns=['name', 'description', 'timestamp', 'owner']).to_dict()

    # constructing field with audits metadata
    audits_info = pd.DataFrame(audits, columns=['dataset_id', 'measure', 'value', 'user']).to_dict()

    # combining
    result = {
        'model': model_info,
        'data': data_info,
        'columns': columns_info,
        'audits': audits_info,
        'aliases': aliases
    }

    return result


@bp.route('/search', methods=('GET', 'POST'))
def search():
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
    tags : MultiDict
        list of tags, all should be strings
    regex : string
        regex for models' names

    Returns
    -------
    list
        Returns a list of models' names that satisfies given restrictions
    """

    info = dict(request.form)

    # parsing R's NAs
    for key in info.keys():
        if info[key] == 'NA':
            info[key] = None

    # creating list of tags from MultiDict
    info['tags'] = request.form.getlist('tags')
    if len(info['tags']) == 0:
        info['tags'] = None

    # search for models
    models = database.search(**info)

    # handling with wrong query
    if models == False:
        return "Wrong query"

    # formatting result
    result = []
    for model in models:
        result.append(model[0])

    return {'models': result}


@bp.route('/audit', methods=('GET', 'POST'))
def audit():
    """Endpoint for auditing the model

    Parameters
    ----------
    model_name : string
        name of the model in the weles base to make an audit of
    measure : string
        name of the measure used on model, must be one of supported
    user : string
        your user name
    password : string
        your password
    data : string
        data frame to make an audit of in csv format or hash of already uploaded data in the weles or path to the dataset
    target : string
        name of the column in the dataset that should be used as the target
    data_name : string
        optional, name of the dataset that will be visible in the weles, unnecessary if data is a hash
    data_desc : string
        optional, description of the dataset, unnecessary if data is a hash
    is_hash : string
        '0', if hash is provided, '1' otherwise
    hash : string, optional
        hash of already uploaded dataset

    Returns
    -------
    string/float
        return the result of the audit or information if something went wrong
    """

    # date in timestamp to use for the names of temporary files
    date = str(datetime.now().timestamp())

    info = dict(request.form)

    model_name = info['model_name']
    measure = info['measure']
    user_name = info['user']
    password = info['password']
    is_hash = info['is_hash']
    target = info['target']

    # checking the user
    response = user.login(user_name, password)

    if response == False:
        return 'Wrong user or wrong password'

    if is_hash == '1':
        # case when hash was provided
        data = info['hash']
    else:
        # case when hash was not provided
        data = info['data']

    if info['is_data_name'] == '1':
        data_name = info['data_name']
        data_desc = info['data_desc']
    else:
        data_name = None
        data_desc = None

    # making an audit
    check, hash, exists, alias = models.audit(model_name, data, is_hash, target, data_name, data_desc, measure,
                                              user_name, date)

    print(check, hash, exists, alias)

    if check:
        # case when making an audit was successful
        result = float(pd.read_csv("flaskr/tmp/" + date + ".txt", header=None).iloc[0, 0])

        database.insert_audit(model_name, hash, measure, result, user_name)
        os.remove("flaskr/tmp/" + date + ".txt")
    else:
        # case when such audit already existed
        result = False

    return {'audit_existed': not check, 'result': result, 'hash': hash, 'dataset_existed': exists, 'alias': alias}


@bp.route('/<model>/requirements', methods=("GET",))
def requirements(model):
    """Endpoint for getting requirements of the model

    Parameters
    ----------
    model : string
        name of the model

    Returns
    -------
    dict
        requirements of the model
    """

    # getting language of the model
    lang = database.get_lang(model)[0]

    # reading requirements
    if lang == 'python':
        req = pd.read_csv('flaskr/V/Models/' + model + '/requirements.txt', sep='==', header=None)
    elif lang == 'r':
        req = pd.read_csv('flaskr/V/Models/' + model + '/requirements.txt', sep=',', header=None)

    # formatting result
    result = {}
    for i in range(req.shape[0]):
        result[req.iloc[i, 0]] = req.iloc[i, 1]

    return result
