#! /usr/bin/python3

import sys
import re
import os
import hashlib
from . import requirement_python, requirement_r


def create_hash_of_requirements(requirements, language, language_version):
    """
    Returns a hash of the requirements.
    requirements - string
    """
    m = hashlib.sha256()
    m.update(bytes(language, 'utf-8'))
    m.update(bytes(language_version, 'utf-8'))
    m.update(requirements)
    return m


def create_requirements(requirements, req_fd, language):
    """
    Standarizes requirements - cast them to the supported ones and sorts them.
    requirements - file storage
    req_fd - file descriptor to requirements file
    """

    if language == 'python':
        return requirement_python.create_requirements(requirements, req_fd)
    elif language == 'r':
        return requirement_r.create_requirements(requirements, req_fd)
