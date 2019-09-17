#' @title Upload the dataset to the weles
#'
#' @description
#' This function uploads the dataset and needed metadata to the weles.
#'
#' @param data the data frame to upload or path
#' @param data_name name of the dataset that will be visible in the weles
#' @param data_desc description of the dataset
#'
#' @return information if uploading the data was successful
#'
#' @references
#' \href{http://192.168.137.64/models}{\bold{models}}
#' \href{http://192.168.137.64/datasets}{\bold{datasets}}
#'
#' @examples
#' library("weles")
#'
#' datasets_upload(X, 'data name', 'Example user', 'example password')
#'
#' @export
datasets_upload = function(data, data_name, data_desc) {

	user_name = readline('user: ')
	password = getPass::getPass('password: ')

	#stopifnot(class(data) == 'data.frame' || class(data) == 'character')
	stopifnot(class(data_name) == 'character')
	stopifnot(class(data_desc) == 'character')
	stopifnot(class(user_name) == 'character')
	stopifnot(class(password) == 'character')

	# making the for the request
	body = list(data_name = data_name, data_desc = data_desc, user_name = user_name, password = password)

	# making the hash for the temporary files
	h = digest::digest(c(data_name, user_name, password, Sys.time()))

	if(class(data) == "character") {
		# case when data is a path to dataset

		data = read.csv(data)

		body[['data']] <- paste0(c(paste0(colnames(data), collapse=','), paste0(apply(data,1, paste0, collapse=','), collapse='\n')), collapse='\n')
	} else {
		# case when dataset is a matrix

		# uploading dataset
		body[['data']] = paste0(c(paste0(colnames(data), collapse=','), paste0(apply(data,1, paste0, collapse=','), collapse='\n')), collapse='\n')

	}

	# uploading data
	r = httr::content(httr::POST(url = 'http://192.168.137.64/datasets/post', body=body), 'text')

	# return
	r
}
