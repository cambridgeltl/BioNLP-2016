#!/bin/bash

# $1 = corpus dir e.g. Big-data_tokenise_text/Big-data_tokenise.txt

mkdir result_vector

data=$1
inFilestr=${data##*/}
echo $inFilestr

#various parameters
win=("2")
dim=("200")
neg=("10")
samp=("1e-4")
min=("5" "10" "20" "50" "100" "200" "400" "800" "1000" "1200" "2400")
alpha=("0.05")


for i in "${min[@]}" ; do
	echo 'Min Count:' $i
	echo -train $data -output $inFilestr-min$i.bin -size 200 -window 2 -sample 1e-4 -negative 10 -hs 0 -binary 1 -cbow 0 -iter 1 -threads 12 -min-count $i -alpha 0.05
	word2vec/word2vec -train $data -output result_vector/$inFilestr-min$i.bin -size 200 -window 2 -sample 1e-4 -negative 10 -hs 0 -binary 1 -cbow 0 -iter 1 -threads 12 -min-count $i -alpha 0.05
done
wait
