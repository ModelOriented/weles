from flaskr.database import database

import hashlib
from flaskr.database import database


def login(user_name, password):
    m = hashlib.sha256()
    m.update(bytes(password, 'utf-8'))
    password = m.hexdigest()
    return database.check_user(user_name, password)


def create_user(user_name, password, mail):
    m = hashlib.sha256()
    m.update(bytes(password, 'utf-8'))
    password = m.hexdigest()
    return database.insert_user(user_name, password, mail)
