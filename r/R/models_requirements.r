#' @title Get package requirements for the model in weles
#'
#' @description
#' You can use this function to download requirements of the model
#'
#' @param model name of the model in weles, character
#'
#' @return named list with requirements
#'
#' @references
#' \href{http://192.168.137.64/models}{\bold{models}}
#' \href{http://192.168.137.64/datasets}{\bold{datasets}}
#'
#' @examples
#' library("weles")
#'
#' models_requirements("example_model")
#' models_requirements("example_model")$pandas
#'
#' @export
models_requirements = function(model) {

	# checking input
	stopifnot(class(model) == 'character')

	# making the request and return
	httr::content(httr::GET(url = paste0('http://192.168.137.64/models/', model, '/requirements')))
}
