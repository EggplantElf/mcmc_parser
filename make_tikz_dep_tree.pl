#!/usr/bin/perl

use strict;
use warnings;
use open ':encoding(utf8)'; #Equivalent to perl -CD,
binmode STDERR,":encoding(utf8)";
binmode STDOUT,":encoding(utf8)"; #Equivalent to -CS
binmode STDIN,":encoding(utf8)";

#use vars qw/ %opt /;
my %opt;
use Getopt::Std;
my $opt_string ='tf:d:l:a:hs:rF:A:E:p:';

getopts("$opt_string",\%opt ) or usage();
usage() if $opt{h};

my $FORM_COL=defined($opt{f})?$opt{f}:1;
my $HEAD_COL=defined($opt{d})?$opt{d}:8;
my $LBL_COL =defined($opt{l})?$opt{l}:10;
my @ADD_COLS=defined($opt{a})?split(",",$opt{a}):();
my $PRINT_PREAMBLE=defined($opt{t});
my $MAX_SEN=defined($opt{s})?$opt{s}:-1;
my $EXPLICIT_ROOT=defined($opt{r});
my $FORM_SIZE=$opt{F};
my $ADD_SIZE=$opt{A};
my $EDGE_PROP=defined($opt{E})?$opt{E}:"";

printPreamble() if($PRINT_PREAMBLE);

my @buffer;
my $senCount=0;
while(<STDIN>){
    chomp;
    if(/^\s*$/){
	printSentence(@buffer);
	@buffer=();
	$senCount++;
	last if($MAX_SEN>0 && $senCount>=$MAX_SEN);
    } else {
	push @buffer,$_;
    }
}

printEnd() if($PRINT_PREAMBLE);


sub printSentence{
    my @lines=@_;
    my @cols;
    for my $l (@lines){ 
	my @c=split(/\s+/,$l);
	push @cols,\@c;
    }
    #tokens
    my @forms = map { escapeTex($_->[$FORM_COL]) } @cols;
    unshift(@forms,'\emph{root}') if($EXPLICIT_ROOT);
    @forms=map {'\begin{'.$FORM_SIZE .'}'.$_.'\end{'.$FORM_SIZE.'}' } @forms if(defined($FORM_SIZE));
    my @addColumns;
    for my $c(@ADD_COLS){
	my @a=map { escapeTex($_->[$c]) } @cols;
	@a=map {'\begin{'.$ADD_SIZE .'}'.$_.'\end{'.$ADD_SIZE.'}' } @a if(defined($ADD_SIZE));
	unshift(@a,"~") if($EXPLICIT_ROOT);
	push @addColumns,\@a;
    }
    print '\begin{dependency}[]',"\n",'\begin{deptext}',"\n";
    #print rows
    print join(" \\& ",@forms),"\\\\\n";
    foreach(@addColumns){
	print join(" \\& ",@{$_}),"\\\\\n";
    }
    print '\end{deptext}',"\n";


    #edges
    ##Note that edges in tikz-dep is one-indexed    
    if($EXPLICIT_ROOT){
	for(my $i=0;$i<scalar(@cols);++$i){
	    my $head=$cols[$i]->[$HEAD_COL]+1;
	    my $dep=$i+2;
	    my $lbl=$cols[$i]->[$LBL_COL];
	    print '\depedge[',$EDGE_PROP,']{',$head,'}{',$dep,'}{',$lbl,'}';
	    print "      % $forms[$dep-1] <- ",$forms[$head-1];
	    print "\n";
	}
    } else {
	for(my $i=0;$i<scalar(@cols);++$i){
	    my $head=$cols[$i]->[$HEAD_COL];
	    my $dep=$i+1;
	    my $lbl=$cols[$i]->[$LBL_COL];
	    if($head==0){ #root edge
		print '\deproot[',$EDGE_PROP,']{',$dep,'}{',$lbl,'}';
		print "     % root";
		print "\n";
	    } else {      #usual edge
		print '\depedge[',$EDGE_PROP,']{',$head,'}{',$dep,'}{',$lbl,'}';
		print "     % $forms[$dep-1] <- $forms[$head-1]";
		print "\n";
	    }
	}
    }
    print '\end{dependency}',"\n\n";
}

