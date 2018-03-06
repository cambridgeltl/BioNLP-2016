#!/bin/bash

mkdir pubmedfiles
cd pubmedfiles
wget ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/*000*.gz

echo 'Unzipping files.'
gunzip '*.gz'
cd ../../

git clone https://github.com/spyysalo/pubmed.git

mv -v pubmed/scripts/* pubmed/

cd BioNLP-2016/

mkdir pubmedtxt
cd pubmedtxt/

../../pubmed/extract-and-pack.sh *.xml
for file in `ls *.tar.gz`; do tar -xf $file; done
