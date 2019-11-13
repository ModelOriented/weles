# SYSTEM

FROM ubuntu:18.04 AS system

ARG database_password
ARG python_interpreter="all"
ARG r_interpreter="all"

ENV TZ=Europe
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# UPDATE

RUN apt-get update -y && apt-get upgrade -y

RUN apt-get install -y build-essential

RUN apt-get install sudo -y python3.7

RUN apt-get update -y && apt-get upgrade -y

RUN apt-get install -y zlib1g-dev libssl-dev libbz2-dev liblzma-dev libxml2-dev libcurl4-openssl-dev

RUN apt-get update -y && apt-get upgrade -y

# PYTHON VIRTUALENV

RUN apt-get update -y && apt-get upgrade -y

RUN apt-get install -y virtualenv

RUN virtualenv --python=python3.7 SERVER

# INSTALL PACKAGES

RUN /SERVER/bin/pip install --upgrade pip
RUN /SERVER/bin/pip install flask celery pandas

# UPDATE

RUN apt-get update -y && apt-get upgrade -y

# INSTALL POSTGRES

RUN apt-get install -y postgresql

RUN apt-get update -y && apt-get upgrade -y

RUN sudo apt install -y libpq-dev python3.7-dev

RUN apt-get update -y && apt-get upgrade -y

# COPY SOURCE CODE

COPY ModelGovernance SERVER/ModelGovernance

RUN sudo service postgresql start && sudo -u postgres psql --command "create database modelmetadata;" && sudo -u postgres psql --command "create user basic with password '$database_password';" && sudo -u postgres psql modelmetadata < /SERVER/ModelGovernance/modelmetadata.pgpsql

ENV FLASK_APP=flaskr

RUN apt-get update -y && apt-get upgrade -y

RUN /SERVER/bin/pip install psycopg2-binary

RUN apt-get install -y rabbitmq-server

RUN apt-get install -y wget

RUN apt-get install -y gcc make gfortran fort77 xorg-dev libblas-dev aptitude libreadline-dev gobjc++ gcc-multilib
RUN apt-get update -y && apt-get upgrade -y

RUN /bin/bash /SERVER/ModelGovernance/interpreters_installation.sh $python_interpreter $r_interpreter

ENTRYPOINT /bin/bash /SERVER/ModelGovernance/entrypoint.sh
