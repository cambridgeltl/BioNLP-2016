#!/usr/bin/ruby

def returnFeatures(prevWord, delimiter, nextWord)
   if nextWord.match(/__ss__/)
      nw = nextWord.sub(/__ss__/, "")
   else
      nw = nextWord
   end

   str = ""
   # prev. word, next word
   str += "pw_" + prevWord.downcase
   str += "\tnw_" + nw.downcase

   # delimiter
   str += "\td_" + delimiter

   # capitalized first char in next word
   # capital in next word excluding first char.
   if nw[0].chr == nw[0].chr.capitalize
      str += "\tnfc_y"
      nwExcluginFirst = nw[1 ... -1]
      if nwExcluginFirst == nil
         str += "\tnwcef_n"
      elsif nwExcluginFirst.downcase == nwExcluginFirst
         str += "\tnwcef_n"
      else
         str += "\tnwcef_y"
      end
   else
      if nw.downcase == nw
         str += "\tnwcef_n"
      else
         str += "\tnwcef_y"
      end
      str += "\tnfc_n"
   end

   # prev. word capital
   if prevWord.downcase == prevWord
      str += "\tpwc_n"
   else
      str += "\tpwc_y"
   end

   # number in prev. word, in next word
   if prevWord.match(/[0-9]/)
      str += "\tpwn_y"
   else
      str += "\tpwn_n"
   end
   if nw.match(/[0-9]/)
      str += "\tnwn_y"
   else
      str += "\tnwn_n"
   end

   # prev., next word excluding braket, camma, etc.
   prevWordEx = prevWord.gsub(/[()'",\[\]]/, "")
   nwEx = nw.gsub(/[()'",\[\]]/, "")
   str += "\tpwex_" + prevWordEx.downcase
   str += "\tnwex_" + nwEx.downcase

   # bracket or quatation in prev. word
   if prevWord.match(/()'"/)
      str += "\tpwcbq_y"
   else
      str += "\tpwcbq_n"
   end
   # camma in prev., next word
   if prevWord.match(/,/)
      str += "\tpwcc_y"
   else
      str += "\tpwcc_n"
   end
   if nw.match(/,/)
   else
      str += "\tnwcc_n"
   end

   # prev. word + delimiter
   str += "\tpw_" + prevWord + "_d_" + delimiter
   # prev. word ex. +  delimiter + next word ex.
   str += "\tpwex_" + prevWordEx + "_d_" + delimiter + "_nwex_" + nwEx
   #str +=
   #str +=
   #str +=
   str += "\n"
end

inFile = $*.first
outFile = $*[1].to_s
outFile2 = inFile + ".tmp"

while File.exist?(outFile2)
  outFile2 = outFile2 += ".tmp"
end

fileIn = open(inFile)
fileOut = open(outFile, "w")
fileOut2 = open(outFile2, "w")


eventCount = 0
fileOut << outFile2 << "\n"

pat = / [^ ]+[.!\?\)\]\"]( +)[^ ]+ /
for line in fileIn do
   while line.match(pat) do
      line.sub!(/ ([^ ]+)([.!\?\)\]\"])( +)([^ ]+) /){
         a, b, d, c = $1, $2, $3, $4
         #p (" " + a + b + "__d__ " + c + " ")
         fileOut << eventCount  << "\t"
         fileOut << returnFeatures(a, b, c)
         (" " + a + b + "__" + eventCount.to_s + "____" + d + "__" + c + " ")
      }
      eventCount += 1
   end
   fileOut2 << line
end


