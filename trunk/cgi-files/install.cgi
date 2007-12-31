#!/usr/bin/perl -Tw

#################################################################################
# Kiriwrite Installer Script (install.cgi)					#
# Installation script for Kiriwrite	     					#
#										#
# Version: 0.1.0								#
#										#
# Copyright (C) 2005-2007 Steve Brokenshire <sbrokenshire@xestia.co.uk>		#
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

use strict;				# Throw errors if there's something wrong.
use warnings;				# Write warnings to the HTTP Server Log file.

use utf8;
use CGI qw(:standard *table *Tr *td);
#use CGI::Carp('fatalsToBrowser'); 	# Output errors to the browser.

# Setup strings in specific languages. Style should be no spacing for
# language title and one tabbed spacing for each string.

# Define some default settings.

my $default_language 		= "en-GB";
my $default_dbdirectory		= "db";
my $default_outputdirectory	= "output";
my $default_imagesuri		= "/images/kiriwrite";

my $default_textarearows	= "10";
my $default_textareacols	= "50";

my $default_server		= "localhost";
my $default_port		= "3306";
my $default_protocol		= "tcp";
my $default_name		= "database";
my $default_username		= "username";
my $default_prefix		= "kiriwrite";

my ($kiriwrite_lang, %kiriwrite_lang);

$kiriwrite_lang{"en-GB"}{"languagename"}	= "English (British)";
	$kiriwrite_lang{"en-GB"}{"testpass"}		= "OK";
	$kiriwrite_lang{"en-GB"}{"testfail"}		= "Error";

	$kiriwrite_lang{"en-GB"}{"generic"}			= "An error occured which is not known to the Kiriwrite installer.";
	$kiriwrite_lang{"en-GB"}{"invalidvariable"}		= "The variable given was invalid.";
	$kiriwrite_lang{"en-GB"}{"invalidvalue"}		= "The value given was invalid.";
	$kiriwrite_lang{"en-GB"}{"invalidoption"}		= "The option given was invalid.";
	$kiriwrite_lang{"en-GB"}{"variabletoolong"}		= "The variable given is too long.";
	$kiriwrite_lang{"en-GB"}{"blankdirectory"}		= "The directory name given is blank.";
	$kiriwrite_lang{"en-GB"}{"invaliddirectory"}		= "The directory name given is invalid.";
	$kiriwrite_lang{"en-GB"}{"moduleblank"}			= "The module filename given is blank.";
	$kiriwrite_lang{"en-GB"}{"moduleinvalid"}		= "The module filename given is invalid.";

	$kiriwrite_lang{"en-GB"}{"dbdirectorytoolong"}		= "The database directory name given is too long.";
	$kiriwrite_lang{"en-GB"}{"outputdirectorytoolong"}	= "The output directory name given is too long.";
	$kiriwrite_lang{"en-GB"}{"imagesuripathtoolong"}	= "The images URI path name given is too long.";
	$kiriwrite_lang{"en-GB"}{"dateformattoolong"}		= "The date format given is too long.";
	$kiriwrite_lang{"en-GB"}{"customdateformattoolong"}	= "The custom date format given is too long.";
	$kiriwrite_lang{"en-GB"}{"languagefilenametoolong"}	= "The language filename given is too long.";

	$kiriwrite_lang{"en-GB"}{"dateformatblank"}		= "The date format given was blank.";
	$kiriwrite_lang{"en-GB"}{"dateformatinvalid"}		= "The date format given is invalid.";
	$kiriwrite_lang{"en-GB"}{"languagefilenameinvalid"}	= "The language filename given is invalid.";

	$kiriwrite_lang{"en-GB"}{"dbdirectoryblank"}		= "The database directory name given is blank.";
	$kiriwrite_lang{"en-GB"}{"dbdirectoryinvalid"}		= "The database directory name given is invalid.";

	$kiriwrite_lang{"en-GB"}{"outputdirectoryblank"}	= "The output directory name given is blank.";
	$kiriwrite_lang{"en-GB"}{"outputdirectoryinvalid"}	= "The output directory name given is invalid.";

	$kiriwrite_lang{"en-GB"}{"textarearowblank"}		= "The text area row value given is blank.";
	$kiriwrite_lang{"en-GB"}{"textarearowtoolong"}		= "The text area row value given is too long.";
	$kiriwrite_lang{"en-GB"}{"textarearowinvalid"}		= "The text area row value given is invalid.";

	$kiriwrite_lang{"en-GB"}{"textareacolsblank"}		= "The text area columns value given is blank.";
	$kiriwrite_lang{"en-GB"}{"textareacolstoolong"}		= "The text area columns value given is too long.";
	$kiriwrite_lang{"en-GB"}{"textareacolsinvalid"}		= "The text area columns value given is invalid.";

	$kiriwrite_lang{"en-GB"}{"presmoduleblank"}		= "The presentation module name given is blank.";
	$kiriwrite_lang{"en-GB"}{"presmoduleinvalid"}		= "The presentation module name given is invalid.";
 
	$kiriwrite_lang{"en-GB"}{"dbmoduleblank"}		= "The database module name given is blank.";
	$kiriwrite_lang{"en-GB"}{"dbmoduleinvalid"}		= "The database module name given is invalid.";
 
	$kiriwrite_lang{"en-GB"}{"presmodulemissing"}		= "The presentation module with the filename given is missing.";
	$kiriwrite_lang{"en-GB"}{"dbmodulemissing"}		= "The database module with the filename given is missing.";
	$kiriwrite_lang{"en-GB"}{"languagefilenamemissing"}	= "The language file with the filename given is missing.";
 
	$kiriwrite_lang{"en-GB"}{"servernametoolong"}		= "The database server name given is too long.";
	$kiriwrite_lang{"en-GB"}{"servernameinvalid"}		= "The database server name given is invalid.";
	$kiriwrite_lang{"en-GB"}{"serverportnumbertoolong"}	= "The database server port number given is too long.";
	$kiriwrite_lang{"en-GB"}{"serverportnumberinvalidcharacters"}	= "The database server port number given contains invalid characters.";
	$kiriwrite_lang{"en-GB"}{"serverportnumberinvalid"}	= "The database server port number given is invalid.";
	$kiriwrite_lang{"en-GB"}{"serverprotocolnametoolong"}	= "The database server protocol name given is too long.";
	$kiriwrite_lang{"en-GB"}{"serverprotocolinvalid"}		= "The database server protocol name is invalid.";
	$kiriwrite_lang{"en-GB"}{"serverdatabasenametoolong"}	= "The database name given is too long.";
	$kiriwrite_lang{"en-GB"}{"serverdatabasenameinvalid"}	= "The database name given is invalid.";
	$kiriwrite_lang{"en-GB"}{"serverdatabaseusernametoolong"}	= "The database server username given is too long.";
	$kiriwrite_lang{"en-GB"}{"serverdatabaseusernameinvalid"}	= "The database server username given is invalid.";
	$kiriwrite_lang{"en-GB"}{"serverdatabasepasswordtoolong"}	= "The database server password is too long.";
	$kiriwrite_lang{"en-GB"}{"serverdatabasetableprefixtoolong"}	= "The database server table prefix given is too long.";
	$kiriwrite_lang{"en-GB"}{"serverdatabasetableprefixinvalid"}	= "The database server table prefix given is invalid.";
 
	$kiriwrite_lang{"en-GB"}{"removeinstallscripttoolong"}	= "The remove install script value given is too long.";
	$kiriwrite_lang{"en-GB"}{"cannotwriteconfigurationindirectory"}	= "The configuration file cannot be written because the directory the install script is running from has invalid permissions.";
	$kiriwrite_lang{"en-GB"}{"configurationfilereadpermissionsinvalid"}	= "The configuration that currently exists has invalid read permissions set.";
	$kiriwrite_lang{"en-GB"}{"configurationfilewritepermissionsinvalid"}	= "The configuration that currently exists has invalid write permissions set.";

	$kiriwrite_lang{"en-GB"}{"errormessagetext"}	= "Please press the back button on your browser or preform the command needed to return to the previous page.";

	$kiriwrite_lang{"en-GB"}{"switch"}		= "Switch";
	$kiriwrite_lang{"en-GB"}{"setting"}		= "Setting";
	$kiriwrite_lang{"en-GB"}{"value"}		= "Value";
	$kiriwrite_lang{"en-GB"}{"filename"}		= "Filename";
	$kiriwrite_lang{"en-GB"}{"module"}		= "Module";
	$kiriwrite_lang{"en-GB"}{"result"}		= "Result";
	$kiriwrite_lang{"en-GB"}{"error"}		= "Error!";
	$kiriwrite_lang{"en-GB"}{"criticalerror"}	= "Critical Error!";
	$kiriwrite_lang{"en-GB"}{"errormessage"}	= "Error: ";
	$kiriwrite_lang{"en-GB"}{"warningmessage"}	= "Warning: ";

	$kiriwrite_lang{"en-GB"}{"doesnotexist"}	= "Does not exist.";
	$kiriwrite_lang{"en-GB"}{"invalidpermissionsset"}	= "Invalid permissions set.";

	$kiriwrite_lang{"en-GB"}{"dependencyperlmodulesmissing"}	= "One or more Perl modules that are needed by Kiriwrite are not installed or has problems. See the Kiriwrite documentation for more information on this.";
	$kiriwrite_lang{"en-GB"}{"databaseperlmodulesmissing"}	= "One or more Perl modules that are needed by the Kiriwrite database modules are not installed or has problems. See the Kiriwrite documentation for more information on this. There should however, be no problems with the database modules which use the Perl modules that have been found.";
	$kiriwrite_lang{"en-GB"}{"filepermissionsinvalid"}	= "One or more of the filenames checked does not exist or has invalid permissions set. See the Kiriwrite documentation for more information on this.";
	$kiriwrite_lang{"en-GB"}{"dependencymodulesnotinstalled"} 	= "One of the required Perl modules is not installed or has errors. See the Kiriwrite documentation for more information on this.";
	$kiriwrite_lang{"en-GB"}{"databasemodulesnotinstalled"}	= "None of Perl modules that are used by the database modules are not installed. See the Kiriwrite documentation for more information on this.";
	$kiriwrite_lang{"en-GB"}{"filepermissionerrors"}	= "One or more filenames checked has errors. See the Kiriwrite documentation for more information on this.",

	$kiriwrite_lang{"en-GB"}{"installertitle"}	= "Kiriwrite Installer";
	$kiriwrite_lang{"en-GB"}{"installertext"}	= "This installer script will setup the configuration file used for Kiriwrite. The settings displayed here can be changed at a later date by selecting the Edit Settings link in the View Settings sub-menu.";
	$kiriwrite_lang{"en-GB"}{"dependencytitle"}	= "Dependency and file testing results";
	$kiriwrite_lang{"en-GB"}{"requiredmodules"}	= "Required Modules";
	$kiriwrite_lang{"en-GB"}{"perlmodules"}		= "These Perl modules are used internally by Kiriwrite.";
	$kiriwrite_lang{"en-GB"}{"databasemodules"}	= "Perl Database Modules";
	$kiriwrite_lang{"en-GB"}{"databasemodulestext"}	= "These Perl modules are used by the database modules.";
	$kiriwrite_lang{"en-GB"}{"filepermissions"}	= "File permissions";
	$kiriwrite_lang{"en-GB"}{"filepermissionstext"}	= "The file permissions are for file and directories that are critical to Kiriwrite such as module and language directories.";
	
	$kiriwrite_lang{"en-GB"}{"settingstitle"}	= "Kiriwrite Settings";
	$kiriwrite_lang{"en-GB"}{"settingstext"}	= "The settings given here will be used by Kiriwrite. Some default settings are given here. Certain database modules (like SQLite) do not need the database server settings and can be left alone.";
	$kiriwrite_lang{"en-GB"}{"directories"}		= "Directories";
	$kiriwrite_lang{"en-GB"}{"databasedirectory"}	= "Database Directory";
	$kiriwrite_lang{"en-GB"}{"outputdirectory"}	= "Output Directory";
	$kiriwrite_lang{"en-GB"}{"imagesuripath"}	= "Images (URI path)";
	$kiriwrite_lang{"en-GB"}{"display"}		= "Display";
	$kiriwrite_lang{"en-GB"}{"textareacols"}	= "Text Area Columns";
	$kiriwrite_lang{"en-GB"}{"textarearows"}	= "Text Area Rows";
	$kiriwrite_lang{"en-GB"}{"date"}		= "Date";
	$kiriwrite_lang{"en-GB"}{"dateformat"}		= "Date Format";
	$kiriwrite_lang{"en-GB"}{"language"}		= "Language";
	$kiriwrite_lang{"en-GB"}{"systemlanguage"}	= "System Language";
	$kiriwrite_lang{"en-GB"}{"modules"}		= "Modules";
	$kiriwrite_lang{"en-GB"}{"presentationmodule"}	= "Presentation Module";
	$kiriwrite_lang{"en-GB"}{"databasemodule"}	= "Database Module";
	$kiriwrite_lang{"en-GB"}{"databaseserver"}	= "Database Server";
	$kiriwrite_lang{"en-GB"}{"databaseport"}	= "Database Port";
	$kiriwrite_lang{"en-GB"}{"databaseprotocol"}	= "Database Protocol";
	$kiriwrite_lang{"en-GB"}{"databasename"}	= "Database Name";
	$kiriwrite_lang{"en-GB"}{"databaseusername"}	= "Database Username";
	$kiriwrite_lang{"en-GB"}{"databasepassword"}	= "Database Password";
	$kiriwrite_lang{"en-GB"}{"databasetableprefix"}	= "Database Table Prefix";
	$kiriwrite_lang{"en-GB"}{"installationoptions"}	= "Installation Options";
	$kiriwrite_lang{"en-GB"}{"installoptions"}	= "Install Options";
	$kiriwrite_lang{"en-GB"}{"removeinstallscript"}	= "Delete this installer script after configuration file has been written.";
	$kiriwrite_lang{"en-GB"}{"savesettingsbutton"}	= "Save Settings";
	$kiriwrite_lang{"en-GB"}{"resetsettingsbutton"}	= "Reset Settings";

	$kiriwrite_lang{"en-GB"}{"installscriptremoved"}	= "The installer script was removed.";
	$kiriwrite_lang{"en-GB"}{"installedmessage"}	= "The configuration file for Kiriwrite has been written. To change the settings in the configuration file at a later date use the Edit Settings link in the View Settings sub-menu at the top of the page when using Kiriwrite.";
	$kiriwrite_lang{"en-GB"}{"cannotremovescript"}	= "Unable to remove the installer script: %s. The installer script will have to be deleted manually.";
	$kiriwrite_lang{"en-GB"}{"usekiriwritetext"}	= "To use Kiriwrite click or select the link below (will not work if the Kiriwrite script is not called kiriwrite.cgi):";
	$kiriwrite_lang{"en-GB"}{"usekiriwritelink"}	= "Start using Kiriwrite.";

