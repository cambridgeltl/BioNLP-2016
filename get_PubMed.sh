#!/bin/bash

mkdir pubmedfiles
cd pubmedfiles

echo 'Downloading files'
wget ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/*.gz

echo 'Unzipping files.'
gunzip *.gz
cd ../../

echo 'Downloading pubmed tools.'
git clone https://github.com/spyysalo/pubmed.git

mv -v ./pubmed/scripts/* ./pubmed/

cd BioNLP-2016/

mkdir pubmedtxt
cd pubmedtxt/

echo 'Exctracting text from xml'
../../pubmed/extract-and-pack.sh ../pubmedfiles/*.xml

echo 'Unzipping tar.gz.'
for file in `ls *.tar.gz`; do tar -xf $file; done

echo 'Removing .tar.gz files.'
rm *.tar.gz

for folder in */ ; do
mv $folder/* . && rmdir $folder
done
