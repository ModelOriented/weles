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

**After running your container, you have to change the urls in your client package to point your container.**
