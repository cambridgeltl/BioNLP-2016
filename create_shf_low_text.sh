#!/bin/bash
# create lower + shuffle text 

#$1 = dir. for all tokenized text 


Dir=$1
cat $1 | perl -MList::Util=shuffle -e 'print shuffle(<STDIN>);' > shuffled_$1

# lower cased text 
tr '[:upper:]' '[:lower:]' < $1 > lower_$1

# create Lowercased + shuffled text 
cat lower_$1 shuffled_$1 > low_shuff_$1