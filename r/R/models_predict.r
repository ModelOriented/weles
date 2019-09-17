#' @title Make a prediction using weles model
#'
#' @description
#' This tool allows you to make a prediction with model in weles.
#'
#' @param model_name name of the model in weles
#' @param X data to make a prediction of, must have named columns, may be path to *.csv* file (must contatin **/** sign) or *hash* of already uploaded data,
#' if X is an object and prepare_columns is True, columns' names will be fetched automatically
#' @param pred_type type of prediction, 'exact' or 'prob'
#' @param prepare_columns if X is an object then columns' names will be fetched automatically
#'
#' @references
#' \href{http://192.168.137.64/models}{\bold{models}}
#' \href{http://192.168.137.64/datasets}{\bold{datasets}}
#'
#' @examples
#' \code {
#' library("weles")
#'
#' models_predict("example_model", iris[,-5])
#' }
#'
#' @export
models_predict <- function(model_name, X, pred_type = 'exact', prepare_columns = TRUE) {

	# checking input
	stopifnot(class(model_name) == 'character')
	stopifnot(class(X) == 'data.frame' || class(X) == 'character')
	stopifnot(class(pred_type) == 'character')
	stopifnot(class(prepare_columns) == 'logical')

	# making the hash for temporary files
	h = digest::digest(c(model_name, Sys.time()))

	# url
	url = paste0('http://192.168.137.64/models/', model_name, '/predict/', pred_type)

	# body for the request
	body = list()

	# uploading data
	if(class(X) == "character" && !grepl("/", X)) {
		# case when X is a hash
		body[['is_hash']] =  1
		body[['hash']] = X

	} else if(class(X) == "character") {
		# case when X is a path
		body[['is_hash']] =  0

		data = read.csv(X)

		body[['data']] = paste0(c(paste0(colnames(data), collapse=','), paste0(apply(data,1, paste0, collapse=','), collapse='\n')), collapse='\n')
	} else {
		# case when X is an object

		# fetching columns
		if(prepare_columns) {
			info = models_info(model_name)
			columns = info$columns
			target = info$model$target
			columns = columns[order(columns$id), 'name']
			columns = columns[columns != target]
			names(X) = columns
		}

		data = paste0(c(paste0(colnames(X), collapse=','), paste0(apply(X,1, paste0, collapse=','), collapse='\n')), collapse='\n')

		body[['is_hash']] =  0
		body[['data']] = data
	}

	# uploading
	r = httr::content(httr::POST(url = url, body = body), as='text')

	# return
	read.csv(text = r, header = F)[,1]
}
