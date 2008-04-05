#!/usr/bin/perl -Tw

#################################################################################
# Kiriwrite (kiriwrite.cgi)							#
# Main program script			     					#
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
use CGI::Lite;
use Tie::IxHash;

binmode STDOUT, ':utf8';

# This is commented out because it uses a fair bit of CPU usage.

#use CGI::Carp('fatalsToBrowser'); 	# Output errors to the browser.

# Declare global variables for Kiriwrite settings and languages.

our ($kiriwrite_config, %kiriwrite_config, %kiriwrite_lang, $kiriwrite_lang, $kiriwrite_version, %kiriwrite_version, $kiriwrite_env, %kiriwrite_env, $kiriwrite_presmodule, $kiriwrite_dbmodule, $form_data);

# Setup the version information for Kiriwrite.

%kiriwrite_version = (
	"major" 	=> 0,
	"minor" 	=> 2,
	"revision" 	=> 0
);

sub BEGIN{
#################################################################################
# BEGIN: Get the enviroment stuff						#
#################################################################################

	# Get the script filename.

	my $env_script_name = $ENV{'SCRIPT_NAME'};

	# Process the script filename until there is only the
	# filename itself.

	my $env_script_name_length = length($env_script_name);
	my $filename_seek = 0;
	my $filename_char = "";
	my $filename_last = 0;

	do {
		$filename_char = substr($env_script_name, $filename_seek, 1);
		if ($filename_char eq "/"){
			$filename_last = $filename_seek + 1;
		}
		$filename_seek++;
	} until ($filename_seek eq $env_script_name_length || $env_script_name_length eq 0);

	my $env_script_name_finallength = $env_script_name_length - $filename_last;
	my $script_filename = substr($env_script_name, $filename_last, $env_script_name_finallength);

	# Setup the needed enviroment variables for Kiriwrite.

	%kiriwrite_env = (
		"script_filename" => $script_filename,
	);

}

#################################################################################
# Begin listing the functions needed.						#
#################################################################################

sub kiriwrite_selectedlist{
#################################################################################
# kiriwrite_page_selectedlist: Get the list of selected pages to use.		#
#										#
# Usage:									#
#										#
# kiriwrite_page_selectedlist();						#
#################################################################################

	my $count	= $form_data->{'count'};

	# Check if the list of files has a value and if not set it 0.

	if (!$count){

		$count = 0;

	}

	# Define some values for later.

	my @filename_list; 
	my @selected_list;
	my @final_list;

	my $filename;
	my $selected;

	my $final_count = 0;
	my $seek = 0;

	# Get the list of filenames.

	do {

		# Get the values from id[]

		$seek++;

		$filename 		= $form_data->{'id[' . $seek . ']'};
		$filename_list[$seek] 	= $filename;

	} until ($seek eq $count || $count eq 0);

	# Get the list of selected filenames.

	$seek = 0;

	do {

		# Get the values from name[]

		$seek++;

		$selected 	= $form_data->{'name[' . $seek . ']'};

		if (!$selected){

			$selected = 'off';

		}

		$selected_list[$seek]	= $selected;

	} until ($seek eq $count || $count eq 0);

	# Create a final list of filenames to be used for
	# processing.

	$seek = 0;

	do {

		# Check if the selected value is on and include
		# the filename in the final list.

		$seek++;

		$selected 	= $selected_list[$seek];

		if ($selected eq "on"){

			$filename	= $filename_list[$seek];
			$final_list[$final_count] = $filename;
			$final_count++;

		}

	} until ($seek eq $count || $count eq 0);

	return @final_list;

}