my $query = new CGI;

my $language_selected = "";
my $http_query_confirm = $query->param('confirm');
my $http_query_installlanguage = $query->param('installlanguage');

if (!$http_query_installlanguage){

	$language_selected = $default_language;

} else {

	$language_selected = $http_query_installlanguage;

}

# Process the list of available languages.

my $language_list_name;
my @language_list_short;
my @language_list_long;

foreach my $language (keys %kiriwrite_lang){

	$language_list_name = $kiriwrite_lang{$language}{"languagename"} . " (" . $language .  ")";
	push(@language_list_short, $language);
	push(@language_list_long, $language_list_name);

}

# The CSS Stylesheet to use.

my $cssstyle = "

a {
	color: #FFFFFF;
}

body {
	background-color: #408080;
	color: #FFFFFF;
	font-family: sans-serif;
	font-size: 12px;
}

input {
	font-size: 12px;
	background-color: #408080;
	color: #FFFFFF;
	border-color: #102020;
	border-style: solid;
	border-width: 1px;
	padding: 3px;

}

select {
	font-size: 12px;
	padding: 3px;
	background-color: #408080;
	color: #FFFFFF;
	border-color: #102020;
	border-style: solid;
	border-width: 1px;
	padding: 3px;
}

td,table {
	padding: 5px;
	border-spacing: 0px;
}

.languagebar {
	background-color: #204040;
	vertical-align: top;
}

.languagebarselect {
	text-align: right;
	background-color: #204040;
}

.tablecellheader {
	background-color: #204040;
	font-weight: bold;
}

.tabledata {
	background-color: #357070;
}

.tablename {

	background-color: #306060;

}

";


#################################################################################
# Begin list of subroutines.							#
#################################################################################

