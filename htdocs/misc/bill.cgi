#!/usr/bin/perl -Tw
#
# $Id: bill.cgi,v 1.2 1998-12-17 09:12:41 ivan Exp $
#
# s/FS:Search/FS::Record/ and cgisuidsetup($cgi) ivan@sisd.com 98-mar-13
#
# Changes to allow page to work at a relative position in server
#       bmccane@maxbaud.net     98-apr-3
#
# $Log: bill.cgi,v $
# Revision 1.2  1998-12-17 09:12:41  ivan
# s/CGI::(Request|Base)/CGI.pm/;
#

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use FS::UID qw(cgisuidsetup);
use FS::CGI qw(popurl eidiot);
use FS::Record qw(qsearchs);
use FS::cust_main;

my($cgi) = new CGI;
&cgisuidsetup($cgi);

#untaint custnum
$cgi->query_string =~ /^(\d*)$/;
my($custnum)=$1;
my($cust_main)=qsearchs('cust_main',{'custnum'=>$custnum});
die "Can't find customer!\n" unless $cust_main;

my($error);

$error = $cust_main->bill(
#                          'time'=>$time
                         );
&eidiot($error) if $error;

$error = $cust_main->collect(
#                             'invoice-time'=>$time,
#                             'batch_card'=> 'yes',
                             'batch_card'=> 'no',
                             'report_badcard'=> 'yes',
                            );
&eidiot($error) if $error;

print $cgi->redirect(popurl(2). "view/cust_main.cgi?$custnum#history");

