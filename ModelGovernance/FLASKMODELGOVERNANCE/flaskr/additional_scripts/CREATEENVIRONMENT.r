# R version
ver = paste0(version$major, '.', version$minor)

# path to the libraris not from virtual environment
path = paste0("/root/SERVER/ModelGovernance/FLASKMODELGOVERNANCE/flaskr/interpreters/r/R-", ver, "/library")

# reading commandline arguemtns
args = commandArgs(trailingOnly=TRUE)

# hash of the environment
hash = args[1]
# path to the requirements of the model
requirements_path = args[2]
# timestamp
t = args[3]

# reading requirements
req = as.data.frame(read.csv(requirements_path, header = F))

# initialization of the virtual environment
packrat::init(paste0("flaskr/VENV/r/ENV-", hash))

# loading libraris not from the virtual environments
library('usethis', lib.loc = path)
library('ps', lib.loc = path)
library('withr', lib.loc = path)
library('desc', lib.loc = path)
library('devtools', lib.loc = path)

options("buildtools.check" = function(x) TRUE)

# installing packages
for(i in 1:nrow(req)) {
	install_version(as.character(req[i,1]), version = as.character(req[i,2]))

	write.table(list(i, as.character(req[i,1])), paste0('../../../tmp/status_', t, '.txt'), row.names=FALSE, col.names=FALSE, sep=',')

}