sub kiriwrite_variablecheck{
#################################################################################
# kiriwrite_variablecheck: Check to see if the data passed is valid.		#
#										#
# Usage:									#
#										#
# kiriwrite_variablecheck(variablename, type, option, noerror);			#
#										#
# variablename	Specifies the variable to be checked.				#
# type		Specifies what type the variable is.				#
# option	Specifies the maximum/minimum length of the variable		#
#		(if minlength/maxlength is used) or if the filename should be   #
#		checked to see if it is blank.					#
# noerror	Specifies if Kiriwrite should return an error or not on		#
#		certain values.							#
#################################################################################

	# Get the values that were passed to the subroutine.

	my ($variable_data, $variable_type, $variable_option, $variable_noerror) = @_;

	if ($variable_type eq "numbers"){

		# Check for numbers and return an error if there is anything else than numebrs.

		my $variable_data_validated = $variable_data;	# Copy the variable_data to variable_data_validated.
		$variable_data_validated =~ tr/0-9//d;		# Take away all of the numbers and from the variable. 
								# If it only contains numbers then it should be blank.

		if ($variable_data_validated eq ""){
			# The validated variable is blank. So continue to the end of this section where the return function should be.
		} else {
			# The variable is not blank, so check if the no error value is set
			# to 1 or not.

			if ($variable_noerror eq 1){

				# The validated variable is not blank and the noerror
				# value is set to 1. So return an value of 1.
				# (meaning that the data is invalid).

				return 1;

			} elsif ($variable_noerror eq 0) {

				# The validated variable is not blank and the noerror
				# value is set to 0.

				kiriwrite_error("invalidvariable");

			} else {

				# The variable noerror value is something else
				# pther than 1 or 0. So return an error.

				kiriwrite_error("invalidvariable");

			}

		}

		return 0;

	} elsif ($variable_type eq "lettersnumbers"){

		# Check for letters and numbers and return an error if there is anything else other
		# than letters and numbers.

		my $variable_data_validated = $variable_data;	# Copy the variable_data to variable_data_validated
		$variable_data_validated =~ tr/a-zA-Z0-9.//d;
		$variable_data_validated =~ s/\s//g;

		if ($variable_data_validated eq ""){
			# The validated variable is blank. So continue to the end of this section where the return function should be.
		} else {
			# The variable is not blank, so check if the no error value is set
			# to 1 or not.

			if ($variable_noerror eq 1){

				# The validated variable is not blank and the noerror
				# value is set to 1. So return an value of 1.
				# (meaning that the data is invalid).

				return 1;

			} elsif ($variable_noerror eq 0) {

				# The validated variable is not blank and the noerror
				# value is set to 0.

				kiriwrite_error("invalidvariable");

			} else {

				# The variable noerror value is something else
				# pther than 1 or 0. So return an error.

				kiriwrite_error("invalidvariable");

			}

		}

		return 0;

	} elsif ($variable_type eq "maxlength"){
		# Check for the length of the variable, return an error if it is longer than the length specified.

		# Check if the variable_data string is blank, if it is then set the variable_data_length
		# to '0'.

		my $variable_data_length = 0;

		if (!$variable_data){

			# Set variable_data_length to '0'.
			$variable_data_length = 0;

		} else {

			# Get the length of the variable recieved.
			$variable_data_length = length($variable_data);

		}



		if ($variable_data_length > $variable_option){

			# The variable length is longer than it should be so check if
			# the no error value is set 1.

			if ($variable_noerror eq 1){

				# The no error value is set to 1, so return an
				# value of 1 (meaning tha the variable is
				# too long to be used).

				return 1;

			} elsif ($variable_noerror eq 0){

				# The no error value is set to 0, so return
				# an error.

				kiriwrite_error("variabletoolong");

			} else {

				# The no error value is something else other
				# than 0 or 1, so return an error.

				kiriwrite_error("variabletoolong");

			}

		} else {

			# The variable length is exactly or shorter than specified, so continue to end of this section where
			# the return function should be.

		}

		return 0;

	} elsif ($variable_type eq "datetime"){
		# Check if the date and time setting format is valid.

		if ($variable_data eq ""){

			if ($variable_noerror eq 1){

				# The no error value is set to 1 so return
				# a value of 1 (meaning that the date and
				# time format was blank).

				return 1;

			} elsif ($variable_noerror eq 0){

				# The no error value is set to 1 so return
				# an error.

				kiriwrite_error("dateformatblank");

			} else {

				# The no error value is something else other
				# than 0 or 1, so return an error.

				kiriwrite_error("invalidvariable");

			}

		}

		my $variable_data_validated = $variable_data;
		$variable_data_validated =~ tr|dDmMyYhms/():[ ]||d;

		if ($variable_data_validated eq ""){

			# The date and time format is valid. So
			# skip this bit.

		} else {

			# The validated data variable is not blank, meaning 
			# that it contains something else, so return an error
			# (or a value).

			if ($variable_noerror eq 1){

				# The no error value is set to 1 so return
				# an value of 2. (meaning that the date and
				# time format was invalid).

				return 2;

			} elsif ($variable_noerror eq 0){

				# The no error value is set to 0 so return
				# an error.

				kiriwrite_error("dateformatinvalid");

			} else {

				# The no error value is something else other
				# than 0 or 1 so return an error.

				kiriwrite_error("invalidvariable");

			}

		}

		return 0;

	} elsif ($variable_type eq "directory"){
		# Check if the directory only contains letters and numbers and
		# return an error if anything else appears.

		my $variable_data_validated = $variable_data;
		$variable_data_validated =~ tr/a-zA-Z0-9//d;

		if ($variable_data eq ""){

			if ($variable_noerror eq 1){

				# The no error value is set to 1 so return
				# a value of 1 (meaning that the directory
				# name was blank).

				return 1;

			} elsif ($variable_noerror eq 0){

				# The no error value is set to 1 so return
				# an error.

				kiriwrite_error("blankdirectory");

			} else {

				# The no error value is something else other
				# than 0 or 1, so return an error.

				kiriwrite_error("invalidvariable");

			}

		}

		if ($variable_data_validated eq ""){

			# The validated data variable is blank, meaning that
			# it only contains letters and numbers.

		} else {

			# The validated data variable is not blank, meaning 
			# that it contains something else, so return an error
			# (or a value).

			if ($variable_noerror eq 1){

				# The no error value is set to 1 so return
				# an value of 2. (meaning that the directory
				# name is invalid).

				return 2;

			} elsif ($variable_noerror eq 0){

				# The no error value is set to 0 so return
				# an error.

				kiriwrite_error("invaliddirectory");

			} else {

				# The no error value is something else other
				# than 0 or 1 so return an error.

				kiriwrite_error("invalidvariable");

			}

		}

		return 0;

	} elsif ($variable_type eq "language_filename"){

		# The variable type is a language filename type.
		# Check if the language file name is blank and 
		# if it is then return an error (or value).

		if ($variable_data eq ""){

			# The language filename is blank so check the
			# no error value and return an error (or value).

			if ($variable_noerror eq 1){

				# Language filename is blank and the no error value
				# is set as 1, so return a value of 1 (saying that
				# the language filename is blank).

				return 1;

			} elsif ($variable_noerror eq 0) {

				# Language filename is blank and the no error value
				# is not set as 1, so return an error.

				kiriwrite_error("languagefilenameblank");

			} else {

				# The noerror value is something else other
				# than 0 or 1 so return an error.

				kiriwrite_error("invalidvariable");

			}

		}

		# Set the following variables for later on.

		my $variable_data_length = 0;
		my $variable_data_char = "";
		my $variable_data_seek = 0;

		# Get the length of the language file name.

		$variable_data_length = length($variable_data);

		do {

			# Get a character from the language filename passed to this 
			# subroutine and the character the seek counter value is set
			# to.

			$variable_data_char = substr($variable_data, $variable_data_seek, 1);

			# Check if the language filename contains a forward slash or a dot, 
			# if the selected character is a forward slash then return an error
			# (or value).

			if ($variable_data_char eq "/" || $variable_data_char eq "."){

				# The language filename contains a forward slash or
				# a dot so depending on the no error value, return
				# an error or a value.

				if ($variable_noerror eq 1){

					# Language filename contains a forward slash or a dot
					# and the no error value has been set to 1, so return 
					# an value of 2 (saying that the language file name is 
					# invalid).

					return 2;

				} elsif ($variable_noerror eq 0) {

					# Language filename contains a forward slash and the no
					# error value has not been set to 1, so return an error.

					kiriwrite_error("languagefilenameinvalid");

				} else {

					# The noerror value is something else other than
					# 1 or 0 so return an error.

					kiriwrite_error("invalidvariable");

				}

			}

			# Increment the seek counter.

			$variable_data_seek++;

		} until ($variable_data_seek eq $variable_data_length);

		return 0;

	} elsif ($variable_type eq "module"){

		# The variable type is a presentation module filename.

		# Check if the variable_data is blank and if it is
		# return an error.

		if ($variable_data eq ""){

			# The presentation module is blank so check if an error
			# value should be returned or a number should be
			# returned.

			if ($variable_noerror eq 1){

				# Module name is blank and the no error value 
				# is set to 1 so return a value of 2 (meaning 
				# that the page filename is blank).

				return 1;

			} elsif ($variable_noerror eq 0) {

				# Module name contains is blank and the no error 
				# value is set to 0 so return an error.

				kiriwrite_critical("moduleblank");

			} else {

				# The no error value is something else other
				# than 0 or 1 so return an error.

				kiriwrite_critical("invalidvalue");

			}

		} else {

		}

		my $variable_data_validated = $variable_data;
		$variable_data_validated =~ tr/a-zA-Z0-9//d;

		if ($variable_data_validated eq ""){

		} else {

			if ($variable_noerror eq 1){

				# Module name contains invalid characters and
				# the no error value is set to 1 so return a 
				# value of 2 (meaning that the page filename
				# is invalid).

				return 2;

			} elsif ($variable_noerror eq 0) {

				# Module name contains invalid characters and
				# the no error value is set to 0 so return an
				# error.

				kiriwrite_critical("moduleinvalid");

			} else {

				# The no error value is something else other
				# than 0 or 1 so return an error.

				kiriwrite_error("invalidvalue");

			}

		}

		return 0;

	} elsif ($variable_type eq "serverprotocol"){

		# Check if the server protocol is TCP or UDP and return
		# an error if it isn't.

		if ($variable_data ne "tcp" && $variable_data ne "udp"){

			# The protocol given is not valid, check if the no
			# error value is set to 1 and return an error if it isn't.

			if ($variable_noerror eq 1){

				# The no error value has been set to 1, so return a
				# value of 1 (meaning that the server protocol is
				# invalid).

				return 1;

			} elsif ($variable_noerror eq 0){

				# The no error value has been set to 0, so return
				# an error.

				kiriwrite_error("serverprotocolinvalid");

			} else {

				# The no error value is something else other than 0
				# or 1, so return an error.

				kiriwrite_error("invalidoption");

			}

		}

		return 0;

	} elsif ($variable_type eq "port"){

		# Check if the port number given is less than 0 or more than 65535
		# and return an error if it is.

		if ($variable_data < 0 || $variable_data > 65535){

			# The port number is less than 0 and more than 65535 so
			# check if the no error value is set to 1 and return an
			# error if it isn't.

			if ($variable_noerror eq 1){

				# The no error value has been set to 1, so return a
				# value of 1 (meaning that the port number is invalid).

				return 1;

			} elsif ($variable_noerror eq 0){

				# The no error value has been set to 0, so return
				# an error.

				kiriwrite_error("serverportnumberinvalid");

			} else {

				# The no error value is something else other than 0
				# or 1, so return an error.

				kiriwrite_error("invalidoption");

			}

		}

		return 0;

	}

	# Another type than the valid ones above has been specified so return an error specifying an invalid option.
	kiriwrite_error("invalidoption");

}

