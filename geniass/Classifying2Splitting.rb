#!/usr/bin/ruby


inFile = $*.first
inFile2 = $*[1].to_s
outFile = $*[2].to_s

fileIn = open(inFile)
fileIn2 = open(inFile2)
fileOut = open(outFile, "w")

line2 = fileIn2.gets
#p line2

count = 0
for line in fileIn do
   pat = "__" + count.to_s + "__"
   until(line2.match(pat)) do
      fileOut << line2
      line2 = fileIn2.gets
      #p line2
   end
   #p "sub"
   splitted = line.chomp.to_i
   line2.sub!(pat){
      if splitted == 1
         "__\n__"
      else
         "____"
      end
   }
   line2.sub!(/__\n____ +__/, "\n")
   line2.sub!(/______( +)__/){
      $1
   }
   count += 1

end
fileOut << line2
until(fileIn2.eof?)
   line2 = fileIn2.gets
   fileOut << line2
end

fileIn2.close
File.delete(inFile)
File.delete(inFile2)
