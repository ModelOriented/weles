from flask import Blueprint, flash, g, redirect, render_template, request, url_for, current_app, request

from flaskr.database import database
from flaskr.data import data
from flaskr.user import user

import pandas as pd

bp = Blueprint('datasets', __name__, url_prefix='/datasets')


@bp.route('/', methods=('GET',))
def print_datasets():
    datasets = database.select_datasets()

    result = ""
    for dataset in datasets:
        result += str(dataset) + '\n'

    return result


@bp.route('/<hash>', methods=('GET',))
def get_dataset(hash):
    with open('flaskr/V/Datasets/' + hash, 'r') as fd:
        result = fd.read()
    return result


@bp.route('/<hash>/head', methods=('GET', 'POST'))
def head(hash):
    n = int(request.form['n'])
    return data.head(hash, n).to_csv(index=False)


@bp.route('/post', methods=('GET', 'POST'))
def post_data():
    # language version and system
    info = dict(request.form)

    response = user.login(info['user_name'], info['password'])

    if response == False:
        return 'Wrong user or wrong password'

    # dataset = request.files['data']
    dataset = info['data']

    hash, exists, alias = data.save_data(dataset, info['data_name'], info['data_desc'], info['user_name'], False)

    result = ""

    if exists:
        result += "Such dataset already exists, "
    else:
        result += "Dataset added, "

    if alias:
        result += "alias added."
    else:
        result += "alias already exists."

    return result


@bp.route('/<dataset_id>/info', methods=('GET',))
def data_info(dataset_id):
    info = database.data_info(dataset_id)

    result = {
        'number_of_rows': info['data'][0],
        'number_of_columns': info['data'][1],
        'timestamp': info['data'][2],
        'owner': info['data'][3],
        'missing': info['data'][4],
        'columns': pd.DataFrame(info['columns'], columns=['id', 'name', 'unqiue', 'missing']).to_dict(),
        'aliases': pd.DataFrame(info['aliases'], columns=['name', 'description', 'timestamp', 'owner']).to_dict()
    }

    return result
