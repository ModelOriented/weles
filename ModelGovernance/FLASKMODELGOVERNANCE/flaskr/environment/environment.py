#! /usr/bin/python3

import subprocess

from flaskr.requirement import requirement
from . import environment_python
from . import environment_r

import os


def create_environment(requirements_path, language, language_version, timestamp):
    """Checks if the environment satisfying given requirements exists. If not, creates such an environment.
    """
    if language == 'python':
        environment_python.create_environment(requirements_path, language_version, timestamp)
    elif language == 'r':
        environment_r.create_environment(requirements_path, language_version, timestamp)