sub kiriwrite_settings_load{
#################################################################################
# kiriwrite_settings_load: Load the configuration settings into the global	#
# variables.									#
#										#
# Usage:									#
#										#
# kiriwrite_settings_load();							#
#################################################################################

	# Load the required Perl modules.

	use Config::Auto;

	# Check if the Kiriwrite configuration file exists before using it and
	# return an critical error if it doesn't exist.

	my $kiriwrite_conf_exist = kiriwrite_fileexists("kiriwrite.cfg");

	if ($kiriwrite_conf_exist eq 1){

		# The configuration really does not exist so return an critical error.

		kiriwrite_critical("configfilemissing");

	}

	# Check if the Kiriwrite configuration file has valid permission settings
	# before using it and return an critical error if it doesn't have the
	# valid permission settings.

	my $kiriwrite_conf_permissions = kiriwrite_filepermissions("kiriwrite.cfg", 1, 0);

	if ($kiriwrite_conf_permissions eq 1){

		# The permission settings for the Kiriwrite configuration file are
		# invalid, so return an critical error.

		kiriwrite_critical("configfileinvalidpermissions");

	}

	# Converts the XML file into meaningful data for later on in this subroutine.

	my $kiriwrite_conf_file = 'kiriwrite.cfg';
	my $config = Config::Auto::parse($kiriwrite_conf_file, format => "ini");

	# Go and fetch the settings and place them into a hash (that is global).

	%kiriwrite_config = (

		"directory_data_db"		=> $config->{config}{directory_data_db},
		"directory_data_output"		=> $config->{config}{directory_data_output},
		"directory_noncgi_images"	=> $config->{config}{directory_noncgi_images},

		"system_language"		=> $config->{config}{system_language},
		"system_presmodule"		=> $config->{config}{system_presmodule},
		"system_dbmodule"		=> $config->{config}{system_dbmodule},
		"system_datetime"		=> $config->{config}{system_datetime},

		"display_textarearows"		=> $config->{config}{display_textarearows},
		"display_textareacols"		=> $config->{config}{display_textareacols},
		"display_pagecount"		=> $config->{config}{display_pagecount},
		"display_templatecount"		=> $config->{config}{display_templatecount},
		"display_filtercount"		=> $config->{config}{display_filtercount},

		"database_server"		=> $config->{config}{database_server},
		"database_port"			=> $config->{config}{database_port},
		"database_protocol"		=> $config->{config}{database_protocol},
		"database_sqldatabase"		=> $config->{config}{database_sqldatabase},
		"database_username"		=> $config->{config}{database_username},
		"database_password"		=> $config->{config}{database_password},
		"database_tableprefix"		=> $config->{config}{database_tableprefix}

	);

	# Do a validation check on all of the variables that were loaded into the global configuration hash.

	kiriwrite_variablecheck($kiriwrite_config{"directory_data_db"}, "maxlength", 64, 0);
	kiriwrite_variablecheck($kiriwrite_config{"directory_data_output"}, "maxlength", 64, 0);
	kiriwrite_variablecheck($kiriwrite_config{"directory_noncgi_images"}, "maxlength", 512, 0);
	kiriwrite_variablecheck($kiriwrite_config{"directory_data_template"}, "maxlength", 64, 0);

	my $kiriwrite_config_language_filename = kiriwrite_variablecheck($kiriwrite_config{"system_language"}, "language_filename", "", 1);
	my $kiriwrite_config_presmodule_filename = kiriwrite_variablecheck($kiriwrite_config{"system_presmodule"}, "module", 0, 1);
	my $kiriwrite_config_dbmodule_filename = kiriwrite_variablecheck($kiriwrite_config{"system_dbmodule"}, "module", 0, 1);

	my $kiriwrite_config_textarearows_maxlength = kiriwrite_variablecheck($kiriwrite_config{"display_textarearows"}, "maxlength", 3, 1);
	my $kiriwrite_config_textarearows_number = kiriwrite_variablecheck($kiriwrite_config{"display_textareacols"}, "numbers", 0, 1);
	my $kiriwrite_config_textareacols_maxlength = kiriwrite_variablecheck($kiriwrite_config{"display_textareacols"}, "maxlength", 3, 1);
	my $kiriwrite_config_textareacols_number = kiriwrite_variablecheck($kiriwrite_config{"display_textareacols"}, "numbers", 0, 1);
	my $kiriwrite_config_pagecount_maxlength = kiriwrite_variablecheck($kiriwrite_config{"display_pagecount"}, "maxlength", 4, 1);
	my $kiriwrite_config_pagecount_number = kiriwrite_variablecheck($kiriwrite_config{"display_pagecount"}, "numbers", 0, 1);
	my $kiriwrite_config_templatecount_maxlength = kiriwrite_variablecheck($kiriwrite_config{"display_templatecount"}, "maxlength", 4, 1);
	my $kiriwrite_config_templatecount_number = kiriwrite_variablecheck($kiriwrite_config{"display_templatecount"}, "numbers", 0, 1);
	my $kiriwrite_config_filtercount_maxlength = kiriwrite_variablecheck($kiriwrite_config{"display_filtercount"}, "maxlength", 4, 1);
	my $kiriwrite_config_filtercount_number = kiriwrite_variablecheck($kiriwrite_config{"display_filtercount"}, "numbers", 0, 1);

	# Check if the language filename is valid and return an critical error if
	# they aren't.

	if ($kiriwrite_config_language_filename eq 1){

		# The language filename is blank so return an critical error.

		kiriwrite_critical("languagefilenameblank");

	} elsif ($kiriwrite_config_language_filename eq 2){

		# The language filename is invalid so return an critical error.

		kiriwrite_critical("languagefilenameinvalid");

	}

	# Check if the presentation and database module names are valid and return a critical
	# error if they aren't.

	if ($kiriwrite_config_presmodule_filename eq 1){

		# The presentation module filename given is blank so return an 
		# critical error.

		kiriwrite_critical("presmoduleblank");

	}

	if ($kiriwrite_config_presmodule_filename eq 2){

		# The presentation module filename is invalid so return an
		# critical error.

		kiriwrite_critical("presmoduleinvalid");

	}

	if ($kiriwrite_config_dbmodule_filename eq 1){

		# The database module filename given is blank so return an
		# critical error.

		kiriwrite_critical("dbmoduleblank");

	}

	if ($kiriwrite_config_dbmodule_filename eq 2){

		# The database module filename given is invalid so return
		# an critical error.

		kiriwrite_critical("dbmoduleinvalid");

	}

	# Check if the text area column and row values are blank and return a critical
	# error if they are.

	if (!$kiriwrite_config{"display_textarearows"}){

		# The text area row value is blank so return
		# a critical error.

		kiriwrite_critical("textarearowblank");

	}

	if (!$kiriwrite_config{"display_textareacols"}){

		# The text area column value is blank so return
		# a critical error.

		kiriwrite_critical("textareacolblank");

	}

	# Check if the text area column and row values to see if they are valid and return
	# a critical error if they aren't.

	if ($kiriwrite_config_textarearows_maxlength eq 1){

		# The text area row value is too long so return an
		# critical error.

		kiriwrite_critical("textarearowtoolong");

	}

	if ($kiriwrite_config_textarearows_number eq 1){

		# The text area row value is invalid so return an
		# critical error.

		kiriwrite_critical("textarearowinvalid");

	}

	if ($kiriwrite_config_textareacols_maxlength eq 1){

		# The text area column value is too long so return
		# an critical error.

		kiriwrite_critical("textareacoltoolong");

	}

	if ($kiriwrite_config_textareacols_number eq 1){

		# The text area column value is invalid so return
		# an critical error.

		kiriwrite_critical("textareacolinvalid");

	}

	# Check if the amount of items per view settings are blank and return a critical
	# error if they are.

	if (!$kiriwrite_config{"display_pagecount"}){

		# The display page count is blank so return a
		# critical error.

		kiriwrite_critical("pagecountblank");

	}

	if (!$kiriwrite_config{"display_templatecount"}){

		# The display template count is blank so return
		# a critical error.

		kiriwrite_critical("templatecountblank");

	}

	if (!$kiriwrite_config{"display_filtercount"}){

		# The display filter count is blank so return a
		# critical error.

		kiriwrite_critical("filtercountblank");

	}

	# Check if the amount of items per view settings are valid and return a critical
	# error message if they aren't.

	if ($kiriwrite_config_pagecount_maxlength eq 1){

		# The length of the page count value is too long
		# so return a critical error.

		kiriwrite_critical("pagecounttoolong");

	}

	if ($kiriwrite_config_pagecount_number eq 1){

		# The page count value is invalid so return
		# a critical error.

		kiriwrite_critical("pagecountinvalid");

	}

	if ($kiriwrite_config_templatecount_maxlength eq 1){

		# The length of the template count value is too
		# long so return a critical error.

		kiriwrite_critical("filtercounttoolong");

	}

	if ($kiriwrite_config_templatecount_number eq 1){

		# The template count value is invalid so return
		# a critical error.

		kiriwrite_critical("filtercountinvalid");

	}

	if ($kiriwrite_config_filtercount_maxlength eq 1){

		# The length of the filter count value is too
		# long so return a critical error.

		kiriwrite_critical("templatecounttoolong");

	}

	if ($kiriwrite_config_filtercount_number eq 1){

		# The filter count value is invalid so return
		# a critical error.

		kiriwrite_critical("templatecountinvalid");

	}

	# Check if the language file does exist before loading it and return an critical error
	# if it does not exist.

	my $kiriwrite_config_language_fileexists = kiriwrite_fileexists("lang/" . $kiriwrite_config{"system_language"} . ".lang");

	if ($kiriwrite_config_language_fileexists eq 1){

		# Language file does not exist so return an critical error.

		kiriwrite_critical("languagefilemissing");

	}

	# Check if the language file has valid permission settings and return an critical error if
	# the language file has invalid permissions settings.

	my $kiriwrite_config_language_filepermissions = kiriwrite_filepermissions("lang/" . $kiriwrite_config{"system_language"} . ".lang", 1, 0);

	if ($kiriwrite_config_language_filepermissions eq 1){

		# Language file contains invalid permissions so return an critical error.

		kiriwrite_critical("languagefilenameinvalidpermissions");

	}

	# Load the language file.

	$kiriwrite_lang = Config::Auto::parse("lang/" . $kiriwrite_config{"system_language"} . ".lang", format => "ini");

 	# Check if the presentation module does exist before loading it and return an critical error
	# if the presentation module does not exist.

	my $kiriwrite_config_presmodule_fileexists = kiriwrite_fileexists("Modules/Presentation/" . $kiriwrite_config{"system_presmodule"} . ".pm");

	if ($kiriwrite_config_presmodule_fileexists eq 1){

		# Presentation module does not exist so return an critical error.

		kiriwrite_critical("presmodulemissing");

	}

	# Check if the presentation module does have the valid permission settings and return a
	# critical error if the presentation module contains invalid permission settings.

	my $kiriwrite_config_presmodule_permissions = kiriwrite_filepermissions("Modules/Presentation/" . $kiriwrite_config{"system_presmodule"} . ".pm", 1, 0);

	if ($kiriwrite_config_presmodule_permissions eq 1){

		# Presentation module contains invalid permissions so return an critical error.

		kiriwrite_critical("presmoduleinvalidpermissions");

	}

	# Check if the database module does exist before loading it and return an critical error
	# if the database module does not exist.

	my $kiriwrite_config_dbmodule_fileexists = kiriwrite_fileexists("Modules/Database/" . $kiriwrite_config{"system_dbmodule"} . ".pm");

	if ($kiriwrite_config_dbmodule_fileexists eq 1){

		# Database module does not exist so return an critical error.

		kiriwrite_critical("dbmodulemissing");

	}

	# Check if the database module does have the valid permission settings and return an
	# critical error if the database module contains invalid permission settings.

	my $kiriwrite_config_dbmodule_permissions = kiriwrite_filepermissions("Modules/Database/" . $kiriwrite_config{"system_dbmodule"} . ".pm", 1, 0);

	if ($kiriwrite_config_dbmodule_permissions eq 1){

		# Presentation module contains invalid permissions so return an critical error.

		kiriwrite_critical("dbmoduleinvalidpermissions");

	}

	# Include the Modules directory.

	use lib "Modules/";

	# Load the presentation module.

	my $presmodulename = "Presentation::" . $kiriwrite_config{"system_presmodule"};
	($presmodulename) = $presmodulename =~ m/^(.*)$/g;
	eval "use " . $presmodulename;
	$presmodulename = "Kiriwrite::Presentation::" . $kiriwrite_config{"system_presmodule"};
	$kiriwrite_presmodule = $presmodulename->new();

	# Load the database module.

	my $dbmodulename = "Database::" . $kiriwrite_config{"system_dbmodule"};
	($dbmodulename) = $dbmodulename =~ m/^(.*)$/g;
	eval "use " . $dbmodulename;
	$dbmodulename = "Kiriwrite::Database::" . $kiriwrite_config{"system_dbmodule"};
	$kiriwrite_dbmodule = $dbmodulename->new();

	# Load the following settings to the database module.

	$kiriwrite_dbmodule->loadsettings({ Directory => $kiriwrite_config{"directory_data_db"}, DateTime => $kiriwrite_config{"system_datetime"}, Server => $kiriwrite_config{"database_server"}, Port => $kiriwrite_config{"database_port"}, Protocol => $kiriwrite_config{"database_protocol"}, Database => $kiriwrite_config{"database_sqldatabase"}, Username => $kiriwrite_config{"database_username"}, Password => $kiriwrite_config{"database_password"}, TablePrefix => $kiriwrite_config{"database_tableprefix"} });

	return;

}

