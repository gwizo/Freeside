#!/usr/bin/perl -Tw
#
# $Id: svc_acct.cgi,v 1.4 1999-01-18 09:22:34 ivan Exp $
#
# Usage: post form to:
#        http://server.name/path/svc_acct.cgi
#
# Note: Should be run setuid freeside as user nobody.
#
# loosely (sp?) based on search/cust_main.cgi
#
# ivan@voicenet.com 96-jan-3 -> 96-jan-4
#
# rewrite (now does browsing too) ivan@sisd.com 98-mar-9
#
# Changes to allow page to work at a relative position in server
#       bmccane@maxbaud.net     98-apr-3
#
# show unlinked accounts ivan@sisd.com 98-jun-22
#
# use FS::CGI, show total ivan@sisd.com 98-jul-17
#
# give service and customer info too ivan@sisd.com 98-aug-16
#
# $Log: svc_acct.cgi,v $
# Revision 1.4  1999-01-18 09:22:34  ivan
# changes to track email addresses for email invoicing
#
# Revision 1.3  1998/12/23 03:06:28  ivan
# $cgi->keywords instead of $cgi->query_string
#
# Revision 1.2  1998/12/17 09:41:10  ivan
# s/CGI::(Base|Request)/CGI.pm/;
#

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use FS::UID qw(cgisuidsetup);
use FS::Record qw(qsearch qsearchs);
use FS::CGI qw(header idiot popurl);
use FS::svc_acct;
use FS::cust_main;

my($cgi)=new CGI;
&cgisuidsetup($cgi);

my(@svc_acct,$sortby);

my($query)=$cgi->keywords;
$query ||= ''; #to avoid use of unitialized value errors
#this tree is a little bit redundant
if ( $query eq 'svcnum' ) {
  $sortby=\*svcnum_sort;
  @svc_acct=qsearch('svc_acct',{});
} elsif ( $query eq 'username' ) {
  $sortby=\*username_sort;
  @svc_acct=qsearch('svc_acct',{});
} elsif ( $query eq 'uid' ) {
  $sortby=\*uid_sort;
  @svc_acct=grep $_->uid ne '', qsearch('svc_acct',{});
} elsif ( $query eq 'UN_svcnum' ) {
  $sortby=\*svcnum_sort;
  @svc_acct = grep qsearchs('cust_svc',{
      'svcnum' => $_->svcnum,
      'pkgnum' => '',
    }), qsearch('svc_acct',{});
} elsif ( $query eq 'UN_username' ) {
  $sortby=\*username_sort;
  @svc_acct = grep qsearchs('cust_svc',{
      'svcnum' => $_->svcnum,
      'pkgnum' => '',
    }), qsearch('svc_acct',{});
} elsif ( $query eq 'UN_uid' ) {
  $sortby=\*uid_sort;
  @svc_acct = grep qsearchs('cust_svc',{
      'svcnum' => $_->svcnum,
      'pkgnum' => '',
    }), qsearch('svc_acct',{});
} else {
  &usernamesearch;
}

if ( scalar(@svc_acct) == 1 ) {
  my($svcnum)=$svc_acct[0]->svcnum;
  print $cgi->redirect(popurl(2). "view/svc_acct.cgi?$svcnum");  #redirect
  exit;
} elsif ( scalar(@svc_acct) == 0 ) { #error
  idiot("Account not found");
  exit;
} else {
  my($total)=scalar(@svc_acct);
  print $cgi->header, header("Account Search Results",''), <<END;
    $total matching accounts found
    <TABLE BORDER=4 CELLSPACING=0 CELLPADDING=0>
      <TR>
        <TH>Service #</TH>
        <TH>Username</TH>
        <TH>UID</TH>
        <TH>Service</TH>
        <TH>Customer #</TH>
        <TH>Contact name</TH>
        <TH>Company</TH>
      </TR>
END

  my(%saw,$svc_acct);
  my $p = popurl(2);
  foreach $svc_acct (
    sort $sortby grep(!$saw{$_->svcnum}++, @svc_acct)
  ) {
    my $cust_svc = qsearchs('cust_svc', { 'svcnum' => $svc_acct->svcnum })
      or die "No cust_svc record for svcnum ". $svc_acct->svcnum;
    my $part_svc = qsearchs('part_svc', { 'svcpart' => $cust_svc->svcpart })
      or die "No part_svc record for svcpart ". $cust_svc->svcpart;
    my($cust_pkg,$cust_main);
    if ( $cust_svc->pkgnum ) {
      $cust_pkg = qsearchs('cust_pkg', { 'pkgnum' => $cust_svc->pkgnum })
        or die "No cust_pkg record for pkgnum ". $cust_svc->pkgnum;
      $cust_main = qsearchs('cust_main', { 'custnum' => $cust_pkg->custnum })
        or die "No cust_main record for custnum ". $cust_pkg->custnum;
    }
    my($svcnum,$username,$uid,$svc,$custnum,$last,$first,$company)=(
      $svc_acct->svcnum,
      $svc_acct->getfield('username'),
      $svc_acct->getfield('uid'),
      $part_svc->svc,
      $cust_svc->pkgnum ? $cust_main->custnum : '',
      $cust_svc->pkgnum ? $cust_main->getfield('last') : '',
      $cust_svc->pkgnum ? $cust_main->getfield('first') : '',
      $cust_svc->pkgnum ? $cust_main->company : '',
    );
    my($pcustnum) = $custnum
      ? "<A HREF=\"${p}view/cust_main.cgi?$custnum\"><FONT SIZE=-1>$custnum</FONT></A>"
      : "<I>(unlinked)</I>"
    ;
    my($pname) = $custnum ? "<A HREF=\"${p}view/cust_main.cgi?$custnum\">$last, $first</A>" : '';
    my $pcompany = $custnum ? "<A HREF=\"${p}view/cust_main.cgi?$custnum\">$company</A>" : '';
    print <<END;
    <TR>
      <TD><A HREF="${p}view/svc_acct.cgi?$svcnum"><FONT SIZE=-1>$svcnum</FONT></A></TD>
      <TD><FONT SIZE=-1>$username</FONT></TD>
      <TD><FONT SIZE=-1>$uid</FONT></TD>
      <TD><FONT SIZE=-1>$svc</FONT></TH>
      <TD><FONT SIZE=-1>$pcustnum</FONT></TH>
      <TD><FONT SIZE=-1>$pname<FONT></TH>
      <TD><FONT SIZE=-1>$pcompany</FONT></TH>
    </TR>
END

  }
 
  print <<END;
    </TABLE>
    </CENTER>
  </BODY>
</HTML>
END
  exit;

}

sub svcnum_sort {
  $a->getfield('svcnum') <=> $b->getfield('svcnum');
}

sub username_sort {
  $a->getfield('username') cmp $b->getfield('username');
}

sub uid_sort {
  $a->getfield('uid') <=> $b->getfield('uid');
}

sub usernamesearch {

  $cgi->param('username') =~ /^([\w\d\-]{2,8})$/; #untaint username_text
  my($username)=$1;

  @svc_acct=qsearch('svc_acct',{'username'=>$username});

}


