#' @title Get the dataset from weles
#'
#' @description
#' You can use this function to download the dataset from weles as a data frame
#'
#' @param dataset_id hash of the dataset
#'
#' @return data frame
#'
#' @references
#' \href{http://192.168.137.64/models}{\bold{models}}
#' \href{http://192.168.137.64/datasets}{\bold{datasets}}
#'
#' @examples
#' library("weles")
#'
#' datasets_get('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
#'
#' @export
datasets_get = function(dataset_id) {

	# checking input
	stopifnot(class(dataset_id) == 'character')
	stopifnot(nchar(dataset_id) == 64)

	# getting dataset	
	df = httr::content(httr::GET(paste0('http://192.168.137.64/datasets/', dataset_id)), 'text')
	result = read.csv(text = df)
	result[,]
}