sub kiriwrite_variablecheck{
#################################################################################
# kiriwrite_variablecheck: Checks the variables for any invalid characters.	#
#										#
# Usage:									#
#										#
# kiriwrite_variablecheck(variable, type, length, noerror);			#
#										#
# variable	Specifies the variable to be checked.				#
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

	} elsif ($variable_type eq "blank"){
		# Check if the variable is blank and if it is blank, then return an error.

		if (!$variable_data){

			# The variable data really is blank, so check what
			# the no error value is set.

			if ($variable_noerror eq 1){

				# The no error value is set to 1, so return
				# a value of 1 (saying that the variable was
				# blank).

				return 1;

			} elsif ($variable_noerror eq 0){

				# The no error value is set to 0, so return
				# an error.

				kiriwrite_error("blankvariable");

			} else {

				# The no error value is something else other
				# than 0 or 1, so return an error.

				kiriwrite_error("invalidvariable");

			}

		}

		return 0;

	} elsif ($variable_type eq "filename"){
		# Check for letters and numbers, if anything else than letters and numbers is there (including spaces) return
		# an error.

		# Check if the filename passed is blank, if it is then return with an error.

		if ($variable_data eq ""){

			# The filename specified is blank, so check what the
			# noerror value is set.

			if ($variable_noerror eq 1){

				# The no error value is set to 1 so return
				# a value of 1 (meaning that the filename
				# was blank).

				return 1;

			} elsif ($variable_noerror eq 0){

				# The no error value is set to 1 so return
				# an error.

				kiriwrite_error("blankfilename");

			} else {

				# The no error value is something else other
				# than 0 or 1, so return an error.

				kiriwrite_error("invalidvariable");

			}

		} else {


		}

		my $variable_data_validated = $variable_data;
		$variable_data_validated =~ tr/a-zA-Z0-9\.//d;

		# Check if the validated data variable is blank, if it is 
		# then continue to the end of this section where the return 
		# function should be, otherwise return an error.

		if ($variable_data_validated eq ""){

			# The validated data variable is blank, meaning that 
			# it only contained letters and numbers.

		} else {

			# The validated data variable is not blank, meaning 
			# that it contains something else, so return an error
			# (or a value).

			if ($variable_noerror eq 1){

				# The no error value is set to 1 so return
				# an value of 2. (meaning that the filename
				# is invalid).


				return 2;

			} elsif ($variable_noerror eq 0){

				# The no error value is set to 0 so return
				# an error.

				kiriwrite_error("invalidfilename");

			} else {

				# The no error value is something else other
				# than 0 or 1 so return an error.

				kiriwrite_error("invalidvariable");

			}

		}

		return 0;

	} elsif ($variable_type eq "filenameindir"){
		# Check if the filename is in the directory and return an
		# error if it isn't.

		if ($variable_data eq ""){

			# The filename specified is blank, so check what the
			# noerror value is set.

			if ($variable_noerror eq 1){

				# The no error value is set to 1 so return
				# a value of 1 (meaning that the filename
				# was blank).

				return 1;

			} elsif ($variable_noerror eq 0){

				# The no error value is set to 1 so return
				# an error.

				kiriwrite_error("blankfilename");

			} else {

				# The no error value is something else other
				# than 0 or 1, so return an error.

				kiriwrite_error("invalidvariable");

			}

		} else {


		}

		# Set the following variables for later on.

		my $variable_data_length = 0;
		my $variable_data_char = "";
		my $variable_data_validated = "";
		my $variable_data_seek = 0;
		my $variable_database_list = "";
		my $variable_database_listcurrent = "";
		my $variable_data_firstlevel = 1;

		# Get the length of the variable recieved.

		$variable_data_length = length($variable_data);

		# Check if the database filename contains the directory command
		# for up a directory level and if it is, return an error
		# or return with a number.

		do {

			# Get a character from the filename passed to this subroutine.

			$variable_data_char = substr($variable_data, $variable_data_seek, 1);

			# Check if the current character is the forward slash character.

			if ($variable_data_char eq "/"){

				# Check if the current directory is blank (and on the first level), or if the
				# current directory contains two dots or one dot, if it does return an error.

				if ($variable_database_listcurrent eq "" && $variable_data_firstlevel eq 1 || $variable_database_listcurrent eq ".." || $variable_database_listcurrent eq "."){

					# Check if the noerror value is set to 1, if it is return an
					# number, else return an proper error.

					if ($variable_noerror eq 1){

						# Page filename contains invalid characters and
						# the no error value is set to 1 so return a 
						# value of 2 (meaning that the page filename
						# is invalid).

						return 2;

					} elsif ($variable_noerror eq 0) {

						# Page filename contains invalid characters and
						# the no error value is set to 0 so return an
						# error.

						kiriwrite_error("invalidfilename");

					} else {

						# The no error value is something else other
						# than 0 or 1 so return an error.

						kiriwrite_error("invalidvariable");

					}

				}

				# Append the forward slash, clear the current directory name and set
				# the first directory level value to 0.

				$variable_database_list = $variable_database_list . $variable_data_char;
				$variable_database_listcurrent = "";
				$variable_data_firstlevel = 0;

			} else {

				# Append the current character to the directory name and to the current
				# directory name.

				$variable_database_list = $variable_database_list . $variable_data_char;
				$variable_database_listcurrent = $variable_database_listcurrent . $variable_data_char;

			}

			# Increment the seek counter.

			$variable_data_seek++;

		} until ($variable_data_seek eq $variable_data_length);

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

				kiriwrite_error("blankdatetimeformat");

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

				kiriwrite_error("invaliddatetimeformat");

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

				kiriwrite_critical("languagefilenameblank");

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

					kiriwrite_critical("languagefilenameinvalid");

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

	} elsif ($variable_type eq "pagesetting"){

		# The variable type is a page setting, so check if the page
		# setting has one of the valid options.

		if ($variable_data eq 0 || $variable_data eq 1 || $variable_data eq 2 || $variable_data eq 3){

			# The variable is one of the options above, so continue
			# to the end of this section.

		} else {

			# The variable is not one of the options above, so check
			# and see if a error or a value should be returned.

			if ($variable_noerror eq 1){

				# The page setting is invalid and the no error
				# value is set 1, so return a value of 1
				# (saying that the page setting value is
				# invalid).

				return 1;

			} elsif ($variable_noerror eq 0) {

				# Page setting is invalid and the no error value
				# is not 1, so return an error.

				kiriwrite_error("invalidvariable");

			} else {

				# The no error value is something else other
				# than 0 or 1 so return an error.

				kiriwrite_error("invalidvariable");

			}

		}

		return 0;

	} elsif ($variable_type eq "page_filename"){
	 
		# The variable type is a page filename type. Check
		# if the data is empty and if it is then return an
		# error (or value).

		if ($variable_data eq ""){

			# The filename is blank so check the no error
			# value and depending on it return an value
			# or an error.

			if ($variable_noerror eq 1){

				# Page filename is blank and the no error value
				# is set as 1, so return a value of 1 (saying
				# the filename is blank).

				return 1;

			} elsif ($variable_noerror eq 0) {

				# Page filename is blank and the no error value
				# is not 1, so return an error.

				kiriwrite_error("emptypagefilename");

			} else {

				# The no error value is something else other
				# than 0 or 1 so return an error.

				kiriwrite_error("invalidvariable");

			}
		}

		# Set the following variables for later on.


		my $variable_data_length = 0;
		my $variable_data_slash = 0;
		my $variable_data_char = "";
		my $variable_data_validated = "";
		my $variable_data_seek = 0;
		my $variable_database_list = "";
		my $variable_database_listcurrent = "";
		my $variable_data_firstlevel = 1;

		# Get the length of the filename.

		$variable_data_length = length($variable_data);

		# Check that only valid characters should be appearing in
		# the filename.

		$variable_data_validated = $variable_data;
		$variable_data_validated =~ tr|a-zA-Z0-9\.\/\-_||d;

		if ($variable_data_validated ne ""){

			# The validated variable is not blank, meaning the
			# variable contains invalid characters, so return
			# an error.

			if ($variable_noerror eq 1){

				# Page filename contains invalid characters and
				# the no error value is set to 1 so return a 
				# value of 2 (meaning that the page filename
				# is invalid).

				return 2;

			} elsif ($variable_noerror eq 0) {

				# Page filename contains invalid characters and
				# the no error value is set to 0 so return an
				# error.

				kiriwrite_error("invalidfilename");

			} else {

				# The no error value is something else other
				# than 0 or 1 so return an error.

				kiriwrite_error("invalidvariable");

			}

		}

		# Check if the page filename contains the directory command
		# for up a directory level and if it is, return an error
		# or return with a number.

		do {

			# Get a character from the filename passed to this subroutine.

			$variable_data_char = substr($variable_data, $variable_data_seek, 1);

			# Check if the current character is the forward slash character.

			if ($variable_data_char eq "/"){

				# Check if the current directory is blank (and on the first level), or if the
				# current directory contains two dots or one dot, if it does return an error.

				$variable_data_slash = 1;

				if ($variable_database_listcurrent eq "" && $variable_data_firstlevel eq 1 || $variable_database_listcurrent eq ".." || $variable_database_listcurrent eq "."){

					# Check if the noerror value is set to 1, if it is return an
					# number, else return an proper error.

					if ($variable_noerror eq 1){

						# Page filename contains invalid characters and
						# the no error value is set to 1 so return a 
						# value of 2 (meaning that the page filename
						# is invalid).

						return 2;

					} elsif ($variable_noerror eq 0) {

						# Page filename contains invalid characters and
						# the no error value is set to 0 so return an
						# error.

						kiriwrite_error("invalidfilename");

					} else {

						# The no error value is something else other
						# than 0 or 1 so return an error.

						kiriwrite_error("invalidvariable");

					}

				}

				# Append the forward slash, clear the current directory name and set
				# the first directory level value to 0.

				$variable_database_list = $variable_database_list . $variable_data_char;
				$variable_database_listcurrent = "";
				$variable_data_firstlevel = 0;

			} else {

				# Append the current character to the directory name and to the current
				# directory name.

				$variable_data_slash = 0;

				$variable_database_list = $variable_database_list . $variable_data_char;
				$variable_database_listcurrent = $variable_database_listcurrent . $variable_data_char;

			}

			# Increment the seek counter.

			$variable_data_seek++;

		} until ($variable_data_seek eq $variable_data_length);

		# Check if the last character is a slash and return an
		# error if it is.

		if ($variable_data_slash eq 1){

			if ($variable_noerror eq 1){

				# Last character is a slash and the no error 
				# value is set to 1 so return a value of 2 
				# (meaning that the page filename is invalid).

				return 2;

			} elsif ($variable_noerror eq 0) {

				# Page filename contains a slash for the last
				# character and the no error value is set to 0 
				# so return an error.

				kiriwrite_error("invalidfilename");

			} else {

				# The no error value is something else other
				# than 0 or 1 so return an error.

				kiriwrite_error("invalidvariable");

			}

		}

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

	} elsif ($variable_type eq "utf8"){

		# The variable type is a UTF8 string.

		if (!$variable_data){

			$variable_data = "";

		}

		my $chunk = 0;
		my $process = 8192;
		my $length = 0;
		my $chunkdata = "";

		while ($chunk < $length){

  			$chunkdata = substr($variable_data, $chunk, $process);

  			if ($chunkdata =~ m/\A(
     				[\x09\x0A\x0D\x20-\x7E]            # ASCII
   				| [\xC2-\xDF][\x80-\xBF]             # non-overlong 2-byte
   				|  \xE0[\xA0-\xBF][\x80-\xBF]        # excluding overlongs
   				| [\xE1-\xEC\xEE\xEF][\x80-\xBF]{2}  # straight 3-byte
   				|  \xED[\x80-\x9F][\x80-\xBF]        # excluding surrogates
   				|  \xF0[\x90-\xBF][\x80-\xBF]{2}     # planes 1-3
				| [\xF1-\xF3][\x80-\xBF]{3}          # planes 4-15
   				|  \xF4[\x80-\x8F][\x80-\xBF]{2}     # plane 16
			)*\z/x){

				# The UTF-8 string is valid.
	
			} else {
	
				# The UTF-8 string is not valid, check if the no error
				# value is set to 1 and return an error if it isn't.
	
				if ($variable_noerror eq 1){
	
					# The no error value has been set to 1, so return
					# a value of 1 (meaning that the UTF-8 string is
					# invalid).
	
					return 1; 
	
				} elsif ($variable_noerror eq 0) {
	
					# The no error value has been set to 0, so return
					# an error.
	
					kiriwrite_error("invalidutf8");
	
				} else {
	
					# The no error value is something else other than 0
					# or 1, so return an error.
	
					kiriwrite_error("invalidoption");
	
				}
	
			}


			$chunk = $chunk + $process;

		}

# 		# Check if the string is a valid UTF8 string.
# 
#   		if ($variable_data =~ m/^(
# 			[\x09\x0A\x0D\x20-\x7E]              # ASCII
# 			| [\xC2-\xDF][\x80-\xBF]             # non-overlong 2-byte
# 			|  \xE0[\xA0-\xBF][\x80-\xBF]        # excluding overlongs
# 			| [\xE1-\xEC\xEE\xEF][\x80-\xBF]{2}  # straight 3-byte
# 			|  \xED[\x80-\x9F][\x80-\xBF]        # excluding surrogates
# 			|  \xF0[\x90-\xBF][\x80-\xBF]{2}     # planes 1-3
# 			| [\xF1-\xF3][\x80-\xBF]{3}          # planes 4-15
# 			|  \xF4[\x80-\x8F][\x80-\xBF]{2}     # plane 16
# 		)*$/x){
# 
# 			# The UTF-8 string is valid.
# 
# 		} else {
# 
# 			# The UTF-8 string is not valid, check if the no error
# 			# value is set to 1 and return an error if it isn't.
# 
# 			if ($variable_noerror eq 1){
# 
# 				# The no error value has been set to 1, so return
# 				# a value of 1 (meaning that the UTF-8 string is
# 				# invalid).
# 
# 				return 1; 
# 
# 			} elsif ($variable_noerror eq 0) {
# 
# 				# The no error value has been set to 0, so return
# 				# an error.
# 
# 				kiriwrite_error("invalidutf8");
# 
# 			} else {
# 
# 				# The no error value is something else other than 0
# 				# or 1, so return an error.
# 
# 				kiriwrite_error("invalidoption");
# 
# 			}
# 
# 		}

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

sub kiriwrite_output_header{
#################################################################################
# kiriwrite_output_header: Outputs the header to the browser/stdout/console.	#
#										#
# Usage:									#
#										#
# kiriwrite_output_header();							#
#################################################################################

	# Print a header saying that the page expires immediately since the
	# date is set in the past.

	print "Expires: Sun, 01 Jan 2006 00:00:00 GMT\r\n";
	print "Content-Type: text/html; charset=utf-8;\r\n\r\n";
	return;
}

sub kiriwrite_processfilename{
#################################################################################
# kiriwrite_processfilename: Processes a name and turns it into a filename that #
# can be used by Kiriwrite.							#
#										#
# Usage:									#
#										#
# kiriwrite_processfilename(text);						#
#										#
# text		Specifies the text to be used in the process for creating a new	#
#		filename.							#
#################################################################################

	# Get the values that have been passed to the subroutine.

	my ($process_text) = @_;

	# Define some variables that will be used later on.

	my $processed_stageone 	= "";
	my $processed_stagetwo 	= "";
	my $processed_length	= "";
	my $processed_char	= "";
	my $processed_seek	= 0;
	my $processed_filename 	= "";

	# Set the first stage value of the processed filename to the
	# process filename and then filter it out to only contain
	# numbers and letters (no spaces) and then convert the
	# capitals to small letters.

	$processed_stageone = $process_text;
 	$processed_stageone =~ tr#a-zA-Z0-9##cd;
	$processed_stageone =~ tr/A-Z/a-z/;

	# Now set the second stage value of the processed filename
	# to the first stage value of the processed filename and
	# then limit the filename down to 32 characters.

	$processed_stagetwo = $processed_stageone;
	$processed_length = length($processed_stagetwo);

	# Process the second stage filename into the final 
	# filename and do so until the seek counter is 32
	# or reaches the length of the second stage filename.

	do {

		# Get the character that is the seek counter
		# is set at.

		$processed_char = substr($processed_stagetwo, $processed_seek, 1);

		# Append to the final processed filename.

		$processed_filename = $processed_filename . $processed_char;

		# Increment the seek counter.

		$processed_seek++;

	} until ($processed_seek eq 32 || $processed_seek eq $processed_length);

	return $processed_filename;

}

sub kiriwrite_language{
#################################################################################
# kiriwrite_language: Process language strings that needs certain text inserted.#
#										#
# Usage:									#
#										#
# kiriwrite_language(string, [text, text, ...]);				#
#										#
# string	Specifies the string to process.				#
# text		Specifies the text to pass to the string (can be repeated many	#
#		times).								#
#################################################################################

        my $string = shift;
        my $item;

        foreach $item (@_){

                $string =~ s/%s/$item/;

        }

        return $string;

}

sub kiriwrite_error{
#################################################################################
# kiriwrite_error: Prints out an error message.					#
# 										#
# Usage:									#
#										#
# kiriwrite_error(errortype, errorext);						#
#										#
# errortype	Specifies the type of error that occured.			#
# errorext	Specifies the extended error information.			#
#################################################################################

	# Get the error type from the subroutine.

	my ($error_type, $error_extended) = @_;

	# Disconnect from the database server.

	if ($kiriwrite_dbmodule){
		$kiriwrite_dbmodule->disconnect();
	}

	# Load the list of error messages.

	my @kiriwrite_error = (

		# Catch all error message.
		"generic", 

		# Standard error messages.
		"blankfilename", "blankvariable", "fileexists",	"internalerror", "invalidoption", "invalidaction", "invalidfilename", "invalidmode", "invalidutf8", "invalidvariable", "variabletoolong",

		# Specific error messages.
		"blankcompiletype", "blankdatabasepageadd", "blankdirectory", "blankfindfilter", "blankdatetimeformat", "browsenumbertoolong", "browsenumberinvalid",  "databaseconnectionerror", "databasecategoriestoolong", "databasecopysame", "databasealreadyexists", "datadirectorymissing", "datadirectoryinvalidpermissions", "databasedescriptiontoolong", "databasefilenameinvalid", "databasefilenametoolong", "databaseerror", "databaseinvalidpermissions", "databasenameinvalid", "databasenametoolong", "databasenameblank", "databasemissingfile", "databasemovemissingfile", "databasenorename", "databasemovesame", "dbmoduleblank", "dbmoduleinvalid", "dbdirectoryblank", "dbdirectoryinvalid", "dbmodulemissing", "filtercountinvalid", "filtercounttoolong", "filtersdatabasenotcreated", "filtersdbdatabaseerror", "filtersdbpermissions", "filtersdbmissing", "filteridblank", "filterdoesnotexist", "filteridinvalid", "filteridtoolong", "findfiltertoolong", "filterpriorityinvalid", "filterpriorityinvalidchars", "filterprioritytoolong", "invalidcompiletype", "invalidpagenumber", "nopagesselected",	"invaliddirectory", "invaliddatetimeformat", "invalidlanguagefilename", "languagefilenamemissing", "moduleblank", "moduleinvalid",	"newcopydatabasedatabaseerror", "newcopydatabasedoesnotexist", "newcopydatabasefileinvalidpermissions", "newmovedatabasedatabaseerror",	"newmovedatabasedoesnotexist", "newmovedatabasefileinvalidpermissions", "nodatabasesavailable", "nodatabaseselected", "noeditvaluesselected", "oldcopydatabasedatabaseerror", "oldcopydatabasedoesnotexist", "oldcopydatabasefileinvalidpermissions", "oldmovedatabasedatabaseerror",	"oldmovedatabasedoesnotexist", "oldmovedatabasefileinvalidpermissions", "outputdirectoryblank", "outputdirectoryinvalid", "outputdirectorymissing", "outputdirectoryinvalidpermissions", "overridetemplatevalueinvalid", "overridetemplatetoolong", "overridetemplateinvalid",  "presmoduleblank", "presmoduleinvalid", "presmodulemissing", "pagecountinvalid", "pagecounttoolong",  "pagefilenamedoesnotexist", "pagefilenameexists", "pagefilenameinvalid", "pagefilenametoolong", "pagefilenameblank", "pagetitletoolong", "pagedescriptiontoolong", "pagesectiontoolong", "pagedatabasefilenametoolong", "pagesettingstoolong", "pagesettingsinvalid", "pagetemplatefilenametoolong", "replacefiltertoolong", "servernameinvalid", "servernametoolong", "serverdatabasenameinvalid", "serverdatabasenametoolong", "serverdatabaseusernameinvalid", "serverdatabaseusernametoolong", "serverdatabasepasswordtoolong", "serverdatabasetableprefixinvalid", "serverdatabasetableprefixtoolong", "serverportnumberinvalid", "serverportnumberinvalidcharacters", "serverportnumbertoolong", "serverprotocolnametoolong", "serverprotocolinvalid", "templatecountinvalid", "templatecounttoolong", "templatenameblank", "templatefilenameexists", "templatefilenameinvalid", "templatedatabaseerror", "templatedatabaseinvalidpermissions", "templatedatabaseinvalidformat", "templatedirectoryblank", "templatedirectoryinvalid", "templatedatabasenotcreated", "templatefilenametoolong", "templatenametoolong", "templatedescriptiontoolong", "templatedatabasemissing", "templatedoesnotexist", "templatefilenameblank", "textarearowblank", "textarearowtoolong", "textarearowinvalid", "textareacolblank", "textareacoltoolong", "textareacolinvalid"

	);

	# Check if the error message name is a valid error message name
	# and return the generic error message if it isn't.

	my $error_string = "";

	if (grep /^$error_type$/, @kiriwrite_error){

		# The error type is valid so get the error language string
		# associated with this error messsage name.

		$error_string = $kiriwrite_lang->{error}->{$error_type};

	} else {

		# The error type is invalid so set the error language
		# string using the generic error message name.

		$error_string = $kiriwrite_lang->{error}->{generic};

	}

	$kiriwrite_presmodule->clear();

	$kiriwrite_presmodule->startbox("errorbox");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{error}->{error}, { Style => "errorheader" });
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addtext($error_string, { Style => "errortext" });

	# Check to see if extended error information was passed.

	if ($error_extended){

		# Write the extended error information.

		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{error}->{extendederror});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->startbox("datalist");
		$kiriwrite_presmodule->addtext($error_extended);
		$kiriwrite_presmodule->endbox();

	}

	$kiriwrite_presmodule->endbox();

	kiriwrite_output_header;
	kiriwrite_output_page($kiriwrite_lang->{error}->{error}, $kiriwrite_presmodule->grab(), "none");

	exit;

}

