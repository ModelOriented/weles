#' @title Get the head of the dataset in the weles
#'
#' @description
#' This tool allows you to view the head of the dataset in the weles.
#'
#' @param dataset_id the dataset hash
#' @param n number of rows to show
#'
#' @return top n rows of the dataset
#'
#' @references
#' \href{http://192.168.137.64/models}{\bold{models}}
#' \href{http://192.168.137.64/datasets}{\bold{datasets}}
#'
#' @examples
#' library("weles")
#'
#' datasets_head('aaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 10)
#'
#' @export
datasets_head = function(dataset_id, n=5) {

	# checking input
	stopifnot(class(dataset_id) == 'character')
	stopifnot(nchar(dataset_id) == 64)
	stopifnot(class(n) == 'numeric')

	# getting data
	df = httr::content(httr::POST(paste0('http://192.168.137.64/datasets/', dataset_id, '/head'), body = list('n' = n)), 'text')
	result = read.csv(text = df)
	result[,-1]
}