sub kiriwrite_error{
#################################################################################
# kiriwrite_error: Subroutine for processing error messages.			#
#										#
# Usage:									#
#										#
# kiriwrite_error(errortype);							#
#										#
# errortype	Specifies the error type to use.				#
#################################################################################

	my $error_type = shift;

	# Load the list of error messages.

	my (%kiriwrite_error, $kiriwrite_error);

	%kiriwrite_error = (

		# Generic Error Messages

		"generic"			=> $kiriwrite_lang{$language_selected}{generic},

		"invalidvariable"		=> $kiriwrite_lang{$language_selected}{invalidvariable},
		"invalidvalue"			=> $kiriwrite_lang{$language_selected}{invalidvalue},
		"invalidoption"			=> $kiriwrite_lang{$language_selected}{invalidoption},
		"variabletoolong"		=> $kiriwrite_lang{$language_selected}{variabletoolong},
		"blankdirectory"		=> $kiriwrite_lang{$language_selected}{blankdirectory},
		"invaliddirectory"		=> $kiriwrite_lang{$language_selected}{invaliddirectory},
		"moduleblank"			=> $kiriwrite_lang{$language_selected}{moduleblank},
		"moduleinvalid"			=> $kiriwrite_lang{$language_selected}{moduleinvalid},

		# Specific Error Messages

		"dbdirectorytoolong" 		=> $kiriwrite_lang{$language_selected}{dbdirectorytoolong},
		"outputdirectorytoolong"	=> $kiriwrite_lang{$language_selected}{outputdirectorytoolong},
		"imagesuripathtoolong"		=> $kiriwrite_lang{$language_selected}{imagesuripathtoolong},
		"dateformattoolong"		=> $kiriwrite_lang{$language_selected}{dateformattoolong},
		"customdateformattoolong"	=> $kiriwrite_lang{$language_selected}{customdateformattoolong},
		"languagefilenametoolong"	=> $kiriwrite_lang{$language_selected}{languagefilenametoolong},
		
		"dateformatblank"		=> $kiriwrite_lang{$language_selected}{dateformatblank},
		"dateformatinvalid"		=> $kiriwrite_lang{$language_selected}{dateformatinvalid},
		"languagefilenameinvalid"	=> $kiriwrite_lang{$language_selected}{languagefilenameinvalid},
		
		"dbdirectoryblank"		=> $kiriwrite_lang{$language_selected}{dbdirectoryblank},
		"dbdirectoryinvalid"		=> $kiriwrite_lang{$language_selected}{dbdirectoryinvalid},

		"textarearowblank"		=> $kiriwrite_lang{$language_selected}{textarearowblank},
		"textarearowtoolong"		=> $kiriwrite_lang{$language_selected}{textarearowtoolong},
		"textarearowinvalid"		=> $kiriwrite_lang{$language_selected}{textarearowinvalid},

		"textareacolsblank"		=> $kiriwrite_lang{$language_selected}{textareacolsblank},
		"textareacolstoolong"		=> $kiriwrite_lang{$language_selected}{textareacolstoolong},
		"textareacolsinvalid"		=> $kiriwrite_lang{$language_selected}{textareacolsinvalid},

		"outputdirectoryblank"		=> $kiriwrite_lang{$language_selected}{outputdirectoryblank},
		"outputdirectoryinvalid"	=> $kiriwrite_lang{$language_selected}{outputdirectoryinvalid},

		"presmoduleblank"		=> $kiriwrite_lang{$language_selected}{presmoduleblank},
		"presmoduleinvalid"		=> $kiriwrite_lang{$language_selected}{presmoduleinvalid},

		"dbmoduleblank"			=> $kiriwrite_lang{$language_selected}{dbmoduleblank},
		"dbmoduleinvalid"		=> $kiriwrite_lang{$language_selected}{dbmoduleinvalid},

		"presmodulemissing"		=> $kiriwrite_lang{$language_selected}{presmodulemissing},
		"dbmodulemissing"		=> $kiriwrite_lang{$language_selected}{dbmodulemissing},
		"languagefilenamemissing"	=> $kiriwrite_lang{$language_selected}{languagefilenamemissing},

		"servernametoolong"		=> $kiriwrite_lang{$language_selected}{servernametoolong},
		"servernameinvalid"		=> $kiriwrite_lang{$language_selected}{servernameinvalid},
		"serverportnumbertoolong"	=> $kiriwrite_lang{$language_selected}{serverportnumbertoolong},
		"serverportnumberinvalidcharacters"	=> $kiriwrite_lang{$language_selected}{serverportnumberinvalidcharacters},
		"serverportnumberinvalid"	=> $kiriwrite_lang{$language_selected}{serverportnumberinvalid},
		"serverprotocolnametoolong"	=> $kiriwrite_lang{$language_selected}{serverprotocolnametoolong},
		"serverprotocolinvalid"		=> $kiriwrite_lang{$language_selected}{serverprotocolinvalid},
		"serverdatabasenametoolong"	=> $kiriwrite_lang{$language_selected}{serverdatabasenametoolong},
		"serverdatabasenameinvalid"	=> $kiriwrite_lang{$language_selected}{serverdatabasenameinvalid},
		"serverdatabaseusernametoolong"	=> $kiriwrite_lang{$language_selected}{serverdatabaseusernametoolong},
		"serverdatabaseusernameinvalid"	=> $kiriwrite_lang{$language_selected}{serverdatabaseusernameinvalid},
		"serverdatabasepasswordtoolong"	=> $kiriwrite_lang{$language_selected}{serverdatabasepasswordtoolong},
		"serverdatabasetableprefixtoolong"	=> $kiriwrite_lang{$language_selected}{serverdatabasetableprefixtoolong},
		"serverdatabasetableprefixinvalid"	=> $kiriwrite_lang{$language_selected}{serverdatabasetableprefixinvalid},

		"removeinstallscripttoolong"	=> $kiriwrite_lang{$language_selected}{removeinstallscripttoolong},
		"cannotwriteconfigurationindirectory"	=> $kiriwrite_lang{$language_selected}{cannotwriteconfigurationindirectory},
		"configurationfilereadpermissionsinvalid"	=> $kiriwrite_lang{$language_selected}{configurationfilereadpermissionsinvalid},
		"configurationfilewritepermissionsinvalid"	=> $kiriwrite_lang{$language_selected}{configurationfilewritepermissionsinvalid},

	);

	# Check if the specified error is blank and if it is
	# use the generic error messsage.

	if (!$kiriwrite_error{$error_type}){
		$error_type = "generic";
	}

	print header();

	print start_html({ -title => $kiriwrite_lang{$language_selected}{error}, -style => { -code => $cssstyle }});

	print h2($kiriwrite_lang{$language_selected}{error});

	print $kiriwrite_error{$error_type};
	print br();
	print $kiriwrite_lang{$language_selected}{errormessagetext};

	print end_html();

	exit;

}

sub kiriwrite_writeconfig{
#################################################################################
# kiriwrite_writeconfig: Writes a configuration file.				#
#										#
# Usage:									#
#										#
# kiriwrite_writeconfig();							#
#################################################################################

	my ($passedsettings) = @_;

	# Open the configuration file for writing.

	open (my $configfile, "> " . "kiriwrite.cfg");

	print $configfile "[config]
		directory_data_db = $passedsettings->{DatabaseDirectory}
		directory_data_output = $passedsettings->{OutputDirectory}
		directory_noncgi_images = $passedsettings->{ImagesURIPath}
		
		system_language = $passedsettings->{Language}
		system_presmodule = $passedsettings->{PresentationModule}
		system_dbmodule = $passedsettings->{DatabaseModule}
		system_datetime = $passedsettings->{DateFormat}
		
		display_textareacols = $passedsettings->{TextAreaCols}
		display_textarearows = $passedsettings->{TextAreaRows}
		
		database_server = $passedsettings->{DatabaseServer}
		database_port = $passedsettings->{DatabasePort}
		database_protocol = $passedsettings->{DatabaseProtocol}
		database_sqldatabase = $passedsettings->{DatabaseName}
		database_username = $passedsettings->{DatabaseUsername}
		database_password = $passedsettings->{DatabasePassword}
		database_tableprefix = $passedsettings->{DatabaseTablePrefix}
	";

	close ($configfile);

}

#################################################################################
# End list of subroutines.							#
#################################################################################

if (!$http_query_confirm){

	$http_query_confirm = 0;

}