sub kiriwrite_fileexists{
#################################################################################
# kiriwrite_fileexists: Check if a file exists and returns a value depending on #
# if the file exists or not.							#
#										# 
# Usage:									#
#										#
# kiriwrite_fileexists(filename);						#
#										#
# filename	Specifies the file name to check if it exists or not.		#
#################################################################################

	# Get the value that was passed to the subroutine.

	my ($filename) = @_;

	# Check if the filename exists, if it does, return a value of 0, else
	# return a value of 1, meaning that the file was not found.

	if (-e $filename){

		# Specified file does exist so return a value of 0.

		return 0;

	} else {

		# Specified file does not exist so return a value of 1.

		return 1;

	}

}

sub kiriwrite_filepermissions{
#################################################################################
# kiriwrite_filepermissions: Check if the file permissions of a file and return #
# either a 1 saying that the permissions are valid or return a 0 saying that	#
# the permissions are invalid.							#
# 										#
# Usage:									#
#										#
# kiriwrite_filepermissions(filename, [read], [write], [filemissingskip]);	#
#										#
# filename		Specifies the filename to check for permissions.	#
# read			Preform check that the file is readable.		#
# write			Preform check that the file is writeable.		#
# filemissingskip	Skip the check of seeing if it can read or write if the #
#			file is missing.					#
#################################################################################

	# Get the values that was passed to the subroutine.

	my ($filename, $readpermission, $writepermission, $ignorechecks) = @_;

	# Check to make sure that the read permission and write permission values
	# are only 1 character long.

	kiriwrite_variablecheck($readpermission, "maxlength", 1, 0);
	kiriwrite_variablecheck($writepermission, "maxlength", 1, 0);
	kiriwrite_variablecheck($ignorechecks, "maxlength", 1, 0);

	my $ignorechecks_result = 0;

	# Check if the file should be ignored for read and write checking if 
	# it doesn't exist.

	if ($ignorechecks){

		if (-e $filename){

			# The file exists so the checks are to be done.

			$ignorechecks_result = 0;

		} else {

			# The file does not exist so the checks don't need to
			# be done to prevent false positives.

			$ignorechecks_result = 1;

		}

	} else {

		$ignorechecks_result = 0;

	}

	# Check if the file should be checked to see if it can be read.

	if ($readpermission && $ignorechecks_result eq 0){

		# The file should be checked to see if it does contain read permissions
		# and return a 0 if it is invalid.

		if (-r $filename){

			# The file is readable, so do nothing.

		} else {

			# The file is not readable, so return 1.

			return 1;

		}

	}

	# Check if the file should be checked to see if it can be written.

	if ($writepermission && $ignorechecks_result eq 0){

		# The file should be checked to see if it does contain write permissions
		# and return a 0 if it is invalid.

		if (-w $filename){

			# The file is writeable, so do nothing.

		} else {

			# The file is not writeable, so return 1.

			return 1;

		}

	}

	# No problems have occured, so return 0.

	return 0;

}

