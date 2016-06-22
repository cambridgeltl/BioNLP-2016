#!/opt/local/bin/perl

# Flexible Evaluation Program

$genefile = "GENE.eval";
$altgenefile = "ALTGENE.eval";

while (substr($ARGV[0],0,1) eq "-")
{
	if ($ARGV[0] eq "-gene") { shift @ARGV; $genefile = $ARGV[0]; }
	if ($ARGV[0] eq "-altgene") { shift @ARGV; $altgenefile = $ARGV[0]; }
	if ($ARGV[0] eq "-ids") { shift @ARGV; $idfile = $ARGV[0]; }
	shift @ARGV;
}
if ($#ARGV == 0)
{
	$evalfile = $ARGV[0];
	shift @ARGV;
} else
{
	print "Usage: perl alt_eval.perl [-gene <genefile>|-altgene <altgenefile>|-ids <idfile>] evalfile\n";
	exit;
}

if ($idfile)
{
	if (! -e $idfile)
	{
		print "$idfile not found.\n";
		exit;
	}

	for (`cat $idfile`)
	{
		chomp;
		$used{$_}++;
	}
}


if (! -e $genefile)
{
	print "$genefile not found.\n";
	exit;
}

for (`cat $genefile`)
{
	chomp;
	$g = $_; # $g = lc($_);
	$g =~ s/^([^\|]+)\|//;
	$id = $1;
	next if ($idfile && ! $used{$id});
	push(@{ $GS{$id} }, $g); # GS{id} = start end|name
}

if (! -e $altgenefile)
{
	print "$altgenefile not found.\n";
	exit;
}
for (`cat $altgenefile`)
{
	chomp;
	$g = $_; # $g = lc($_);
	$g =~ s/^([^\|]+)\|//;
	$id = $1;
	next if ($idfile && ! $used{$id});
	push(@{ $S{$id} }, $g);
}

for (`cat $evalfile`)
{
	chomp;
	$g = $_; # $g = lc($_);
	$g =~ s/^([^\|]+)\|//;
	$id = $1;
	next if ($idfile && ! $used{$id});
	push(@{ $T{$id} }, $g);
}

$tp = $fp = $fn = 0;

foreach $pmid ( keys %GS )
{
	LINE:
	foreach $i (0..$#{ $GS{$pmid} })
	{
		@a = split(/\|/, $GS{$pmid}[$i]);
		$gs_ind  = $a[0];
		@ga = split(/\s/, $gs_ind);
		$startg = $ga[0];
		$endg = $ga[1];
		$gs_gene = $a[1];
		$found = 0;
		foreach $j (0..$#{ $T{$pmid} })
		{
			@aa = split(/\|/, $T{$pmid}[$j]);
			$t_ind  = $aa[0];
			@ta = split(/\s/,$t_ind);
			$startt = $ta[0];
			$endt = $ta[1];
			$t_gene = $aa[1];
			if ($gs_ind eq $t_ind)
			{
				$found=1;
				$tp++;
				print STDOUT "TP|$pmid|$gs_gene|$gs_ind|$t_gene|$t_ind\n";
				next LINE;
			}

			# check alternative forms of GS gene

			foreach $k (0..$#{ $S{$pmid} })
			{
				@aa = split(/\|/, $S{$pmid}[$k]);
				$s_ind  = $aa[0];
				@sa = split(/\s/,$s_ind);
				$starts = $sa[0];
				$ends = $sa[1];
				$s_gene = $aa[1];

				# substring of GS gene occurs in both S and T

				if ($starts >= $startg && $ends <= $endg)
				{
					if ($t_ind eq $s_ind)
					{
						$found=1;
						$tp++;
						print STDOUT "*TP|$pmid|$gs_gene|$gs_ind|$t_gene|$t_ind\n";
						next LINE;
					}
				}

				# superstring of GS gene occurs in both S and T

				elsif ($startg >= $starts && $endg <= $ends)
				{
					if ($t_ind eq $s_ind)
					{
						$found=1;
						$tp++;
						print STDOUT "**TP|$pmid|$gs_gene|$gs_ind|$t_gene|$t_ind\n";
						next LINE;
					}
				}

				# overlapping ends

				elsif ($startg <= $starts && $starts <= $endg && $endg <= $ends)
				{
					if ($t_ind eq $s_ind)
					{
						$found=1;
						$tp++;
						print STDOUT "***TP|$pmid|$gs_gene|$gs_ind|$t_gene|$t_ind\n";
						next LINE;
					}
				}
				elsif ($starts <= $startg && $startg <= $ends && $ends <= $endg)
				{
					if ($t_ind eq $s_ind)
					{
						$found=1;
						$tp++;
						print STDOUT "****TP|$pmid|$gs_gene|$gs_ind|$t_gene|$t_ind\n";
						next LINE;
					}
				}
			}
		}

		if (!$found)
		{
			print STDOUT "FN|$pmid|$gs_ind|$gs_gene\n";
			$fn++;
		}
	}
}

foreach $pmid (keys %T)
{
	LINE1:
	foreach $i (0..$#{ $T{$pmid} })
	{
		$found = 0;
		@aa = split(/\|/, $T{$pmid}[$i]);
		$t_ind  = $aa[0];
		@ta = split(/\s/,$t_ind);
		$startt = $ta[0];
		$endt = $ta[1];
		$t_gene = $aa[1];
		foreach $j (0..$#{ $GS{$pmid} })
		{
			@a = split(/\|/, $GS{$pmid}[$j]);
			$gs_ind  = $a[0];
			@ga = split(/\s/, $gs_ind);
			$startg = $ga[0];
			$endg = $ga[1];
			$gs_gene = $a[1];
			if ($gs_ind eq $t_ind)
			{
				$found = 1;
				next LINE1;
			}
		}

		# check for alternative forms of T gene in S

		foreach $k (0..$#{$S{$pmid}})
		{
			@aa = split(/\|/, $S{$pmid}[$k]);
			$s_ind  = $aa[0];
			@sa = split(/\s/,$s_ind);
			$starts = $sa[0];
			$ends = $sa[1];
			$s_gene = $aa[1];
			if ($starts >= $startt && $ends <= $endt)
			{
				if ($t_ind eq $s_ind)
				{
					$found = 1;
					next LINE1;
				}
			}
			elsif ($startt >= $starts && $endt <= $ends)
			{
				if ($t_ind eq $s_ind)
				{
					$found = 1;
					next LINE1;
				}
			}
			elsif ($startt <= $starts && $starts <= $endt && $endt <= $ends)
			{
				if ($t_ind eq $s_ind)
				{
					$found = 1;
					next LINE1;
				}
			}
			elsif ($starts <= $startt && $startt <= $ends && $ends <= $endt)
			{
				if ($t_ind eq $s_ind)
				{
					$found = 1;
					next LINE1;
				}
			}
		}

		if (!$found)
		{
			print STDOUT "FP|$pmid|$T{$pmid}[$i]\n";
			$fp++;
		}
	}
}

$pre = $tp / ($tp + $fp);
$rec  = $tp / ($fn + $tp);
$f = 2 / (1 / $pre + 1 / $rec);

print STDOUT "\nTP: $tp\nFP: $fp\nFN: $fn\nPrecision: $pre Recall: $rec F: $f\n\n";

