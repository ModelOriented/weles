#! /usr/bin/python3

import os

from flask import Flask, g
from celery import Celery

celery = Celery(__name__, broker='amqp://guest@localhost//', backend='amqp')


def create_app(test_config=None):
    """
    App factory.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY=os.environ['SECRET_KEY'])
    celery.conf.update(app.config)

    # ensure the instance folder exists

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # adding model blueprint
    from . import model
    app.register_blueprint(model.bp)

    # adding datasets blueprint
    from . import datasets
    app.register_blueprint(datasets.bp)

    # adding users blueprint
    from . import users
    app.register_blueprint(users.bp)

    return app
