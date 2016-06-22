#!/usr/bin/perl
require 5.000;

use Getopt::Std;
getopts('ha:r:l:e');

$afield = -1;
$rfield = -1;

@objs=("protein", "DNA", "RNA", "cell_type", "cell_line");
$alls="[-ALL-]";

if (($opt_h) || ($#ARGV != 1)) {
    die "\n" .
	"[evalIOB2] 2004.10.14 Jin-Dong Kim (jdkim\@is.s.u-tokyo.ac.jp)\n" .
	"\n" .
	"<DESCRIPTION>\n" .
	"\n" .
	"It evaluates the performance of object identification in terms of precision and recall. " .
	"This is done by comparing the answer file to the reference file which is assumed to have the correct answer. " .
	"It assumes the object identification is encoded in IOB2 tagging scheme.\n" .
	"\n" .
	"<USAGE>\n" .
	"\n" .
	"evalIOB2.pl answer_file reference_file\n" .
	"\n" .
	"<OPTIONS>\n" .
	"\n" .
	"-h               displays this instructions.\n" .
	"-a answer_field  specifies the field of IOB-tags in the answer_file.\n" .
	"                 It is 0-oriented and defaulted to -1 (the last field).\n" . 
	"-r refer_field   specifies the field of IOB-tags in the reference_file.\n" .
	"                 It is 0-oriented and defaulted to -1 (the last field).\n" . 
	"-l list_file     specifies the file containing a list of UIDs.\n" .
	"                 Only the abstracts of the UIDs will be evaluated.\n" .
	"                 If omitted, all the abstracts will be evaluated.\n" .
	"\n";
} # if

if (defined($opt_a)) {$afield = $opt_a}
if (defined($opt_r)) {$rfield = $opt_r}

open (AFILE, $ARGV[0]) or die "can't open [$ARGV[0]].\n";
open (RFILE, $ARGV[1]) or die "can't open [$ARGV[1]].\n";

if ($opt_l) {
    open (LFILE, $opt_l) or die "can't open [$opt_l].\n";
    while (<LFILE>) {chomp; $abstogo{$_} = 1}
} # if
if (defined($opt_e)) {open (EFILE, ">" . $ARGV[0] . ".chk") or die "can't open [$ARGV[0].chk].\n"}


push @objs, $alls;
foreach $obj (@objs) {$nref{$obj} = $nans{$obj} = $nfcrt{$obj} = $nlcrt{$obj} = $nrcrt{$obj} = 0;}
pop @objs;
@rwrds = @rtags = @atags = @chks = ();
$linenum = 0;

while ($rline = <RFILE>) {
    chomp $rline;

    if ($aline = <AFILE>) {chomp $aline}
    else {die "insufficient answers.\n"}
    $linenum++;

    if ($rline eq "") {
	if ($aline ne "") {die "sentence alignment error at line $linenum.\n"}

	if ((!$opt_l) || ($abstogo{$medid})) {
	    @rtags = iob2_iobes(@rtags);
	    @atags = iob2_iobes(@atags);

	    $match = 0;
	    for ($i=0; $i<=$#rtags; $i++) {

		$rtag = $rtags[$i]; $riob = substr($rtag, 0, 1);
		if (substr($rtag, 1, 1) eq "-") {$rcls = substr($rtag, 2)}
		else {$rcls = ""}

		$atag = $atags[$i]; $aiob = substr($atag, 0, 1);
		if (substr($atag, 1, 1) eq "-") {$acls = substr($atag, 2)}
		else {$acls = ""}

		if ($rtag eq $atag) {$chks[$i] = ">>>>>TRUE"}
		else {
		    $chks[$i] = ">>>>>FALSE";

		    if ($atag ne "O") {
			if ($rtag eq "O") {$chks[$i] .= "+"}
			elsif ($rtag ne $atag) {$chks[$i] .= "^"}
			else {$chks[$i] .= "@"}
		    } # if
		} # if

		#####
		# object evaluation
		#####
		if (($riob eq "S") || ($riob eq "B")) {$nref{$rcls}++;}
		if (($aiob eq "S") || ($aiob eq "B")) {$nans{$acls}++}

		if ($acls eq $rcls) {
		    if (($aiob eq "S") && ($riob eq "S")) {$nfcrt{$rcls}++; $nlcrt{$rcls}++; $nrcrt{$rcls}++;}
		    if (($aiob eq "S") && ($riob eq "E")) {$nrcrt{$rcls}++}
		    if (($aiob eq "E") && ($riob eq "S")) {$nrcrt{$rcls}++}
		    if (($aiob eq "S") && ($riob eq "B")) {$nlcrt{$rcls}++}
		    if (($aiob eq "B") && ($riob eq "S")) {$nlcrt{$rcls}++}
		    if (($aiob eq "B") && ($riob eq "B")) {$nlcrt{$rcls}++; $match = 1;}
		    if (($aiob eq "E") && ($riob eq "E")) {$nrcrt{$rcls}++; if ($match) {$nfcrt{$rcls}++;}}
		} # if

		if (($atag ne $rtag) || (($aiob ne "B") && ($aiob ne "I"))) {$match = 0}

	    } # for ($i)

	    if (defined($opt_e)) {
		for ($i=0; $i<=$#rtags; $i++) {
		    print EFILE join ("\t", $rwrds[$i], $rtags[$i], $atags[$i], $chks[$i]), "\n";
		} # for
		print EFILE "\n";
	    } # if
	} # if
	@rwrds = @rtags = @atags = @chks = ();
    } # if

    elsif (substr($rline, 0, 11) eq "###MEDLINE:") {
	print EFILE $rline, "\n\n";

	$medid = substr($rline, 11);

	if ($rline = <RFILE>) {chomp $rline}
	else {die "suspicious error at the end of the reference file.\n"}

	if ($aline = <AFILE>) {chomp $aline}
	else {die "suspicious error at the end of the answer file.\n"}
	$linenum++;

	if (($rline ne "")||($aline ne "")) {die "format mismatch error at the line $linenum.\n"}
    } # if
 

    else {
	@rvals = split(/\t/, $rline);
	push @rwrds, $rvals[$wfield];
	push @rtags, $rvals[$rfield];

	@avals = split(/\t/, $aline);
	push @atags, $avals[$afield];
    } # else
} # while


foreach $obj (@objs) {
    $nref{$alls}+=$nref{$obj}; $nans{$alls}+=$nans{$obj};
    $nfcrt{$alls}+=$nfcrt{$obj}; $nlcrt{$alls}+=$nlcrt{$obj}; $nrcrt{$alls}+=$nrcrt{$obj};
} # foreach

push @objs, $alls;


#####
# Performance Report: Total
#####

$title  = "                              Biomedical Entity Recognition Performance (Genaral)                                         \n";
$legend = "                                                                                         number(recall/precision/f-score) \n";
$border = "+------------------+---------------------------------+---------------------------------+---------------------------------+\n";
$ctitle = "|                  |          complete match         |       right boundary match      |       left boundary match       |\n";

format PERFROW =
| @|||||||| (@###) | @|||||||||||||||||||||||||||||| | @|||||||||||||||||||||||||||||| | @|||||||||||||||||||||||||||||| |
$obj, $nref{$obj}, &perfs($nref{$obj}, $nans{$obj}, $nfcrt{$obj}), &perfs($nref{$obj}, $nans{$obj}, $nrcrt{$obj}), &perfs($nref{$obj}, $nans{$obj}, $nlcrt{$obj})
.

print $title, $legend, $border, $ctitle, $border;
$~ = "PERFROW";
foreach $obj (@objs) {
    write (STDOUT); print $border;
} # foreach

print "\n\n\n";


sub perfs {
    my ($numref, $numans, $numcrt) = @_;
    if ($numref==0) {$recall=0} else {$recall=$numcrt/$numref}
    if ($numans==0) {$precision=0} else {$precision=$numcrt/$numans}
    if ($precision+$recall==0) {$fscore = 0} else {$fscore=2*$precision*$recall/($precision+$recall)}

    $recall*=100; $precision*=100; $fscore*=100;
    return sprintf("%4d (%5.2f\% / %5.2f\% / %5.2f\%)", $numcrt, $recall, $precision, $fscore);
} # perfs


sub iob2_iobes {
    my (@tags) = @_;
    my ($i);

    for ($i=0; $i<=$#tags; $i++) {

	if (substr($tags[$i], 0, 1) eq "I") {

	    if (($i==$#tags)||(substr($tags[$i+1], 0, 1) ne "I"))
		{substr($tags[$i], 0, 1) = "E"}

	} elsif (substr($tags[$i], 0, 1) eq "B") {

	    if (($i==$#tags)||(substr($tags[$i+1], 0, 1) ne "I"))
		{substr($tags[$i], 0, 1) = "S"}

	} # elsif

    } # for

    return @tags;
} # iob2_iobes
