#################################################################################
# Kiriwrite Presentation Module - HTML 4.0 Strict (HTML4S.pm)			#
# Output Module for writing pages to the HTML 4.0 Strict Standard		#
#										#
# Copyright (C) 2007 Steve Brokenshire <sbrokenshire@xestia.co.uk>		#
#										#
# This module is licensed under the same license as Kiriwrite which is the GPL. #
#										#
# This program is free software; you can redistribute it and/or modify it under #
# the terms of the GNU General Public License as published by the Free		#
# Software Foundation; as version 2 of the License.				#
#										#
# This program is distributed in the hope that it will be useful, but WITHOUT 	#
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS	#
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.#
#										#
# You should have received a copy of the GNU General Public License along with	#
# this program; if not, write to the Free Software Foundation, Inc., 51 	#
# Franklin St, Fifth Floor, Boston, MA 02110-1301 USA				#
#################################################################################

# Define the package (perl module) name.

package Kiriwrite::Presentation::HTML4S;

# Enable strict and use warnings.

use strict;
use warnings;

# Set the following values.

our $VERSION = "0.1.0";
my $pagedata = "";
my $tablevel = 0;

#################################################################################
# Generic Subroutines.								#
#################################################################################

sub new{
#################################################################################
# new: Create an instance of Kiriwrite::Presentation::HTML4S			#
# 										#
# Usage:									#
#										#
# $presmodule = Kiriwrite::Presentation::HTML4S->new();				#
#################################################################################
	
	# Get the perl module name.

	my $class = shift;
	my $self = {};

	return bless($self, $class);

}

sub clear{
#################################################################################
# clear: Clear the current layout created by this module.			#
# 										#
# Usage:									#
# 										#
# $presmodule->clear();								#
#################################################################################

	$pagedata = "";
	return;

}

sub grab{
#################################################################################
# grab: Grab the current layout created by this module.				#
#										#
# Usage:									#
#										#
# $presmodule->grab();								#
#################################################################################

	return $pagedata;

}

sub convert{
#################################################################################
# convert: Converts the data passed into data that is compliant with the output #
# format.									#
# 										#
# Usage:									#
#										#
# $presmodule->convert(data, type);						#
#										#
# data		Specifies the data to be converted.				#
# type		Specifies the type the data should be converted to.		#
#################################################################################

	# Get the data and type passed.

	my $class = shift;
	my ($data, $type) = @_;

	# Check if certain values are undefined and if they are
	# then set them blank or return an error.

	if (!$data){
		$data = "";
	}

	if (!$type){
		die("No type was specified");
	}

	# Check what type is being used and process the data
	# according the type being used.

	if ($type eq "content"){

		$data =~ s/&/&amp;/g;
		$data =~ s/#/&#35;/g;
		$data =~ s/\"/&#34;/g;
		$data =~ s/'/'/g;
		$data =~ s/>/&gt;/g;
 		$data =~ s/</&lt;/g;
		$data =~ s/\+/&#43;/g;
		$data =~ s/-/&#45;/g;
		$data =~ s/_/&#95;/g;
		$data =~ s/\@/&#64;/g;
		$data =~ s/~/&#126;/g;
		$data =~ s/\?/&#63;/g;
		$data =~ s/'/&#39;/g;
		$data =~ s/\0//g;
		$data =~ s/\b//g;

	} elsif ($type eq "link"){

		$data =~ s/&/&amp;/g;
		$data =~ s/\+/\%2B/g;
		$data =~ s/\?/\%3F/g;
		$data =~ s/%3F/\?/;
		$data =~ s/-/\%2D/g;
		$data =~ s/_/\%5F/g;
		$data =~ s/\@/\%40/g;
		$data =~ s/#/\%23/g;
		$data =~ s/>/\%3E/g;
		$data =~ s/</\%3C/g;
		$data =~ s/~/\%7E/g;
		$data =~ s/'/\%27/;
 		$data =~ s/!/\%21/g;

	} else {

		die("An invalid type was specified.");

	}

	return $data;

}

#################################################################################
# Tags for creating tables.							#
#################################################################################

