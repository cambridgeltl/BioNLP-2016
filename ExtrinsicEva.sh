#!/bin/bash

# $1 = folder for testing word2vec vector.bin

home=$(pwd)/keras/
dataPath=$home'/data/ner/'
echo $home

#DIR=$home'/ner/evaluation' #"$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#echo $DIR
FILES=$(find $1 -type f -name '*.bin')
for file in $FILES
do
	for f in $dataPath/BC2GM $dataPath/BC2GM-IOB $dataPath/BC2GM-narrow $dataPath/JNLPBA
	do 
	echo $f
	python $home/ner/mlp.py $f $file  
	done
done

# result located in log and prediction file
wait