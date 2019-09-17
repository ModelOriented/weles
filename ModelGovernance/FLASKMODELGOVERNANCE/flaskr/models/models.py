from . import model_python, model_r
from flaskr.database import database
from flaskr.environment import environment

from flaskr import celery
from datetime import datetime
from flaskr.data import data
import hashlib


def print_model(model, language, language_version):
    """
    Wrapper for printing models written in different languages

    model - model_name, string
    language - model's language, string
    language_version - version of the language, string
    """

    if language == 'python':
        result = model_python.print_model(model, language_version)
    elif language == 'r':
        result = model_r.print_model(model, language_version)

    return result


def hash_model(model):
    """
    Function calculates hash of the model.

    Parameters
    ----------
    model : string
        model's name

    Returns
    -------
    string
        model's hash
    """

    # reading model in binary mode
    with open("flaskr/V/Models/" + model + "/model", 'rb') as fd:
        m = hashlib.sha256()
        m.update(fd.read())

    return m.hexdigest()


def post_model(model, model_name, model_desc, target, is_train_dataset_hash, train_data, train_data_name, dataset_desc,
               system, system_release, distribution, distribution_version, language, language_version, architecture,
               processor, requirements, sessionInfo, timestamp, user_name, tags, **kwargs):
    """
    Wrapper for adding models written in diffrent languages

    Parameters
    ----------
    model : FileStorage
        model in binary wrapped in FileStorage
    model_name : string
        name of the model
    model_desc : string
        desciprition of the model
    target : string
        name of the target column
    is_train_dataset_hash : bool
        flag if dataset is a hash
    train_data : string
        dataset in csv format or hash of already uploaded dataset
    train_data_name : string
        name of the dataset
    dataset_desc : string
        description of the dataset
    system : string
        name of the model's system
    system_release : string
        system's release
    distribution : string
        system's distribution
    distribution_version : string
        distribution's version
    language : string
        model's language
    language_version : string
        language's version
    architecture : string
        computer's architecture
    processor : string
        computer's processor
    requirements : FileStorage
        requirements file in binary wrapped in FileStorage
    sessionInfo : FileStorage
        R's sessionInfo in binary wrapped in FileStorage or None
    timestamp : string
        timestamp
    user_name : string
        user's name
    tags : list
        list with model's tags
    """

    # choosing proper function
    if language == 'python':
        n, model_exists = model_python.post_model(model=model, model_name=model_name, requirements=requirements)
    elif language == 'r':
        n, model_exists = model_r.post_model(model=model, model_name=model_name, requirements=requirements,
                                             sessionInfo=sessionInfo)

    # asynchronous task for uploading model
    task = post_model_task.delay(n, model_exists, model_name, model_desc, target, is_train_dataset_hash, train_data,
                                 train_data_name, dataset_desc, system, system_release, distribution,
                                 distribution_version, language, language_version, architecture, processor, timestamp,
                                 user_name, tags, **kwargs)

    # returning task's id
    return {'task_id': task.id}


