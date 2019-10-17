from flaskr.requirement import requirement
import os
import subprocess


def create_environment(requirements_path, language_version, timestamp):
    # creating hash of the requirements
    m = None
    with open(requirements_path, 'rb') as fd:
        m = requirement.create_hash_of_requirements(fd.read(), 'python', language_version)

    # checking if requested environment already exists
    if os.path.exists("flaskr/VENV/python/ENV-" + m.hexdigest()):
        return

    # create virtual environment
    subprocess.run(["virtualenv", "--python=flaskr/interpreters/python/Python-" + language_version + '/bin/python3',
                    "flaskr/VENV/python/ENV-" + m.hexdigest()])

    # install required packages
    subprocess.run(["flaskr/VENV/python/ENV-" + m.hexdigest() + "/bin/pip", "install", "-r", requirements_path])
