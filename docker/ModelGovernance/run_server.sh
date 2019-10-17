cd /root/SERVER/
source bin/activate
cd /root/SERVER/ModelGovernance/FLASKMODELGOVERNANCE/
celery worker -A celery_worker.celery --loglevel=info 1>worker.log 2>worker.err &
disown
export FLASK_APP=flaskr
python -m flask run --host=0.0.0.0 --port=80 1>server.log 2>server.err &
disown
