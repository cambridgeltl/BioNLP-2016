#!/usr/bin/perl
require 5.000;

$ref_filename="Genia4EReval.ref";

print "[1978-1989 SET]\n\n";
print `./evalIOB2.pl -l 1978-1989.lst $ARGV[0] $ref_filename`;
print "\n\n";

print "[1990-1999 SET]\n\n";
print `./evalIOB2.pl -l 1990-1999.lst $ARGV[0] $ref_filename`;
print "\n\n";

print "[2000-2001 SET]\n\n";
print `./evalIOB2.pl -l 2000-2001.lst $ARGV[0] $ref_filename`;
print "\n\n";

print "[1998-2001 SET]\n\n";
print `./evalIOB2.pl -l S1998-2001.lst $ARGV[0] $ref_filename`;
print "\n\n";
