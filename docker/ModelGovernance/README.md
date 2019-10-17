# WELES BASE

This is the **weles** base. Here are stored all models, datasets and here are done all operations.

# Installation

To install the **weles** base on your server (LINUX):
* create **python** virtual environment called *SERVER*
* clone the repo
* move the directory *ModelGovernance* into *SERVER*
* from root run with bash *download_all_PYTHON_versions.sh*
* from root run with bash *download_all_R_versions.sh*

Downloading **python** and **R** interpreters may take few hours or even more than a day.

```
cd /
virtualenv --python=python3.7 SERVER
git clone https://github.com/ModelOriented/weles.git
mv weles/ModelGovernance SERVER
bash download_all_PYTHON_versions.sh
bash download_all_R_versions.sh
```

Then install and configurate the celery and **RabbitMQ**.

At the end install the relational database *modelmetadata.pqsql*.

# Running the base

## With script

```
bash run_server.sh
```

## Manually

You will need to terminals. In first type

```
export FLASK_APP=flaskr
cd SERVER/ModelGovernance/FLASKMODELGOVERNANCE
python -m flask run [--host][--port]
```

In the second terminal type

```
celery worker -A celery_worker.celery [--loglevel=info]
```
