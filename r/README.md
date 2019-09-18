# Simple usage in R

## Creating an account
To upload your model you need to create your account.

```
library(weles)

users_create()
```

In response you will get information if your account was created succesfully.

## Uploading model
First you need to have a trained mlr, caret or parsnip model. Let's make an mlr random forest.

### Example
```
library(mlr)

task <- makeClassifTask(data = iris, target = 'Species')
model <- makeLearner("classif.randomForest")
model <- train(model, task)
```

To upload the model to the base you need to import client package and pass classifier, its name that will be visible in the **weles**, its description, tags, training dataset with target column and column names, its name, its description, your user name and password. Names should be unique.

```
library('weles')

models_upload(model, 'example_model', 'This is an example model.', 'Species', c('example', 'easy'), iris, 'example_data', 'This is an example data')
models_upload(model, 'example_model', 'This is an example model.', 'Species', c('example', 'easy'), data_hash)
models_upload(model, 'example_model', 'This is an example model.', 'Species', c('example', 'easy'), data_hash, 'example_data', 'This is an example data')
```

In this moment *model* is being uploaded to the **weles**. If requested environment had not been already created in the **weles**, it will be created. You will receive special *id*, that you can pass to the function *status* to check the progress of the uploading.

### Status

```
models_status(id)
models_status(id, interactive=FALSE)
```

### Summary

You can also pass your model as the path (must contain **/** sign) to *.rds* file. Training data parameter can be a path to *.csv* file (must constain **/** sign) or *hash* of already uploaded dataset in the **weles**. 

**Please, have loaded in your namespace only packages that are required to make a model, because creating an environment will take a while**

## Reading an info about model

If you want to read an info about the model already uploaded in **weles** you can run:

```
library('weles')

models_info("example_model")
models_info("example_model")$columns
models_info("example_model")$audits
models_info("example_model")$data$dataset_id
```

*"example_model"* is a name of **weles** model.

Returned value is a *R* named list containing all information about the model.

## Making predictions

If you want to make a prediction, type:

```
library('weles')

models_predict("example_model", data)
models_predict("example_model", data, prepare_columns=FALSE)
```

*"example_model"* is the name of **weles** model, *data* is the data frame with named columns without target column, or path to *.csv* (must contain **/** sign) file or *hash* of already uploaded data.

Be aware that some models may require from you exactly the same column names in passed data. If you passed data as an object then column names will be fetched by default. If you do not want this behaviour pass as argument *prepare_data* value *False*. You may also easily manually obtain columns with:

```
columns <- models_info("example_model")$columns
```

## Searching for model

You can also search for model with some specific restrictions.

Just type:

```
library(weles)

models_search(row = '>1000;<10000;', column='=12;', user='Example user', tags = c('example', 'easily'))
```

You will receive in response all models with at least one of these tags.

## Testing model

You can also test already uploaded model.

```
models_audit('model_name', 'acc', 'target_column', new_data, 'new_test_data', 'new data for testing')
models_audit('model_name', 'mse', 'target_column', data_hash)
```
