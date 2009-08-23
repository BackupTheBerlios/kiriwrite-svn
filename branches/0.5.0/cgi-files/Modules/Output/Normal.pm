#################################################################################
# Kiriwrite Output Module - Normal Output Module.				#
# Outputs the pages exactly as previous versions of Kiriwrite (before 0.5.0).	#
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

package Modules::Output::Normal;

# Enable strict and use warnings.

use strict;
use warnings;
use Encode qw(decode_utf8);
use Tie::IxHash;
use Modules::System::Common;

# Set the following values.

our $VERSION = "0.5.0";
my ($pages, %pages);
my $error_flag = 0;
my $error_message = "";
my $language_name = "";
my %optionshash = ();

tie(%pages, "Tie::IxHash");

sub new{
#################################################################################
# new: Create an instance of Modules::Output::Normal				#
# 										#
# Usage:									#
#										#
# $dbmodule = Modules::Output::Normal->new();					#
#################################################################################
	
	# Get the perl module name.

	my $class = shift;
	my $self = {};

	return bless($self, $class);

}

sub initialise{
#################################################################################
# initialise: Initialises the output module.					#
#										#
# Usage:									#
#										#
# $outputmodule->initialise();							#
#################################################################################

}

sub loadsettings{
#################################################################################
# loadsettings: Loads some settings for the output module.			#
#										#
# Usage:									#
#										#
# $outputmodule->loadsettings(language, optionshash);				#
#										#
# language	Specifies the language to use.					#
# datetime	Specifies the date and time format.				#		
# optionshash	Specifies the hash that contains the options for the module.	#
#################################################################################

	my $class = shift;
	my $passed_lang = shift;

	(%optionshash) = @_;

	$language_name = $passed_lang;

	# Check for any blank variables.

	$optionshash{outputmodule_seperatedirdatabase} = "off" if !$optionshash{outputmodule_seperatedirdatabase};

}

sub getoptions{
#################################################################################
# getoptions: Gets the options that will be used.				#
#										#
# Usage:									#
#										#
# %options = $outputmodule->getoptions();					#
#################################################################################

	my (%options, $options);
	tie(%options, "Tie::IxHash");

	$options{seperatedirdatabase}{type} = "checkbox";
	$options{seperatedirdatabase}{string} = languagestrings("seperatedirdatabase");
	return %options;

}

sub addpage{
#################################################################################
# addpage: Adds a page.								#
#										#
# Usage:									#
#										#
# $outputmodule->addpage({ Page => "index.html", Data => $pagedata,		#
#				Title => $title, Section => $section, 		#
#				LastModified => $lastmodified, 			#
#				Database => $database });			#	
#										#
# Page		Specifies the page name to use.					#
# Data		Specifies the data of the page.					#
# Title		Specifies the title of the page.				#
# Section	Specifies the section of the page.				#
# LastModified	Specifies when the page was last modified.			#
# Database	Specifies the name of the database it came from.		#
#################################################################################

	# Not needed for this module.

	return;

}