@celery.task(bind=True)
def post_model_task(self, n, model_exists, model_name, model_desc, target, is_train_dataset_hash, train_data,
                    train_data_name, dataset_desc, system, system_release, distribution, distribution_version, language,
                    language_version, architecture, processor, timestamp, user_name, tags, **kwargs):
    """Asynchronous task for uploading model

    Parameters
    ----------
    n : int
        number of packages to install
    model_exists : bool
        flag if model existed before
    model_name : string
        name of the model
    model_desc : string
        desciprition of the model
    target : string
        name of the target column
    is_train_dataset_hash : bool
        flag if dataset is a hash
    train_data : string
        dataset in csv format or hash of already uploaded dataset
    train_data_name : string
        name of the dataset
    dataset_desc : string
        description of the dataset
    system : string
        name of the model's system
    system_release : string
        system's release
    distribution : string
        system's distribution
    distribution_vesrion : string
        distribution's version
    language : string
        model's language
    language_version : string
        language's version
    architecture : string
        computer's architecture
    processor : string
        computer's processor
    timestamp : string
        timestamp
    user_name : string
        user's name
    tags : list
        list with model's tags

    Returns
    -------
    dict
        dictionary with metadata about uploading
    """

    # timestamp for temporary files
    t = str(datetime.now().timestamp())

    # init of the task's state
    self.update_state(state='UPLOADING',
                      meta={
                          'current': 0, 'total': n + 5,
                          'status': 'creating environment',
                          'language': language,
                          'timestamp': t
                      }
                      )
    if model_exists:
        # case when model already existed, return fixed metadata
        return {'model_existed': model_exists, 'training_data_hash': False, 'training_data_existed': False,
                'added_alias_for_data': False}

    # update task's state - starting creating environment
    self.update_state(state='CREATING ENVIRONMENT',
                      meta={
                          'current': 1, 'total': n + 5,
                          'status': 'creating environment',
                          'language': language,
                          'timestamp': t
                      }
                      )

    # run proper create environment function
    if language == 'python':
        environment.create_environment('flaskr/V/Models/' + model_name + "/requirements.txt", 'python',
                                       language_version, t)
    elif language == 'r':
        environment.create_environment('flaskr/V/Models/' + model_name + "/requirements.txt", 'r', language_version, t)

    # update task's state
    self.update_state(state='UPLOADING',
                      meta={
                          'current': n + 2, 'total': n + 5,
                          'status': 'saving dataset',
                          'language': language,
                          'timestamp': t
                      }
                      )

    # saving training data
    if is_train_dataset_hash == '1':
        is_hash = True
    else:
        is_hash = False

    # saving data's metadata
    train_hash, exists, alias = data.save_data(train_data, train_data_name, dataset_desc, user_name, is_hash)

    # update task's state
    self.update_state(state='UPLOADING',
                      meta={
                          'current': n + 3, 'total': n + 5,
                          'status': 'hashing model',
                          'language': language,
                          'timestamp': t
                      }
                      )

    # model hash
    hash = hash_model(model_name)

    # update task's state
    self.update_state(state='UPLOADING',
                      meta={
                          'current': n + 4, 'total': n + 5,
                          'status': 'saving metadata',
                          'language': language,
                          'timestamp': t
                      }
                      )

    # insert metadata into database
    database.insert_into_database(model_name, model_desc, hash, target, train_hash, timestamp, system, system_release,
                                  distribution, distribution_version, language, language_version, architecture,
                                  processor, user_name, tags, **kwargs)

    # return metadata
    return {'total': n + 5, 'model_existed': model_exists, 'training_data_hash': train_hash,
            'training_data_existed': exists, 'added_alias_for_data': alias}


def predict(model, language, language_version, date, type, is_hash, hash, target):
    """Wrapper for making predictions using models written in different languages.

    Parameters
    ----------
    model : string
        model's name
    language : string
        model's language
    date : string
        timestamp
    type : string
        type of the prediction
    is_hash : bool
        flag if hash of the dataset was provided
    hash : string
        hash of the dataset if was provided
    target : string
        name of the target column

    Returns
    -------
    """

    # running proper function
    if language == 'python':
        model_python.predict(model, language_version, date, type, is_hash, hash, target)
    elif language == 'r':
        model_r.predict(model, language_version, date, type, is_hash, hash, target)


def audit(model_name, data, is_hash, target, data_name, data_desc, measure, user, date):
    """Wrapper function for making audits

    Parameters
    ----------
    model_name : string
        model's name
    data : string
        data in csv format or hash of already uploaded dataset
    is_hash : bool
        flag if data is a hash
    target : string
        name of the target column
    data_name : string
        name of the dataset
    data_desc : string
        dataset description
    measure : string
        measure to use
    user : string
        user's name
    date : string
        timestamp

    Returns
    -------
    bool
        flag if audit has not existed yet
    string
        data's hash
    bool
        flag if dataset already existed
    bool
        flag if alias for dataset was added
    """

    # getting model's language
    language, language_version = database.get_lang(model_name)

    # running proper function
    if language == 'python':
        return model_python.audit(model_name, data, is_hash, target, data_name, data_desc, measure, user,
                                  language_version, date)
    elif language == 'r':
        return model_r.audit(model_name, data, is_hash, target, data_name, data_desc, measure, user, language_version,
                             date)
