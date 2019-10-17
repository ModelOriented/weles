import os
import psycopg2
import hashlib
from . import additional
import shutil
import re


def insert_into_database(model_name, model_desc, hash, target, train_data_id, timestamp, system, system_release,
                         distribution, distribution_version, language, language_version, architecture, processor,
                         user_name, tags, **kwargs):
    """Insert metadata of the model to the database

    Parameters
    ----------
    model_name : string
        name of the model
    model_desc : string
        model description
    hash : string
        model's hash
    target : string
        target column name
    train_data_id : string
        hash of the training dataset
    timestamp : string
        timestamp of the uploading
    system : string
        model's system
    system_release : string
        system's release
    distribution : string
        distribution of the system
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
    user_name : string
        user name
    tags : list
        list of tags of the model

    Returns
    -------
    """

    try:
        conn = psycopg2.connect(user='basic',
                                password=os.environ['database_password'],
                                host='127.0.0.1',
                                port='5432',
                                database='modelmetadata')

        cur = conn.cursor()

        # data to insert
        insert_data = (
        model_name, hash, target, train_data_id, timestamp, system, system_release, distribution, distribution_version,
        language, language_version, architecture, processor, model_desc, user_name)

        # query
        query = """insert into models (model_name, hash, target, train_data_id, timestamp, system, system_release, distribution, distribution_version, language, language_version, architecture, processor, description, owner)
			values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        # execution of the query
        cur.execute(query, insert_data)

        # query for the tags
        query = """insert into tags (model_name, tag) values(%s, %s)"""

        # inserting tags
        for tag in tags:
            cur.execute(query, (model_name, tag))

        # commit
        conn.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        shutil.rmtree('flaskr/V/Models/' + model_name, ignore_errors=True)
        shutil.rmtree('flaskr/V/Datasets/' + train_data_id, ignore_errors=True)
    finally:
        # closing database connection.
        if (conn):
            cur.close()
            conn.close()


def get_lang(model_name):
    """Get language of the model

    Parameters
    ----------
    model_name : string
        name of the model

    Returns
    -------
    tuple
        language and language version
    """

    try:
        conn = psycopg2.connect(user='basic',
                                password=os.environ['database_password'],
                                host='127.0.0.1',
                                port='5432',
                                database='modelmetadata')

        cur = conn.cursor()

        # query
        query = """select language, language_version from models where model_name = %s"""

        # format the model_name
        model_name = (model_name,)

        # execution of the query
        cur.execute(query, model_name)

        # fetching result
        lang = cur.fetchone()


    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (conn):
            cur.close()
            conn.close()

    return lang


def add_dataset(dataset_hash, number_of_rows, number_of_columns, columns, unique, missing_col, owner, missing_all,
                timestamp):
    """Insert dataset metadata

    Parameters
    ----------
    dataset_hash : string
        hash of the dataset
    number_of_rows : int
        number of rows in the dataset
    numer_of_columns : int
        number of columns in the dataset
    columns : list
        list with names of the columns
    unique : list
        list with number of unique values in each column
    missing_col : list
        list with number of missing values in each column
    owner : string
        owner of the dataset
    missing_all : int
        number of all missing values
    timestamp : string
        timestamp of uploading

    Returns
    -------
    """

    try:
        conn = psycopg2.connect(user='basic',
                                password=os.environ['database_password'],
                                host='127.0.0.1',
                                port='5432',
                                database='modelmetadata')

        cur = conn.cursor()

        # query for insertion
        query = """insert into datasets (dataset_id, number_of_rows, number_of_columns, timestamp, owner, missing)
				values(%s,%s,%s,%s,%s,%s)"""

        # data to insert
        dataset = (dataset_hash, number_of_rows, number_of_columns, timestamp, owner, int(missing_all))

        # execution of the query
        cur.execute(query, dataset)

        # query to insert the features of the dataset
        query = """insert into features (dataset_id, id, name, unique_val, missing) values (%s, %s, %s, %s, %s)"""
        for id, column in enumerate(columns):
            # execution of the query
            cur.execute(query, (dataset_hash, id, column, unique[id], missing_col[id]))

        # commit
        conn.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (conn):
            cur.close()
            conn.close()


def select_datasets(dataset=None):
    try:
        conn = psycopg2.connect(user='basic',
                                password=os.environ['database_password'],
                                host='127.0.0.1',
                                port='5432',
                                database='modelmetadata')

        cur = conn.cursor()

        if dataset is None:
            query = """select * from datasets"""
            cur.execute(query)
            result = cur.fetchall()
        else:
            query = """select * from datasets where dataset_id = %s"""
            cur.execute(query, (dataset,))
            result = cur.fetchone()


    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (conn):
            cur.close()
            conn.close()

    return result


def model_info(model_name):
    """Get metadata of the model

    Parameters
    ----------
    model_name : string
        name of the model

    Returns
    -------
    dict
        dictionary with all metadata of the model
    """

    try:
        conn = psycopg2.connect(user='basic',
                                password=os.environ['database_password'],
                                host='127.0.0.1',
                                port='5432',
                                database='modelmetadata')

        cur = conn.cursor()

        # query for selecting model's metadata
        query = """select m.model_name, m.hash, m.timestamp, m.system, m.system_release, m.distribution, m.distribution_version, m.language, m.language_version, m.architecture, m.processor, m.description, m.target, m.owner from models m where m.model_name = %s"""

        # execution of the dataset
        cur.execute(query, (model_name,))

        # fetching result
        model = cur.fetchone()

        # query for selecting dataset metadata
        query = """select d.dataset_id, d.number_of_rows, d.number_of_columns, d.timestamp, d.missing, d.owner from models m join datasets d on train_data_id = dataset_id where m.model_name = %s"""

        # execution of the query
        cur.execute(query, (model_name,))

        # fetching result
        data = cur.fetchone()

        # query for selecting features
        query = """select f.id, f.name, f.unique_val, f.missing from features f join models m on m.train_data_id = f.dataset_id where m.model_name = %s"""

        # execution of the query
        cur.execute(query, (model_name,))

        # fetching result
        columns = cur.fetchall()

        # query for selecting audits
        query = """select dataset_id, measure, value, user_name from audits where model_name = %s"""

        # execution of the query
        cur.execute(query, (model_name,))

        # fetching result
        audits = cur.fetchall()

        # query for selecting aliases
        query = """select d.name, d.description, d.timestamp, d.owner from datasets_aliases d join models m on m.train_data_id = d.dataset_id
				where m.model_name = %s"""

        # execution of the query
        cur.execute(query, (model_name,))

        # fetching result
        aliases = cur.fetchall()

        # constructing result
        result = {'model': model, 'data': data, 'columns': columns, 'audits': audits, 'aliases': aliases}

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (conn):
            cur.close()
            conn.close()

    return result


def insert_user(user_name, password, mail):
    """Insert user

    Parameters
    ----------
    user_name : string
        user name
    password : string
        password of the user
    mail : string
        user's mail

    Returns
    -------
    string
        Information if the insertion was successful
    """

    try:
        conn = psycopg2.connect(user='basic',
                                password=os.environ['database_password'],
                                host='127.0.0.1',
                                port='5432',
                                database='modelmetadata')

        cur = conn.cursor()

        # query for checking if user exists
        query = """select count(*) from users where user_name = %s"""

        # execution of the query
        cur.execute(query, (user_name,))

        # count of users
        count = cur.fetchone()[0]

        if count != 0:
            # case when user with such nick already exists
            result = "Such user already exists"
        else:
            # case when user can be inserted

            # query for insertion
            query = """insert into users values(%s,%s,%s)"""

            # user data
            user = (user_name, password, mail)

            # execution of the query
            cur.execute(query, user)

            # commit
            conn.commit()

            result = "User added"

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (conn):
            cur.close()
            conn.close()
        return result


def check_user(user_name, password):
    """Check if password matches user

    Parameters
    ----------
    user_name : string
        user name
    password : string
        user's password

    Returns
    -------
    bool
        True, if password matches user, False otherwise
    """

    if user_name is None or password is None:
        return False
    try:
        conn = psycopg2.connect(user='basic',
                                password=os.environ['database_password'],
                                host='127.0.0.1',
                                port='5432',
                                database='modelmetadata')

        cur = conn.cursor()

        # query for selecting password
        query = """select password from users where user_name = %s"""

        # formatting user
        user = (user_name,)

        # execution of the query
        cur.execute(query, user)

        # fetching password
        true_password = cur.fetchone()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (conn):
            cur.close()
            conn.close()

    # check
    if true_password is None:
        return False
    elif password == true_password[0]:
        return True
    else:
        return False


def search(language=None, language_version=None, row=None, column=None, missing=None, classes=None, owner=None,
           tags=None, regex=None):
    """Search for models

    Parameters
    ----------
    language : string
        model's language
    language_version : string
        language version
    row : string
        query for number of rows
    column : string
        query for number of columns
    missing : string
        query for number of missing values
    classes : string
        query for number of classes
    owner : string
        owner of the model
    tags : list
        list with tags of the model
    regex : string
        regex for name of the model

    Returns
    -------
    List of all models satisfying those restrictions
    """

    # parsing
    row = additional.parse(row)
    column = additional.parse(column)
    missing = additional.parse(missing)
    classes = additional.parse(classes)
    language_version = additional.parse(language_version, dots=True)

    # checking
    row = additional.check_values('d.number_of_rows', row)
    column = additional.check_values('d.number_of_columns', column)
    missing = additional.check_values('d.missing', missing)
    classes = additional.check_values('d.classes', classes)
    language_version = additional.check_values('m.language_version', language_version, True)

    # wrong query
    if (row and column and missing and classes and language_version) == False:
        return False

    try:
        conn = psycopg2.connect(user='basic',
                                password=os.environ['database_password'],
                                host='127.0.0.1',
                                port='5432',
                                database='modelmetadata')

        cur = conn.cursor()

        # initialization of the query
        query = """select distinct t.model_name from tags t join models m on m.model_name = t.model_name join datasets d on d.dataset_id = m.train_data_id where """

        # flag if first restriction has not appeared yet
        first = True

        if row == True and column == True and missing == True and classes == True and language_version == True and (
                tags is None) and (owner is None) and (language is None):
            # case when there is no restrictions
            # returning all models in the base

            # query for returning models
            query = "select model_name from models"

            # execution of the query
            cur.execute(query)

            # fetching result
            result = cur.fetchall()
        else:
            # case when there are some restrictions

            if tags is not None:
                # case when there are some tags provided

                tags = str(tags)

                # adding to query
                query += """t.tag in """ + '(' + tags[1:-1] + ')'

                # first restriction appeared
                first = False

            # adding to query rows
            query, first = additional.add_to_query(query, row, first)

            # adding to query columns
            query, first = additional.add_to_query(query, column, first)

            # adding to query missing values
            query, first = additional.add_to_query(query, missing, first)

            # adding to query classes
            query, first = additional.add_to_query(query, classes, first)

            # adding to query language version
            query, first = additional.add_to_query(query, language_version, first)

            if owner is not None:
                # case when owner was provided

                # adding to query
                if first:
                    query += 'm.owner = \'' + owner + '\''
                    first = False
                else:
                    query += ' and m.owner = \'' + owner + '\''
                    first = False

            if language is not None:
                # case when language was provided

                # adding to query
                if first:
                    query += 'm.language = \'' + language + '\''
                    first = False
                else:
                    query += ' and m.language = \'' + language + '\''

            # execution of the query
            cur.execute(query)

            # fetching result
            result = cur.fetchall()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (conn):
            cur.close()
            conn.close()

    if regex is not None:
        # case when regex was provided

        # constructing regex
        r = re.compile(regex)

        result2 = []
        for model in result:
            if r.search(model[0]) is not None:
                result2.append(model)
        result = result2

    return result


def get_target(model):
    """Get target of the model

    Parameters
    ----------
    model : string
        model name

    Returns
    -------
    string
        target of the model
    """

    try:
        conn = psycopg2.connect(user='basic',
                                password=os.environ['database_password'],
                                host='127.0.0.1',
                                port='5432',
                                database='modelmetadata')

        cur = conn.cursor()

        # query for selecting target
        query = """select target from models where model_name = %s"""

        # formatting model_name
        model_name = (model,)

        # execution of the query
        cur.execute(query, model_name)

        # fetching the result
        target = cur.fetchone()[0]


    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (conn):
            cur.close()
            conn.close()

    return target


def check_audit(model, dataset_id, measure):
    """Check if audit already exists

    Parameters
    ----------
    model : string
        name of the model
    dataset_id : string
        hash of the datasets
    measure : string
        name of the measure

    Returns
    -------
    bool
        True if audit does not exists, False otherwise
    """

    try:
        conn = psycopg2.connect(user='basic',
                                password=os.environ['database_password'],
                                host='127.0.0.1',
                                port='5432',
                                database='modelmetadata')

        cur = conn.cursor()

        # query for selecting audits
        query = """select count(*) from audits where model_name = %s and dataset_id = %s and measure = %s"""

        # execution of the query
        cur.execute(query, (model, dataset_id, measure))

        # count of the audits
        count = cur.fetchone()[0]

        if count != 0:
            result = False
        else:
            result = True

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (conn):
            cur.close()
            conn.close()
        return result


def insert_audit(model, dataset_id, measure, value, user_name):
    """Insert audit of the model

    Parameters
    ----------
    model : string
        name of the model
    dataset_id : string
        hash of the dataset
    measure : string
        name of the measure
    value : string
        value of the measure
    user_name : string
        name of the model

    Returns
    -------
    bool
        True if insertion of the audit was successful, False otherwise
    """

    try:
        conn = psycopg2.connect(user='basic',
                                password=os.environ['database_password'],
                                host='127.0.0.1',
                                port='5432',
                                database='modelmetadata')

        cur = conn.cursor()

        # query for audit insertion
        query = """insert into audits (model_name, dataset_id, measure, value, user_name) values
				(%s, %s, %s, %s, %s)"""

        # execution of the query
        cur.execute(query, (model, dataset_id, measure, float(value), user_name))

        # commit
        conn.commit()

        result = True

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        result = False
    finally:
        # closing database connection.
        if (conn):
            cur.close()
            conn.close()
        return result


def data_info(dataset_id):
    """Get metadata of the dataset

    Parameters
    ----------
    dataset_id : string
        hash of the dataset

    Returns
    -------
    dict
        dictionary with all metadata of the dataset
    """

    try:
        conn = psycopg2.connect(user='basic',
                                password=os.environ['database_password'],
                                host='127.0.0.1',
                                port='5432',
                                database='modelmetadata')

        cur = conn.cursor()

        # query for selecting metadata of the dataset
        query = """select number_of_rows, number_of_columns, timestamp, owner, missing
				from datasets where dataset_id = %s"""

        # execution of the query
        cur.execute(query, (dataset_id,))

        # fetching result
        data = cur.fetchone()

        # query for selecting features
        query = """select id, name, unique_val, missing from features where dataset_id = %s"""

        # execution of the query
        cur.execute(query, (dataset_id,))

        # fetching result
        columns = cur.fetchall()

        # query for aliases
        query = """select name, description, timestamp, owner from datasets_aliases where dataset_id = %s"""

        # execution of the query
        cur.execute(query, (dataset_id,))

        # fetching result
        aliases = cur.fetchall()

        # constructing result
        result = {'data': data, 'columns': columns, 'aliases': aliases}

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (conn):
            cur.close()
            conn.close()

    return result


def insert_alias(data_hash, dataset_name, dataset_desc, owner, timestamp):
    if dataset_name is None:
        return False

    try:
        conn = psycopg2.connect(user='basic',
                                password=os.environ['database_password'],
                                host='127.0.0.1',
                                port='5432',
                                database='modelmetadata')

        cur = conn.cursor()

        # query to check if alias exists
        query = """select count(*) from datasets_aliases where dataset_id = %s and name = %s"""

        # execution of the query
        cur.execute(query, (data_hash, dataset_name))

        # count of the aliases
        count = cur.fetchone()[0]

        if count == 0:
            # query for alias insertion
            query = """insert into datasets_aliases (dataset_id, name, description, timestamp, owner) values
					(%s, %s, %s, %s, %s)"""

            # execution of the query
            cur.execute(query, (data_hash, dataset_name, dataset_desc, timestamp, owner))

            # commit
            conn.commit()

            result = True
        else:
            result = False

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        result = False
    finally:
        # closing database connection.
        if (conn):
            cur.close()
            conn.close()
        return result
