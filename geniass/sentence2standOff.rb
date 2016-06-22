#!/usr/local/bin/ruby

$inputFile = File.expand_path($*.first) # non sentence-split txt
$inputFile2 = File.expand_path($*[1].to_s) # sentence-split txt
$outputFile = File.expand_path($*[2].to_s) # stand-off

def main
   marker = "\n"[0]
   tag = "sentence"
   position = 0
   sentenceCount = 1
   target = ''
   targetNew = ''
   start = 0
   finish = 0

   inTxtStrict = open($inputFile)
   inTxtNew = open($inputFile2)
   outStandOff = open($outputFile, "w")

   p marker

   while(!inTxtNew.eof) do
      targetNew = inTxtNew.getc
      target = inTxtStrict.getc
      position += 1
      if targetNew == marker
         sentenceCount += 1
         finish = position - 1
         outStandOff << start << "\t" << finish << "\t" << tag << "\n"
         if targetNew == target
            start = position
         else
            targetNew = inTxtNew.getc
            while targetNew != target do
               target = inTxtStrict.getc
               position += 1
            end
            start = position - 1
         end
      end

   end

end

main
