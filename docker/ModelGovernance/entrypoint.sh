source SERVER/bin/activate
cd SERVER/ModelGovernance/FLASKMODELGOVERNANCE/
service postgresql start
service rabbitmq-server start
celery worker -A celery_worker.celery --loglevel=info 1>worker.log 2>worker.err &
disown
/bin/bash
#source ../../bin/activate
#python -m flask run --host=0.0.0.0 --port=80 # 1>server.log 2>server.err &
#disown
#/bin/bash
