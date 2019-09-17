#' @title Get the status of the uploading model
#'
#' @description
#' If you know the uploading id, you can check the progress.
#'
#' @param task_id id of the uploading, it is always returned by function models_upload
#' @param interactive display the progressbar
#'
#' @return named list containing meta data about uploading
#'
#'
#' @examples
#' library("weles")
#'
#' models_status("aaaaaaaaaaaaaaaaaaaaaaaaa")
#' models_status("aaaaaaaaaaaaaaaaaaaaaaaaa")$model_existed
#' models_status("aaaaaaaaaaaaaaaaaaaaaaaaa", interactive = FALSE)
#'
#' @export
models_status = function(task_id, interactive=TRUE) {

	# url
	url = paste0('http://192.168.137.64/models/status/', task_id)

	# getting metadata
	r = httr::content(httr::GET(url))

	# display the progressbar
	if(interactive) {
		pb = txtProgressBar(min = 0, max = r$total, style = 3)
		setTxtProgressBar(pb, r$current)
		while(r$state != 'SUCCESS') {
			# update progress once per every 3 seconds
			Sys.sleep(3)
			r = httr::content(httr::GET(url))
			setTxtProgressBar(pb, r$current)
		}
		close(pb)
	}

	# return
	r
}
