#!/bin/bash

# $1 = corpus dir e.g. Big-data_tokenise_text/Big-data_tokenise.txt

mkdir result_vector

data=$1
inFilestr=${data##*/}
echo $inFilestr
# default setting from word2vec, except iter (time issue)
word2vec/word2vec -train $data -output result_vector/$inFilestr-default-skipGram.bin -size 100 -window 5 -sample 1e-3 -negative 5 -hs 0 -binary 1 -cbow 0 -iter 1 -threads 12 -min-count 5 -alpha 0.025 

#cbow vs skip-gram
word2vec/word2vec -train $data -output result_vector/$inFilestr-default-cbow.bin -size 100 -window 5 -sample 1e-3 -negative 5 -hs 0 -binary 1 -cbow 1 -iter 1 -threads 12 -min-count 5 -alpha 0.025 

#various parameter
win=("1" "2" "4" "5" "8" "16" "20" "25" "30")
dim=("25" "50" "100" "200" "400" "500" "800")
neg=("1" "2" "3" "5" "8" "10" "15")
samp=("0" "1e-1" "1e-2" "1e-3" "1e-4" "1e-5" "1e-6" "1e-6" "1e-7" "1e-8" "1e-9" '1e-10')
min=("0" "5" "10" "20" "50" "100" "200" "400" "800" "1000" "1200" "2400")
alpha=("0.05" "0.025" "0.0125" "0.1" "0.2" "0.5")

for i in "${win[@]}" ; do
	echo 'window size:' $i
	echo -train $data -output result_vector/$inFilestr-win$i.bin -size 100 -window $i -sample 1e-3 -negative 5 -hs 0 -binary 1 -cbow 0 -iter 1 -threads 12 -min-count 5 -alpha 0.025
	word2vec/word2vec -train $data -output result_vector/$inFilestr-win$i.bin -size 100 -window $i -sample 1e-3 -negative 5 -hs 0 -binary 1 -cbow 0 -iter 1 -threads 12 -min-count 5 -alpha 0.025 

done

for i in "${dim[@]}" ; do
	echo 'vector length:' $i
	echo -train $data -output $inFilestr-dim$i.bin -size $i -window 5 -sample 1e-3 -negative 5 -hs 0 -binary 1 -cbow 0 -iter 1 -threads 12 -min-count 5 -alpha 0.025
	word2vec/word2vec -train $data -output result_vector/$inFilestr-dim$i.bin -size $i -window 5 -sample 1e-3 -negative 5 -hs 0 -binary 1 -cbow 0 -iter 1 -threads 12 -min-count 5 -alpha 0.025 

done
#wait

for i in "${neg[@]}" ; do
	echo 'negative sampling:' $i
	echo -train $data -output $inFilestr-neg$i.bin -size 100 -window 5 -sample 1e-3 -negative $i -hs 0 -binary 1 -cbow 0 -iter 1 -threads 12 -min-count 5 -alpha 0.025
	word2vec/word2vec -train $data -output result_vector/$inFilestr-neg$i.bin -size 100 -window 5 -sample 1e-3 -negative $i -hs 0 -binary 1 -cbow 0 -iter 1 -threads 12 -min-count 5 -alpha 0.025 
done
#wait

for i in "${samp[@]}" ; do
	echo 'sampling:' $i
	echo -train $data -output $inFilestr-samp$i.bin -size 100 -window 5 -sample $i -negative 5 -hs 0 -binary 1 -cbow 0 -iter 1 -threads 12 -min-count 5 -alpha 0.025
	word2vec/word2vec -train $data -output result_vector/$inFilestr-samp$i.bin -size 100 -window 5 -sample $i -negative 5 -hs 0 -binary 1 -cbow 0 -iter 1 -threads 12 -min-count 5 -alpha 0.025 
done
#wait

for i in "${min[@]}" ; do
	echo 'Min Count:' $i
	echo -train $data -output $inFilestr-min$i.bin -size 100 -window 5 -sample 1e-3 -negative 5 -hs 0 -binary 1 -cbow 0 -iter 1 -threads 12 -min-count $i -alpha 0.025
	word2vec/word2vec -train $data -output result_vector/$inFilestr-min$i.bin -size 100 -window 5 -sample 1e-3 -negative 5 -hs 0 -binary 1 -cbow 0 -iter 1 -threads 12 -min-count $i -alpha 0.025 
done
#wait

for i in "${alpha[@]}" ; do
	echo 'alpha:' $i
	echo -train $data -output $inFilestr-alpha$i.bin -size 100 -window 5 -sample 1e-3 -negative 5 -hs 0 -binary 1 -cbow 0 -iter 1 -threads 12 -min-count 5 -alpha $i
	word2vec/word2vec -train $data -output result_vector/$inFilestr-alpha$i.bin -size 100 -window 5 -sample 1e-3 -negative 5 -hs 0 -binary 1 -cbow 0 -iter 1 -threads 12 -min-count 5 -alpha $i 
done
wait