# SYSTEM

FROM ubuntu:18.04 AS system

ARG database_password

RUN echo $database_password

# UPDATE

RUN apt-get update -y && apt-get upgrade -y

RUN apt-get install sudo

RUN apt-get install -y python3.7

RUN apt-get install -y zlib1g-dev

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

RUN apt-get install -y gcc make
RUN apt-get update -y && apt-get upgrade -y

RUN cd /

RUN /bin/bash /SERVER/ModelGovernance/download_all_PYTHON_versions.sh

RUN /bin/bash /SERVER/ModelGovernance/download_all_R_versions.sh

ENTRYPOINT /bin/bash /SERVER/ModelGovernance/entrypoint.sh
