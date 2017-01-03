#!/usr/bin/perl

use strict;
use warnings;	
use File::Path qw(make_path remove_tree);
use Cwd;
use Getopt::Long;
use Pod::Usage;
use FileHandle;

our $WORKING_DIR    = getcwd();
our $TEST_FILE_NAME = 'test_file.txt';

MAIN_CODE: {
	if(scalar @ARGV == 0) { pod2usage(); }

    my $opt = {'dir'   => undef};

    GetOptions($opt,
               'dir=s@');

    my $ra_dir = $opt->{'dir'};
    foreach my $dir (@$ra_dir) {
    	my $o = $WORKING_DIR . '/' . $dir;
    	make_path($dir);
    	my $t = $o . '/' . $TEST_FILE_NAME;
    	my $fh_OUT = FileHandle->new;
   		$fh_OUT->open(">$t") || die "ERROR: Cannot open $t for writing.\n";
   		print $fh_OUT "this is the content of the test file.\n";
   		$fh_OUT->close();
    }
}

=head1 SYNOPSIS

write_multi_subdir_test_files.pl -dir *Multiple output directories okay*
