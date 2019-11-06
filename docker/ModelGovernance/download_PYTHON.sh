cd /

prefix='https://www.python.org/ftp/python/'
url=$prefix$2/Python-$2.tgz
wget $url

tar -xf Python-$2.tgz
rm Python-$2.tgz

cd Python-$2

./configure --prefix=$1"Python-"$2
make
make install

cd ..
rm -r Python-$2