if ($http_query_confirm eq 1){

	# The confirm value has been given so get the data from the query.

	my $http_query_dbdirectory		= $query->param('dbdirectory');
	my $http_query_outputdirectory		= $query->param('outputdirectory');
	my $http_query_imagesuripath		= $query->param('imagesuripath');

	my $http_query_textarearows		= $query->param('textarearows');
	my $http_query_textareacols		= $query->param('textareacols');

	my $http_query_dateformat		= $query->param('dateformat');
	my $http_query_customdateformat		= $query->param('customdateformat');

	my $http_query_language			= $query->param('language');

	my $http_query_presmodule		= $query->param('presmodule');
	my $http_query_dbmodule			= $query->param('dbmodule');

	my $http_query_databaseserver		= $query->param('databaseserver');
	my $http_query_databaseport		= $query->param('databaseport');
	my $http_query_databaseprotocol		= $query->param('databaseprotocol');
 	my $http_query_databasename		= $query->param('databasename');
 	my $http_query_databaseusername		= $query->param('databaseusername');
 	my $http_query_databasepassword		= $query->param('databasepassword');
 	my $http_query_databasetableprefix	= $query->param('databasetableprefix');
 	my $http_query_removeinstallscript	= $query->param('removeinstallscript');

	# Check if the text area rows and column values are blank.

	if (!$http_query_textarearows){

		# The text area rows value is blank so return
		# an error.

		kiriwrite_error("textarearowblank");

	}

	if (!$http_query_textareacols){

		# The text area columns value is blank so
		# return an error.

		kiriwrite_error("textareacolsblank");

	}

	# Check the length of the variables.

	my $kiriwrite_dbdirectory_length_check 		= kiriwrite_variablecheck($http_query_dbdirectory, "maxlength", 64, 1);
	my $kiriwrite_outputdirectory_length_check	= kiriwrite_variablecheck($http_query_outputdirectory, "maxlength", 64, 1);
	my $kiriwrite_imagesuripath_length_check 	= kiriwrite_variablecheck($http_query_imagesuripath, "maxlength", 512, 1);
	my $kiriwrite_textarearow_length_check		= kiriwrite_variablecheck($http_query_textarearows, "maxlength", 3, 1);
	my $kiriwrite_textareacols_length_check		= kiriwrite_variablecheck($http_query_textareacols, "maxlength", 3, 1);
	my $kiriwrite_dateformat_length_check 		= kiriwrite_variablecheck($http_query_dateformat, "maxlength", 32, 1);
	my $kiriwrite_customdateformat_length_check	= kiriwrite_variablecheck($http_query_customdateformat, "maxlength", 32, 1);
	my $kiriwrite_language_length_check		= kiriwrite_variablecheck($http_query_language, "maxlength", 16, 1);

	# Check if any errors occured while checking the
	# length of the variables.

	if ($kiriwrite_dbdirectory_length_check eq 1){

		# The database directory given is too long
		# so return an error.

		kiriwrite_error("dbdirectorytoolong");

	}

	if ($kiriwrite_outputdirectory_length_check eq 1){

		# The output directory given is too long
		# so return an error.

		kiriwrite_error("outputdirectorytoolong");

	}

	if ($kiriwrite_imagesuripath_length_check eq 1){

		# The images URI path given is too long
		# so return an error.

		kiriwrite_error("imagesuripathtoolong");

	}

	if ($kiriwrite_dateformat_length_check eq 1){

		# The date format given is too long
		# so return an error.

		kiriwrite_error("dateformattoolong");

	}

	if ($kiriwrite_customdateformat_length_check eq 1){

		# The date format given is too long
		# so return an error.

		kiriwrite_error("customdateformattoolong");

	}

	if ($kiriwrite_language_length_check eq 1){

		# The language filename given is too long
		# so return an error.

		kiriwrite_error("languagefilenametoolong");

	}

	if ($kiriwrite_textarearow_length_check eq 1){

		# The text area rows length is too long
		# so return an error.

		kiriwrite_error("textarearowtoolong");

	}

	if ($kiriwrite_textareacols_length_check eq 1){

		# The text area columns length is too long
		# so return an error.

		kiriwrite_error("textareacolstoolong");

	}

	# Check if the custom date and time setting has anything
	# set and if it doesn't then use the predefined one set.

	my $finaldateformat = "";

	if ($http_query_customdateformat ne ""){

		$finaldateformat = $http_query_customdateformat;

	} else {

		$finaldateformat = $http_query_dateformat;

	}

	my $kiriwrite_datetime_check		= kiriwrite_variablecheck($finaldateformat, "datetime", 0, 1);

	if ($kiriwrite_datetime_check eq 1){

		# The date and time format is blank so return
		# an error.

		kiriwrite_error("dateformatblank");

	} elsif ($kiriwrite_datetime_check eq 2){

		# The date and time format is invalid so
		# return an error.

		kiriwrite_error("dateformatinvalid");

	}

	# Check if the language filename given is valid.

	my $kiriwrite_language_languagefilename_check = kiriwrite_variablecheck($http_query_language, "language_filename", "", 1);

	if ($kiriwrite_language_languagefilename_check eq 1) {

		# The language filename given is blank so
		# return an error.

		kiriwrite_error("languagefilenameblank");

	} elsif ($kiriwrite_language_languagefilename_check eq 2){

		# The language filename given is invalid so
		# return an error.

		kiriwrite_error("languagefilenameinvalid");

	}

	# Check if the directory names only contain letters and numbers and
	# return a specific error if they don't.

	my $kiriwrite_dbdirectory_check 	= kiriwrite_variablecheck($http_query_dbdirectory, "directory", 0, 1);
	my $kiriwrite_outputdirectory_check 	= kiriwrite_variablecheck($http_query_outputdirectory, "directory", 0, 1);

	if ($kiriwrite_dbdirectory_check eq 1){

		# The database directory name is blank, so return
		# an error.

		kiriwrite_error("dbdirectoryblank");

	} elsif ($kiriwrite_dbdirectory_check eq 2){

		# The database directory name is invalid, so return
		# an error.

		kiriwrite_error("dbdirectoryinvalid");

	}

	if ($kiriwrite_outputdirectory_check eq 1){

		# The output directory name is blank, so return
		# an error.

		kiriwrite_error("outputdirectoryblank");

	} elsif ($kiriwrite_outputdirectory_check eq 2){

		# The output directory name is invalid, so return
		# an error.

		kiriwrite_error("outputdirectoryinvalid");

	}

	if ($kiriwrite_dbdirectory_check eq 1){

		# The database directory name is blank, so return
		# an error.

		kiriwrite_error("dbdirectoryblank");

	} elsif ($kiriwrite_dbdirectory_check eq 2){

		# The database directory name is invalid, so return
		# an error.

		kiriwrite_error("dbdirectoryinvalid");

	}

	if ($kiriwrite_outputdirectory_check eq 1){

		# The output directory name is blank, so return
		# an error.

		kiriwrite_error("outputdirectoryblank");

	} elsif ($kiriwrite_outputdirectory_check eq 2){

		# The output directory name is invalid, so return
		# an error.

		kiriwrite_error("outputdirectoryinvalid");

	}

	# Check to see if the text area rows and column values
	# are valid.

	my $kiriwrite_textarearow_number_check		= kiriwrite_variablecheck($http_query_textarearows, "numbers", 0, 1);
	my $kiriwrite_textareacols_number_check		= kiriwrite_variablecheck($http_query_textareacols, "numbers", 0, 1);

	if ($kiriwrite_textarearow_number_check eq 1){

		# The text area row value is invalid so return
		# an error.

		kiriwrite_error("textarearowinvalid");

	}

	if ($kiriwrite_textareacols_number_check eq 1){

		# The text area columns value is invalid so return
		# an error.

		kiriwrite_error("textareacolsinvalid");

	}

	# Check the module names to see if they're valid.

	my $kiriwrite_presmodule_modulename_check 	= kiriwrite_variablecheck($http_query_presmodule, "module", 0, 1);
	my $kiriwrite_dbmodule_modulename_check		= kiriwrite_variablecheck($http_query_dbmodule, "module", 0, 1);

	if ($kiriwrite_presmodule_modulename_check eq 1){

		# The presentation module name is blank, so return
		# an error.

		kiriwrite_error("presmoduleblank");

	}

	if ($kiriwrite_presmodule_modulename_check eq 2){

		# The presentation module name is invalid, so return
		# an error.

		kiriwrite_error("presmoduleinvalid");

	}

	if ($kiriwrite_dbmodule_modulename_check eq 1){

		# The database module name is blank, so return
		# an error.

		kiriwrite_error("dbmoduleblank");

	}

	if ($kiriwrite_dbmodule_modulename_check eq 2){

		# The database module name is invalid, so return
		# an error.

		kiriwrite_error("dbmoduleinvalid");

	}

	# Check if the database module, presentation module and
	# language file exists.

	if (!-e "Modules/Presentation/" . $http_query_presmodule . ".pm"){

		# The presentation module is missing so return an
		# error.

		kiriwrite_error("presmodulemissing");

	}

	if (!-e "Modules/Database/" . $http_query_dbmodule . ".pm"){

		# The database module is missing so return an
		# error.

		kiriwrite_error("dbmodulemissing");

	}

	if (!-e "lang/" . $http_query_language . ".lang"){

		# The language file is missing so return an
		# error.

		kiriwrite_error("languagefilenamemissing");

	}

	# Check the database server settings.

	my $kiriwrite_databaseserver_length_check		= kiriwrite_variablecheck($http_query_databaseserver, "maxlength", 128, 1);
	my $kiriwrite_databaseserver_lettersnumbers_check	= kiriwrite_variablecheck($http_query_databaseserver, "lettersnumbers", 0, 1);
	my $kiriwrite_databaseport_length_check			= kiriwrite_variablecheck($http_query_databaseport, "maxlength", 5, 1);
	my $kiriwrite_databaseport_numbers_check		= kiriwrite_variablecheck($http_query_databaseport, "numbers", 0, 1);
	my $kiriwrite_databaseport_port_check			= kiriwrite_variablecheck($http_query_databaseport, "port", 0, 1);
	my $kiriwrite_databaseprotocol_length_check		= kiriwrite_variablecheck($http_query_databaseprotocol, "maxlength", 5, 1);
	my $kiriwrite_databaseprotocol_protocol_check		= kiriwrite_variablecheck($http_query_databaseprotocol, "serverprotocol", 0, 1);
	my $kiriwrite_databasename_length_check			= kiriwrite_variablecheck($http_query_databasename, "maxlength", 32, 1);
	my $kiriwrite_databasename_lettersnumbers_check		= kiriwrite_variablecheck($http_query_databasename, "lettersnumbers", 0, 1);
	my $kiriwrite_databaseusername_length_check		= kiriwrite_variablecheck($http_query_databaseusername, "maxlength", 16, 1);
	my $kiriwrite_databaseusername_lettersnumbers_check	= kiriwrite_variablecheck($http_query_databaseusername, "lettersnumbers", 0, 1);
	my $kiriwrite_databasepassword_length_check		= kiriwrite_variablecheck($http_query_databasepassword, "maxlength", 64, 1);
	my $kiriwrite_databasetableprefix_length_check		= kiriwrite_variablecheck($http_query_databasetableprefix, "maxlength", 16, 1);
	my $kiriwrite_databasetableprefix_lettersnumbers_check	= kiriwrite_variablecheck($http_query_databasetableprefix, "lettersnumbers", 0, 1);

	if ($kiriwrite_databaseserver_length_check eq 1){

		# The length of the database server name is too long so
		# return an error.

		kiriwrite_error("servernametoolong");

	}

	if ($kiriwrite_databaseserver_lettersnumbers_check eq 1){

		# The database server name contains characters other
		# than letters and numbers, so return an error.

		kiriwrite_error("servernameinvalid");

	}

	if ($kiriwrite_databaseport_length_check eq 1){

		# The database port number length is too long so return
		# an error.

		kiriwrite_error("serverportnumbertoolong");

	}

	if ($kiriwrite_databaseport_numbers_check eq 1){

		# The database port number contains characters other
		# than numbers so return an error.

		kiriwrite_error("serverportnumberinvalidcharacters");

	}

	if ($kiriwrite_databaseport_port_check eq 1){

		# The database port number given is invalid so return
		# an error.

		kiriwrite_error("serverportnumberinvalid");

	}

	if ($kiriwrite_databaseprotocol_length_check eq 1){

		# The database protocol name given is too long so
		# return an error.

		kiriwrite_error("serverprotocolnametoolong");

	}

	if ($kiriwrite_databaseprotocol_protocol_check eq 1){

		# The server protcol given is invalid so return
		# an error.

		kiriwrite_error("serverprotocolinvalid");

	}

	if ($kiriwrite_databasename_length_check eq 1){

		# The SQL database name is too long so return
		# an error.

		kiriwrite_error("serverdatabasenametoolong");

	}

	if ($kiriwrite_databasename_lettersnumbers_check eq 1){

		# The database name contains invalid characters
		# so return an error.

		kiriwrite_error("serverdatabasenameinvalid");

	}

	if ($kiriwrite_databaseusername_length_check eq 1){

		# The database username given is too long so
		# return an error.

		kiriwrite_error("serverdatabaseusernametoolong");

	}

	if ($kiriwrite_databaseusername_lettersnumbers_check eq 1){

		# The database username contains invalid characters
		# so return an error.

		kiriwrite_error("serverdatabaseusernameinvalid");

	}

	if ($kiriwrite_databasepassword_length_check eq 1){

		# The database password given is too long so return
		# an error.

		kiriwrite_error("serverdatabasepasswordtoolong");

	}

	if ($kiriwrite_databasetableprefix_length_check eq 1){

		# The database table prefix given is too long so
		# return an error.

		kiriwrite_error("serverdatabasetableprefixtoolong");

	}

	if ($kiriwrite_databasetableprefix_lettersnumbers_check eq 1){

		# The database table prefix given contains invalid
		# characters so return an error.

		kiriwrite_error("serverdatabasetableprefixinvalid");

	}

	# Check the length of value of the checkboxes.

	my $kiriwrite_removeinstallscript_length_check	= kiriwrite_variablecheck($http_query_removeinstallscript, "maxlength", 2, 1);

	if ($kiriwrite_removeinstallscript_length_check eq 1){

		# The remove install script value is too long
		# so return an error.

		kiriwrite_error("removeinstallscripttoolong");

	}

	# Check if there is write permissions for the directory.

	if (!-w '.'){

		# No write permissions for the directory the
		# script is running from so return an error.

		kiriwrite_error("cannotwriteconfigurationindirectory");

	}

	# Check if the configuration file already exists.

	if (-e 'kiriwrite.cfg'){

		# Check if the configuration file has read permissions.

		if (!-r 'kiriwrite.cfg'){

			# The configuration file has invalid read permissions
			# set so return an error.

			kiriwrite("configurationfilereadpermissionsinvalid");

		}

		# Check if the configuration file has write permissions.

		if (!-w 'kiriwrite.cfg'){

			# The configuration file has invalid write permissions
			# set so return an error.

			kiriwrite("configurationfilewritepermissionsinvalid");

		}

	}

	# Write the new configuration file.

	kiriwrite_writeconfig({ DatabaseDirectory => $http_query_dbdirectory, OutputDirectory => $http_query_outputdirectory, ImagesURIPath => $http_query_imagesuripath, TextAreaCols => $http_query_textareacols, TextAreaRows => $http_query_textarearows, DateFormat => $finaldateformat, Language => $http_query_language, PresentationModule => $http_query_presmodule, DatabaseModule => $http_query_dbmodule, DatabaseServer => $http_query_databaseserver, DatabasePort => $http_query_databaseport, DatabaseProtocol => $http_query_databaseprotocol, DatabaseName => $http_query_databasename, DatabaseUsername => $http_query_databaseusername, DatabasePassword => $http_query_databasepassword, DatabaseTablePrefix => $http_query_databasetableprefix });

	my $installscriptmessage	= "";

	# Check if the installation script should be deleted.

	if (!$http_query_removeinstallscript){

		$http_query_removeinstallscript = "off";

	}

	if ($http_query_removeinstallscript eq "on"){

		if (unlink("install.cgi")){

			$installscriptmessage = $kiriwrite_lang{$language_selected}{installscriptremoved};

		} else {

			$installscriptmessage = $kiriwrite_lang{$language_selected}{cannotremovescript};
			$installscriptmessage =~ s/%s/$!/g;

		}

	}

	print header();

	print start_html({ -title => $kiriwrite_lang{$language_selected}{installertitle}, -style => { -code => $cssstyle }});
	print h2($kiriwrite_lang{$language_selected}{installertitle});
	print $kiriwrite_lang{$language_selected}{installedmessage};

	if ($installscriptmessage){

		print br();
		print br();
		print $installscriptmessage;

	}

	print br();
	print br();
	print $kiriwrite_lang{$language_selected}{usekiriwritetext};
	print br();
	print br();
	print a({-href=>'kiriwrite.cgi'}, $kiriwrite_lang{$language_selected}{usekiriwritelink});

	exit;

}

