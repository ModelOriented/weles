#' @title Make an audit of the model in the weles
#'
#' @description
#' You can use this function to audit in different ways models already uploaded in the weles.
#'
#' @param model_name name of the model in the weles, character
#' @param measure name of the measure used in the audit, character
#' @param data data frame to make an audit on or path or hash of already uploaded dataset
#' @param target name of the target column in the dataset
#' @param data_name name of the dataset that will be visible in the weles, unnecessary if data is a hash
#' @param data_desc description of the dataset, unnecessary if data is a hash
#'
#' @return result of the audit or information if somethin went wrong
#'
#' @references
#' \href{http://192.168.137.64/models}{\bold{models}}
#' \href{http://192.168.137.64/datasets}{\bold{datasets}}
#'
#' @examples
#' \code{
#' library("weles")
#'
#' models_audit('example_model', 'mae', 'Example user', 'example password', iris, 'Species', 'iris', 'Flowers')
#' models_audit('example_model', 'acc', 'Example user', 'example password', 'aaaaaaaaaaaaaaaaaaaaaaaaaa', 'Species')
#' }
#'
#' @export
models_audit = function(model_name, measure, data, target, data_name=NA, data_desc=NA) {

	user = readline('user: ')
	password = getPass::getPass('password: ')

	# checking input
	stopifnot(class(model_name) == 'character')
	stopifnot(class(measure) == 'character')
	stopifnot(class(user) == 'character')
	stopifnot(class(password) == 'character')
	stopifnot((class(data) == 'data.frame' && !is.na(data_name) && !is.na(data_desc)) || (class(data) == 'character' && nchar(data) == 64))
	stopifnot(class(target) == 'character')
	stopifnot(is.na(data_name) || class(data_name) == 'character')
	stopifnot(is.na(data_desc) || class(data_desc) == 'character')

	# making the body for the request
	info = list('model_name'= model_name, 'measure'= measure, 'user'= user, 'password'= password, 'target'= target)

	# creating hash for the temporary files
	h = digest::digest(Sys.time())

	info[['is_data_name']] = 1
	# uploading data
	if (class(data) == 'character' && !grepl('/', data)) {
		# case when data is a hash
		info[['is_hash']] = 1
		info[['hash']] = data

		if(!is.na(data_name) && is.na(data_desc)) {
			stop('If your dataset name is specified, you need to pass dataset_desc')
		}
		if(is.na(data_name) && !is.na(data_desc)) {
			stop('If your dataset description is specified, you need to pass its name')
		}

		if(is.na(data_name)) {
			info[['is_data_name']] = 0
		}
	} else if (class(data) == 'character') {
		# case when data is a path
		info[['is_hash']] = 0

		data = read.csv(data)

		info[['data']] = paste0(c(paste0(colnames(data), collapse=','), paste0(apply(data,1, paste0, collapse=','), collapse='\n')), collapse='\n')
	} else {
		# case when data is an object

		info[['is_hash']] = 0

		info[['data']] <- paste0(c(paste0(colnames(data), collapse=','), paste0(apply(data,1, paste0, collapse=','), collapse='\n')), collapse='\n')
	}

	if(info[['is_data_name']] == 1) {
		info[['data_name']] = data_name

		if(class(data_desc) == 'character' && grepl('/', data)) {
			info[['data_desc']] = paste0(readLines(dataset_desc), collapse='')
		} else if(class(data_desc) == 'character') {
			info[['data_desc']] = data_desc
		}
	}

	# uploading
	r = httr::POST('http://192.168.137.64/models/audit', body=info)

	# return
	#r = httr::content(r, 'text')
	#read.csv(text = r, header = F)[,1]
	httr::content(r)
}
