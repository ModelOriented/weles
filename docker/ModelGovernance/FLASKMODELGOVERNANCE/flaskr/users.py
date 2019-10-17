#! /usr/bin/python3

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, current_app, request

from flaskr.database import database
from flaskr.user import user

bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('/create_user', methods=('GET', 'POST',))
def create_user():
    info = dict(request.form)

    return user.create_user(info['user_name'], info['password'], info['mail'])
