# Simple usage in Python

## Creating an account
To be able to upload your model you need to have an account on **weles**. So here is what you need to do:

```
from weles import users

users.create()
```

You will receive information if your account was created correctly.

## Uploading model
First you need to have a trained scikit-learn or keras model. Let's make a scikit random forest.

### Example
```
from sklearn import datasets
from sklearn.ensemble import RandomForestClassifier

data = datasets.load_wine()
model = RandomForestClassifier(n_estimators = 777)
model.fit(data.data, data.target)
```

To upload the model to the base you need to import client package and pass classifier, its name that will be visible in the **weles**, its description, list of tags, training dataset with target column and with the column names, its name, its description, requirements file, your user name and password.

So first let's prepare our data.

```
import pandas as pd

train_data_to_upload = pd.DataFrame(data.data, colums=data.feature_names)
train_data_to_upload['target'] = data.target
```

Due to our respect for your privacy we do not investigate your environment. To allow us to make a virtualization please run in command line:

```
pip freeze > requirements.txt
```

This will make a *Python* style requirements file.

Now we are ready to push our model to the base. Its name has to be unique in the base. Dataset name either.

```
from weles import models

models.upload(model, 'example_model', 'This is an example model.', 'target', ['example', 'easy'], train_data_to_upload, 'example_data', 'This is an example dataset', 'requirements.txt')
```

In this moment *model* is being uploaded to the **weles**. If requested environment had not been already created in the **weles**, it will be created. You do not have to wait for its creation. You will receive special *id*, that you can pass to the function *status* to check the progress of the uploading.

### Status

```
models.status(id)
```

### Summary

You can also pass your model as the path (must contain **/** sign) to *Python* pickle. Training data parameter can be a path to *.csv* file (must contain **/** sign) or *hash* of already uploaded dataset in the **weles**.

## Reading an info about model

If you want to read an info about the model already uploaded in **weles** you can run:

```
from weles import models

models.info("example_model")
models.info("example_model")['columns']
models.info("example_model")['audits']
models.info("example_model")['data']['dataset_id']
```

*"example_model"* is a name of **weles** model.

Returned value is a *Python* dictionary containing all information about the model.

## Making predictions

If you want to make a prediction, type:

```
from weles import models

models.predict("example_model", data)
```

*"example_model"* is the name of **weles** model, *data* is the data frame with named columns without target column, or path to *.csv* (must contain **/** sign) file or *hash* of already uploaded data.

Be aware that some models may require from you exactly the same column names in passed data. If you are passing data as an object then by default columns are fetched from original dataset. If you do not want this behaviour set *prepare_data* to *False*. You may easily manually obtain columns with:

```
columns = models.info("example_model")['columns']
```

## Searching model

You can also search models in **weles** satisfying some restrictions.

```
from weles import models

models.search(row = '>1000;<10000;', column='=12;', user='Example user', tags = ['example', 'easy'])
```

You will get list of all models satisfying your restrictions.

## Testing model

You can also test already uploaded model on some new data.

```
models.audit('model_name', 'acc', new_data, 'target_column', 'new_data', 'new data for testing')
```