sub kiriwrite_utf8convert{
#################################################################################
# kiriwrite_utf8convert: Properly converts values into UTF-8 values.		#
#										#
# Usage:									#
#										#
# utfstring	# The UTF-8 string to convert.					#
#################################################################################

	# Get the values passed to the subroutine.

	my ($utfstring) = @_;

	# Load the Encode perl module.

	use Encode qw(decode_utf8);

	# Convert the string.

	my $finalutf8 = Encode::decode_utf8( $utfstring );

	return $finalutf8;
	#return $utfstring;

}

sub kiriwrite_critical{
#################################################################################
# kiriwrite_critical: Displays an critical error message that cannot be		#
# normally by the kiriwrite_error subroutine.					#
#										#
# Usage:									#
#										#
# errortype	Specifies the type of critical error that has occured.		#
#################################################################################

	# Get the value that was passed to the subroutine.

	my ($error_type) = @_;

	my %error_list;

	# Get the error type from the errortype string.

	%error_list = (

		# Generic critical error message.

		"generic"			=> "A critical error has occured but the error is not known to Kiriwrite.",

		# Specific critical error messages.

		"configfilemissing" 		=> "The Kiriwrite configuration file is missing! Running the installer script for Kiriwrite is recommended.",
		"configfileinvalidpermissions"	=> "The Kiriwrite configuration file has invalid permission settings set! Please set the valid permission settings for the configuration file.",
		"dbmodulemissing"		=> "The database module is missing! Running the installer script for Kiriwrite is recommended.",
		"dbmoduleinvalidpermissions"	=> "The database module cannot be used as it has invalid permission settings set! Please set the valid permission settings for the configuration file.",
		"dbmoduleinvalid"		=> "The database module name given is invalid. Running the installer script for Kiriwrite is recommended.",
		"invalidvalue"			=> "An invalid value was passed.",
		"languagefilenameblank"		=> "The language filename given is blank! Running the installer script for Kiriwrite is recommended.",
		"languagefilenameinvalid"	=> "The language filename given is invalid! Running the installer script for Kiriwrite is recommended.",
		"languagefilemissing"	=> "The language filename given does not exist. Running the installer script for Kiriwrite is recommended.",
		"languagefilenameinvalidpermissions"	=> "The language file with the filename given has invalid permissions set. Please set the valid permission settings for the language file.",
		"presmodulemissing"		=> "The presentation module is missing! Running the installer script for Kiriwrite is recommended.",
		"presmoduleinvalidpermissions"	=> "The presentation module cannot be used as it has invalid permission settings set! Please set the valid permission settings for the presentation module.",
		"presmoduleinvalid"		=> "The presentation module name given is invalid. Running the installer script for Kiriwrite is recommended.",
		"textarearowblank"		=> "The text area row value given is blank. Running the installer script for Kiriwrite is recommended.",
		"textarearowtoolong"		=> "The text area row value is too long. Running the installer script for Kiriwrite is recommended.",
		"textarearowinvalid"		=> "The text area row value is invalid. Running the installer script for Kiriwrite is recommended.",
		"textareacolblank"		=> "The text area row value given is blank. Running the installer script for Kiriwrite is recommended.",
		"textareacoltoolong"		=> "The text area column value is too long. Running the installer script for Kiriwrite is recommended.",
		"textareacolinvalid"		=> "The text area column value is invalid. Running the installer script for Kiriwrite is recommended.",
		"pagecountblank"		=> "The page count value is blank. Running the installer script for Kiriwrite is recommended.",
		"templatecountblank"		=> "The template count value is blank. Running the installer script for Kiriwrite is recommended.",
		"filtercountblank"		=> "The filter count value is blank. Running the installer script for Kiriwrite is recommended.",
		"pagecounttoolong"		=> "The page count value is too long. Running the installer script for Kiriwrite is recommended.",
		"templatecounttoolong"		=> "The template count value is too long. Running the installer script for Kiriwrite is recommended.",
		"filtercounttoolong"		=> "The filter count value is too long. Running the installer script for Kiriwrite is recommended.",
		"pagecountinvalid"		=> "The page count value is invalid. Running the installer script for Kiriwrite is recommended.",
		"templatecountinvalid"		=> "The template count value is invalid. Running the installer script for Kiriwrite is recommended.",
		"filtercountinvalid"		=> "The filter count is invalid. Running the installer script for Kiriwrite is recommended."

	);

	if (!$error_list{$error_type}){

		$error_type = "generic";

	}

	print "Expires: Sun, 01 Jan 2006 00:00:00 GMT\r\n";
	print "Content-Type: text/html; charset=utf-8;\r\n\r\n";
	print "Critical Error: " . $error_list{$error_type};
	exit;

}

