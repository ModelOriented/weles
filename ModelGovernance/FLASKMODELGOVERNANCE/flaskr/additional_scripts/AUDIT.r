# reading commandline arguments
args = commandArgs(trailingOnly=TRUE)

# model name
model = args[1]
# hash of the dataset
hash = args[2]
# target column name
target = args[3]
# measure used in auditing
measure = args[4]
# timestamp
date = args[5]

# reading model
model = readRDS(paste0('../../../V/Models/', model, '/model'))

# reading data
data = read.csv(paste0('../../../V/Datasets/', hash), header=T)

# dropping target column
X = data[-which(colnames(data) == target)]
y = data[[target]]

# making prediction
if(class(model)[1] == 'WrappedModel') {
	# case when model is mlr model
	library(mlr)
	pred = predict(model, newdata = X)$data$response
} else if(class(model)[1] == 'train' && class(model)[2] == 'train.formula') {
	# case when model is caret model
	pred = predict(model, X)
} else if(class(model)[2] == 'model_fit') {
	# case when model is parsnip model
	pred = parsnip::predict(model, X)
}

if (measure == 'acc') {
	result = mean(pred == y)
} else if (measure == 'mae') {
	result = mean(sum(abs(pred - y)))
} else if (measure == 'mse') {
	result = mean(sum((pred - y)^2))
}

# writting result
write.table(result, paste0('../../../tmp/', date, '.txt'), row.names=FALSE, col.names=FALSE)
