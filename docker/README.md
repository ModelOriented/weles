# DOCKER

## Installation

You should set `database_password` arguments. Database password is a password of POSTGRESQL user that selects and inserts metadata in the server.

`python_interpreter` argument defines what *Python* interpreter you would like to have on server, possible values are:
* none
* all
* specific version, eg. 3.6.8

`r_interpreter` is similar to `python_interpreter` however referes to *R*

By default docker downloads all **R** and **Python** interpreters.

```
# build
sudo docker build weles/docker -t weles --build-arg database_password=$database_password --build-arg python_interpreter=3.6.8 --build-arg r_interpreter=none
```

## Run

To run a server you need to pass `SECRET_KEY` argument. `SECRET_KEY` is a server key. You need to also pass `database_password`, the same you passed during building the image.

```
# run
sudo docker run -ti -e SECRET_KEY='KEY' -e database_password=$database_password weles
```

## Install new interpreter

You may have running server for a while, however you need a new interpreter. You can use script "download_R.sh" or download_Python.sh" to download new version of interpreter to an existing container. To do so:

```
# access to the server
sudo docker exec -ti DOCKER_ID /bin/bash

# choose version of the interpreter
ver=3.6.1

# then for R simply run
/bin/bash /SERVER/ModelGovernance/download_R.sh /SERVER/ModelGovernance/FLASKMODELGOVERNANCE/flaskr/interpreters/r/ $ver

# or for Python simply run

/SERVER/ModelGovernance/download_PYTHON.sh /SERVER/ModelGovernance/FLASKMODELGOVERNANCE/flaskr/interpreters/python/ $ver
```

**After running your container, you have to change the urls in your client package to point your container.**