# Create a list of common date and time formats.

my @datetime_formats = [ 
	'DD/MM/YY (hh:mm:ss)', 'DD/MM/YY hh:mm:ss', 'D/M/Y (hh:mm:ss)',
	'D/M/Y hh:mm:ss', 'D/M/YY (hh:mm:ss)', 'D/M/YY hh:mm:ss',
	'DD/MM (hh:mm:ss)', 'D/M (hh:mm:ss)', 'DD/MM hh:mm:ss', 
	'D/M hh:mm:ss', 'DD/MM hh:mm', 'D/M hh:mm',
	'DD/MM/YY', 'D/M/Y', 'DD/MM',

	'YY-MM-DD (hh:mm:ss)', 'YY-MM-DD hh:mm:ss', 'Y-M-D (hh:mm:ss)',
	'Y-M-D hh:mm:ss', 'M-D (hh:mm:ss)', 'M-D hh:mm:ss',
	'YY-MM-DD', 'MM-DD' 
];

# Create the list of tests to do.

my ($test_list, %test_list);
my %dependency_results;
my %database_results;
my %file_results;
my $test;
my $date;

my $dependency_error = 0;
my $database_onemodule = 0;
my $database_error = 0;
my $file_error = 0;

my $language_name;
my $language_xml_data;
my $language_file_friendly;

my $presentation_file_friendly;