sub outputpage{
#################################################################################
# outputpage: Outputs a page.							#
#										#
# Usage:									#
#										#
# $outputmodule->outputpage({ Page => "index.html", Data => $pagedata,		#
#				Title => $title, Section => $section, 		#
#				LastModified => $lastmodified, 			#
#				Database => $database });			#	
#										#
# Page		Specifies the page name to use.					#
# Data		Specifies the data of the page.					#
# Title		Specifies the title of the page.				#
# Section	Specifies the section of the page.				#
# LastModified	Specifies when the page was last modified.			#
# Database	Specifies the name of the database it came from.		#
#################################################################################

	my $class = shift;
	my ($options) = @_;

	my $page_filename 	= $options->{"Page"};
	my $page_data		= $options->{"Data"};
	my $page_database	= $options->{"Database"};

 	my $page_filename_length	= 0;
 	my $page_filename_seek 		= 0;
 	my $page_filename_dircount	= 0;
	my $page_filename_permissions	= 0;
	my $page_filename_directory	= "";
	my $page_filename_char		= "";
	my $page_filename_exists	= "";
	my $page_directory_name		= "";
	my $page_directory_path 	= "";
	my @pagedirectories;
	my $filehandle_page;

	# Check if the use seperate directory option is enabled and add the
	# database name to the start of the filename.

	if ($optionshash{outputmodule_seperatedirdatabase} eq "on"){
		($page_database) = $page_database =~ m/^(.*)$/g;
		$page_filename = $page_database . "/" . $page_filename;
	}

	# Process the page filename and check what directories
	# need to be created.

	$page_filename_length = int(length($page_filename));

	do {

		$page_filename_char = substr($page_filename, $page_filename_seek, 1);

		# Check if a forward slash appears and add it to
		# the list of directories array.

		if ($page_filename_char eq '/'){

			# Append the directory name to the list of
			# directories array.

			$pagedirectories[$page_filename_dircount] = $page_filename_directory;
			$page_filename_directory 	= "";
			$page_filename_char		= "";
			$page_filename_dircount++;

		} else {

			# Append the character to the directory/filename.

			$page_filename_directory = $page_filename_directory . $page_filename_char;

		}

		$page_filename_seek++;

	} until ($page_filename_length eq $page_filename_seek);

	foreach $page_directory_name (@pagedirectories){

		# Check if the directory name is undefined and if it
		# is then set it blank.

		if (!$page_directory_name){
			$page_directory_name = "";
		}

		if (!$page_directory_path){
			$page_directory_path = "";
		}

		# Check if the directory exists and create 
		# the directory if it doesn't exist.

		$page_directory_path = $page_directory_path . '/' . $page_directory_name;

		mkdir($main::kiriwrite_config{"directory_data_output"} . '/' . $page_directory_path);

	}

	# Check if the file already exists and if it does then check
	# the permissions of the file and return an error if the
	# permissions set are invalid.

	$page_filename_exists = kiriwrite_fileexists($main::kiriwrite_config{"directory_data_output"} . '/' . $page_filename);	

	if ($page_filename_exists eq 0){

		# The page filename exists, so check if the permissions given are
		# valid.

		$page_filename_permissions = kiriwrite_filepermissions($main::kiriwrite_config{"directory_data_output"} . '/' . $page_filename, 1, 1);

		if ($page_filename_permissions eq 1){

			# The file has invalid permissions set.

			$error_flag = 1;
			$error_message = languagestrings("invalidpermissionset");
			return;

		}

	}

	# Write the file to the output directory.

	($page_filename) = $page_filename =~ m/^(.*)$/g;
	($main::kiriwrite_config{"directory_data_output"}) = $main::kiriwrite_config{"directory_data_output"} =~ m/^(.*)$/g;

	open($filehandle_page, "> ",  $main::kiriwrite_config{"directory_data_output"} . '/' . $page_filename) or ($error_flag = 1, $error_message = $!, return);

	binmode $filehandle_page, ':utf8';
	print $filehandle_page $page_data;
	close($filehandle_page);

	if (!$page_data){

		$page_data = "";

	}

	return;

}

sub outputall{
#################################################################################
# outputall: Outputs all pages.							#
#										#
# Usage:									#
#										#
# $outputmodule->outputall({ FinishedProcessing => 1 });			#
#										#
# FinishedProcessing	Indicate that this should be the last time outputall is #
#			going to be called.					#
#################################################################################

	# Not needed for this module.

	return;
	
}

sub clearpages{
#################################################################################
# clearpages: Clears all of the pages.						#
#										#
# Usage:									#
#										#
# $outputmodule->clearpages();							#
#################################################################################
}

sub errorflag{
#################################################################################
# errorflag: Returns an error flag (if any).					#
#										#
# Usage:									#
#										#
# $errorflag 	= $outputmodule->errorflag();					#
#################################################################################
	
	return $error_flag;

}

sub errormessage{
#################################################################################
# errormessage: Returns an error message (if any).				#
#										#
# Usage:									#
#										#
# $errormessage = $outputmodule->errormessage();				#
#################################################################################

	return $error_message;

}

sub clearflag{
#################################################################################
# clearflag: Clears the error message flag and the error message itself.	#
#										#
# Usage:									#
#										#
# $outputmodule->clearflag();							#
#################################################################################

	$error_flag 	= 0;
	$error_message	= "";

}

sub languagestrings{
#################################################################################
# languagestrings: Language strings that are used in this module.		#
#										#
# Usage:									#
#										#
# $string = $outputmodule->languagestrings("langstring");			#
#################################################################################

	my $langstring = shift;

	my $language_string;
	my ($language_strings, %language_strings);
	my $item;

	if ($language_name eq "en-GB" or !$language_name){

		# Language strings for English (British) language.

		$language_strings{seperatedirdatabase} = "Seperate directory for each database.";
		$language_strings{invalidpermissionset} = "Invalid file permissions set.";

	} else {

		# Invalid language so use English (British) as default.

		$language_strings{seperatedirdatabase} = "Seperate directory for each database.";
		$language_strings{invalidpermissionset} = "Invalid file permissions set.";

	}

	$language_string = $language_strings{$langstring};
	
	foreach $item (@_){

                $language_string =~ s/%s/$item/;

        }

	return $language_string;

}

sub finish{
#################################################################################
# finish: Close anything that was open.						#
#										#
# Usage:									#
#										#
# $outputmodule->finish();							#
#################################################################################
}

1;