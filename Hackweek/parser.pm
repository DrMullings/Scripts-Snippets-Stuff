#!/usr/bin/perl
# blablbala License
# 
use strict;
use warnings;
use Data::Dumper;
use JSON;

my $libdir = '/home/jora/Git/os-autoinst-distri-opensuse/lib';


# %data{file}{function}{description} = Comment above sub
my %data;
my $inPod = 0;

sub is_comment {
    my $row = shift;
    return ($row =~ /^#/);
}

sub is_pod_start {
    my $row = shift;
    return ($row =~ /^=head.*/);
}

sub is_pod_end {
    my $row = shift;
    return ($row =~ /^=cut/);
}

sub is_sub {
    my $row = shift;
    return ($row =~ /^sub/);
}

# open the dir

opendir (DIR, $libdir) or die "cannot open directory ($libdir)";
my @docs = grep(/\.pm$/,readdir(DIR));

# loop over files

foreach my $file (@docs) {
    open (my $fh, "<" ,"$libdir/$file") or die "could not open $file\n";

    my %filedata;
    my @buffer;
    my $count = 0;    

    while (my $row = <$fh>) {
        if (is_comment $row) {
            chomp $row;
            $row =~ s/\#//g;
            push @buffer, $row;
        }
        elsif (is_pod_start $row) {
            $inPod = 1;
            next;
        }
        elsif (is_pod_end $row) {
            $inPod = 0;
            next;
        }
        elsif ($inPod) {
            chomp $row;
            push @buffer, $row;
            next;   
        }
        else
        {
            if (is_sub $row) {
                chomp $row;
                $row =~ s/.*sub\s(.*)\s\{/$1/;
                $filedata{"$row"} = "@buffer";
            }
            else {
                $count++;
            }
        }
        if ($count ge 2) {
            @buffer = ();
        }
    }

    $data{"$file"} = \%filedata;
    close ($fh) or warn "Error closing file $file";
}

my $json = encode_json \%data;
unless (open FILE, '>', "functions.json") {
    die "could not create JSON file";
}

print FILE $json;

1;