sub starttable{
#################################################################################
# starttable: Start a table.							#
# 										#
# Usage:									#
#										#
# $presmodule->starttable(cssstyle, {options});					#
# 										#
# cssstyle	Specifies the CSS style name to use.				#
# options	Specifies the following options (in any order):			#
#										#
# CellPadding	The cell padding to be used for each table.			#
# CellSpacing	The cell spacing to be used for each table.			#
#################################################################################

	# Get the CSS style and options.

	my $class = shift;
	my ($cssstyle, $options) = @_;

	my $tagdata = "";
	my $tabcount = $tablevel;

	my $cellpadding = $options->{'CellPadding'};
	my $cellspacing = $options->{'CellSpacing'};

	# Check if the cell padding and cell spacing and 
	# CSS style values are blank and if they are then 
	# set them blank.

	if (!$cellpadding){
		$cellpadding = 0;
	}

	if (!$cellspacing){
		$cellspacing = 0;
	}

	if (!$cssstyle){
		$cssstyle = "";
	}

	# Check if the cell padding and cell spacing values
	# are valid and die if it isn't.

	my $cellpadding_validated = $cellpadding;
	my $cellspacing_validated = $cellspacing;

	$cellpadding_validated =~ tr/0-9//d;
	$cellspacing_validated =~ tr/0-9//d;

	if ($cellpadding_validated ne ""){
		die("Cell padding value given is invalid.");
	}

	if ($cellspacing_validated ne ""){
		die("Cell spacing value given is invalid.");
	}

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	# Start a table.

	$tagdata = $tagdata . "<table";

	# Check if the cell spacing and cell padding has values
	# more than 0.

	if ($cellspacing >= 0){
		$tagdata = $tagdata . " cellspacing=\"" . $cellspacing . "\"";
	}

	if ($cellpadding > 0){
		$tagdata = $tagdata . " cellpadding=\"" . $cellpadding . "\"";
	}

	if ($cssstyle ne ""){
		$tagdata = $tagdata . " class=\"" . $class->convert($cssstyle, "content") . "\"";
	}

	$tagdata = $tagdata . ">" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;
	$tablevel++;

}

sub startheader{
#################################################################################
# startheader: Start a table header.						#
#										#
# Usage:									#
#										#
# $presmodule->startheader();							#
#################################################################################

	# Start a table header row.

	my $tagdata = "";
	my $tabcount = $tablevel;

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	$tagdata = $tagdata . "<tr>" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;
	$tablevel++;

}

