'''
Created on 22 Mar 2016

@author: Billy
'''
import string
import io
# Import various modules for string cleaning
#from bs4 import BeautifulSoup

from nltk.corpus import stopwords
from nltk.tokenize import TreebankWordTokenizer
from itertools import islice
import nltk
import sys  
import os
import codecs

class utilities:
    def __init__(self):
        ''' Constructor for this class. '''
 
    @classmethod       
    def removePunctuation(self, inputString):
        no_punct = ""
        punctuations = set(string.punctuation)
        for char in inputString:
            if char not in punctuations:
                no_punct = no_punct + char
        return no_punct
    
    def appendFile(self, inputString,filePath):
        print "appending",filePath
        fh = io.open(filePath, 'a', encoding='utf-8')
        #print inputString
        fh.write(inputString)
        fh.close()
    
        
    def readFile(self, filePath):
        print "reading",filePath
        with io.open(filePath, 'r', encoding='utf-8') as myfile:
            data=myfile.readlines()
        return data
    
    def readFileLineByLine(self, filePath):
        print "reading",filePath
        with open(filePath, "r") as ins:
            array = []
            for line in ins:
                array.append(line)
        return array
    
    def text_to_wordlist(self, text, remove_stopwords=False):
        # Function to convert a document to a sequence of words,
        # optionally removing stop words.  Returns a list of words.
        #
        # 1. Remove HTML
        #res_text = BeautifulSoup(text, "html.parser").get_text()
        
        #  
        # 2. Remove non-letters
        #res_text = re.sub("[^a-zA-Z]"," ", res_text)
        
        #
        # 3. Convert words to lower case and split them
        words = text.lower().split()
        
        #
        # 4. Optionally remove stop words (false by default)
        if remove_stopwords:
            stops = set(stopwords.words("english"))
            words = [w for w in words if not w in stops]
        
        # 5. Return a list of words
        return(words)
    
    # Define a function to split a review into parsed sentences
    def text_to_sentences(self, text, tokenizer, remove_stopwords=False ):
        print "text_to_sentence"
        #from nltk.tokenize import wordpunct_tokenize
        # Function to split a review into parsed sentences. Returns a 
        # list of sentences, where each sentence is a list of words
        #
        text=text.decode("utf8")
        from nltk.tokenize import sent_tokenize,wordpunct_tokenize
        # 1. Use the NLTK tokenizer to split the paragraph into sentences
        #raw_sentences = tokenizer.tokenize(text.strip())
        raw_sentences = sent_tokenize(text.strip())
        print "finish tokenize sentence",len(raw_sentences)
        #
        # 2. Loop over each sentence
        sentences = []
        for raw_sentence in raw_sentences:
            
            #print "sentence:",raw_sentence
            # If a sentence is empty, skip it
            if len(raw_sentence) > 0:
                # Otherwise, call review_to_wordlist to get a list of words
                #sentences.append( text_to_wordlist( raw_sentence, \
    #               remove_stopwords ))
                #print removePunctuation(raw_sentence).lower().split()
                print raw_sentence
                sentences.append(wordpunct_tokenize(raw_sentence))#raw_sentence.split())
                print wordpunct_tokenize(raw_sentence)
                #print  text_to_wordlist( raw_sentence, remove_stopwords )
        #    
        # Return the list of sentences (each sentence is a list of words,
        # so this returns a list of lists
        return sentences
    
    def writeListOfList2File(self, fname,inputList):
        # write list of list to file, one item per line
        print "wrting file to list",fname
        with io.open(fname, 'a', encoding='utf-8') as f:
            for item in inputList:
                #print item
                text = " ".join(item)
                #print text
                text = unicode(text, encoding='utf-8', errors='ignore')
                f.write(text + "\n")
    #     import csv
    #     with open(fname, 'ab') as f:
    #         writer = csv.writer(f,delimiter=" ", quoting=csv.QUOTE_NONE, quotechar='')
    #         writer.writerows(inputList)
            
    def readFile2List(self, fname,spilter):
        print "reading file to list",fname
        listed = []
        with open(fname) as f:
            for line in f:
                lineList = line.split(spilter)
                listed.append([word.strip("\r\n") for word in lineList])
                
        return listed
    
    def readFile2Dict(self, fname,spilter):
        print "reading file to Dict",fname
        wordDict = {}
        with open(fname) as f:
            for line in f:
                try:
                    line = line.decode('utf-8')
                except:
                    try:
                        line = line.decode('latin-1')
                    except:
                        print 'skipping broken line'
                        line = u''
                        pass
                lineList = line.split(spilter)
                #print line
                wordDict[lineList[0]] = int(lineList[1])
        
        
        #with io.open(fname, encoding='utf-8') as f:
        #    for line in f:
        #        lineList = line.split(spilter)
        #        #print line
        #        wordDict[lineList[0]] = int(lineList[1])
                
        return wordDict
    
    def writeText2File (self, fname, text):
        with io.open(fname, 'a', encoding='utf-8') as f:
            print text
            f.write(unicode(text, encoding='utf-8', errors='ignore'))
            f.write(u'\n')
            f.close()
                
    def read_in_chunks(self, fname, N):
        with io.open(fname, encoding='utf-8') as f:
            while True:
                next_n_lines = list(islice(f, N))
                next_n_lines =map(lambda s: s.strip(), next_n_lines)
                if not next_n_lines:
                    break
                yield next_n_lines
                
    def writeText2w2vFormat(self, inputFile, outputFile):
        rawText = self.readFile(inputFile)
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        sentences = self.text_to_sentences(rawText, tokenizer, remove_stopwords=False )
        self.writeList2File(outputFile,sentences)
        
    # def readLine2List(fname):
    #     print "reading file to list",fname
    #     listed = []
    #     with open(fname) as f:
    #         for line in f:
    #             listed.append(line)
    #     return listed
    
    def readGzip2List(self, fname):
        #print "reading file to list",fname
        listed = []
        import gzip
        #f=gzip.open(input,'rb')
        #file_content=f.read()
        with gzip.open(fname,'rb') as f:
            for line in f:
                listed.append(line)
        return listed
                
    def find_ngrams(self, input_list, n):
      return zip(*[input_list[i:] for i in range(n)])
      
    def getWordsWithRandomWindowSize(self, inputlist,windowSize,fname):
        from random import randint
        from collections import defaultdict
        reduced_window = randint(0,windowSize)
        wordDict={}
        
        for pos, root in enumerate(inputlist):
            #print pos,root
            start = max(0, pos - windowSize + reduced_window)
            #wordDict[root] = {'word2':[],'pos2':[]}
            for pos2, word2 in enumerate(inputlist[start:(pos + windowSize + 1 - reduced_window)], start):
                if pos2 != pos:
                    text = root.strip()+" "+str(pos2-pos)+""+word2.strip()
                    #appendFile(text, fname)
                    print text
                    
                    #wordDict[root]['word2'].append(word2)
                    #wordDict[root]['pos2'].append(pos2-pos)
        #return wordDict
                    
    def get_filepaths(self, directory):
        """
        This function will generate the file names in a directory 
        tree by walking the tree either top-down or bottom-up. For each 
        directory in the tree rooted at directory top (including top itself), 
        it yields a 3-tuple (dirpath, dirnames, filenames).
        """
        file_paths = []  # List which will store all of the full filepaths.
    
        # Walk the tree.
        for root, directories, files in os.walk(directory):
            for filename in files:
                # Join the two strings in order to form the full filepath.
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)  # Add it to the list.
    
        return sorted(file_paths)  # Self-explanatory.
    
    ''' Read all the word vectors and normalize them '''
    def read_word_vecs(self, filename):
        #print "read_word_vecs",filename
        import gzip
        import numpy
        import math
        wordVectors = {}
        if filename.endswith('.gz'): fileObject = gzip.open(filename, 'r')
        else: fileObject = open(filename, 'r')
      
        for line in fileObject:
            line = line.strip().lower()
            word = line.split()[0]
            #print word
            wordVectors[word] = numpy.zeros(len(line.split())-1, dtype=float)
        for index, vecVal in enumerate(line.split()[1:]):
            wordVectors[word][index] = float(vecVal)
        ''' normalize weight vector '''
        wordVectors[word] /= math.sqrt((wordVectors[word]**2).sum() + 1e-6)
        
        sys.stderr.write("Vectors read from: "+filename+" \n")
        return wordVectors
    

    def write_word_vecs(self, wordVectors, outFileName):
        #import io
        sys.stderr.write('\nWriting down the vectors in '+outFileName+'\n')
        outFile = io.open(outFileName, 'w' , encoding='utf-8')  
        for word, values in wordVectors.iteritems():
            if word.strip():
                print word
                outFile.write(unicode(word, errors='ignore')+' ')
                for val in wordVectors[word]:
                    outFile.write(u'%.4f' %(val)+' ')
                outFile.write(u'\n')      
        outFile.close()
        
    def SentenceTokenize(self, text):
        tokens = TreebankWordTokenizer().tokenize(text)
        
        return tokens