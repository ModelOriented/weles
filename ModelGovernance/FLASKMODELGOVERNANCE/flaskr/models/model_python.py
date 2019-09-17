from flaskr.requirement import requirement
from flaskr.database import database
from flaskr.environment import environment
from flaskr.data import data
import subprocess
import os
import hashlib


def predict(model, language_version, date, type, is_hash, hash, target):
    """Function makes a prediction using model written in Python in its virtual evironment.

    Parameters
    ----------
    model : FileStorage
        model in binary wrapped in FileStorage
    language_version : str
        version of the language
    date : str
        timestamp
    type : str
        type of the prediction
    is_hash : bool
        flag if dataset provided previously was hash
    hash : bool
        hash of the dataset
    target : str
        name of the target column

    Returns
    -------
    """

    # creating hash of requirements
    with open("flaskr/V/Models/" + model + "/requirements.txt", 'rb') as fd:
        m = requirement.create_hash_of_requirements(fd.read(), 'python', language_version)

    # running script "PREDICT.py" in the virtual environment
    if is_hash == 1:
        # case when dataset provided previously was hash
        x = subprocess.run(
            ["flaskr/VENV/python/ENV-" + m.hexdigest() + "/bin/python", "flaskr/additional_scripts/PREDICT.py", model,
             date, type, str(is_hash), hash, target], stdout=subprocess.PIPE)
    else:
        # case when dataset provided previously was csv
        x = subprocess.run(
            ["flaskr/VENV/python/ENV-" + m.hexdigest() + "/bin/python", "flaskr/additional_scripts/PREDICT.py", model,
             date, type, str(is_hash)], stdout=subprocess.PIPE)


def post_model(model, model_name, requirements, **kwargs):
    """Function for saving model and requirements in Python

    Parameters
    ----------
    model : FileStorage
        model in binary wrapped in FileStorage
    model_name : string
        model's name
    requirements : FileStorage
        requirements file in binary wrapped in FileStorage

    Returns
    -------
    int
        always 0
    bool
        flag if such model already existed
    """

    m = None

    # path to model
    path = "flaskr/V/Models/" + model_name

    # checking if file already exists
    model_exists = False
    if os.path.exists(path):
        model_exists = True
    else:
        os.mkdir(path)

        # saving model
        with open(path + "/model", 'wb') as fd:
            model.save(fd)

        # saving requirements
        with open(path + "/requirements.txt", 'w') as fd:
            requirement.create_requirements(requirements, fd, 'python')

    return 0, model_exists


def print_model(model, language_version):
    # creating hash of the requirements
    with open("flaskr/V/Models/" + model + "/requirements.txt", 'rb') as fd:
        m = requirement.create_hash_of_requirements(fd.read(), 'python', language_version)

    # printing model in its environment
    x = subprocess.run(
        ["flaskr/VENV/python/ENV-" + m.hexdigest() + "/bin/python", "flaskr/additional_scripts/PRINTMODEL.py", model],
        stdout=subprocess.PIPE)

    return x.stdout


def audit(model_name, dataset, is_hash, target, data_name, data_desc, measure, user, language_version, date):
    """Function to audit the Python model in the base

    Parameters
    ----------
    model_name : str
        name of the model
    dataset : str
        dataset in the csv format or hash of already uploaded
    is_hash : bool
        flag if dataset is a hash
    target : str
        name of the target column
    data_name : str
        name of the dataset
    data_desc : str
        description of the dataset
    measure : str
        name of the measure used in auditting
    user : str
        user's name
    language_version : str
        version of the language
    date : str
        timestamp

    Returns
    -------
    bool
        flag if audit has not exiested yet
    str
        hash of the dataset
    bool
        flag if dataset existed
    bool
        flag if alias for dataset was added
    """
    # creating hash of requirements
    with open("flaskr/V/Models/" + model_name + "/requirements.txt", 'rb') as fd:
        m = requirement.create_hash_of_requirements(fd.read(), 'python', language_version)

    # translating from str to bool
    if is_hash == '0':
        is_hash = False
    else:
        is_hash = True

    # saving metadata about the dataset
    hash, exists, alias = data.save_data(dataset, data_name, data_desc, user, is_hash)

    # check if audit has existed yet
    check = database.check_audit(model_name, hash, measure)

    if check:
        # case when audit has not existed yet
        x = subprocess.run(
            ["flaskr/VENV/python/ENV-" + m.hexdigest() + "/bin/python", "flaskr/additional_scripts/AUDIT.py",
             model_name, hash, target, measure, date], stdout=subprocess.PIPE)

    return check, hash, exists, alias
