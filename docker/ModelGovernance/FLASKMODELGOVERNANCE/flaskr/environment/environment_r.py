import os
from flaskr.requirement import requirement
import subprocess


def create_environment(requirements_path, language_version, timestamp):
    # creating hash of the requirements
    m = None
    with open(requirements_path, 'rb') as fd:
        m = requirement.create_hash_of_requirements(fd.read(), 'r', language_version)

    # checking if requested environment already exists
    if os.path.exists("flaskr/VENV/r/ENV-" + m.hexdigest()):
        return

    os.mkdir("flaskr/VENV/r/ENV-" + m.hexdigest())

    # create virtual environment
    subprocess.run(['flaskr/interpreters/r/R-' + language_version + '/bin/Rscript',
                    'flaskr/additional_scripts/CREATEENVIRONMENT.r', m.hexdigest(), requirements_path, timestamp])

    os.remove('flaskr/tmp/status_' + timestamp + '.txt')
