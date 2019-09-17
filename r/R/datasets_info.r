#' @title Get an info about the dataset in weles
#'
#' @description
#' This tool is used for getting a meta data about the model that is already uploaded to weles.
#'
#' @param model_name Name of the model in weles, character
#'
#' @return named list containing all meta data about model
#'
#' @references
#' \href{http://192.168.137.64/models}{\bold{models}}
#' \href{http://192.168.137.64/datasets}{\bold{datasets}}
#'
#' @examples
#' library("weles")
#'
#' datasets_info("aaaaaaaaaaaaaaaaaaaaaaa")
#' datasets_info("aaaaaaaaaaaaaaaaaaaaaaa")$number_of_rows
#' datasets_info("aaaaaaaaaaaaaaaaaaaaaaa")$number_of_columns
#' datasets_info("aaaaaaaaaaaaaaaaaaaaaaa")$columns
#'
#' @export
datasets_info = function(dataset_id) {

	# checking input
	stopifnot(class(dataset_id) == 'character')
	stopifnot(nchar(dataset_id) == 64)

	# receiving data
	content = httr::content(httr::GET(url = paste0('http://192.168.137.64/datasets/', dataset_id, '/info')))

	# formatting
	columns = content$columns
	content[['columns']] = NULL

	cols = list()
	for(name in names(columns)) {
		v = c()
		v[as.numeric(names(unlist(columns[[name]])))+1] = unlist(columns[[name]])
		cols[[name]] = v
	}

	als = list()
	for(name in names(aliases)) {
		v = c()
		v[as.numeric(names(unlist(aliases[[name]])))+1] = unlist(aliases[[name]])
		als[[name]] = v
	}

	# return
	list(data = content, columns = data.frame(cols), aliases = data.frame(als))
}
