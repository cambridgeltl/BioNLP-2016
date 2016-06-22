#!/bin/bash

#$1 = dir. for all raw text 
# remeber to "make" the geniass class

cd geniass/
mkdir segmentText

echo 'sentence spliting'
Dir=$1
FILES=$(find $Dir -name *.txt)

for file in $FILES
do
inFilestr=${file##*/}
echo $inFilestr
echo $file
./geniass $file segmentText/$inFilestr 
done

cd .. 
mkdir tokenizeText
echo 'Tokenise'
Dir=geniass/segmentText/
FILES=$(find $Dir -name *.txt)
for file in $FILES ; do
inFilestr=${file##*/}
echo $inFilestr
echo $file
python tokenize_Text.py $file tokenizeText/$inFilestr 
done

cd tokenizeText/
cat *.txt > ../combine_tokenized.txt