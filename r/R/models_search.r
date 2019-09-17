#' @title Find model that interests you the most
#'
#' @description
#' Function allows you advanced search of models in weles. If all parameters are default then returns all models' name in weles.
#'
#' @param language search only among models written in this language
#' @param language_version what language version should be model written, '<n;' '>n;' '=n;' '>a;<b;'
#' @param row parameter descibing number of rows in training dataset, '<n;' '>n;' '=n;' '>a;<b'
#' @param column parameter descibing number of columns in training dataset, '<n;' '>n;' '=n;' '>a;<b'
#' @param missing parameter descibing number of missing values in training dataset, '<n;' '>n;' '=n;' '>a;<b'
#' @param classes parameter descibing number of classes in training dataset, '<n;' '>n;' '=n;' '>a;<b'
#' @param owner show only models created by this user
#' @param tags vector of tags, should be all strings
#' @param regex regex for searching names of models
#'
#' @return vector of models' names satisfying those restrictions
#'
#' @references
#' \href{http://192.168.137.64/models}{\bold{models}}
#' \href{http://192.168.137.64/datasets}{\bold{datasets}}
#'
#' @examples
#' \code{
#' library("weles")
#'
#' models_search(tags = c('example', 'easy'))
#'
#' models_search(row='<15000;', tags = c('example', 'easy'))
#'
#' models_search(column='>10;<15;', owner='Example user')
#'
#' models_search(language='python', language_version='3.6.8', row='>1000;<10000;', column='=14;', classes='=2;', missing='=0;', owner='Example user', tags=
#'c('example', 'easy'), regex='^R')
#' }
#'
#' @export
models_search = function(language=NA, language_version=NA, row=NA, column=NA, missing=NA, classes=NA, owner=NA, tags=c(), regex=NA) {

	stopifnot(is.na(language) || class(language) == 'character')
	stopifnot(is.na(language_version) || class(language_version) == 'character')
	stopifnot(is.na(row) || class(row) == 'character')
	stopifnot(is.na(column) || class(column) == 'character')
	stopifnot(is.na(missing) || class(missing) == 'character')
	stopifnot(is.na(classes) || class(classes) == 'character')
	stopifnot(is.na(owner) || class(owner) == 'character')
	stopifnot(class(tags) == 'NULL' || class(tags) == 'character')
	stopifnot(is.na(regex) || class(regex) == 'character')

	# making the body for the request
	body = as.list(tags)
	names(body) = rep('tags', length(body))
	body[['language']] = language
	body[['language_version']] = language_version
	body[['row']] = row
	body[['column']] = column
	body[['missing']] = missing
	body[['classes']] = classes
	body[['owner']] = owner
	body[['regex']] = regex

	# receiving data
	result = httr::content(httr::POST(url = 'http://192.168.137.64/models/search', body = body))

	# return
	unlist(result$models)
}
