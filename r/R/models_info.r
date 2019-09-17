#' @title Get an info about the model in weles
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
#' models_info("example_model")
#' models_info("example_model")$model
#' models_info("example_model")$data
#' models_info("example_model")$data$dataset_id
#'
#' @export
models_info = function(model_name) {

	# checking input
	stopifnot(class(model_name) == 'character')

	# receiving data
	content = httr::content(httr::GET(url = paste0('http://192.168.137.64/models/', model_name, '/info')))

	# formatting
	audits = content$audits

	auds = list()
	for(name in names(audits)) {
		v = c()
		v[as.numeric(names(unlist(audits[[name]])))+1] = unlist(audits[[name]])
		auds[[name]] = v
	}

	# formatting
	columns = content$columns

	cols = list()
	for(name in names(columns)) {
		v = c()
		v[as.numeric(names(unlist(columns[[name]])))+1] = unlist(columns[[name]])
		cols[[name]] = v
	}

	# formatting
	aliases = content$aliases

	als = list()
	for(name in names(aliases)) {
		v = c()
		v[as.numeric(names(unlist(aliases[[name]])))+1] = unlist(aliases[[name]])
		als[[name]] = v
	}

	# return	
	list(model = content$model, data = content$data, audits = data.frame(auds), columns = data.frame(cols), aliases = data.frame(als))
}