sub kiriwrite_output_page{
#################################################################################
# kiriwrite_output_page: Outputs the page to the browser/stdout/console.	#
#										#
# Usage:									#
# 										#
# kiriwrite_output_page(pagetitle, pagedata, menutype);				#
# 										#
# pagetitle	Specifies the page title.					#
# pagedata	Specifies the page data.					#
# menutype	Prints out which menu to use.					#
#################################################################################

	my ($pagetitle, $pagedata, $menutype) = @_;

	# Open the script page template and load it into the scriptpage variable,
	# while declaring the variable.

	open (my $filehandle_scriptpage, "<:utf8", 'page.html');
	my @scriptpage = <$filehandle_scriptpage>;
	binmode $filehandle_scriptpage, ':utf8';
	close ($filehandle_scriptpage);

	# Define the variables required.

	my $scriptpageline = "";
	my $pageoutput = "";
	my $menuoutput = "";

	$kiriwrite_presmodule->clear();

	# Print out the main menu for Kiriwrite.

	$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=db", { Text => $kiriwrite_lang->{menu}->{viewdatabases} });
	$kiriwrite_presmodule->addtext(" | ");
	$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=page", { Text => $kiriwrite_lang->{menu}->{viewpages} });
	$kiriwrite_presmodule->addtext(" | ");
	$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=filter", { Text => $kiriwrite_lang->{menu}->{viewfilters} });
	$kiriwrite_presmodule->addtext(" | ");
	$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=template", { Text => $kiriwrite_lang->{menu}->{viewtemplates} });
	$kiriwrite_presmodule->addtext(" | ");
	$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=compile", { Text => $kiriwrite_lang->{menu}->{compilepages} });
	$kiriwrite_presmodule->addtext(" | ");
	$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=settings", { Text => $kiriwrite_lang->{menu}->{viewsettings} });
	$kiriwrite_presmodule->addlinebreak();

	# Check what menu is going to be printed along with the default 'top' menu.

	if ($menutype eq "database"){

		# If the menu type is database then print out the database sub-menu.

		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=db", { Text => $kiriwrite_lang->{database}->{submenu_viewdatabases} });
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=db&action=new", { Text => $kiriwrite_lang->{database}->{submenu_adddatabase} });

	} elsif ($menutype eq "pages"){
		# If the menu type is pages then print out the pages sub-menu.

		# First, fetch the database name from the HTTP query string.

		my $db_filename = $form_data->{'database'};

		# Check if a value has been placed in the db_filename string.

		if (!$db_filename){

			# As the database filename is blank, don't add an option to add a page.

		} else {

			# A database file has been specified so add an option to add a page to
			# the selected database.

			$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=page&action=add&database="  . $db_filename, { Text => $kiriwrite_lang->{pages}->{submenu_addpage} });

		}

	} elsif ($menutype eq "filter"){

		# If the menu type is filters then print out the filter sub-menu.

		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=filter", { Text => $kiriwrite_lang->{filter}->{submenu_showfilters} });
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=filter&action=add", { Text => $kiriwrite_lang->{filter}->{submenu_addfilter} });

	} elsif ($menutype eq "settings"){

		# If the menu type is options then print out the options sub-menu.

		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=settings", { Text => $kiriwrite_lang->{setting}->{submenu_viewsettings} });
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=settings&action=edit", { Text => $kiriwrite_lang->{setting}->{submenu_editsettings} });

	} elsif ($menutype eq "template"){

		# If the menu type is template then print out the template sub-menu.

		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=template", { Text => $kiriwrite_lang->{template}->{submenu_showtemplates} });
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=template&action=add", { Text => $kiriwrite_lang->{template}->{submenu_addtemplate} });

	} elsif ($menutype eq "compile"){

		# If the menu type is compile then print out the compile sub-menu.

		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=compile", { Text => $kiriwrite_lang->{compile}->{submenu_listdatabases} });
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=compile&action=all", { Text => $kiriwrite_lang->{compile}->{submenu_compileall} });
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=compile&action=clean", { Text => $kiriwrite_lang->{compile}->{submenu_cleanoutputdirectory} });

	}

	$menuoutput = $kiriwrite_presmodule->grab();

	# Find <kiriwrite> tages and replace with the apporiate variables.

	foreach $scriptpageline (@scriptpage){

		$scriptpageline =~ s/<kiriwrite:menu>/$menuoutput/g;
		$scriptpageline =~ s/<kiriwrite:imagespath>/$kiriwrite_config{"directory_noncgi_images"}/g;
		$scriptpageline =~ s/<kiriwrite:pagedata>/$pagedata/g;

		# Check if page title specified is blank, otherwise add a page title
		# to the title.

		if ($pagetitle eq ""){
			$scriptpageline =~ s/<kiriwrite:title>//g;
		} else {
			$scriptpageline =~ s/<kiriwrite:title>/ ($pagetitle)/g;
		}

		

		# Append processed line to the pageoutput variable.

		$pageoutput = $pageoutput . $scriptpageline;

	}

	print $pageoutput;

	return;

}