sub escapeTex {
    my $str=shift;
    # Escaping ', `, and & isn't easy with tikz-dependency, to lazy to figure out a workaround
#    $str=~s/'/\\'/g; #Escape '
#    $str=~s/`/\\`/g; #Escape `
    $str=~s/&/AMPERSAND/g; #Escape
    $str=~s/\$/\\\$/g;
    $str=~s/_/\\_/g;
    return $str;
}

sub printPreamble{
    print '\documentclass[11pt,a4paper]{article}',"\n";
    print '\usepackage{tikz-dependency}',"\n";
    print '\usepackage[utf8]{inputenc}',"\n";
    print "\n\n";
    if(defined($opt{p})){
	open IF,$opt{p} or die("failed to open preamble file $opt{p}");
	print $_ while(<IF>);
	close IF;
	print "\n\n";
    }
    print '\begin{document}',"\n";
    print '\pagestyle{empty}',"\n";
}


sub printEnd{
    print '\end{document}',"\n";
}

sub usage{
    print STDERR << "END";

This script takes CoNLL-style input and prints out trees for tikz
dependency. The columns for form, head, and dependency relation can be
configured, but default to CoNLL09 format (using gold heads and
labels).

It can also include additional columns that are put underneath the
text.

It generates either just the tikz-dependency code for the tree, or
with document preamble so that it can be compiled immediately.

Columns are 0-indexed.

Font sizes can be adjusted with -F and -A, by passing, e.g., -A
footnotesize.

The script reads from STDIN and prints to STDOUT.

usage: 
  $0 [-rth] [-f col] [-d col] [-l col] [-a cols] [-s max] [-F size] [-A size] [-E prop] [-p file]

  -h      : this help message
  -f col  : column for forms  (default 1)
  -d col  : column for heads  (default 8)
  -l col  : column for labels (default 10)
  -a cols : additional columns, comma-separated
  -t      : also generate the document preamble
  -s max  : take at most max sentences (default -1 = no limit)
  -r      : make the root token explicit
  -F size : size for forms (default normalsize)
  -A size : size for additional columns (default normalsize)
  -E prop : properties on \\depedge and \\deproot
  -p file : insert the lines from file into the preamble (when using -t)

Examples:

  $0 -t -s 2 < test.conll09

  Generate the first two trees from test.conll09, using CoNLL09
  format, including preamble. 

  ------------------------------------------------------------

  $0 -r -t -s 2 < test.conll09

  Same as above, but make the root token explicit.  

  ------------------------------------------------------------
  
  $0 -t -r -a 4,6 -A small < test.conll09 

  Generate trees from all files in test.conll09, using CoNLL09
  format. Add columns 4 (gold POS) and 6 (gold morphology) to the rows
  below the forms, and make them size small. Make root token explicit,
  and generate preamble.

  ------------------------------------------------------------

  $0 -t -r -d 6 -l 7 < test.conll06

  Generate trees from test.conll06. Heads are in column 6, labels in
  column 7. Make root node explicit and include preamble. (Forms are
  still in column 1, which is the default, so that index does not have
  to be specified explicitly.

  ------------------------------------------------------------

  $0 -t -r -E "edge unit distance=1ex" < test.conll09

  Generate trees from test.conll09. Set the edge property 'edge unit
  distance=1ex' on every edge.

  ------------------------------------------------------------

  $0 -t -r -E "uniapfelgruen" -t color-defs.tex < test.conll09

  Generate trees from test.conll09. Set the edge property
  'uniapfelgruen' on every edge (which will be the color on the
  edges). The color defs are read from the file color-defs.tex, which
  has the following two lines:
  1. \\usepackage{xcolor}
  2. \\definecolor{uniapfelgruen}{cmyk}{.5,0,1,0}

END
exit; 
}
