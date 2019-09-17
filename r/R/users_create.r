#' @title Create user in the weles
#'
#' @description
#' This function is used to create an user account. You need this to have an access to all features in weles.
#'
#' @param mail your mail, character
#'
#' @return Information if creating an account was successful.
#'
#' @references
#' \href{http://192.168.137.64/models}{\bold{models}}
#' \href{http://192.168.137.64/datasets}{\bold{datasets}}
#'
#' @examples
#' \code{
#' library("weles")
#'
#' users_create("Example user", "example password", "example_mail@gmail.com")
#' }
#'
#' @export
users_create = function(mail) {

	user_name = readline('user: ')
	password = getPass::getPass('password: ')
	password2 = getPass::getPass('password: ')

	stopifnot(password == password2)

	# checking input
	stopifnot(class(user_name) == 'character')
	stopifnot(class(password) == 'character')
	stopifnot(class(mail) == 'character')

	# making the body for the request
	body = list('user_name' = user_name, 'password' = password, 'mail' = mail)

	# request
	httr::content(httr::POST('http://192.168.137.64/users/create_user', body=body), 'text')
}
