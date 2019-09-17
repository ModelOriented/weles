#! /usr/bin/python3

import subprocess
from flaskr.requirement import requirement
import os
from flaskr.database import database
from flaskr.environment import environment
from flaskr.data import data
import hashlib


def predict(model, language_version, date, type, is_hash, hash, target):
    """Make a prediction with R model in the base

    Parameters
    ----------
    model : FileStorage
        model in binary (RDS) wrapped in FileStorage
    language_version : str
        version of the language
    date : str
        timestamp
    type : str
        type of the prediction
    is_hash : bool
        flag if dataset provided previously was hash
    hash : str
        hash of the dataset
    target : str
        name of the target column

    Returns
    -------
    """
    # creating hash of requirements
    with open("flaskr/V/Models/" + model + "/requirements.txt", 'rb') as fd:
        m = requirement.create_hash_of_requirements(fd.read(), 'r', language_version)
    print(m.hexdigest())
    # running script "PREDICT.py" in the virtual environment
    if is_hash == 1:
        x = subprocess.run(
            'cd flaskr/VENV/r/ENV-' + m.hexdigest() + '; ../../../interpreters/r/R-' + language_version + '/bin/Rscript ../../../additional_scripts/PREDICT.r ' + model + ' ' + date + ' ' + type + ' ' + str(
                is_hash) + ' ' + hash + ' ' + target, stdout=subprocess.PIPE, shell=True)
    else:
        x = subprocess.run(
            'cd flaskr/VENV/r/ENV-' + m.hexdigest() + '; ../../../interpreters/r/R-' + language_version + '/bin/Rscript ../../../additional_scripts/PREDICT.r ' + model + ' ' + date + ' ' + type + ' ' + str(
                is_hash), stdout=subprocess.PIPE, shell=True)


def print_model(model, language_version):
    # create hash of requirements
    with open("flaskr/V/Models/" + model + "/requirements.txt", 'rb') as fd:
        m = requirement.create_hash_of_requirements(fd.read(), 'r', language_version)
    x = subprocess.run(
        'cd flaskr/VENV/r/ENV-' + m.hexdigest() + '; ../../../interpreters/r/R-' + language_version + '/bin/Rscript ../../../additional_scripts/PRINTMODEL.r ' + model,
        stdout=subprocess.PIPE, shell=True)
    return x.stdout


def post_model(model, model_name, requirements, sessionInfo, **kwargs):
    """Function for saving model and requirements in Python

    Parameters
    ----------
    model : FileStorage
        model in binary wrapped in FileStorage
    model_name : string
        model's name
    requirements : FileStorage
        requirements file in binary wrapped in FileStorage
    sessionInfo : FileStorage
        session info in binary wrapped in FileStorage

    Returns
    -------
    int
        number of packages to install
    bool
        flag if model already existed
    """

    m = None

    # path to model
    path = "flaskr/V/Models/" + model_name

    # checking if file already exists
    model_exists = False
    n = 0
    if os.path.exists(path):
        model_exists = True
    else:
        os.mkdir(path)

        # saving model
        with open(path + "/model", 'wb') as fd:
            model.save(fd)

        # saving requirements
        with open(path + "/requirements.txt", 'w') as fd:
            n += requirement.create_requirements(requirements, fd, 'r')

        # saving sessionInfo
        with open(path + "/sessionInfo.rds", 'wb') as fd:
            sessionInfo.save(fd)

    return n, model_exists


def audit(model_name, dataset, is_hash, target, data_name, data_desc, measure, user, language_version, date):
    # creating hash of requirements
    with open("flaskr/V/Models/" + model_name + "/requirements.txt", 'rb') as fd:
        m = requirement.create_hash_of_requirements(fd.read(), 'r', language_version)

    if is_hash == '0':
        is_hash = False
    else:
        is_hash = True

    hash, exists, alias = data.save_data(dataset, data_name, data_desc, user, is_hash)

    check = database.check_audit(model_name, hash, measure)

    if check:
        x = subprocess.run(
            'cd flaskr/VENV/r/ENV-' + m.hexdigest() + '; ../../../interpreters/r/R-' + language_version + '/bin/Rscript ../../../additional_scripts/AUDIT.r ' + model_name + ' ' + hash + ' ' + target + ' ' + measure + ' ' + str(
                date), stdout=subprocess.PIPE, shell=True)

    return check, hash, exists, alias