# Check to see if the needed Perl modules are installed.

$test_list{CheckConfigAuto}{Name}	= "Config::Auto";
$test_list{CheckConfigAuto}{Type}	= "dependency";
$test_list{CheckConfigAuto}{Code}	= "Config::Auto";

$test_list{CheckDBI}{Name} 		= "DBI";
$test_list{CheckDBI}{Type} 		= "dependency";
$test_list{CheckDBI}{Code} 		= "DBI";

$test_list{CheckTieHash}{Name}		= "Tie::IxHash";
$test_list{CheckTieHash}{Type} 		= "dependency";
$test_list{CheckTieHash}{Code} 		= "Tie::IxHash";

$test_list{CheckCGILite}{Name}		= "CGI::Lite";
$test_list{CheckCGILite}{Type}		= "dependency";
$test_list{CheckCGILite}{Code}		= "CGI::Lite";

$test_list{Encode}{Name}		= "Encode";
$test_list{Encode}{Type}		= "dependency";
$test_list{Encode}{Code}		= "Encode";

$test_list{DBDmysql}{Name}		= "DBD::mysql";
$test_list{DBDmysql}{Type}		= "database";
$test_list{DBDmysql}{Code}		= "DBD::mysql";

$test_list{DBDSQLite}{Name}		= "DBD::SQLite";
$test_list{DBDSQLite}{Type}		= "database";
$test_list{DBDSQLite}{Code}		= "DBD::SQLite";

# Check the file and directory permissions to see if they are correct.

$test_list{MainDirectory}{Name}		= "Kiriwrite Directory (.)";
$test_list{MainDirectory}{Type}		= "file";
$test_list{MainDirectory}{Code}		= ".";
$test_list{MainDirectory}{Writeable}	= "1";

$test_list{LanguageDirectory}{Name}		= "Language Directory (lang)";
$test_list{LanguageDirectory}{Type}		= "file";
$test_list{LanguageDirectory}{Code}		= "lang";
$test_list{LanguageDirectory}{Writeable}	= "0";

$test_list{LibraryDirectory}{Name}		= "Library Directory (lib)";
$test_list{LibraryDirectory}{Type}		= "file";
$test_list{LibraryDirectory}{Code}		= "lib";
$test_list{LibraryDirectory}{Writeable}		= "0";

$test_list{ModulesDirectory}{Name}		= "Modules Directory (Modules)";
$test_list{ModulesDirectory}{Type}		= "file";
$test_list{ModulesDirectory}{Code}		= "Modules";
$test_list{ModulesDirectory}{Writeable}		= "0";

$test_list{DBModulesDirectory}{Name}		= "Database Modules Directory (Modules/Database)";
$test_list{DBModulesDirectory}{Type}		= "file";
$test_list{DBModulesDirectory}{Code}		= "Modules/Database";
$test_list{DBModulesDirectory}{Writeable}	= "0";

$test_list{PresModulesDirectory}{Name}		= "Presentation Modules Directory (Modules/Presentation)";
$test_list{PresModulesDirectory}{Type}		= "file";
$test_list{PresModulesDirectory}{Code}		= "Modules/Presentation";
$test_list{PresModulesDirectory}{Writeable}	= "0";

# Preform those tests.

foreach $test (keys %test_list){

	# Check the type of test.

	if ($test_list{$test}{Type} eq "dependency"){

		if (eval "require " . $test_list{$test}{Code}){

			# The module exists and is working correctly.

			$dependency_results{$test_list{$test}{Name}}{result} 	= $kiriwrite_lang{$language_selected}{testpass};

		} else {

			# The module does not exist or has an error.

			$dependency_error = 1;
			$dependency_results{$test_list{$test}{Name}}{result} 	= $kiriwrite_lang{$language_selected}{testfail};

		}

	} elsif ($test_list{$test}{Type} eq "database"){

		if (eval "require " . $test_list{$test}{Code}){

			# The module exists and it is working correctly.

			$database_results{$test_list{$test}{Name}}{result} 	= $kiriwrite_lang{$language_selected}{testpass};
			$database_onemodule = 1;

		} else {

			# The module does not exist or has an error.

			$database_error = 1;
			$database_results{$test_list{$test}{Name}}{result} 	= $kiriwrite_lang{$language_selected}{testfail};

		}

	} elsif ($test_list{$test}{Type} eq "file"){

		if (-e $test_list{$test}{Code}){

			# The filename given does exist.

		} else {

			# the filename given does not exist.

			$file_error = 1;
			$file_results{$test_list{$test}{Name}}{result} 	= $kiriwrite_lang{$language_selected}{errormessage} . $kiriwrite_lang{$language_selected}{doesnotexist};

		}	

		# Test to see if the filename given has read
		# permissions.

		if (-r $test_list{$test}{Code}){

			# The filename given has valid permissions set.

			$file_results{$test_list{$test}{Name}}{result} 	= $kiriwrite_lang{$language_selected}{testpass};

		} else {

			# The filename given has invalid permissions set.

			$file_error = 1;
			$file_results{$test_list{$test}{Name}}{result} = $kiriwrite_lang{$language_selected}{errormessage} . $kiriwrite_lang{$language_selected}{invalidpermissionsset};

		}

		if ($test_list{$test}{Writeable} eq 1){

			# Test to see if the filename given has write
			# permissions.

			if (-w $test_list{$test}{Code}){

				# The filename given has valid permissions set.

				$file_results{$test_list{$test}{Name}}{result} 	= $kiriwrite_lang{$language_selected}{testpass};

			} else {

				# The filename given has invalid permissions set.

				$file_error = 1;
				$file_results{$test_list{$test}{Name}}{result} 	= $kiriwrite_lang{$language_selected}{errormessage} . $kiriwrite_lang{$language_selected}{invalidpermissionsset};

			}

		}

	}

}

# Print the header.

print header();

# Print the page for installing Kiriwrite.

print start_html( -title=> $kiriwrite_lang{$language_selected}{installertitle}, -style => { -code => $cssstyle });

print start_table( { -width=> "100%" } );
print start_Tr();
print start_td({ -class => "languagebar" });
print $kiriwrite_lang{$language_selected}{installertitle};
print end_td();
print start_td({ -class => "languagebarselect" });
print start_form("POST", "install.cgi");

# This is a bodge for the language list.

my $language_name_short;
my $language_list_seek = 0;

print "<select name=\"installlanguage\">";

foreach $language_name_short (@language_list_short){

	print "<option value=\"" . $language_name_short . "\">" . $language_list_long[$language_list_seek] . "</option>";
	$language_list_seek++;

}

print "</select> ";
print submit($kiriwrite_lang{$language_selected}{switch});

print end_form;
print end_td();
print end_Tr();
print end_table();

print h2($kiriwrite_lang{$language_selected}{installertitle});

print $kiriwrite_lang{$language_selected}{installertext};

print h3($kiriwrite_lang{$language_selected}{dependencytitle});
print h4($kiriwrite_lang{$language_selected}{requiredmodules});
print $kiriwrite_lang{$language_selected}{perlmodules};
print br();;
print br();;

if ($dependency_error eq 1){

	print $kiriwrite_lang{$language_selected}{errormessage};
	print $kiriwrite_lang{$language_selected}{dependencyperlmodulesmissing};
	print br();
	print br();

}

print start_table();
print start_Tr();
print start_td({ -class => "tablecellheader" });
print $kiriwrite_lang{$language_selected}{module};
print end_td();
print start_td({ -class => "tablecellheader" });
print $kiriwrite_lang{$language_selected}{result};
print end_td();
print end_Tr();

foreach $test (keys %dependency_results) {

	print start_Tr();
	print start_td({ -class => "tablename" });
		print $test;
	print end_td();
	print start_td({ -class => "tabledata" });
		print $dependency_results{$test}{result};
	print end_td();
	print end_Tr();

}

print end_table();

print h4($kiriwrite_lang{$language_selected}{databasemodules});
print $kiriwrite_lang{$language_selected}{databasemodulestext};
print br();
print br();

if ($database_error eq 1){

	print $kiriwrite_lang{$language_selected}{warningmessage};
	print $kiriwrite_lang{$language_selected}{databaseperlmodulesmissing};
	print br();
	print br();

}

print start_table();
print start_Tr();
print start_td({ -class => "tablecellheader" });
print $kiriwrite_lang{$language_selected}{module};
print end_td();
print start_td({ -class => "tablecellheader" });
print $kiriwrite_lang{$language_selected}{result};
print end_td();
print end_Tr();

foreach $test (keys %database_results) {

	print start_Tr();
	print start_td({ -class => "tablename" });
		print $test;
	print end_td();
	print start_td({ -class => "tabledata" });
		print $database_results{$test}{result};
	print end_td();
	print end_Tr();

}

print end_table();

print h4($kiriwrite_lang{$language_selected}{filepermissions});

print $kiriwrite_lang{$language_selected}{filepermissionstext};
print br();
print br();

if ($file_error eq 1){

	print $kiriwrite_lang{$language_selected}{errormessage};
	print $kiriwrite_lang{$language_selected}{filepermissionsinvalid};
	print br();
	print br();

}

print start_table();
print start_Tr();
print start_td({ -class => "tablecellheader" });
print "Filename";
print end_td();
print start_td({ -class => "tablecellheader" });
print "Result";
print end_td();
print end_Tr();

