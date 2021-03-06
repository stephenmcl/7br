#!/usr/local/bin/perl

use strict;
use warnings;
use FileHandle;
use Getopt::Long;
use Pod::Usage;
use File::Basename;
use Path::Class qw / dir file /;
use Cwd;
use File::Copy;

our $OUT_DIR = '/data/output/IGV/mySnapshotDirectory/';
our $IGV_JAR = '/IGV/IGV_Snapshot/igv.jar';
our $JAVA    = 'java';
our $WORKING_DIR = getcwd();
$WORKING_DIR = dir($WORKING_DIR)->absolute();

#example command:
#xvfb-run --server-args="-screen 0, 1024x768x24" java -Xmx1000m -jar /IGV/IGV_Snapshot/igv.jar -b /igv_batch.test

sub create_igv_batch_file {
    my $opt = shift;
    my $fh_OUT = new FileHandle;
    my $output_batch_script = $OUT_DIR . '/' . 'igv_batch.igv';
    $fh_OUT->open(">$output_batch_script") || die "ERROR: Cannot open output file $output_batch_script for writing.\n";
    
    my $ra_bam = $opt->{'bam'};
    my $bam_list;
    foreach my $i (@$ra_bam) {
	$bam_list .= $i . ",";
    }
    chop $bam_list; #trailing comma.
    print $fh_OUT "new\n";
    print $fh_OUT 'load ' . $bam_list . "\n";
    print $fh_OUT 'snapshotDirectory ' . $OUT_DIR . "\n";
    print $fh_OUT 'genome hg19' . "\n";
    print $fh_OUT 'goto ' . $opt->{'chr'} . ':' . $opt->{'start'} . '-' . $opt->{'stop'} . "\n";
    print $fh_OUT 'sort position' . "\n";
    print $fh_OUT 'collapse' . "\n";
    my $file_name = $opt->{'chr'} . '_' . $opt->{'start'} . '-' . $opt->{'stop'} . '.png';
    print $fh_OUT 'snapshot ' .  $file_name . "\n";
    print $fh_OUT "exit\n";
    $fh_OUT->close();
    return $output_batch_script;
}

MAIN_CODE: {
    if(scalar @ARGV == 0) { pod2usage(); }
    my $opt = {'bam'   => undef,
               'chr'   => undef, 
	       'start' => undef,
	       'stop'  => undef,
	       'debug' => undef};

    GetOptions($opt,
	       'bam=s@',
	       'chr=s',
	       'start=i',
	       'stop=i',
	       'debug+');

    my $batch_file = create_igv_batch_file($opt);
    my $cmd = 'xvfb-run --server-args="-screen 0, 1024x768x24" ' . $JAVA . ' -Xmx900m -jar ' . $IGV_JAR . ' -b ' . $batch_file;
    unless ($opt->{'debug'}) { 
	system($cmd);
	my $screen_shot_file = $OUT_DIR . '/' . $opt->{'chr'} . '_' . $opt->{'start'} . '-' . $opt->{'stop'} . '.png';
	print $screen_shot_file, "\n";
	my $destination_file = $WORKING_DIR . '/' . basename($screen_shot_file);
	copy($screen_shot_file, $destination_file);
    } else {
	print $cmd, "\n";
    }
}

=head1 SYNOPSIS

igv_screenshot.pl -bam *multiple OK* -chr -start -stop [OPTIONAL] -debug *print command without executing*
