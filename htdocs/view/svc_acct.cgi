#!/usr/bin/perl -Tw
#
# $Id: svc_acct.cgi,v 1.5 1999-01-18 09:22:36 ivan Exp $
#
# Usage: svc_acct.cgi svcnum
#        http://server.name/path/svc_acct.cgi?svcnum
#
# Note: Should be run setuid freeside as user nobody.
#
# ivan@voicenet.com 96-dec-17
#
# added link to send info
# ivan@voicenet.com 97-jan-4
#
# added navigation bar and ability to change username, etc.
# ivan@voicenet.com 97-jan-30
#
# activate 800 service
# ivan@voicenet.com 97-feb-10
#
# modified navbar code (should be a subroutine?), added link to cancel account (only if not audited)
# ivan@voicenet.com 97-apr-16
#
# INCOMPLETELY rewrote some things for new API
# ivan@voicenet.com 97-jul-29
#
# FS::Search became FS::Record, use strict, etc. ivan@sisd.com 98-mar-9
#
# Changes to allow page to work at a relative position in server
# Changed 'password' to '_password' because Pg6.3 reserves the password word
#       bmccane@maxbaud.net     98-apr-3
#
# /var/spool/freeside/conf/domain ivan@sisd.com 98-jul-17
#
# displays arbitrary radius attributes ivan@sisd.com 98-aug-16
#
# $Log: svc_acct.cgi,v $
# Revision 1.5  1999-01-18 09:22:36  ivan
# changes to track email addresses for email invoicing
#
# Revision 1.4  1998/12/23 03:09:19  ivan
# $cgi->keywords instead of $cgi->query_string
#
# Revision 1.3  1998/12/17 09:57:23  ivan
# s/CGI::(Base|Request)/CGI.pm/;
#
# Revision 1.2  1998/12/16 05:24:29  ivan
# use FS::Conf;
#

use strict;
use vars qw( $conf );
use CGI;
use CGI::Carp qw( fatalsToBrowser );
use FS::UID qw( cgisuidsetup );
use FS::CGI qw( header popurl );
use FS::Record qw( qsearchs fields );
use FS::Conf;
use FS::svc_acct;
use FS::cust_svc;
use FS::cust_pkg;
use FS::part_svc;
use FS::svc_acct_pop;

my($cgi) = new CGI;
&cgisuidsetup($cgi);

$conf = new FS::Conf;
my $mydomain = $conf->config('domain');

#untaint svcnum
my($query) = $cgi->keywords;
$query =~ /^(\d+)$/;
my($svcnum)=$1;
my($svc_acct)=qsearchs('svc_acct',{'svcnum'=>$svcnum});
die "Unkonwn svcnum" unless $svc_acct;

my($cust_svc)=qsearchs('cust_svc',{'svcnum'=>$svcnum});
my($pkgnum)=$cust_svc->getfield('pkgnum');
my($cust_pkg,$custnum);
if ($pkgnum) {
  $cust_pkg=qsearchs('cust_pkg',{'pkgnum'=>$pkgnum});
  $custnum=$cust_pkg->getfield('custnum');
}

my($part_svc)=qsearchs('part_svc',{'svcpart'=> $cust_svc->svcpart } );
die "Unkonwn svcpart" unless $part_svc;

print $cgi->header, header('Account View', '');

my $p = popurl(2);
if ($pkgnum || $custnum) {
  print <<END;
<A HREF="${p}view/cust_pkg.cgi?$pkgnum">View this package (#$pkgnum)</A> | 
<A HREF="${p}view/cust_main.cgi?$custnum">View this customer (#$custnum)</A> | 
END
} else {
  print <<END;
<A HREF="${p}misc/cancel-unaudited.cgi?$svcnum">Cancel this (unaudited)account</A> |
END
}

print <<END;
<A HREF="${p}">Main menu</A></CENTER><BR>
<FONT SIZE=+1>Service #$svcnum</FONT>
END

print qq!<BR><A HREF="${p}edit/svc_acct.cgi?$svcnum">Edit this information</A>!;
#print qq!<BR><A HREF="../misc/sendconfig.cgi?$svcnum">Send account information</A>!;
print qq!<BR><BR><A HREF="#general">General</A> | <A HREF="#shell">Shell account</A> | !;
print qq!<A HREF="#slip">SLIP/PPP account</A></CENTER>!;

#formatting
print qq!<HR><CENTER><FONT SIZE=+1><A NAME="general">General</A></FONT></CENTER>!;

#svc
print "Service: <B>", $part_svc->svc, "</B>";

#username
print "<BR>Username: <B>", $svc_acct->username, "</B>";

#password
if (substr($svc_acct->_password,0,1) eq "*") {
  print "<BR>Password: <I>(Login disabled)</I><BR>";
} else {
  print "<BR>Password: <I>(hidden)</I><BR>";
}

# popnum -> svc_acct_pop record
my($svc_acct_pop)=qsearchs('svc_acct_pop',{'popnum'=>$svc_acct->popnum});

#pop
print "POP: <B>", $svc_acct_pop->city, ", ", $svc_acct_pop->state,
      " (", $svc_acct_pop->ac, ")/", $svc_acct_pop->exch, "<\B>"
  if $svc_acct_pop;

#shell account
print qq!<HR><CENTER><FONT SIZE=+1><A NAME="shell">!;
if ($svc_acct->uid ne '') {
  print "Shell account";
  print "</A></FONT></CENTER>";
  print "Uid: <B>", $svc_acct->uid, "</B>";
  print "<BR>Gid: <B>", $svc_acct->gid, "</B>";

  print qq!<BR>Finger name: <B>!, $svc_acct->finger, qq!</B><BR>!;

  print "Home directory: <B>", $svc_acct->dir, "</B><BR>";

  print "Shell: <B>", $svc_acct->shell, "</B><BR>";

  print "Quota: <B>", $svc_acct->quota, "</B> <I>(unimplemented)</I>";
} else {
  print "No shell account.</A></FONT></CENTER>";
}

# SLIP/PPP
print qq!<HR><CENTER><FONT SIZE=+1><A NAME="slip">!;
if ($svc_acct->slipip) {
  print "SLIP/PPP account</A></FONT></CENTER>";
  print "IP address: <B>", ( $svc_acct->slipip eq "0.0.0.0" || $svc_acct->slipip eq '0e0' ) ? "<I>(Dynamic)</I>" : $svc_acct->slipip ,"</B>";
  my($attribute);
  foreach $attribute ( grep /^radius_/, fields('svc_acct') ) {
    #warn $attribute;
    $attribute =~ /^radius_(.*)$/;
    my($pattribute) = ($1);
    $pattribute =~ s/_/-/g;
    print "<BR>Radius $pattribute: <B>". $svc_acct->getfield($attribute), "</B>";
  }
} else {
  print "No SLIP/PPP account</A></FONT></CENTER>"
}

print "<HR>";

	#formatting
	print <<END;

  </BODY>
</HTML>
END