sub addheader{
#################################################################################
# addheader: Add a table header.						#
#										#
# Usage:									#
#										#
# $presmodule->addheader(headername, {options});				#
#										#
# headername	Specifies the name of the table header to use.			#
# options	Specifies the following options below (in any order):		#
#										#
# Style		Specifies the CSS Style to use for the table header.		#
#################################################################################

	# Get the header name and options.

	my $class	= shift;
	my ($headername, $options)	= @_;

	my $cssstyle	= $options->{'Style'};

	# Check if the CSS Style or header name is undefined and
	# if they are then set them blank.

	if (!$headername){
		$headername = "";
	}

	if (!$cssstyle){
		$cssstyle = "";
	}

	my $tagdata = "";
	my $tabcount = $tablevel;

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	$tagdata = $tagdata . "<th";
	
	if ($cssstyle ne ""){
		$tagdata = $tagdata . " class=\"" . $class->convert($cssstyle, "content") . "\"";
	}

	$tagdata = $tagdata . ">" . $class->convert($headername, "content") . "</th>" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

sub endheader{
#################################################################################
# endheader: End a table header row						#
#										#
# Usage:									#
#										#
# $presmodule->endheader();							#
#################################################################################

	# End a table header row.

	my $tagdata = "";
	$tablevel = ($tablevel - 1);
	my $tabcount = $tablevel;

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	$tagdata = $tagdata . "</tr>" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

sub startrow{
#################################################################################
# startrow: Start a table row.							#
#										#
# Usage:									#
#										#
# $presmodule->startrow();							#
#################################################################################

	# Start a table row.

	my $tagdata = "";
	my $tabcount = $tablevel;

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	$tagdata = $tagdata . "<tr>" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;
	$tablevel++;

}

sub addcell{
#################################################################################
# addcell: Add a table cell.							#
#										#
# Usage:									#
#										#
# $presmodule->addcell(style);							#
#										#
# style		Specifies which CSS Style to use.				#
#################################################################################

	# Get the cell information and options.

	my $class	= shift;
	my ($cssstyle) 	= @_;
	my $tabcount	= $tablevel;
	my $tagdata	= "";

	# Check if the cell data and CSS style are undefined
	# and if they are then set them blank.

	if (!$cssstyle){
		$cssstyle = "";
	}

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	$tagdata = $tagdata . "<td";

	if ($cssstyle ne ""){
		$tagdata = $tagdata . " class=\"" . $class->convert($cssstyle, "content") . "\"";
	}

	$tagdata = $tagdata . ">";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

sub endcell{
#################################################################################
# endcell: End a table cell.							#
#										#
# Usage:									#
#										#
# $presmodule->endcell();							#
################################################################################# 

	# End a table cell.

	my $tagdata = "";

	$tagdata = $tagdata . "</td>" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

sub endrow{
#################################################################################
# endrow: Ends a table row.							#
#										#
# Usage:									#
#										#
# $presmodule->endrow();							#
#################################################################################

	# End a table row.

	my $tagdata = "";
	$tablevel = ($tablevel - 1);
	my $tabcount = $tablevel;

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	$tagdata = $tagdata . "</tr>" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

sub endtable{
#################################################################################
# endtable: Ends a table.							#
#										#
# Usage:									#
#										#
# $presmodule->endtable();							#
#################################################################################

	# End a table.

	my $tagdata = "";
	$tablevel = ($tablevel - 1);
	my $tabcount = $tablevel;

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	$tagdata = $tagdata . "</table>" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

#################################################################################
# Information box.								#
#################################################################################

sub startbox{
#################################################################################
# startbox: Start an information box.						#
#										#
# Usage:									#
#										#
# $presmodule->startbox(cssstyle);						#
#										#
# cssstyle	Specifies the CSS Style to use.					#
#################################################################################

	# Get the CSS Style name.

	my $class 	= shift;
	my $cssstyle	= shift;

	# Check if the CSS style given is undefined and
	# if it is then set it blank.

	if (!$cssstyle){
		$cssstyle = "";
	}

	my $tagdata = "";
	my $tabcount = $tablevel;

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	# Start an information box.

	$tagdata = $tagdata . "<div";
	
	if ($cssstyle ne ""){
		$tagdata = $tagdata . " class=\"" . $class->convert($cssstyle, "content") . "\"";
	}

	$tagdata = $tagdata . ">";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

sub enterdata{
#################################################################################
# enterdata: Enter data into a information box.					#
#										#
# Usage:									#
#										#
# $presmodule->enterdata(data);							#
#										#
# data		Specifies what data should be entered into the information box.	#
#################################################################################

	# Get the data for the information box.

	my $class 	= shift;
	my $data	= shift;

	# Append the data to the page data.

	$pagedata = $pagedata . $class->convert($data, "content");

}

sub endbox{
#################################################################################
# endbox: End an information box.						#
#										#
# Usage:									#
#										#
# $presmodule->endbox();							#
#################################################################################

	# End an information box.

	my $tagdata = "";
	$tagdata = $tagdata . "</div>" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

#################################################################################
# Form boxes.									#
#################################################################################

sub startform{
#################################################################################
# startform: Start a form.							#
#										#
# Usage:									#
#										#
# $presmodule->startform(action, method);					#
#										#
# action	Specifies the action (address) the data should be sent to.	#
# method	Specifies the method to use (POST, GET)				#
#################################################################################

	my $class	= shift;
	my $action	= shift;
	my $method	= shift;

	my $tagdata	= "";
	my $tabcount	= $tablevel;

	# Check if the action and method values given
	# are undefined and if they are set default
	# values.

	if (!$action){
		$action = "";
	}

	if (!$method){
		# The method is blank so set it to POST.
		$method = "POST";
	}

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	$tagdata = $tagdata . "<form action=\"" . $class->convert($action, "content") . "\" method=\"" . $class->convert($method, "content") . "\">" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;
	$tablevel++;

}

sub addcheckbox{
#################################################################################
# addcheckbox: Add a check box.							#
#										#
# Usage:									#
#										#
# $presmodule->addcheckbox(checkboxname, {options});				#
#										#
# checkboxname	Specifies the check box name.					#
# options	Specifies the following options below (in any order).		#
#										#
# OptionDescription	Specifies a description for the checkbox value.		#
# Style			Specifies the CSS style to use.				#
# Checked		Specifies if the checkbox is checked.			#
# LineBreak		Specifies if a line break should be added.		#
#################################################################################

	# Get the options recieved.

	my $class	= shift;
	my ($checkboxname, $options) = @_;

	my $tagdata	= "";
	my $tabcount	= $tablevel;

	# Get certain values from the hash.

	my $optiondescription 	= $options->{'OptionDescription'};
	my $style		= $options->{'Style'};
	my $checked		= $options->{'Checked'};
	my $linebreak		= $options->{'LineBreak'};

	# Check if certain values are undefined and if they
	# are then set them blank or to a default value.

	if (!$checkboxname){
		die("The checkbox name is blank.");
	}

	if (!$optiondescription){
		$optiondescription = "";
	}

	if (!$style){
		$style = "";
	}

	if (!$checked){
		$checked = 0;
	}

	if (!$linebreak){
		$linebreak = 0;
	}

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	# Add a check box.

	$tagdata = $tagdata . "<input type=\"checkbox\" name=\"" . $class->convert($checkboxname, "content") . "\"";

	if ($style ne ""){
		$tagdata = $tagdata . " class=\"" . $class->convert($style, "content") . "\"";
	}

	if ($checked eq 1){
		$tagdata = $tagdata . " checked";
	}

	$tagdata = $tagdata . ">";

	if ($optiondescription ne ""){
		$tagdata = $tagdata . "&nbsp;" . $class->convert($optiondescription, "content");
	}

	if ($linebreak eq 1){
		$tagdata = $tagdata . "<br>";
	}

	$tagdata = $tagdata . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

sub addradiobox{
#################################################################################
# addradiobox: Add a radio box.							#
# 										#
# Usage:									#
#										#
# $presmodule->addradiobox(radioboxname, {options});				#
#										#
# radioboxname	The name of the radio box.					#
# options	Specifies the following options below (in any order).		#
#										#
# Description		Specifies a description for the checkbox value.		#
# Style			Specifies the CSS style to use.				#
# Selected		Specifies if the radio box is selected.			#
# LineBreak		Specifies if a line break should be used.		#
# Value			Specifies the value of the radio box.			#
#################################################################################

	# Get the options recieved.

	my $class	= shift;
	my ($radioboxname, $options) = @_;

	my $tagdata	= "";
	my $tabcount	= $tablevel;

	# Get certain values from the hash.

	my $optiondescription	= $options->{'Description'};
	my $style		= $options->{'Style'};
	my $selected		= $options->{'Selected'};
	my $linebreak		= $options->{'LineBreak'};
	my $value		= $options->{'Value'};

	# Check if certain values are undefined and if they
	# are then set them blank or to a default value.	

	if (!$radioboxname){
		die("The radio box name is blank.");
	}

	if (!$value){
		$value = "";
	}

	if (!$optiondescription){
		$optiondescription = "";
	}

	if (!$style){
		$style = "";
	}

	if (!$selected){
		$selected = 0;
	}

	if (!$linebreak){
		$linebreak = 0;
	}

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	# Add a radio box.

	$tagdata = $tagdata . "<input type=\"radio\" name=\"" . $class->convert($radioboxname, "content") . "\"";

	if ($style ne ""){
		$tagdata = $tagdata . " class=\"" . $class->convert($style, "content") . "\"";
	}

	if ($selected eq 1){
		$tagdata = $tagdata . " checked";
	}

	if ($value ne ""){
		$tagdata = $tagdata . " value=\"" . $class->convert($value, "content") . "\"";
	} else {
		$tagdata = $tagdata . " value=\"0\"";
	}

	$tagdata = $tagdata . ">";

	if ($optiondescription ne ""){
		$tagdata = $tagdata . "&nbsp;" . $class->convert($optiondescription, "content");
	}

	if ($linebreak eq 1){
		$tagdata = $tagdata . "<br>";
	}

	$tagdata = $tagdata . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;
}

sub addselectbox{
#################################################################################
# addselectbox: Add a select box.						#
#										#
# Usage:									#
#										#
# $presmodule->addselectbox(selectname, {options});				#
#										#
# selectboxname	Specifies the name of the select box.				#
# options	Specifies the following options (in any order).			#
#										#
# Style		Specifies the CSS style to use.					#
#################################################################################

	# Get the options recieved.

	my $class	= shift;
	my ($selectboxname, $options) = @_;

	my $tagdata 	= "";
	my $tabcount	= $tablevel;

	# Get certain values from the hash.

	my $style	= $options->{'Style'};

	# Check if certain values are undefined and if they
	# are then set them blank or to a default value.

	if (!$selectboxname){
		die("The select box name is blank.")
	}

	if (!$style){
		$style = "";
	}

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	# Add a select box.

	$tagdata = $tagdata . "<select name=\"" . $class->convert($selectboxname, "content") . "\"";

	if ($style ne ""){
		$tagdata = $tagdata = " class=\"" . $class->convert($style, "content") . "\"";
	}

	$tagdata = $tagdata . ">";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;
	$tablevel++;

}

sub addoption{
#################################################################################
# addoption: Add an option for a select box.					#
#										#
# Usage:									#
#										#
# $presmodule->addoption(optionname, options);					#
#										#
# optionname	Specifies the name (description) of the option.			#
# options	Specifies the following options (in any order).			#
#										#
# Style		Specifies the CSS style to be used.				#
# Value		Specifies the value of the option.				#
# Selected	This option is selected as default when the page is displayed.	#
#################################################################################

	# Get the options recieved.

	my $class 	= shift;
	my ($optionname, $options) = @_;

	my $tagdata	= "";
	my $tabcount	= $tablevel;

	# Get certain values from the hash.

	my $style	= $options->{'Style'};
	my $value	= $options->{'Value'};
	my $selected	= $options->{'Selected'};

	# Check if certain values are undefined and if they
	# are then set them blank or to a default value.

	if (!$optionname){
		die("The option name given is blank.");
	}

	if (!$value){
		die("No value for the option was given.");
	}

	if (!$style){
		$style = "";
	}

	if (!$selected){
		$selected = 0;
	}

	# Check if certain values are valid and return
	# an error if they aren't.

	my $selected_validated = $selected;

	$selected_validated =~ tr/0-9//d;

	if ($selected_validated ne ""){
		die("The selection option is invalid.");
	}

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	# Add an option for a select box.

	$tagdata = $tagdata . "<option value=\"" . $class->convert($value, "content") . "\"";
	
	if ($style ne ""){
		$tagdata = $tagdata . " class=\"" . $class->convert($style, "content") . "\"";
	}

	if ($selected eq 1){
		$tagdata = $tagdata . " selected";
	}
	
	$tagdata = $tagdata . ">" . $class->convert($optionname, "content") .  "</option>\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

sub endselectbox{
#################################################################################
# endselectbox: Ends a select box.						#
# 										#
# Usage:									#
#										#
# $presmodule->endselectbox();							#
#################################################################################

	# End a select box.

	my $tagdata = "";
	$tablevel = ($tablevel - 1);
	my $tabcount = $tablevel;

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	$tagdata = $tagdata . "</select>" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

sub addinputbox{
#################################################################################
# addinputbox: Add a input text box.						#
#										#
# Usage:									#
#										#
# $presmodule->addinputbox(inputboxname, options);				#
#										#
# inputboxname	Specifies the name of the input text box.			#
# options	Specifies the following options (in any order).			#
#										#
# Size		Specifies the size of the input text box.			#
# MaxLength	Specifies the maximum length of the input text box.		#
# Style		Specifies the CSS style to use.					#
# Value		Specifies a value for the input box.				#
#################################################################################

	# Get the options recieved.

	my $class	= shift;
	my ($inputboxname, $options) = @_;

	my $tagdata	= "";
	my $tabcount	= $tablevel;

	# Get certain values from the hash.

	my $size	= $options->{'Size'};
	my $maxlength	= $options->{'MaxLength'};
	my $style	= $options->{'Style'};
	my $value	= $options->{'Value'};
	my $password	= $options->{'Password'};

	# Check if certain values are undefined and if they
	# are then set them blank or to a default value.

	if (!$inputboxname){
		die("The input box name given is blank.");
	}

	if (!$size){
		$size = 0;
	}

	if (!$maxlength){
		$maxlength = 0;
	}

	if (!$style){
		$style = "";
	}

	if (!$value){
		$value = "";
	}

	if (!$password){
		$password = 0;
	}

	# Check if certain values are valid and return
	# an error if they aren't.

	my $size_validated = $size;
	my $maxlength_validated = $maxlength;

	$size_validated 	=~ tr/0-9//d;
	$maxlength_validated 	=~ tr/0-9//d;

	if ($size_validated ne ""){
		die("The size given is invalid.");
	}

	if ($maxlength_validated ne ""){
		die("The maximum length given is invalid.");
	}

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	# Add an input text box.

	$tagdata = "<input "; 

	# Check if it should be a password field.

	if ($password eq 1){

		# The field should be a password field.

		$tagdata = $tagdata . "type=\"password\" ";

	} else {

		# The field should be a text field.

		$tagdata = $tagdata . "type=\"text\" ";

	}

	$tagdata = $tagdata . "name=\"" . $class->convert($inputboxname, "content") . "\"";
	
	if ($size > 0){
		$tagdata = $tagdata . " size=\"" . $class->convert($size, "content") . "\"";
	}

	if ($maxlength > 0){
		$tagdata = $tagdata . " maxlength=\"" . $class->convert($maxlength, "content") . "\"";
	}

	if ($style ne ""){
		$tagdata = $tagdata . " class=\"" . $class->convert($style, "content") . "\"";
	}

	if ($value ne ""){
		$tagdata = $tagdata . " value=\"" . $class->convert($value, "content") . "\"";
	}

	$tagdata = $tagdata . ">" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

sub addtextbox{
#################################################################################
# addtextbox: Add a multiple line text box.					#
#										#
# Usage:									#
#										#
# $presmodule->addtextbox(textboxname, options);				#
#										#
# textboxname	Specifies the name of the multiple line text box.		#
# options	Specifies the following options (in any order).			#
#										#
# Columns	Specifies the width of the multiple line text box.		#
# Rows		Specifies the height of the multiple line text box.		#
# Style		Specifies the CSS style to use.					#
# Value		Specifies a value for the multiple line text box.		#
#################################################################################

	# Get the options recieved.

	my $class	= shift;
	my ($textboxname, $options) = @_;

	my $tagdata	= "";
	my $tabcount	= $tablevel;

	# Get certain values from the hash.

	my $columns	= $options->{'Columns'};
	my $rows	= $options->{'Rows'};
	my $style	= $options->{'Style'};
	my $value	= $options->{'Value'};

	# Check if certain values are undefined and if they
	# are then set them blank or to a default value.

	if (!$textboxname){
		die("The multiple line text box name is blank.");
	}
	
	if (!$columns){
		$columns = 0;
	}

	if (!$rows){
		$rows = 0;
	}

	if (!$style){
		$style = "";
	}

	if (!$value){
		$value = "";
	}

	# Check if certain values are valid and return
	# an error if they aren't.

	my $columns_validated 	= $columns;
	my $rows_validated	= $rows;

	$columns_validated 	=~ tr/0-9//d;
	$rows_validated 	=~ tr/0-9//d;

	if ($columns_validated ne ""){
		die("The columns value given is invalid.");
	}

	if ($rows_validated ne ""){
		die("The rows value given is invalid.");
	}

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	# Add a multiple line text box.

	$tagdata = $tagdata . "<textarea name=\"" . $class->convert($textboxname, "content") . "\"";

	if ($columns > 0){
		$tagdata = $tagdata . " cols=\"" . $class->convert($columns, "content") . "\"";
	}	

	if ($rows > 0){
		$tagdata = $tagdata . " rows=\"" . $class->convert($rows, "content") . "\"";
	}

	if ($style ne ""){
		$tagdata = $tagdata . " class=\"" . $class->convert($style, "content") . "\"";
	}	

	$tagdata = $tagdata . ">";
	$tagdata = $tagdata . $class->convert($value, "content");
	$tagdata = $tagdata . "</textarea>" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

sub addsubmit{
#################################################################################
# addsubmit: Add a submit button.						#
#										#
# Usage:									#
#										#
# $pagemodule->addsubmit(submitname, options);					#
# 										#
# submitname	Specifies the name (label) of the submit button.		#
# options	Specifies the following options (in any order).			#
#										#
# Style		Specifies the CSS style to use.					#
#################################################################################

	# Get the options recieved.

	my $class	= shift;
	my ($submitname, $options) = @_;

	my $tagdata	= "";
	my $tabcount	= $tablevel;
	
	# Get certain values from the hash.

	my $style	= $options->{'Style'};

	# Check if certain values are undefined and if they
	# are then set them blank or to a default value.

	if (!$submitname){
		die("The submit name is blank.");
	}

	if (!$style){
		$style = "";
	}

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	# Add a submit button.

	$tagdata = $tagdata . "<input type=\"submit\" value=\"" . $class->convert($submitname, "content") . "\"";

	if ($style ne ""){
		$tagdata = $tagdata . " class=\"" . $class->convert($style, "content") . "\"";
	}

	$tagdata = $tagdata . ">" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

sub addreset{
#################################################################################
# addreset: Add a reset button.							#
#										#
# Usage:									#
#										#
# $pagemodule->addreset(resetname, options);					#
# 										#
# resetname	Specifies the name (label) of the reset button.			#
# options	Specifies the following options (in any order).			#
#										#
# Style		Specifies the CSS style to use.					#
#################################################################################

	# Get the options recieved.

	my $class	= shift;
	my ($resetname, $options) = @_;

	my $tagdata	= "";
	my $tabcount	= $tablevel;
	
	# Get certain values from the hash.

	my $style	= $options->{'Style'};

	# Check if certain values are undefined and if they
	# are then set them blank or to a default value.

	if (!$resetname){
		die("The reset name is blank.");
	}

	if (!$style){
		$style = "";
	}

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	# Add a reset button.

	$tagdata = $tagdata . "<input type=\"reset\" value=\"" . $class->convert($resetname, "content") . "\"";

	if ($style ne ""){
		$tagdata = $tagdata . " class=\"" . $class->convert($style, "content") . "\"";
	}

	$tagdata = $tagdata . ">" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

sub addhiddendata{
#################################################################################
# addhiddendata: Adds hidden data to the form.					#
#										#
# Usage:									#
#										#
# $presmodule->addhiddendata(name, value);					#
#										#
# name		Specifies the name of the hidden data.				#
# value		Specifies the value of the hidden data.				#
#################################################################################

	# Get the name and value.

	my $class	= shift;
	my ($name, $value) = @_;

	my $tagdata	= "";
	my $tabcount	= $tablevel;

	# Check if certain values are undefined and if they
	# are then set them blank or to a default value.

	if (!$name){
		die("The name for the hidden data is blank.");
	}

	if (!$value){
		$value = "";
	}

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	# Add hidden data.

	$tagdata = $tagdata . "<input type=\"hidden\" name=\"" . $class->convert($name, "content") . "\"";

	if ($value ne ""){
		$tagdata = $tagdata . " value=\"" . $class->convert($value, "content") . "\"";
	}

	$tagdata = $tagdata . ">" . "\r\n";

	# Add the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

sub addbutton{
#################################################################################
# addbutton: Add a button.							#
# 										#
# Usage:									#
#										#
# $presmodule->addbutton(buttonname, options);					#
#										#
# buttonname	Specifies the name of button.					#
# options	Specifies the following options below (in any order).		#
#										#
# Value		Specifies the value of the button.				#
# Description	Specifies the description (label) of the button.		#
# Style		Specifies the CSS style to use.					#
#################################################################################

	# Get the options recieved.

	my $class	= shift;
	my ($buttonname, $options) = @_;

	my $tagdata	= "";
	my $tabcount	= $tablevel;

	# Get certain values from the hash.

	my $value	= $options->{'Value'};
	my $description	= $options->{'Description'};
	my $style	= $options->{'Style'};

	# Check if certain values are undefined and if they
	# are then set them blank or to a default value.

	if (!$buttonname){
		die("The name for button is blank.");
	}

	if (!$value){
		$value = "";
	}

	if (!$description){
		die("The description for the button is blank.");
	}

	if (!$style){
		$style = "";
	}

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	# Add a button.

	$tagdata = $tagdata . "<button name=\"" . $class->convert($buttonname, "content") . "\"";	

	if ($value ne ""){
		$tagdata = $tagdata . " value=\"" . $class->convert($value, "content") . "\"";
	}

	if ($style ne ""){
		$tagdata = $tagdata . " class=\"" . $class->convert($style, "content") . "\"";
	}

	$tagdata = $tagdata . ">" . $class->convert($description, "content") . "</button>\r\n";

	# Add the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

sub endform{
#################################################################################
# endform: Ends a form.								#
#										#
# Usage:									#
#										#
# $presmodule->endform();							#
#################################################################################

	# End a form.

	my $tagdata = "";
	$tablevel = ($tablevel - 1);
	my $tabcount = $tablevel;

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	$tagdata = $tagdata . "</form>" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

#################################################################################
# Page Link.									#
#################################################################################

sub addlink{
#################################################################################
# addlink: Adds a link.								#
#										#
# Usage:									#
#										#
# $presmodule->addlink(link, options);						#
#										#
# Link		Specifies the location of the link.				#
# options	Specifies the following options below (in any order).		#
#										#
# Target	Specifies the target window for the link.			#
# Text		Specifies the text to use.					#
#################################################################################

	# Get the options recieved.

	my $class	= shift;
	my ($link, $options) = @_;

	my $tagdata	= "";
	my $tabcount	= $tablevel;

	# Get certain values from the hash.

	my $target	= $options->{'Target'};	
	my $name	= $options->{'Text'};
	my $embed	= $options->{'Embed'};

	# Check if certain values are undefined and if they
	# are then set them blank or to a default value.

	if (!$link){
		die("The link specified was blank.");
	}

	if (!$target){
		$target = "";
	}

	if (!$embed){
		$embed = 0;
	}

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	# Add a link.

	$tagdata = "<a href=\"" . $class->convert($link, "link") . "\"";	

	if ($target ne ""){
		$tagdata = $tagdata . " target=\"" . $class->convert($target, "content") . "\"";
	}

	$tagdata = $tagdata . ">" . $class->convert($name, "content")  . "</a>" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

#################################################################################
# Image.									#
#################################################################################

sub addimage{
#################################################################################
# addimage: Adds an image.							#
#										#
# Usage:									#
#										#
# $presmodule->addimage(image, options);					#
#										#
# image		Specifies the location of the image.				#
# options	Specifies the following options below (in any order).		#
#										#
# Style		Specifies the CSS style to use.					#
# Description	Specifies the description of the image.				#
# Width		Specifies the width of the image.				#
# Height	Specifies the height of the image.				#
#################################################################################

	# Get the options recieved.

	my $class	= shift;
	my ($image, $options) = @_;

	my $tagdata	= "";
	my $tabcount 	= $tablevel;

	# Get certain values from the hash.

	my $style	= $options->{'Style'};
	my $width	= $options->{'Width'};
	my $height	= $options->{'Height'};

	# Check if certain values are undefined and if they
	# are then set them blank or to a default value.

	if (!$image){
		die("The link to the image given is blank");
	}

	if (!$style){
		$style = "";
	}

	if (!$width){
		$width = 0;
	}

	if (!$height){
		$height = 0;
	}

	# Check if certain values are valid and return
	# an error if they aren't.

	my $width_validated 	= $width;
	my $height_validated	= $height;

	$width_validated 	=~ tr/0-9//d;
	$height_validated 	=~ tr/0-9//d;

	if (!$width_validated){
		die("The width value given is invalid.");
	}

	if (!$height_validated){
		die("The height value given is invalid.");
	}

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	# Add an image.

	$tagdata = $tagdata . "<img src=\"" . $class->convert($image, "content") . "\"";

	if ($style ne ""){
		$tagdata = $tagdata . " class=\"" . $class->convert($style, "content") . "\"";
	}

	if ($width ne 0){
		$tagdata = $tagdata . " width=\"" . $class->convert($width, "content") . "\"";
	}

	if ($height ne 0){
		$tagdata = $tagdata . " height=\"" . $class->convert($height, "content") . "\"";
	}

	$tagdata = $tagdata . ">" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

#################################################################################
# Text.										#
#################################################################################

sub addtext{
#################################################################################
# addtext: Adds some text.							#
#										#
# Usage:									#
#										#
# $presmodule->addtext(text, options);						#
#										#
# text		Specifies the text to add.					#
# options	Specifies the following options below (in any order).		#
#										#
# Style		Specifies the CSS style to use.					#
#################################################################################

	# Get the options recieved.

	my $class	= shift;
	my ($text, $options) = @_;

	my $tagdata 	= "";
	my $tabcount	= $tablevel;

	# Get certain values from the hash.

	my $style	= $options->{'Style'};

	# Check if certain values are undefined and if they
	# are then set them blank or to a default value.

	if (!$style){
		$style = "";
	}

	if (!$text){
		$text = "";
	}

	# Add some text.

	if ($style ne ""){
		$tagdata = $tagdata . "<span class=\"" . $class->convert($style, "content") . "\">" . $class->convert($text, "content") . "</span>";
	} else {
		$tagdata = $tagdata . $class->convert($text, "content");
	}	

	# Append the tagdata to the pagedata.

	$pagedata = $pagedata . $tagdata;

}

sub addboldtext{
#################################################################################
# addboldtext: Adds some bold text.						#
#										#
# Usage:									#
#										#
# $presmodule->addboldtext(text, options);					#
#										#
# text		Specifies the text to add.					#
# options	Specifies the following options below (in any order).		#
#										#
# Style		Specifies the CSS style to use.					#
#################################################################################

	# Get the options recieved.

	my $class	= shift;
	my ($text, $options) = @_;

	my $tagdata 	= "";
	my $tabcount	= $tablevel;

	# Get certain values from the hash.

	my $style	= $options->{'Style'};

	# Check if certain values are undefined and if they
	# are then set them blank or to a default value.

	if (!$text){
		die("The text given was blank.");
	}	

	if (!$style){
		$style = "";
	}

	# Add some bold text.

	if ($style ne ""){
		$tagdata = $tagdata . "<span class=\"" . $style . "\">" . $class->convert($text, "content") . "</span>";
	} else {
		$tagdata = $tagdata . "<b>" . $class->convert($text, "content") . "</b>";
	}

	# Append the tagdata to the pagedata.

	$pagedata = $pagedata . $tagdata;

}

sub additalictext{
#################################################################################
# addboldtext: Adds some italic text.						#
#										#
# Usage:									#
#										#
# $presmodule->additalictext(text, options);					#
#										#
# text		Specifies the text to add.					#
# options	Specifies the following options below (in any order).		#
#										#
# Style		Specifies the CSS style to use.					#
#################################################################################

	# Get the options recieved.

	my $class	= shift;
	my ($text, $options) = @_;

	my $tagdata	= "";
	my $tabcount	= $tablevel;

	# Get certain values from the hash.

	my $style	= $options->{'Style'};

	# Check if certain values are undefined and if they
	# are then set them blank or to a default value.

	if (!$text){
		die("The text given was blank.");
	}	

	if (!$style){
		$style = "";
	}

	# Add some italic text.

	if ($style ne ""){
		$tagdata = $tagdata . "<span class=\"\">" . $class->convert($text, "content") . "</span>";		
	} else {
		$tagdata = $tagdata . "<i>" . $class->convert($text, "content") . "</i>";
	}

	# Append the tagdata to the pagedata.

	$pagedata = $pagedata . $tagdata;

}

sub addlinebreak{
#################################################################################
# addlinebreak: Adds a line break specific to the output format.		#
#										#
# Usage:									#
#										#
# $presmodule->addlinebreak();							#
#################################################################################

	# Add a line break.

	my $tagdata = "";

	$tagdata = "<br>" . "\r\n";

	# Append the tagdata to the pagedata.

	$pagedata = $pagedata . $tagdata;

}

sub addhorizontalline{
#################################################################################
# addhorizontalline: Adds a horizontal line.					#
#										#
# Usage:									#
#										#
# $presmodule->addhorizontalline();						#
#################################################################################

	# Add a horizontal line.

	my $tagdata = "";
	
	$tagdata = "<hr>" . "\r\n";

	# Append the tagdata to the pagedata.

	$pagedata = $pagedata . $tagdata;

}

#################################################################################
# Other.									#
#################################################################################

sub startlist{
#################################################################################
# startlist: Start a list.							#
#										#
# Usage:									#
#										#
# $presmodule->startlist();							#
#################################################################################

	# Start a list.

	my $tagdata = "";
	my $tabcount = $tablevel;

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	$tagdata = $tagdata . "<ul>" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;
	$tablevel++;

}

sub additem{
#################################################################################
# additem: Adds an item to the list.						#
#										#
# Usage:									#
#										#
# $presmodule->additem(text, options);						#
#										#
# text		Specifies the text to use for the item.				#
# options	Specifies the following options (in any order).			#
#										#
# Style		Specifies the CSS style to use.					#
#################################################################################

	 # Get the options recieved.

	my $class	= shift;
	my ($text, $options) = @_;

	my $tagdata	= "";
	my $tabcount	= $tablevel;

	# Get certain values from the hash.

	my $style	= $options->{'Style'};

	# Check if certain values are undefined and if they
	# are then set them blank or to a default value.

	if (!$text){
		die("The text given was blank.");
	}

	if (!$style){
		$style = "";
	}

	# Add an item to the list.

	$tagdata = $tagdata . "<li ";

	if ($style ne ""){
		$tagdata = $tagdata . " class=\"" . $class->convert($style, "content") . "\"";
	}

	$tagdata = $tagdata . ">" . $class->convert($text, "content");

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

sub endlist{
#################################################################################
# endlist: End a list.								#
#										#
# Usage:									#
#										#
# $presmodule-endlist();							#
#################################################################################

	# End a list.

	my $tagdata = "";
	$tablevel = ($tablevel - 1);
	my $tabcount = $tablevel;

	while ($tabcount > 0){
		$tagdata = $tagdata . "\t";
		$tabcount = $tabcount - 1;
	}

	$tagdata = $tagdata . "</ul>" . "\r\n";

	# Append the tag data to the page data.

	$pagedata = $pagedata . $tagdata;

}

1;