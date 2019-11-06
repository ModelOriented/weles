cd /

if [ $1 = "all" ]
then
	/bin/bash /SERVER/ModelGovernance/download_all_PYTHON_versions.sh
elif [ $1 = "none" ]
then
	echo "No Python interpreter will be installed"
else
	/bin/bash /SERVER/ModelGovernance/download_PYTHON.sh /SERVER/ModelGovernance/FLASKMODELGOVERNANCE/flaskr/interpreters/python/ $1
fi

if [ $2 = "all" ]
then
	/bin/bash /SERVER/ModelGovernance/download_all_R_versions.sh
elif [ $2 = "none" ]
then
	echo "No R interpreter will be installed"
else
	/bin/bash /SERVER/ModelGovernance/download_R.sh /SERVER/ModelGovernance/FLASKMODELGOVERNANCE/flaskr/interpreters/r/ $2
fi