#################################################################################
# End listing the functions needed. 						#
#################################################################################

#################################################################################
# Begin proper script execution.						#
#################################################################################

kiriwrite_settings_load;	# Load the configuration options.

my $query_lite = new CGI::Lite;

# Check if a mode has been specified and if a mode has been specified, continue
# and work out what mode has been specified.

$form_data = $query_lite->parse_form_data;

if ($form_data->{'mode'}){
	my $http_query_mode = $form_data->{'mode'};

	if ($http_query_mode eq "db"){

		# If mode is 'db' (database), then load the database perl library and
		# check what action is required.

		require "./lib/database.lib";

	} elsif ($http_query_mode eq "page"){

		# If mode is 'page', load the page library and then check what 
		# action is required.

		require "./lib/page.lib";

	} elsif ($http_query_mode eq "filter"){

		# Load the filter perl library and then check the
		# value of the action HTTP query.

		require "./lib/filter.lib";

	} elsif ($http_query_mode eq "template"){

		# Load the template perl library and check if an action has
		# been specified in the HTTP query.

		require "./lib/template.lib";

	} elsif ($http_query_mode eq "compile"){

		# Load the compile perl library.

		require "./lib/compile.lib";

	} elsif ($http_query_mode eq "settings"){

		# Load the settings perl library.

		require "./lib/settings.lib";

	} else {
		# Another mode has been specified than the ones above, so return an error saying that
		# an invalid option was specified.

		kiriwrite_error("invalidmode");
	}

} else {

	# No mode has been specified, so print the default "first-run" view of the
	# database list.

	require "./lib/database.lib";

	my $pagedata = kiriwrite_database_list();

	kiriwrite_output_header;		# Output the header to browser/console/stdout.
	kiriwrite_output_page("", $pagedata, "database");	# Output the page to browser/console/stdout.
	exit;					# End the script.

}

__END__

=head1 NAME

Kiriwrite

=head1 DESCRIPTION

Web-based webpage compiler.

=head1 AUTHOR

Steve Brokenshire <sbrokenshire@xestia.co.uk>

=head1 USAGE

This perl script is intended to be used on a web server which has CGI with Perl support or with mod_perl support.

=head1 DOCUMENTATION

For more information on how to use Kiriwrite, please see the documentation that was included with Kiriwrite.

- From the Xestia Documentation website: http://documentation.xestia.co.uk and click on the Kiriwrite link on the page.

- From the Documentation directory from the Kiriwrite source packages (.tar/.tar.gz/.tar.bz2).

- In the /usr/share/doc/kiriwrite directory if you installed the distribution-specific packages (and also have access to the server itself).