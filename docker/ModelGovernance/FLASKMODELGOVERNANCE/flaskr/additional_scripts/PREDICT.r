# command line arguments
args = commandArgs(trailingOnly=TRUE)

# model name
model = args[1]
# timestamp
date = args[2]
# type of the prediction
type = args[3]
# flag if hash was provided
is_hash = args[4]

# reading model
model = readRDS(paste0('../../../V/Models/', model, '/model'))

if(is_hash == '1') {
	# case when hash was provided
	# hash
	hash = args[5]
	# target column
	target = args[6]
	# reading data
	data = read.csv(paste0('../../../V/Datasets/', hash), header=T)
	# droping target
	data = data[-which(colnames(data) == target)]
} else {
	# case when hash was not provided
	# reading the data
	data = read.csv(paste0('../../../tmp/', date, '.csv'), header=T)
}

# making predictions
if(class(model)[1] == 'WrappedModel') {
	# case when model is mlr model
	library(mlr)
	result = predict(model, newdata = data)$data$response
} else if(class(model)[1] == 'train' && class(model)[2] == 'train.formula') {
	# case when model is caret model
	result = predict(model, data)
} else if(class(model)[2] == 'model_fit') {
	# case when model is parsnip model
	result = parsnip::predict(model, data)
}

# writting result
write.table(result, paste0('../../../tmp/', date, '.txt'), sep=',', col.names=F, row.names = F)