foreach $test (keys %file_results) {

	print start_Tr();
	print start_td({ -class => "tablename" });
		print $test;
	print end_td();
	print start_td({ -class => "tabledata" });
		print $file_results{$test}{result};
	print end_td();
	print end_Tr();

}

print end_table();

if ($dependency_error eq 1){

	print hr();
	print h4($kiriwrite_lang{$language_selected}{criticalerror});
	print $kiriwrite_lang{$language_selected}{dependencymodulesnotinstalled};
	print end_html;
	exit;

}

if ($database_onemodule eq 0){

	print hr();
	print h4($kiriwrite_lang{$language_selected}{criticalerror});
	print $kiriwrite_lang{$language_selected}{databasemodulesnotinstalled};
	print end_html;
	exit;

}

if ($file_error eq 1){

	print hr();
	print h4($kiriwrite_lang{$language_selected}{criticalerror});
	print $kiriwrite_lang{$language_selected}{filepermissionerrors};
	print end_html;
	exit;

}

my @language_short;
my (%available_languages, $available_languages);
my @presentation_modules;
my @database_modules;

my $presentation_modules_ref = \@presentation_modules;
my $database_modules_ref = \@database_modules;

# Get the list of available languages.

tie(%available_languages, 'Tie::IxHash');

opendir(LANGUAGEDIR, "lang");
my @language_directory = grep /m*\.lang$/, readdir(LANGUAGEDIR);
closedir(LANGUAGEDIR);

my $language_data;

foreach my $language_file (@language_directory){

	# Load the language file.

	$language_data = Config::Auto::parse("lang/" . $language_file, format => "ini");

	# Load the XML data.
	#$language_xml_data = $xsl->XMLin("lang/" . $language_file);

	# Get the friendly name for the language file.

	$language_file_friendly = $language_file;
	$language_file_friendly =~ s/.lang$//g;

	$language_name = $language_data->{about}->{name};

	$available_languages{$language_file_friendly} = $language_name . " (" . $language_file_friendly . ")";

}

# Get the list of presentation modules.

opendir(OUTPUTSYSTEMDIR, "Modules/Presentation");
my @presmodule_directory = grep /m*\.pm$/, readdir(OUTPUTSYSTEMDIR);
closedir(OUTPUTSYSTEMDIR);

foreach my $presmodule_file (@presmodule_directory){

	# Get the friendly name for the database module.

	$presmodule_file =~ s/.pm$//g;

	push(@presentation_modules, $presmodule_file);

}

# Get the list of database modules.

opendir(DATABASEDIR, "Modules/Database");
my @dbmodule_directory = grep /m*\.pm$/, readdir(DATABASEDIR);
closedir(DATABASEDIR);

foreach my $dbmodule_file (@dbmodule_directory){

	# Get the friendly name for the database module.

	$dbmodule_file =~ s/.pm$//g;

	push(@database_modules, $dbmodule_file);

}

print h3($kiriwrite_lang{$language_selected}{settingstitle});

print $kiriwrite_lang{$language_selected}{settingstext};
print br();
print br();

print start_form("POST", "install.cgi");
print hidden( -name => 'confirm', -default => '1');
print hidden( -name => 'installlanguage', -default => $language_selected);

print start_table({ -width => "100%" });

print start_Tr();
print start_td({ -class => "tablecellheader" });
print $kiriwrite_lang{$language_selected}{setting};
print end_td();
print start_td({ -class => "tablecellheader" });
print $kiriwrite_lang{$language_selected}{value};
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablecellheader" });
print $kiriwrite_lang{$language_selected}{directories};
print end_td();
print start_td({ -class => "tablecellheader" });
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablename" });
print $kiriwrite_lang{$language_selected}{databasedirectory};
print end_td();
print start_td({ -class => "tabledata" });
print textfield({ -name => "dbdirectory", -size => 32, -maxlength => 64, -value => $default_dbdirectory });
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablename" });
print $kiriwrite_lang{$language_selected}{outputdirectory};
print end_td();
print start_td({ -class => "tabledata" });
print textfield({ -name => "outputdirectory", -size => 32, -maxlength => 64, -value => $default_outputdirectory });
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablename" });
print $kiriwrite_lang{$language_selected}{imagesuripath};
print end_td();
print start_td({ -class => "tabledata" });
print textfield({ -name => "imagesuripath", -size => 32, -maxlength => 64, -value => $default_imagesuri });
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablecellheader" });
print $kiriwrite_lang{$language_selected}{display};
print end_td();
print start_td({ -class => "tablecellheader" });
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablename" });
print $kiriwrite_lang{$language_selected}{textarearows};
print end_td();
print start_td({ -class => "tabledata" });
print textfield({ -name => "textarearows", -size => 3, -maxlength => 3, -value => $default_textarearows });
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablename" });
print $kiriwrite_lang{$language_selected}{textareacols};
print end_td();
print start_td({ -class => "tabledata" });
print textfield({ -name => "textareacols", -size => 3, -maxlength => 3, -value => $default_textareacols });
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablecellheader" });
print $kiriwrite_lang{$language_selected}{date};
print end_td();
print start_td({ -class => "tablecellheader" });
print "";
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablename" });
print $kiriwrite_lang{$language_selected}{dateformat};
print end_td();
print start_td({ -class => "tabledata" });

print popup_menu( -name => "dateformat", -values => @datetime_formats );
print textfield({ -name => "customdateformat", -size => 32, -maxlength => 64, });

print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablecellheader" });
print $kiriwrite_lang{$language_selected}{language};
print end_td();
print start_td({ -class => "tablecellheader" });
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablename" });
print $kiriwrite_lang{$language_selected}{systemlanguage};
print end_td();
print start_td({ -class => "tabledata" });

# Note: This the following code is bodge. If anyone can fix it so that it all works
# with popup_menu properly it will be appriciated.

print "<select name=\"language\">";

foreach my $language (keys %available_languages){

	if ($language eq $language_selected){

		print "<option value=\"" . $language . "\" selected=selected>" . $available_languages{$language} . "</option>";

	} else {

		print "<option value=\"" . $language . "\">" . $available_languages{$language} . "</option>";

	}

}

print "</select>";

print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablecellheader" });
print $kiriwrite_lang{$language_selected}{modules};
print end_td();
print start_td({ -class => "tablecellheader" });
print "";
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablename" });
print $kiriwrite_lang{$language_selected}{presentationmodule};
print end_td();
print start_td({ -class => "tabledata" });
print popup_menu({ -name => 'presmodule', -values => $presentation_modules_ref, -default => "HTML4S" });
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablename" });
print $kiriwrite_lang{$language_selected}{databasemodule};
print end_td();
print start_td({ -class => "tabledata" });
print popup_menu({ -name => 'dbmodule', -values => $database_modules_ref, -default => "SQLite" });
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablename" });
print $kiriwrite_lang{$language_selected}{databaseserver};
print end_td();
print start_td({ -class => "tabledata" });
print textfield({ -name => "databaseserver", -size => 32, -maxlength => 128, -value => $default_server });
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablename" });
print $kiriwrite_lang{$language_selected}{databaseport};
print end_td();
print start_td({ -class => "tabledata" });
print textfield({ -name => "databaseport", -maxlength => 5, -size => 5, -value => $default_port });
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablename" });
print $kiriwrite_lang{$language_selected}{databaseprotocol};
print end_td();
print start_td({ -class => "tabledata" });
print popup_menu( -name => "databaseprotocol", -values => [ 'tcp', 'udp' ], -default => $default_protocol);
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablename" });
print $kiriwrite_lang{$language_selected}{databasename};
print end_td();
print start_td({ -class => "tabledata" });
print textfield({ -name => "databasename", -size => 32, -maxlength => 32, -default => $default_name });
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablename" });
print $kiriwrite_lang{$language_selected}{databaseusername};
print end_td();
print start_td({ -class => "tabledata" });
print textfield({ -name => "databaseusername", -size => 16, -maxlength => 16, -default => $default_username });
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablename" });
print $kiriwrite_lang{$language_selected}{databasepassword};
print end_td();
print start_td({ -class => "tabledata" });
print password_field({ -name => "databasepassword", -size => 32, -maxlength => 64 });
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablename" });
print $kiriwrite_lang{$language_selected}{databasetableprefix};
print end_td();
print start_td({ -class => "tabledata" });
print textfield({ -name => "databasetableprefix", -size => 32, -maxlength => 32, -default => $default_prefix });
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablecellheader" });
print $kiriwrite_lang{$language_selected}{installationoptions};
print end_td();
print start_td({ -class => "tablecellheader" });
print "";
print end_td();
print end_Tr();

print start_Tr();
print start_td({ -class => "tablename" });
print $kiriwrite_lang{$language_selected}{installoptions};
print end_td();
print start_td({ -class => "tabledata" });
print checkbox( -name => 'removeinstallscript', -checked => 1, -label => " " . $kiriwrite_lang{$language_selected}{removeinstallscript});
print end_td();
print end_Tr();

print end_table();

print br();
print submit($kiriwrite_lang{$language_selected}{savesettingsbutton});
print " | ";
print reset($kiriwrite_lang{$language_selected}{resetsettingsbutton});

print end_form();

print end_html;
exit;

__END__