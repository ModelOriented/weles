#! /bin/bash

# $1 path to install
# $2 version

export TMPDIR=~/tmp

prefix="https://cloud.r-project.org/src/base/R-3/R-"
sufix=".tar.gz"
url="$prefix$2$sufix"
wget $url

tar -xf R-$2.tar.gz
rm R-$2.tar.gz

cd R-$2
./configure --prefix=$1"R-"$2
make
echo 'local({r <- getOption("repos")
       r["CRAN"] <- "http://cran.r-project.org"
       options(repos=r)})' > etc/Rprofile.site
bin/R -e 'install.packages("devtools")'
bin/R -e 'install.packages("packrat")'

cd ..
