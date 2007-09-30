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
use CGI qw(header);
use Tie::IxHash;

# This is commented out because it uses a fair bit of CPU usage.

#use CGI::Carp('fatalsToBrowser'); 	# Output errors to the browser.

# Declare global variables for Kiriwrite settings and languages.

my ($kiriwrite_config, %kiriwrite_config, $kiriwrite_lang, $kiriwrite_version, %kiriwrite_version, $kiriwrite_env, %kiriwrite_env, $kiriwrite_presmodule, $kiriwrite_dbmodule, $xsl);

# Setup the version information for Kiriwrite.

%kiriwrite_version = (
	"major" 	=> 0,
	"minor" 	=> 1,
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

	$ENV{XML_SIMPLE_PREFERRED_PARSER} = "XML::Parser";

}

#################################################################################
# Begin listing the functions needed.						#
#################################################################################

sub kiriwrite_page_add{
#################################################################################
# kiriwrite_page_add: Adds a page to a database					#
#										#
# Usage:									#
#										#
# kiriwrite_page_add(database, pagefilename, title, description, section,	#
#			template, settings, info, confirm);			#
#										#
# database	Specifies the database name.					#
# pagefilename	Specifies the page filename.					#
# title		Specifies the page title to be used.				#
# description	Specifies the short description of the page.			#
# section	Specifies the section assigned to the page.			#
# template	Specifies the template to use.					#
# settings	Specifies the settings to be used on the page.			#
# data		Specifies the data which consists the page.			#
# confirm	Confirms action to add an page.					#
#################################################################################

	# Fetch the required variables that have been passed to the subroutine.

	my ($pagedatabase, $pagefilename, $pagetitle, $pagedescription, $pagesection, $pagetemplate, $pagesettings, $pagefiledata, $confirm) = @_;

	# Check if the action to add a new page has been confirmed (or not).

	if (!$confirm){

		$confirm = 0;

	}

	kiriwrite_variablecheck($confirm, "maxlength", 1, 0);

	# Check if the database filename is valid and return an error if
	# it isn't.

	my $pagedatabase_filename_check = kiriwrite_variablecheck($pagedatabase, "filename", 0, 1);

	if ($pagedatabase_filename_check eq 1){

		# The database filename is blank, so return an error.

		kiriwrite_error("blankdatabasepageadd");

	} elsif ($pagedatabase_filename_check eq 2){

		# The database filename is invalid, so return an error.

		kiriwrite_error("databasefilenameinvalid");

	}

	# Check the length the database name and return an error if it's
	# too long.

	my $pagedatabase_length_check 	= kiriwrite_variablecheck($pagedatabase, "maxlength", 32, 1);

	if ($pagedatabase_length_check eq 1){

		# The database name is too long, so return an error.

		kiriwrite_error("databasefilenametoolong");

	}

	if ($confirm eq "1"){

		# Check all the variables to see if they UTF8 valid.

		kiriwrite_variablecheck($pagefilename, "utf8", 0, 0);
		kiriwrite_variablecheck($pagetitle, "utf8", 0, 0);
		kiriwrite_variablecheck($pagedescription, "utf8", 0, 0);
		kiriwrite_variablecheck($pagesection, "utf8", 0, 0);
		kiriwrite_variablecheck($pagedatabase, "utf8", 0, 0);
		kiriwrite_variablecheck($pagesettings, "utf8", 0, 0);
		kiriwrite_variablecheck($pagetemplate, "utf8", 0, 0);
		kiriwrite_variablecheck($pagefiledata, "utf8", 0, 0);

		# Convert the values into proper UTF8 values.

		$pagefilename 		= kiriwrite_utf8convert($pagefilename);
		$pagetitle		= kiriwrite_utf8convert($pagetitle);
		$pagedescription	= kiriwrite_utf8convert($pagedescription);
		$pagesection		= kiriwrite_utf8convert($pagesection);
		$pagedatabase		= kiriwrite_utf8convert($pagedatabase);
		$pagesettings		= kiriwrite_utf8convert($pagesettings);
		$pagetemplate		= kiriwrite_utf8convert($pagetemplate);
		$pagefiledata		= kiriwrite_utf8convert($pagefiledata);

		# Check all the variables (except for the page data, filename and settings 
		# will be checked more specifically later if needed) that were passed to 
		# the subroutine.

		my $pagefilename_maxlength_check 		= kiriwrite_variablecheck($pagefilename, "maxlength", 256, 1);
		my $pagetitle_maxlength_check			= kiriwrite_variablecheck($pagetitle, "maxlength", 512, 1);
		my $pagedescription_maxlength_check		= kiriwrite_variablecheck($pagedescription, "maxlength", 512, 1);
		my $pagesection_maxlength_check			= kiriwrite_variablecheck($pagesection, "maxlength", 256, 1);
		my $pagedatabase_maxlength_check		= kiriwrite_variablecheck($pagedatabase, "maxlength", 32, 1);
		my $pagesettings_maxlength_check		= kiriwrite_variablecheck($pagesettings, "maxlength", 1, 1);
		my $pagetemplate_maxlength_check 		= kiriwrite_variablecheck($pagetemplate, "maxlength", 64, 1);

		# Check if an value returned is something else other than 0.

		if ($pagefilename_maxlength_check eq 1){

			# The page filename given is too long, so return an error.

			kiriwrite_error("pagefilenametoolong");

		}

		if ($pagetitle_maxlength_check eq 1){

			# The page title given is too long, so return an error.

			kiriwrite_error("pagetitletoolong");

		}

		if ($pagedescription_maxlength_check eq 1){

			# The page description given is too long, so return an error.

			kiriwrite_error("pagedescriptiontoolong");

		}

		if ($pagesection_maxlength_check eq 1){

			# The page section given is too long, so return an error.

			kiriwrite_error("pagesectiontoolong");

		}

		if ($pagedatabase_maxlength_check eq 1){

			# The page database given is too long, so return an error.

			kiriwrite_error("pagedatabasefilenametoolong");

		}

		if ($pagesettings_maxlength_check eq 1){

			# The page settings given is too long, so return an error.

			kiriwrite_error("pagesettingstoolong");

		}

		if ($pagetemplate_maxlength_check eq 1){

			# The page template given is too long, so return an error.

			kiriwrite_error("pagetemplatefilenametoolong");

		}

		# The action to create a new page has been confirmed, so add the page to the
		# selected database.

		if (!$pagefilename){
			kiriwrite_error("pagefilenameblank");
		}

		# Check the page filename and page settings.

		my $pagefilename_filename_check = kiriwrite_variablecheck($pagefilename, "page_filename", 0, 1);
		my $pagesettings_setting_check	= kiriwrite_variablecheck($pagesettings, "pagesetting", 0, 1);
		my $pagetemplate_filename_check	= 0;

		if ($pagetemplate ne "!none"){

			# A template is being used so check the filename of the
			# template.

			$pagetemplate_filename_check	= kiriwrite_variablecheck($pagetemplate, "page_filename", 0, 1);

		}

		if ($pagefilename_filename_check ne 0){

			# The page filename given is invalid, so return an error.

			kiriwrite_error("pagefilenameinvalid");

		}

		if ($pagesettings_setting_check eq 1){

			# The page settings given is invalid, so return an error.

			kiriwrite_error("pagesettingsinvalid");

		}

		if ($pagetemplate_filename_check eq 1){

			# The template filename given is invalid, so return an error

			kiriwrite_error("templatefilenameinvalid");

		}

		# Check if the database has write permissions.

		my $database_permissions = $kiriwrite_dbmodule->dbpermissions($pagedatabase, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Select the database to add the page to.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $pagedatabase });

		# Check if any errors had occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		my %database_info = $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any error occured while getting the database information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		};

		# Add the page to the selected database.

		$kiriwrite_dbmodule->addpage({ PageFilename => $pagefilename, PageName => $pagetitle, PageDescription => $pagedescription, PageSection => $pagesection, PageTemplate => $pagetemplate, PageContent => $pagefiledata, PageSettings => $pagesettings });

		# Check if any errors occured while adding the page.

		if ($kiriwrite_dbmodule->geterror eq "PageExists"){

			# A page with the filename given already exists so
			# return an error.

			kiriwrite_error("pagefilenameexists");

		} elsif ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error
			# with extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		}

		my $database_name = $database_info{"DatabaseName"};

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{addpage}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{pageaddedmessage}, $pagetitle, $database_name));
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $pagedatabase, { Text => kiriwrite_language($kiriwrite_lang->{pages}->{returnpagelist}, $database_name) });

		return $kiriwrite_presmodule->grab();

	} elsif ($confirm eq 0) {

		# The action to create a new page has not been confirmed, so print out a form
		# for adding a page to a database.

		my %template_list;
		my %template_info;
		my @templates_list;
		my %database_info;
		my $template_filename;
		my $template_name;
		my $template_data = "";
		my $template_warningmessage;
		my $template_warning = 0;
		my $template_count = 0;
		my $template;

		tie(%template_list, 'Tie::IxHash');

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $pagedatabase });

		# Check if any errors had occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Check if the database has write permissions.

		my $database_permissions = $kiriwrite_dbmodule->dbpermissions($pagedatabase, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		%database_info = $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any error occured while getting the database information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		};

		# Connect to the template database.

		$kiriwrite_dbmodule->connecttemplate();

		# Check if any errors occured while connecting to the template database.

		if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseDoesNotExist"){

			# The template database does not exist so set the template
			# warning message.

			$template_warningmessage = $kiriwrite_lang->{pages}->{notemplatedatabase};
 			$template_warning = 1;

		} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so write
			# the template warning message.

 			$template_warningmessage = $kiriwrite_lang->{pages}->{templatepermissionserror};
 			$template_warning = 1;

		}

		if ($template_warning eq 0){

			# Get the list of templates available.

			@templates_list = $kiriwrite_dbmodule->gettemplatelist();

			# Check if any errors had occured.

			if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

				# A database error occured while getting the list
				# of templates so return a warning message with the 
				# extended error information.

				$template_warningmessage = kiriwrite_language($kiriwrite_lang->{pages}->{templatedatabaseerror}, $kiriwrite_dbmodule->geterror(1));
				$template_warning = 1;

			}

			if ($template_warning eq 0){

				# Check to see if there are any templates in the templates
				# list array.

				my $template_filename = "";
				my $template_name = "";

				foreach $template (@templates_list){

					# Get information about the template.

					%template_info = $kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $template });

					# Check if any error occured while getting the template information.

					if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

						# A database error has occured, so return an error.

						kiriwrite_error("templatedatabaseerror", $kiriwrite_dbmodule->geterror(1));

					} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

						# The template does not exist, so process the next template.

						next;

					}

					# Get the template filename and name.

					$template_filename = $template_info{"TemplateFilename"};
					$template_name = $template_info{"TemplateName"};

					$template_list{$template_count}{Filename} = $template_filename;
					$template_list{$template_count}{Name} = $template_name;

					$template_count++;

				}

				# Check if the final template list is blank.

				if (!%template_list){

					# The template list is blank so write the template
					# warning message.

					$template_warningmessage = $kiriwrite_lang->{pages}->{notemplatesavailable};

				}

			}

		}

 		my $database_name 	= $database_info{"DatabaseName"};

		# Disconnect from the template database.

		$kiriwrite_dbmodule->disconnecttemplate();

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# write out the form for adding a page.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{addpage}, { Style => "pageheader" });
		$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");#
		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addhiddendata("mode", "page");
		$kiriwrite_presmodule->addhiddendata("action", "add");
 		$kiriwrite_presmodule->addhiddendata("database", $pagedatabase);
		$kiriwrite_presmodule->addhiddendata("confirm", "1");
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

		$kiriwrite_presmodule->startheader();
		$kiriwrite_presmodule->addcell("tablecellheader");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{setting});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecellheader");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{value});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endheader();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{database});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addtext($database_name);
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagename});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("pagename", { Size => 64, MaxLength => 512 });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagedescription});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("pagedescription", { Size => 64, MaxLength => 512 });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagesection});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("pagesection", { Size => 64, MaxLength => 256 });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagetemplate});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");

		# Check if the template warning value has been set
		# and write the error message in place of the templates
		# list if it is.

		if ($template_warning eq 1){

			$kiriwrite_presmodule->addhiddendata("pagetemplate", "!none");
			$kiriwrite_presmodule->addtext($template_warningmessage);

		} else {

			my $template_file;
			my $page_filename;
			my $page_name;

			$kiriwrite_presmodule->addselectbox("pagetemplate");

			foreach $template_file (keys %template_list){

				$page_filename 	= $template_list{$template_file}{Filename};
				$page_name	= $template_list{$template_file}{Name};
				$kiriwrite_presmodule->addoption($page_name . " (" . $page_filename . ")", { Value => $page_filename });
				$template_count++;

				$template_count = 0;
			}

			$kiriwrite_presmodule->addoption($kiriwrite_lang->{pages}->{usenotemplate}, { Value => "!none", Selected => 1 });
			$kiriwrite_presmodule->endselectbox();

		}

		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagefilename});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("pagefilename", { Size => 64, MaxLength => 256 });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagecontent});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addtextbox("pagecontent", { Columns => 50, Rows => 10 });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->startbox("datalist");
		$kiriwrite_presmodule->addboldtext($kiriwrite_lang->{common}->{tags});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagetitle});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagename});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagedescription});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagesection});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pageautosection});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pageautotitle});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagesettings});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addradiobox("pagesettings", { Description => $kiriwrite_lang->{pages}->{usepageandsection}, Value => "1", Selected => 1, LineBreak => 1});
		$kiriwrite_presmodule->addradiobox("pagesettings", { Description => $kiriwrite_lang->{pages}->{usepagename}, Value => "2", Selected => 0, LineBreak => 1});
		$kiriwrite_presmodule->addradiobox("pagesettings", { Description => $kiriwrite_lang->{pages}->{usesectionname}, Value => "3", Selected => 0, LineBreak => 1});
		$kiriwrite_presmodule->addradiobox("pagesettings", { Description => $kiriwrite_lang->{pages}->{nopagesection}, Value => "0", Selected => 0, LineBreak => 1});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->endtable();

		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{pages}->{addpagebutton});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addreset($kiriwrite_lang->{common}->{clearvalues});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $pagedatabase, { Text => kiriwrite_language($kiriwrite_lang->{pages}->{returnpagelist}, $database_name) });
		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endform();


		return $kiriwrite_presmodule->grab();

	} else {

		# The confirm value is something else than '1' or '0' so
		# return an error.

		kiriwrite_error("invalidvalue");

	}



}

sub kiriwrite_page_delete{
#################################################################################
# kiriwrite_page_delete: Deletes a (single) page from a database.		#
#										#
# Usage:									#
#										#
# kiriwrite_page_delete(database, page, [confirm]);				#
#										#
# database	Specifies the database to delete from.				#
# page		Specifies the page to delete.					#
# confirm	Confirms the action to delete the page.				#
#################################################################################

	my ($database, $page, $confirm) = @_;

	# Check if the database filename is valid and return an error if
	# it isn't.

	my $pagedatabase_filename_check = kiriwrite_variablecheck($database, "filename", 0, 1);

	if ($pagedatabase_filename_check eq 1){

		# The database filename is blank, so return an error.

		kiriwrite_error("blankdatabasepageadd");

	} elsif ($pagedatabase_filename_check eq 2){

		# The database filename is invalid, so return an error.

		kiriwrite_error("databasefilenameinvalid");

	}

	# Check the length the database name and return an error if it's
	# too long.

	my $pagedatabase_length_check 	= kiriwrite_variablecheck($database, "maxlength", 32, 1);

	if ($pagedatabase_length_check eq 1){

		# The database name is too long, so return an error.

		kiriwrite_error("databasefilenametoolong");

	}

	# Check if the page name is specified is blank and return an error if
	# it is.

	if (!$page){

		# The page name is blank, so return an error.

		kiriwrite_error("blankfilename");

	}

	# If the confirm value is blank, then set the confirm value to 0.

	if (!$confirm){

		$confirm = 0;

	}

	if ($confirm eq 1){

		# The action to delete the selected page from the database
		# has been confirmed.

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Select the database to delete the page from.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors had occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Check if the database has write permissions.

		my $database_permissions = $kiriwrite_dbmodule->dbpermissions($database, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get the information about the database.

		my %database_info = $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any error occured while getting the database information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Get the information about the page that is going to be deleted.

		my %page_info = $kiriwrite_dbmodule->getpageinfo({ PageFilename => $page });

		# Check if any errors occured while getting the page information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

			# The page does not exist, so return an error.

			kiriwrite_error("pagefilenamedoesnotexist");

		}

		# Delete the page from the database.

		$kiriwrite_dbmodule->deletepage({ PageFilename => $page });

		# Check if any errors occured while deleting the page from the database.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

			# The page does not exist, so return an error.

			kiriwrite_error("pagefilenamedoesnotexist");

		}

		# Get the database name and page name.

		my $database_name 	= $database_info{"DatabaseName"};
		my $page_name		= $page_info{"PageName"};

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# Write out a message saying that the selected page from
		# the database has been deleted.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagedeleted}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{pagedeletedmessage}, $page_name, $database_name));
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($kiriwrite_lang->{pages}->{returnpagelist}, $database_name)});

		return $kiriwrite_presmodule->grab();

	} elsif ($confirm eq 0){

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors had occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		my %database_info = $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors occured while getting the database information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Get information about the page that is going to be deleted.

		my %page_info = $kiriwrite_dbmodule->getpageinfo({ PageFilename => $page });

		# Check if any errors occured while getting the page information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

			# The page does not exist, so return an error.

			kiriwrite_error("pagefilenamedoesnotexist");

		}

		my $database_name 	= $database_info{"DatabaseName"};
		my $page_name		= $page_info{"PageName"};

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# Write a message asking the user to confirm the deletion of the
		# page.

		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{deletepage}, $page_name), { Style => "pageheader" });
		$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addhiddendata("mode", "page");
		$kiriwrite_presmodule->addhiddendata("action", "delete");
		$kiriwrite_presmodule->addhiddendata("database", $database);
		$kiriwrite_presmodule->addhiddendata("page", $page);
		$kiriwrite_presmodule->addhiddendata("confirm", "1");
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{deletepagemessage}, $page_name, $database_name));
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{pages}->{deletepagebutton});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($kiriwrite_lang->{pages}->{deletepagesreturnlink}, $database_name)});
		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endform();

		return $kiriwrite_presmodule->grab();

	} else {

		# Another page deletion type was specified, so return an error.

		kiriwrite_error("invalidoption");

	}

}

sub kiriwrite_page_edit{
#################################################################################
# kiriwrite_page_edit: Edits a page from a database.				#
#										#
# Usage:									#
#										#
# kiriwrite_page_edit(database, filename, newfilename, newname, newdescription, #
#			newsection, newtemplate,  newsettings, newpagecontent	#
#			confirm);						#
#										#
# database	 Specifies the database to edit from.				#
# filename	 Specifies the filename to use.					#
# newfilename	 Specifies the new page filename to use.			#
# newname	 Specifies the new page name to use.				#
# newdescription Specifies the new description for the page.			#
# newsection	 Specifies the new section name to use.				#
# newtemplate	 Specifies the new template filename to use.			#
# newsettings	 Specifies the new page settings to use.			#
# newpagecontent Specifies the new page content to use.				#
# confirm	 Confirms the action to edit the page.				#
#################################################################################

	# Get the values that have been passed to the subroutine.

	my ($database, $pagefilename, $pagenewfilename, $pagenewtitle, $pagenewdescription, $pagenewsection, $pagenewtemplate, $pagenewsettings, $pagenewcontent, $confirm) = @_;

	# Check if the confirm value is blank and if it is, then set it to '0'.

	if (!$confirm){

		$confirm = 0;

	}

	# Check if the confirm value is more than one character long and if it
	# is then return an error.

	kiriwrite_variablecheck($confirm, "maxlength", 1, 0);

	# Check if the database filename is valid and return an error if
	# it isn't.

	my $pagedatabase_filename_check = kiriwrite_variablecheck($database, "filename", 0, 1);

	if ($pagedatabase_filename_check eq 1){

		# The database filename is blank, so return an error.

		kiriwrite_error("blankdatabasepageadd");

	} elsif ($pagedatabase_filename_check eq 2){

		# The database filename is invalid, so return an error.

		kiriwrite_error("databasefilenameinvalid");

	}

	# Check the length the database name and return an error if it's
	# too long.

	my $pagedatabase_length_check 	= kiriwrite_variablecheck($database, "maxlength", 32, 1);

	if ($pagedatabase_length_check eq 1){

		# The database name is too long, so return an error.

		kiriwrite_error("databasefilenametoolong");

	}

	# Check if the page identification number is blank (which it shouldn't
	# be) and if it is, then return an error.

	if (!$pagefilename){

		kiriwrite_error("blankfilename");

	}

	# Check if the confirm value is '1' and if it is, edit the specified
	# page in the database.

	if ($confirm eq 1){

		# Check if the new page filename is blank.

		if (!$pagenewfilename){

			# The page filename is blank so return an error.

			kiriwrite_error("pagefilenameblank");

		}

		# The action to edit a page has been confirmed so check the
		# variables recieved are UTF8 compiliant before converting.

		kiriwrite_variablecheck($database, "utf8", 0, 0);
		kiriwrite_variablecheck($pagefilename, "utf8", 0, 0);
		kiriwrite_variablecheck($pagenewfilename, "utf8", 0, 0);
		kiriwrite_variablecheck($pagenewtitle, "utf8", 0, 0);
		kiriwrite_variablecheck($pagenewdescription, "utf8", 0, 0);
		kiriwrite_variablecheck($pagenewsection, "utf8", 0, 0);
		kiriwrite_variablecheck($pagenewsettings, "utf8", 0, 0);
		kiriwrite_variablecheck($pagenewtemplate, "utf8", 0, 0);
		kiriwrite_variablecheck($pagenewcontent, "utf8", 0, 0);

		# Convert the variables into proper UTF8 variables.

		$database		= kiriwrite_utf8convert($database);
		$pagefilename 		= kiriwrite_utf8convert($pagefilename);
		$pagenewfilename	= kiriwrite_utf8convert($pagenewfilename);
		$pagenewtitle		= kiriwrite_utf8convert($pagenewtitle);
		$pagenewdescription	= kiriwrite_utf8convert($pagenewdescription);
		$pagenewsection		= kiriwrite_utf8convert($pagenewsection);
		$pagenewsettings	= kiriwrite_utf8convert($pagenewsettings);
		$pagenewtemplate	= kiriwrite_utf8convert($pagenewtemplate);
		$pagenewcontent		= kiriwrite_utf8convert($pagenewcontent);

		# Check the lengths of the variables.

		my $pagenewfilename_maxlength_check	= kiriwrite_variablecheck($pagenewfilename, "maxlength", 256, 1);
		my $pagenewtitle_maxlength_check	= kiriwrite_variablecheck($pagenewtitle, "maxlength", 512, 1);
		my $pagenewdescription_maxlength_check	= kiriwrite_variablecheck($pagenewdescription, "maxlength", 512, 1);
		my $pagenewsection_maxlength_check	= kiriwrite_variablecheck($pagenewsection, "maxlength", 256, 1);
		my $pagenewsettings_maxlength_check	= kiriwrite_variablecheck($pagenewsettings, "maxlength", 1, 1);
		my $pagenewtemplate_maxlength_check	= kiriwrite_variablecheck($pagenewtemplate, "maxlength", 64, 1);

		# Check each result to see if the length of the variable
		# is valid and return an error if it isn't.

		if ($pagenewfilename_maxlength_check eq 1){

			# The new page filename given is too long, so return an error.

			kiriwrite_error("pagefilenametoolong");

		}

		if ($pagenewtitle_maxlength_check eq 1){

			# The new page title given is too long, so return an error.

			kiriwrite_error("pagetitletoolong");

		}

		if ($pagenewdescription_maxlength_check eq 1){

			# The new page description given is too long, so return an error.

			kiriwrite_error("pagedescriptiontoolong");

		}

		if ($pagenewsection_maxlength_check eq 1){

			# The new page section given is too long, so return an error.

			kiriwrite_error("pagesectiontoolong");

		}

		if ($pagenewsettings_maxlength_check eq 1){

			# The new page settings given is too long, so return an error.

			kiriwrite_error("pagesettingstoolong");

		}

		if ($pagenewtemplate_maxlength_check eq 1){

			# The new page template given is too long, so return an error.

			kiriwrite_error("pagetemplatefilenametoolong");

		}

		# Check if the new page filename and new page settings
		# are valid.

		my $pagenewfilename_filename_check	= kiriwrite_variablecheck($pagenewfilename, "page_filename", 0, 1);
		my $pagenewsettings_settings_check	= kiriwrite_variablecheck($pagenewsettings, "pagesetting", 0, 1);
		my $pagetemplate_filename_check	= 0;

		if ($pagenewtemplate ne "!none"){

			# A template is being used so check the filename of the
			# template.

			$pagetemplate_filename_check	= kiriwrite_variablecheck($pagenewtemplate, "page_filename", 0, 1);

		}

		# Check each result to see if the variables have passed
		# their tests and return an error if they haven't.

		if ($pagenewfilename_filename_check ne 0){

			# The new page filename is invalid, so return an error.

			kiriwrite_error("pagefilenameinvalid");

		}

		if ($pagenewsettings_settings_check eq 1){

			# The new page settings is invalid, so return an error.

			kiriwrite_error("pagesettingsinvalid");

		}

		if ($pagetemplate_filename_check eq 1){

			# The template filename given is invalid, so return an error

			kiriwrite_error("templatefilenameinvalid");

		}

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors had occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Check if the database has write permissions.

		my $database_permissions = $kiriwrite_dbmodule->dbpermissions($database, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get the database information.

		my %database_info = $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		};

		my $database_name = $database_info{"DatabaseName"};

		# Edit the selected page.

		$kiriwrite_dbmodule->editpage({ PageFilename => $pagefilename, PageNewFilename => $pagenewfilename, PageNewName => $pagenewtitle, PageNewDescription => $pagenewdescription, PageNewSection => $pagenewsection, PageNewTemplate => $pagenewtemplate, PageNewContent => $pagenewcontent, PageNewSettings => $pagenewsettings });

		# Check if any errors occured while editing the page.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

			# The pages does not exist in the database.

			kiriwrite_error("pagefilenamedoesnotexist");

		} elsif ($kiriwrite_dbmodule->geterror eq "PageExists"){

			# A page already exists with the new filename.

			kiriwrite_error("pagefilenameexists");

		}

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{editedpage}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{editedpagemessage}, $pagenewtitle));
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($kiriwrite_lang->{pages}->{returnpagelist}, $database_name) });

		return $kiriwrite_presmodule->grab();

	} elsif ($confirm eq 0) {

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors had occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get the information about the database.

		my %database_info = $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		};

		my $database_name = $database_info{"DatabaseName"};

		# Get the page info.

		my %page_info = $kiriwrite_dbmodule->getpageinfo({ PageFilename => $pagefilename });

		# Check if any errors occured while getting the page information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

			# The page does not exist, so return an error.

			kiriwrite_error("pagefilenamedoesnotexist");

		}

		# Get the values from the hash.

		my $data_filename		= $page_info{"PageFilename"};
		my $data_name			= $page_info{"PageName"};
		my $data_description		= $page_info{"PageDescription"};
		my $data_section		= $page_info{"PageSection"};
		my $data_template		= $page_info{"PageTemplate"};
		my $data_content		= $page_info{"PageContent"};
		my $data_settings		= $page_info{"PageSettings"};
		my $data_lastmodified		= $page_info{"PageLastModified"};

		my $template_warning;
		my $page_count = 0;
		my %template_list;
		my %template_info;
		my @database_pages;
		my @database_info;
		my @database_templates;
		my @template_filenames;
		my $template_file;
		my $template_filename;
		my $template_name;
		my $template_count = 0;
		my $template_found = 0;

		tie(%template_list, 'Tie::IxHash');

		# Connect to the template database.

		$kiriwrite_dbmodule->connecttemplate();

		# Check if any errors occured while connecting to the template database.

		if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseDoesNotExist"){

			# The template database does not exist so set the template
			# warning message.

			$template_warning = $kiriwrite_lang->{pages}->{notemplatedatabasekeep};

		} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so write
			# the template warning message.

 			$template_warning = $kiriwrite_lang->{pages}->{templatepermissionserrorkeep};

		}

		if (!$template_warning){

			# Get the list of available templates.

			@template_filenames = $kiriwrite_dbmodule->gettemplatelist();

			# Check if any errors had occured.

			if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

				# A database error occured while getting the list
				# of templates so return an error with the 
				# extended error information.

				$template_warning = kiriwrite_language($kiriwrite_lang->{pages}->{templatedatabaseerrorkeep} , $kiriwrite_dbmodule->geterror(1));

			}

			if (!$template_warning){

				foreach $template_filename (@template_filenames){

					# Get the information about each template.

					%template_info = $kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $template_filename });

					# Check if any errors occured while getting the template information.

					if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

						# A template database error has occured so return a warning message
						# with the extended error information.

						$template_warning = kiriwrite_language($kiriwrite_lang->{pages}->{templatedatabaseerrorkeep} , $kiriwrite_dbmodule->geterror(1));
						last;

					} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

						# The template does not exist so process the next template.

						next;

					}

					# Append the template name and filename to the list of available templates.

					$template_list{$template_count}{Filename} = $template_info{"TemplateFilename"};
					$template_list{$template_count}{Name}	  = $template_info{"TemplateName"};

					# Append the template filename and name and make it the selected
					# template if that is the template the page is using.

					if ($data_template eq $template_filename && !$template_found){

						$template_list{$template_count}{Selected} 	= 1;
						$template_found = 1;

					} else {

						$template_list{$template_count}{Selected} 	= 0;

					}

					$template_count++;

				}

			}

		}

		# Check if certain values are undefined and if they
		# are then set them blank (defined).

		if (!$data_name){
			$data_name = "";
		}

		if (!$data_description){
			$data_description = "";
		}

		if (!$data_section){
			$data_section = "";
		}

		if (!$data_template){
			$data_template = "";

		}

		if (!$data_content){
			$data_content = "";
		}

		if (!$data_settings){
			$data_settings = "";
		}

		if (!$data_lastmodified){
			$data_lastmodified = "";
		}

		# Begin writing out the form for editing the selected page.

		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{editpage}, $data_name), { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();

		$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addhiddendata("mode", "page");
		$kiriwrite_presmodule->addhiddendata("action", "edit");
		$kiriwrite_presmodule->addhiddendata("database", $database);
		$kiriwrite_presmodule->addhiddendata("page", $pagefilename);
		$kiriwrite_presmodule->addhiddendata("confirm", 1);
		$kiriwrite_presmodule->endbox();

		$kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

		$kiriwrite_presmodule->startheader();
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{setting}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{value}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->endheader();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{database});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addtext($database_name);
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagename});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("pagename", { Size => 64, MaxLength => 256, Value => $data_name });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagedescription});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("pagedescription", { Size => 64, MaxLength => 256, Value => $data_description });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagesection});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("pagesection", { Size => 64, MaxLength => 256, Value => $data_section });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagetemplate});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");

		# Check if any template warnings have occured.

		if ($template_warning){

			$kiriwrite_presmodule->addtext($template_warning);
			$kiriwrite_presmodule->addlinebreak();

		}

		$kiriwrite_presmodule->addselectbox("pagetemplate");

		# Process the list of templates, select one if the
		# template filename for the page matches, else give
		# an option for the user to keep the current template
		# filename.

		$template_count = 0;

		foreach $template_file (keys %template_list){

			if ($template_list{$template_count}{Selected}){

				$kiriwrite_presmodule->addoption($template_list{$template_count}{Name} . " (" . $template_list{$template_count}{Filename} . ")", { Value => $template_list{$template_count}{Filename}, Selected => 1 });

			} else {

				$kiriwrite_presmodule->addoption($template_list{$template_count}{Name} . " (" . $template_list{$template_count}{Filename} . ")", { Value => $template_list{$template_count}{Filename} });

			}

			$template_count++;

		}

		if ($data_template eq "!none"){

			$kiriwrite_presmodule->addoption($kiriwrite_lang->{pages}->{usenotemplate}, { Value => "!none", Selected => 1 });
			$template_found = 1;

		} else {

			$kiriwrite_presmodule->addoption($kiriwrite_lang->{pages}->{usenotemplate}, { Value => "!none" });

		}

		if ($template_found eq 0 && $data_template ne "!none"){

			# The template with the filename given was not found.

			$kiriwrite_presmodule->addoption(kiriwrite_language($kiriwrite_lang->{pages}->{keeptemplatefilename}, $data_template), { Value => $data_template, Selected => 1, Style => "warningoption" });

		}

		# Disconnect from the template database.

		$kiriwrite_dbmodule->disconnecttemplate();

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		$kiriwrite_presmodule->endselectbox();

		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagefilename});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("pagefilename", { Size => 64, MaxLength => 256, Value => $data_filename });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagecontent});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addtextbox("pagecontent", { Columns => 50, Rows => 10, Value => $data_content });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->startbox("datalist");
		$kiriwrite_presmodule->addboldtext($kiriwrite_lang->{common}->{tags});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagetitle});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagename});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagedescription});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagesection});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pageautosection});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pageautotitle});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagesettings});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");

		# Check if the page settings value is set to a 
		# certain number and select that option based
		# on the number else set the value to 0.

		if ($data_settings eq 1){
			$kiriwrite_presmodule->addradiobox("pagesettings", { Description => $kiriwrite_lang->{pages}->{usepageandsection}, Value => "1", Selected => 1, LineBreak => 1});
		} else {
			$kiriwrite_presmodule->addradiobox("pagesettings", { Description => $kiriwrite_lang->{pages}->{usepageandsection}, Value => "1", LineBreak => 1});
		}

		if ($data_settings eq 2){
			$kiriwrite_presmodule->addradiobox("pagesettings", { Description => $kiriwrite_lang->{pages}->{usepagename}, Value => "2", Selected => 1, LineBreak => 1});
		} else {
			$kiriwrite_presmodule->addradiobox("pagesettings", { Description => $kiriwrite_lang->{pages}->{usepagename}, Value => "2", LineBreak => 1});
		}

		if ($data_settings eq 3){
			$kiriwrite_presmodule->addradiobox("pagesettings", { Description => $kiriwrite_lang->{pages}->{usesectionname}, Value => "3", Selected => 1, LineBreak => 1});
		} else {
			$kiriwrite_presmodule->addradiobox("pagesettings", { Description => $kiriwrite_lang->{pages}->{usesectionname}, Value => "3", LineBreak => 1});
		}

		if ($data_settings eq 0 || ($data_settings ne 1 && $data_settings ne 2 && $data_settings ne 3)){
			$kiriwrite_presmodule->addradiobox("pagesettings", { Description => $kiriwrite_lang->{pages}->{nopagesection}, Value => "0", Selected => 1, LineBreak => 1});
		} else {
			$kiriwrite_presmodule->addradiobox("pagesettings", { Description => $kiriwrite_lang->{pages}->{nopagesection}, Value => "0", LineBreak => 1});
		}

		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();
		$kiriwrite_presmodule->endtable();

		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{pages}->{editpagebutton});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addreset($kiriwrite_lang->{common}->{restorecurrent});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($kiriwrite_lang->{pages}->{returnpagelist}, $database_name) } );
		$kiriwrite_presmodule->endbox();

		$kiriwrite_presmodule->endform();

		return $kiriwrite_presmodule->grab();

	} else {

		# The confirm value is a value other than '0' and '1' so
		# return an error.

		kiriwrite_error("invalidvalue");

	}

}

sub kiriwrite_page_multidelete{
#################################################################################
# kiriwrite_page_multidelete: Delete mulitple pages from the database.		#
#										#
# Usage:									#
#										#
# kiriwrite_page_multidelete(database, confirm, filelist);			#
#										#
# database	Specifies the database to delete multiple pages from.		#
# confirm	Confirms the action to delete the selected pages from the	#
#		database.							#
# filelist	The list of files to delete from the selected database.		#
#################################################################################

	# Get the information passed to the subroutine.

	my ($database, $confirm, @filelist) = @_;

	# Check if the database name is blank and return an error if
	# it is.

	if (!$database){

		# The database name is blank so return an error.

		kiriwrite_error("databasenameblank");

	}

	# Check if the file list array has any values and return
	# an error if it doesn't.

	if (!@filelist){

		# The page list really is blank so return
		# an error.

		kiriwrite_error("nopagesselected");
	}

	# Check if the database filename is valid and return an error if
	# it isn't.

	my $pagedatabase_filename_check = kiriwrite_variablecheck($database, "filename", 0, 1);

	if ($pagedatabase_filename_check eq 1){

		# The database filename is blank, so return an error.

		kiriwrite_error("blankdatabasepageadd");

	} elsif ($pagedatabase_filename_check eq 2){

		# The database filename is invalid, so return an error.

		kiriwrite_error("databasefilenameinvalid");

	}

	# Check the length the database name and return an error if it's
	# too long.

	my $pagedatabase_length_check 	= kiriwrite_variablecheck($database, "maxlength", 32, 1);

	if ($pagedatabase_length_check eq 1){

		# The database name is too long, so return an error.

		kiriwrite_error("databasefilenametoolong");

	}

	# Check if the confirm value is blank and if it is, then
	# set it to 0.

	if (!$confirm){

		# The confirm value is blank so set the confirm value
		# to 0.

		$confirm = 0;

	}

	if ($confirm eq 1){

		# The action to delete multiple pages from the database has
		# been confirmed.

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Check if the database has read and write permissions.

		my $database_permissions = $kiriwrite_dbmodule->dbpermissions($database, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		my %database_info = $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		};

		my $database_name	= $database_info{"DatabaseName"};

		# Define some variables for later.

		my @database_page;
		my %page_info;
		my $filelist_filename;
		my %deleted_list;
		my $page;
		my $page_name;
		my $page_found = 0;
		my $page_count = 0;

		tie (%deleted_list, 'Tie::IxHash');

		my $deleted_list = "";

		foreach $filelist_filename (@filelist){

			# Get the page information.

			%page_info = $kiriwrite_dbmodule->getpageinfo({ PageFilename => $filelist_filename });

			# Check if any errors occured.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

			} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page does not exist, so process the next page.

				next;

			}

			# Add the page to the list of deleted pages.

			$deleted_list{$page_count}{Filename}	= $page_info{"PageFilename"};
			$deleted_list{$page_count}{Name}	= $page_info{"PageName"};

			# Delete the page.

			$kiriwrite_dbmodule->deletepage({ PageFilename => $filelist_filename });

			# Check if any errors occured while deleting the page from the database.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

			} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page does not exist, so process the next page.

				next;

			}

			$page_found = 0;
			$page_count++;

		}

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{selectedpagesdeleted}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{selectedpagesdeletedmessage}, $database_name));
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->startbox("datalist");

		foreach $page (keys %deleted_list){

			if (!$deleted_list{$page}{Name}){
				$kiriwrite_presmodule->additalictext($kiriwrite_lang->{blank}->{noname});
				$kiriwrite_presmodule->addtext(" (" . $deleted_list{$page}{Filename} . ")");

			} else {
				$kiriwrite_presmodule->addtext($deleted_list{$page}{Name} . " (" . $deleted_list{$page}{Filename} . ")");
			}

			$kiriwrite_presmodule->addlinebreak();
		}

		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($kiriwrite_lang->{pages}->{returnpagelist}, $database_name)});

		return $kiriwrite_presmodule->grab();

	} elsif ($confirm eq 0){

		# The action to delete multiple pages from the database has
		# not been confirmed, so write a form asking the user to confirm
		# the deletion of those pages.

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Check if the database has read and write permissions.

		my $database_permissions = $kiriwrite_dbmodule->dbpermissions($database, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		my %database_info = $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		};

 		my $database_name	= $database_info{"DatabaseName"};

		# Define some variables for later.

		my %page_info;
		my %delete_list;
		my $pagename;
		my $page = "";
		my $filelist_filename;
		my $filelist_filename_sql;
		my $pageseek = 0;

		tie(%delete_list, 'Tie::IxHash');

		# Process each filename given.

		foreach $filelist_filename (@filelist){

			# Get the page information.

			%page_info = $kiriwrite_dbmodule->getpageinfo({ PageFilename => $filelist_filename });

			# Check if any errors occured.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

			} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page does not exist, so process the next page.

				next;

			}

			# Add the page file name and name to the list
			# of pages to delete.

			$delete_list{$pageseek}{Filename}	= $page_info{"PageFilename"};
			$delete_list{$pageseek}{Name}		= $page_info{"PageName"};

			# Increment the page seek counter and reset the
			# page found value.

			$pageseek++;

		}

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# Check if any files were selected and return
		# an error if there wasn't.

		if ($pageseek eq 0){

			# No pages were selected so return an error.

			kiriwrite_error("nopagesselected");

		}

		# Write the form for displaying pages.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{deletemultiplepages}, { Style => "pageheader" });
		$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addhiddendata("mode", "page");
		$kiriwrite_presmodule->addhiddendata("action", "multidelete");
		$kiriwrite_presmodule->addhiddendata("database", $database);
		$kiriwrite_presmodule->addhiddendata("confirm", "1");
		$kiriwrite_presmodule->addhiddendata("count", $pageseek);

		$pageseek = 1;

		foreach $page (keys %delete_list){

			$kiriwrite_presmodule->addhiddendata("name[" . $pageseek . "]", "on");
			$kiriwrite_presmodule->addhiddendata("id[" . $pageseek . "]", $delete_list{$page}{Filename});

			$pageseek++;

		}

		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{deletemultiplemessage}, $database_name));
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->startbox("datalist");

		foreach $page (keys %delete_list){

			if (!$delete_list{$page}{Name}){
				$kiriwrite_presmodule->additalictext($kiriwrite_lang->{blank}->{noname});
				$kiriwrite_presmodule->addtext(" (" . $delete_list{$page}{Filename} . ")");
			} else {
				$kiriwrite_presmodule->addtext($delete_list{$page}{Name} . " (" . $delete_list{$page}{Filename} . ")");
			}
			$kiriwrite_presmodule->addlinebreak();

		}

		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{pages}->{deletepagesbutton});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($kiriwrite_lang->{pages}->{deletepagesreturnlink}, $database_name)});
		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endform();

		return $kiriwrite_presmodule->grab();

	} else {

		# A confirm value other than 0 or 1 is given, so
		# return an error.

		kiriwrite_error("invaildvalue");

	}

}

sub kiriwrite_page_multimove{
#################################################################################
# kiriwrite_page_multimove: Move several pages from one database to another	#
# database.									#
#										#
# Usage:									#
# 										#
# kiriwrite_page_multimove(database, newdatabase, confirm, filelist);		#
#										#
# database	Specifies the database to move the selected pages from.		#
# newdatabase	Specifies the database to move the selected pages to.		#
# confirm	Confirms the action to move the pages from one database to	#
#		another.							#
# filelist	Specifies the list of pages to move.				#
#################################################################################

	# Get the values that were passed to the subroutine.

	my ($database, $newdatabase, $confirm, @filelist) = @_;

	# Check if the database filename is valid and return
	# an error if it isn't.

	my $newpagedatabase_filename_check = kiriwrite_variablecheck($database, "filename", 0, 1);

	if ($newpagedatabase_filename_check eq 1){

		# The database filename is blank, so return an error.

		kiriwrite_error("blankdatabasepageadd");

	} elsif ($newpagedatabase_filename_check eq 2){

		# The database filename is invalid, so return an error.

		kiriwrite_error("databasefilenameinvalid");

	}

	# Check if the file list is blank and return an error
	# if it is.

	if (!@filelist){

		# The file list really is blank so return
		# an error.

		kiriwrite_error("nopagesselected");

	}

	# Check if the confirm value is blank and if it is then
	# set the confirm value to 0.

	if (!$confirm){

		$confirm = 0;

	}

	if ($confirm eq 1){

		# The action to move several pages from one database
		# to another has been confirmed.

		# Check if the database that the pages are moving from 
		# is the same as the database the pages are moving to.
		# Return an error if it is.

		if ($database eq $newdatabase){

			# The database that the pages are moving from
			# and the database the pages are moving to
			# is the same, so return an error.

			kiriwrite_error("databasemovesame");

		}

		# Check if the new database filename is valid and return an error if
		# it isn't.

		my $newpagedatabase_filename_check = kiriwrite_variablecheck($newdatabase, "filename", 0, 1);

		if ($newpagedatabase_filename_check eq 1){

			# The database filename is blank, so return an error.

			kiriwrite_error("blankdatabasepageadd");

		} elsif ($newpagedatabase_filename_check eq 2){

			# The database filename is invalid, so return an error.

			kiriwrite_error("databasefilenameinvalid");

		}

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Select the database the pages are going to be moved from.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors had occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("oldmovedatabasedoesnotexist");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("oldmovedatabasefileinvalidpermissions");

		}

		# Check if the database has read and write permissions.

		my $database_permissions = $kiriwrite_dbmodule->dbpermissions($database, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Select the database the pages are going to be moved to.

		$kiriwrite_dbmodule->selectseconddb({ DatabaseName => $newdatabase });

		# Check if any errors had occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("newmovedatabasedoesnotexist");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("newmovedatabasefileinvalidpermissions");

		}

		# Check if the database has read and write permissions.

		$database_permissions = $kiriwrite_dbmodule->dbpermissions($newdatabase, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Define some values for later.

		my %moved_list;
		my %warning_list;
		my %page_info;

		my $filename;

		my $olddatabase_name;
		my $newdatabase_name;

		my $page;
		my $warning;

		my $page_found = 0;
		my $move_count = 0;
		my $warning_count = 0;

		tie(%moved_list, 'Tie::IxHash');
		tie(%warning_list, 'Tie::IxHash');

		# Get information about the database that the selected pages are moving from.

		my %olddatabase_info = $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("oldmovedatabasedatabaseerror", $kiriwrite_dbmodule->geterror(1));

		};

		$olddatabase_name = $olddatabase_info{"DatabaseName"};

		# Get information about the database that the selected pages are moving to.

		my %newdatabase_info = $kiriwrite_dbmodule->getseconddatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("newmovedatabasedatabaseerror", $kiriwrite_dbmodule->geterror(1));

		};

		$newdatabase_name = $newdatabase_info{"DatabaseName"};

		# Get each file in the old database, get the page values,
		# put them into the new database and delete the pages
		# from the old database.

		foreach $filename (@filelist){

			# Get the page information.

			%page_info = $kiriwrite_dbmodule->getpageinfo({ PageFilename => $filename });

			# Check if any errors occured.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so write a warning message and
				# also the extended error information.

				$warning_list{$warning_count}{Message} = kiriwrite_language($kiriwrite_lang->{pages}->{databasepageerror}, $filename, $kiriwrite_dbmodule->geterror(1));
				$warning_count++;
				next;

			} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page does not exist, so process the next page.

				$warning_list{$warning_count}{Message} = kiriwrite_language($kiriwrite_lang->{pages}->{pagedoesnotexist}, $filename);
				$warning_count++;
				next;

			}

			# Move the selected page.

			$kiriwrite_dbmodule->movepage({ PageFilename => $filename });

			# Check if any errors occured while moving the page.

			if ($kiriwrite_dbmodule->geterror eq "OldDatabaseError"){

				# A database error has occured while moving the pages from
				# the old database, so write a warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($kiriwrite_lang->{pages}->{databasemovefrompageerror}, $filename, $kiriwrite_dbmodule->geterror(1));
				$warning_count++;
				next;

			} elsif ($kiriwrite_dbmodule->geterror eq "NewDatabaseError"){

				# A database error has occured while moving the pages to
				# the new database, so write a warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($kiriwrite_lang->{pages}->{databasemovetopageerror}, $filename, $kiriwrite_dbmodule->geterror(1));
				$warning_count++;
				next;

			} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page with the filename given in the database that
				# the page is to be moved from doesn't exist so write
				# a warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($kiriwrite_lang->{pages}->{databasemovefrompagenotexist}, $filename);
				$warning_count++;
				next;

			} elsif ($kiriwrite_dbmodule->geterror eq "PageAlreadyExists"){

				# The page with the filename given in the database that
				# the page is to be moved to already exists so write a
				# warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($kiriwrite_lang->{pages}->{databasemovetopageexists}, $filename);
				$warning_count++;
				next;

			}

			$moved_list{$move_count}{Filename} 	= $page_info{"PageFilename"};
			$moved_list{$move_count}{Name} 		= $page_info{"PageName"};

			$move_count++;

		}

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# Write out a message saying that the pages were moved (if any)
		# to the new database (and any warnings given).

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{movepages}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();

		if (%moved_list){

			$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{movedpagesmessage}, $olddatabase_name, $newdatabase_name));
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addlinebreak();

			$kiriwrite_presmodule->startbox("datalist");
			foreach $page (keys %moved_list){
				if (!$moved_list{$page}{Name}){
					$kiriwrite_presmodule->additalictext($kiriwrite_lang->{blank}->{noname});
					$kiriwrite_presmodule->addtext(" (" . $moved_list{$page}{Filename} . ")");
				} else {
					$kiriwrite_presmodule->addtext($moved_list{$page}{Name} . " (" . $moved_list{$page}{Filename} . ")");
				}

				$kiriwrite_presmodule->addlinebreak();
			}
			$kiriwrite_presmodule->endbox();

		} else {

			$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{nopagesmoved}, $olddatabase_name, $newdatabase_name));
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addlinebreak();

		}

		if (%warning_list){

			$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{errormessages});
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->startbox("datalist");
			foreach $warning (keys %warning_list){
				$kiriwrite_presmodule->addtext($warning_list{$warning}{Message});
				$kiriwrite_presmodule->addlinebreak();
			}
			$kiriwrite_presmodule->endbox();

		}

		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($kiriwrite_lang->{pages}->{returnpagelist}, $olddatabase_name)}); 
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $newdatabase, { Text => kiriwrite_language($kiriwrite_lang->{pages}->{viewpagelist}, $newdatabase_name)});

		return $kiriwrite_presmodule->grab();

	} elsif ($confirm eq 0) {

		# The action to move several pages from one database
		# to another has not been confirmed so write a form.

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Check if the database has read and write permissions.

		my $database_permissions = $kiriwrite_dbmodule->dbpermissions($database, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		my %database_info = $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		};

 		my $database_name	= $database_info{"DatabaseName"};

		# Define some values for later.

		my %db_list;
		my %move_list;
		my %page_info;
		my $page;
		my $data_file;
		my $db_name;
		my $filename;
		my $filelist_filename;
		my $pagename;
		my $pageseek	= 0;
		my $dbseek	= 0;

		# Process each filename given.

		tie (%move_list, 'Tie::IxHash');
		tie (%db_list, 'Tie::IxHash');

		foreach $filelist_filename (@filelist){

			# Get the page information.

			%page_info = $kiriwrite_dbmodule->getpageinfo({ PageFilename => $filelist_filename });

			# Check if any errors occured.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

			} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page does not exist, so process the next page.

				next;

			}

			# Add the page name and file name to the list of
			# pages to move.

			$move_list{$pageseek}{Filename}	= $page_info{"PageFilename"};
			$move_list{$pageseek}{Name} 	= $page_info{"PageName"};

			# Increment the page seek counter and reset the
			# page found value.

			$pageseek++;

		}

		# Check if any pages exust and return an error if
		# there wasn't.

		if ($pageseek eq 0){

			# None of the selected pages exist, so return
			# an error.

			kiriwrite_error("nopagesselected");

		}

		# Get the list of databases.

		my @database_list	= $kiriwrite_dbmodule->getdblist();

		# Check if any errors occured while trying to get the list of databases.

 		if ($kiriwrite_dbmodule->geterror eq "DataDirMissing"){

			# The database directory is missing so return an error.

			kiriwrite_error("datadirectorymissing");

		} elsif ($kiriwrite_dbmodule->geterror eq "DataDirInvalidPermissions"){

			# The database directory has invalid permissions set so return
			# an error.

			kiriwrite_error("datadirectoryinvalidpermissions");

		}

		# Get the information about each database (the short name and friendly name).

		foreach $data_file (@database_list){

			$kiriwrite_dbmodule->selectdb({ DatabaseName => $data_file });

			# Check if any errors occured while selecting the database.

			if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

				# The database does not exist, so process the next
				# database.

				next;

			} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

				# The database has invalid permissions set, so process
				# the next database.

				next;

			}

			# Get the database information.

			%database_info = $kiriwrite_dbmodule->getdatabaseinfo();

			# Check if any errors had occured while getting the database
			# information.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so process the next
				# database.

				next;

			};

			# Check if the database name is undefined and if it is
			# then set it blank.

			if (!$database_name){
				$database_name = "";
			}

			# Append the database to the list of databases available.

 			$db_list{$dbseek}{Filename}	= $data_file;
 			$db_list{$dbseek}{Name}		= $database_info{"DatabaseName"};

			$dbseek++;

		}

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# Write out the form.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{movepages}, { Style => "pageheader" });
		$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addhiddendata("mode", "page");
		$kiriwrite_presmodule->addhiddendata("action", "multimove");
		$kiriwrite_presmodule->addhiddendata("database", $database);
		$kiriwrite_presmodule->addhiddendata("count", $pageseek);
		$kiriwrite_presmodule->addhiddendata("confirm", "1");

		# Write the page form data.

		$pageseek = 1;

		foreach $page (keys %move_list){
			$kiriwrite_presmodule->addhiddendata("name[" . $pageseek . "]", "on");
			$kiriwrite_presmodule->addhiddendata("id[" . $pageseek . "]", $move_list{$page}{Filename});
			$pageseek++;
		}

		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{movepagesmessage}, $database_name));
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->startbox("datalist");

		foreach $page (keys %move_list){
			if (!$move_list{$page}{Name}){
				$kiriwrite_presmodule->additalictext($kiriwrite_lang->{blank}->{noname});
				$kiriwrite_presmodule->addtext(" (" . $move_list{$page}{Filename} . ")");
			} else {
				$kiriwrite_presmodule->addtext($move_list{$page}{Name} . " (" . $move_list{$page}{Filename} . ")");
			}
			$kiriwrite_presmodule->addlinebreak();
		}

		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{movepagesto});

		$kiriwrite_presmodule->addselectbox("newdatabase");

		foreach $db_name (keys %db_list){
			$kiriwrite_presmodule->addoption($db_list{$db_name}{Name} . " (" . $db_list{$db_name}{Filename} . ")", { Value => $db_list{$db_name}{Filename}});
		}

		$kiriwrite_presmodule->endselectbox();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{pages}->{movepagesbutton});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($kiriwrite_lang->{pages}->{returnpagelist}, $database_name)});
		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endform();

		return $kiriwrite_presmodule->grab();

	} else {

		# The confirm value is other than 0 or 1, so return
		# an error.

		kiriwrite_error("invalidvariable");

	}


}


sub kiriwrite_page_multicopy{
#################################################################################
# kiriwrite_page_multicopy: Copy several pages from one database to another	#
# database.									#
#										#
# Usage:									#
#										#
# kiriwrite_page_multicopy(database, newdatabase, confirm, filelist);		#
# 										#
# database	Specifies the database to copy the selected pages from.		#
# newdatabase	Specifies the database to copy the selected page to.		#
# confirm	Confirms the action to copy the pages.				#
# filelist	A list of filenames to copy in an array.			#
#################################################################################

	# Get the values that were passed to the subroutine.

	my ($database, $newdatabase, $confirm, @filelist) = @_;

	# Check if the file list is blank and return an error
	# if it is.

	if (!@filelist){

		# The file list really is blank so return
		# an error.

		kiriwrite_error("nopagesselected");

	}

	# Check if the confirm value is blank and if it is then
	# set the confirm value to 0.

	if (!$confirm){

		$confirm = 0;

	}

	# Check if the database filename is valid and return an error if
	# it isn't.

	my $pagedatabase_filename_check = kiriwrite_variablecheck($database, "filename", 0, 1);

	if ($pagedatabase_filename_check eq 1){

		# The database filename is blank, so return an error.

		kiriwrite_error("blankdatabasepageadd");

	} elsif ($pagedatabase_filename_check eq 2){

		# The database filename is invalid, so return an error.

		kiriwrite_error("databasefilenameinvalid");

	}

	if ($confirm eq 1){

		# The action to copy several pages from one database
		# to another has been confirmed.

		# Check if the database that the pages are copied from 
		# is the same as the database the pages are copied to.
		# Return an error if it is.

		if ($database eq $newdatabase){

			# The database that the pages are being copied from
			# and the database that the pages are copied to
			# is the same, so return an error.

			kiriwrite_error("databasecopysame");

		}

		# Check if the new database filename is valid and return an error if
		# it isn't.

		my $pagedatabase_filename_check = kiriwrite_variablecheck($newdatabase, "filename", 0, 1);

		if ($pagedatabase_filename_check eq 1){

			# The database filename is blank, so return an error.

			kiriwrite_error("blankdatabasepageadd");

		} elsif ($pagedatabase_filename_check eq 2){

			# The database filename is invalid, so return an error.

			kiriwrite_error("databasefilenameinvalid");

		}

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Select the database the pages are going to be copied from.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors had occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("oldcopydatabasedoesnotexist");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("oldcopydatabasefileinvalidpermissions");

		}

		# Select the database the pages are going to be copied to.

		$kiriwrite_dbmodule->selectseconddb({ DatabaseName => $newdatabase });

		# Check if any errors had occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("newcopydatabasedoesnotexist");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("newcopydatabasefileinvalidpermissions");

		}

		# Check if the database has read and write permissions.

		my $database_permissions = $kiriwrite_dbmodule->dbpermissions($newdatabase, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Define some values for later.

		my %copied_list;
		my %warning_list;
		my %page_info;

		my @olddatabase_info;
		my @olddatabase_page;
		my @newdatabase_info;
		my @newdatabase_page;

		my $filename;

		my $olddatabase_name;
		my $newdatabase_name;

		my $page;
		my $warning;
		my $page_filename;
		my $page_name;
		my $page_description;
		my $page_section;
		my $page_template;
		my $page_data;
		my $page_settings;
		my $page_lastmodified;

		my $page_seek = 0;
		my $warning_count = 0;

		my $page_found = 0;

		tie(%copied_list, 'Tie::IxHash');
		tie(%warning_list, 'Tie::IxHash');

		# Get information about the database that the selected pages are moving from.

		my %olddatabase_info = $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("oldcopydatabasedatabaseerror", $kiriwrite_dbmodule->geterror(1));

		};

		$olddatabase_name = $olddatabase_info{"DatabaseName"};

		# Get information about the database that the selected pages are moving to.

		my %newdatabase_info = $kiriwrite_dbmodule->getseconddatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("newcopydatabasedatabaseerror", $kiriwrite_dbmodule->geterror(1));

		};

		$newdatabase_name = $newdatabase_info{"DatabaseName"};

		# Check if the database filename is valid and return an error if
		# it isn't.

		my $newpagedatabase_filename_check = kiriwrite_variablecheck($newdatabase, "filename", 0, 1);

		if ($newpagedatabase_filename_check eq 1){

			# The database filename is blank, so return an error.

			kiriwrite_error("blankdatabasepageadd");

		} elsif ($newpagedatabase_filename_check eq 2){

			# The database filename is invalid, so return an error.

			kiriwrite_error("databasefilenameinvalid");

		}

		foreach $filename (@filelist){

			# Get the page information.

			%page_info = $kiriwrite_dbmodule->getpageinfo({ PageFilename => $filename });

			# Check if any errors occured.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				$warning_list{$warning_count}{Message} = kiriwrite_language($kiriwrite_lang->{pages}->{databasepageerror}, $filename, $kiriwrite_dbmodule->geterror(1));
				$warning_count++;
				next;

			} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page does not exist, so process the next page.

				$warning_list{$warning_count}{Message} = kiriwrite_language($kiriwrite_lang->{pages}->{databasecopyfrompageerror}, $filename);
				$warning_count++;
				next;

			}

			$kiriwrite_dbmodule->copypage({ PageFilename => $filename });

			# Check if any errors occured while copying the page.

			if ($kiriwrite_dbmodule->geterror eq "OldDatabaseError"){

				# A database error has occured while copying the pages from
				# the old database, so write a warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($kiriwrite_lang->{pages}->{databasecopyfromdatabaseerror}, $filename,  $kiriwrite_dbmodule->geterror(1));
				$warning_count++;
				next;

			} elsif ($kiriwrite_dbmodule->geterror eq "NewDatabaseError"){

				# A database error has occured while copying the pages to
				# the new database, so write a warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($kiriwrite_lang->{pages}->{databasecopytodatabaseerror}, $filename, $kiriwrite_dbmodule->geterror(1));
				$warning_count++;
				next;

			} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page with the filename given in the database that
				# the page is to be copied from doesn't exist so write
				# a warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($kiriwrite_lang->{pages}->{databasecopyfrompagenotexist}, $filename);
				$warning_count++;
				next;

			} elsif ($kiriwrite_dbmodule->geterror eq "PageAlreadyExists"){

				# The page with the filename given in the database that
				# the page is to be copied to already exists so write a
				# warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($kiriwrite_lang->{pages}->{databasecopytopageexists}, $filename);
				$warning_count++;
				next;

			}

			# Append the copied page (filename and name) to the list of
			# copied pages.

			$copied_list{$page_seek}{Filename} 	= $filename;
			$copied_list{$page_seek}{Name}		= $page_info{"PageName"};
			$page_seek++;

		}

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# Write out a message saying that the pages were moved (if any)
		# to the new database (and any warnings given).

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{copypages}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();

		if (%copied_list){

			$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{copypagesresultmessage}, $olddatabase_name, $newdatabase_name));
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->startbox("datalist");
			foreach $page (keys %copied_list){
				if (!$copied_list{$page}{Name}){
					$kiriwrite_presmodule->additalictext($kiriwrite_lang->{blank}->{noname});
					$kiriwrite_presmodule->addtext(" (" . $copied_list{$page}{Filename} . ")");
				} else {
					$kiriwrite_presmodule->addtext($copied_list{$page}{Name} . " (" . $copied_list{$page}{Filename} . ")");
				}
				$kiriwrite_presmodule->addlinebreak();
			}
			$kiriwrite_presmodule->endbox();

		} else {

			$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{nopagescopied}, $olddatabase_name, $newdatabase_name));

		}

		if (%warning_list){

			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{copypageswarnings});
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->startbox("datalist");
			foreach $warning (keys %warning_list){
				$kiriwrite_presmodule->addtext($warning_list{$warning}{Message});
							$kiriwrite_presmodule->addlinebreak();
			}
			$kiriwrite_presmodule->endbox();

		}

		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($kiriwrite_lang->{pages}->{returnpagelist}, $olddatabase_name)});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $newdatabase, { Text => kiriwrite_language($kiriwrite_lang->{pages}->{viewpagelist}, $newdatabase_name)});

		return $kiriwrite_presmodule->grab();

	} elsif ($confirm eq 0) {

		# The action to copy several pages from one database
		# to another has not been confirmed so write a form.

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Select the database to copy the pages from.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		my %database_info = $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		};

		my $database_name	= $database_info{"DatabaseName"};

		# Define some values for later.

		my %page_info;
		my %copy_list;
		my %db_list;
		my @page_info;
		my $page;
		my $data_file;
		my $dbname;
		my $filename;
		my $pageseek	= 0;
		my $dbseek	= 0;
		my $pagefound 	= 0;

		tie(%copy_list, 'Tie::IxHash');
		tie(%db_list, 'Tie::IxHash');

		# Process each filename given.

		foreach $filename (@filelist){

			# Get the page information.

			%page_info = $kiriwrite_dbmodule->getpageinfo({ PageFilename => $filename });

			# Check if any errors occured.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

			} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page does not exist, so process the next page.

				next;

			}

			# Add the page name and file name to the list of
			# pages to move.

			$copy_list{$pageseek}{Filename}	= $page_info{"PageFilename"};
			$copy_list{$pageseek}{Name} 	= $page_info{"PageName"};

			# Increment the page seek counter.

 			$pageseek++;

		}

		# Check if any pages exust and return an error if
		# there wasn't.

		if ($pageseek eq 0){

			# None of the selected pages exist, so return
			# an error.

			kiriwrite_error("nopagesselected");

		}

 		# Get the database filenames and names.

		my @database_list	= $kiriwrite_dbmodule->getdblist();

		# Check if any errors occured while trying to get the list of databases.

 		if ($kiriwrite_dbmodule->geterror eq "DataDirMissing"){

			# The database directory is missing so return an error.

			kiriwrite_error("datadirectorymissing");

		} elsif ($kiriwrite_dbmodule->geterror eq "DataDirInvalidPermissions"){

			# The database directory has invalid permissions set so return
			# an error.

			kiriwrite_error("datadirectoryinvalidpermissions");

		}

		# Process each database to get the database name.

		foreach $data_file (@database_list){

			$kiriwrite_dbmodule->selectdb({ DatabaseName => $data_file });

			# Check if any errors occured while selecting the database.

			if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

				# The database does not exist, so process the next
				# database.

				next;

			} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

				# The database has invalid permissions set, so process
				# the next database.

				next;

			}

			# Get the database information.

			%database_info = $kiriwrite_dbmodule->getdatabaseinfo();

			# Check if any errors had occured while getting the database
			# information.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so process the next
				# database.

				next;

			};

			# Check if the database name is undefined and if it is
			# then set it blank.

			if (!$database_name){
				$database_name = "";
			}

			# Append the database filename and name to the list of databases
			# to move the pages to.

			$db_list{$dbseek}{Filename}	= $data_file;
			$db_list{$dbseek}{Name}		= $database_info{"DatabaseName"};

			$dbseek++;

		}

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# Write out the form.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{copypages}, { Style => "pageheader" });
		$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addhiddendata("mode", "page");
		$kiriwrite_presmodule->addhiddendata("action", "multicopy");
		$kiriwrite_presmodule->addhiddendata("database", $database);
		$kiriwrite_presmodule->addhiddendata("count", $pageseek);
		$kiriwrite_presmodule->addhiddendata("confirm", 1);

		$pageseek = 1;

		foreach $page (keys %copy_list){
			$kiriwrite_presmodule->addhiddendata("name[" . $pageseek . "]", "on");
			$kiriwrite_presmodule->addhiddendata("id[" . $pageseek . "]", $copy_list{$page}{Filename});
			$pageseek++;
		}

		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{copypagesmessage}, $database_name));

		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();

		$kiriwrite_presmodule->startbox("datalist");

		foreach $page (keys %copy_list){
			if (!$copy_list{$page}{Name}){
				$kiriwrite_presmodule->additalictext($kiriwrite_lang->{blank}->{noname});
				$kiriwrite_presmodule->addtext(" (" . $copy_list{$page}{Filename} . ")");
			} else {
				$kiriwrite_presmodule->addtext($copy_list{$page}{Name} . " (" . $copy_list{$page}{Filename} . ")");
			}
			$kiriwrite_presmodule->addlinebreak();
		}

		$kiriwrite_presmodule->endbox();

		$kiriwrite_presmodule->addlinebreak();

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{copypagesto});
		$kiriwrite_presmodule->addselectbox("newdatabase");

		foreach $dbname (keys %db_list){
			$kiriwrite_presmodule->addoption($db_list{$dbname}{Name} . " (" . $db_list{$dbname}{Filename} . ")", { Value => $db_list{$dbname}{Filename}});
		}

		$kiriwrite_presmodule->endselectbox();

		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{pages}->{copypagesbutton});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($kiriwrite_lang->{pages}->{returnpagelist}, $database_name) });

		$kiriwrite_presmodule->endbox();		
		$kiriwrite_presmodule->endform();

		return $kiriwrite_presmodule->grab();

	} else {

		# The confirm value is other than 0 or 1, so return
		# an error.

		kiriwrite_error("invalidvariable");

	}

}

sub kiriwrite_page_multiedit{
#################################################################################
# kiriwrite_page_multiedit: Edit several pages from a database.			#
#										#
# Usage:									#
#										#
# kiriwrite_page_multiedit(database, newsection, altersection, newtemplate, 	#
#				altertemplate, newsettings, altersettings	#
#				confirm, filelist);				#
#										#
# database	Specifies the database to edit the pages from.			#
# newsection	Specifies the new section name to use on the selected pages.	#
# altersection	Specifies if the section name should be altered.		#
# newtemplate	Specifies the new template filename to use on the selected	#
#		pages.								#
# altertemplate	Specifies if the template filename should be altered.		#
# newsettings	Specifies the new settings to use on the selected pages.	#
# altersettings	Specifies if the settings should be altered.			#
# confirm	Confirms the action to edit the selected pages.			#
# filelist	The list of file names to edit.					#
#################################################################################

	# Get the values that were passed to the subroutine.

	my ($database, $newsection, $altersection, $newtemplate, $altertemplate, $newsettings, $altersettings, $confirm, @filelist) = @_;

	# Check if the file list is blank and return an error
	# if it is.

	if (!@filelist){

		# The file list really is blank so return
		# an error.

		kiriwrite_error("nopagesselected");

	}

	# Check if certain values are undefined and define them if
	# they are.

	if (!$altersection){

		# The alter section value is blank, so set it to
		# off.

		$altersection 	= "off";

	}

	if (!$altertemplate){

		# The alter template value is blank, so set it to
		# off.

		$altertemplate 	= "off";

	}

	if (!$altersettings){

		# The alter settings value is blank, so set it to
		# off.

		$altersettings 	= "off";

	}

	# Check if the database filename is valid and return an error if
	# it isn't.

	my $pagedatabase_filename_check = kiriwrite_variablecheck($database, "filename", 0, 1);

	if ($pagedatabase_filename_check eq 1){

		# The database filename is blank, so return an error.

		kiriwrite_error("blankdatabasepageadd");

	} elsif ($pagedatabase_filename_check eq 2){

		# The database filename is invalid, so return an error.

		kiriwrite_error("databasefilenameinvalid");

	}

	# Check if the confirm value is blank and if it is then
	# set the confirm value to 0.

	if (!$confirm){

		$confirm = 0;

	}

	if ($confirm eq 1){

		# The action to edit the template has been confirmed so
		# edit the selected pages.

		# Check the values recieved at UTF8 compliant before
		# converting.

		kiriwrite_variablecheck($newsection, "utf8", 0, 0);
		kiriwrite_variablecheck($newtemplate, "utf8", 0, 0);
		kiriwrite_variablecheck($newsettings, "utf8", 0, 0);

		# Convert the values into proper UTF8 values.

		$newsection 	= kiriwrite_utf8convert($newsection);
		$newtemplate	= kiriwrite_utf8convert($newtemplate);
		$newsettings	= kiriwrite_utf8convert($newsettings);

		# Check the length of the variables.

		kiriwrite_variablecheck($altersection, "maxlength", 3, 0);
		kiriwrite_variablecheck($altertemplate, "maxlength", 3, 0);
		kiriwrite_variablecheck($altersettings, "maxlength", 3, 0);
		my $newsection_maxlength_check 	= kiriwrite_variablecheck($newsection, "maxlength", 256, 1);
		my $newtemplate_maxlength_check = kiriwrite_variablecheck($newtemplate, "maxlength", 256, 1);
		my $newtemplate_filename_check	= kiriwrite_variablecheck($newtemplate, "filename", 0, 1);
		my $newsettings_maxlength_check	= kiriwrite_variablecheck($newsettings, "maxlength", 1, 1);
		my $newsettings_settings_check	= kiriwrite_variablecheck($newsettings, "pagesetting", 0, 1);

		# Check the values and return an error if needed.

		if ($newsection_maxlength_check eq 1 && $altersection eq "on"){

			# The new section name is too long, so return an
			# error.

			kiriwrite_error("pagesectiontoolong");

		}

		if ($newtemplate_maxlength_check eq 1 && $altertemplate eq "on"){

			# The new template name is too long, so return an
			# error.

			kiriwrite_error("templatefilenametoolong");

		}

		# Check if the template filename is set to !skip or !none
		# and skip this check if it is.

		if ($newtemplate eq "!skip" || $newtemplate eq "!none"){

			# Skip this check as the template filename is 
			# !skip or !none.

		} else {
			if ($newtemplate_filename_check eq 1 && $altertemplate eq "on" || $newtemplate_filename_check eq 2 && $altertemplate eq "on"){

				# The new template filename is invalid, so return
				# an error.

				kiriwrite_error("templatefilenameinvalid");

			}
		}

		if ($newsettings_maxlength_check eq 1 && $altertemplate eq "on"){

			# The new settings value is too long, so return
			# an error.

			kiriwrite_error("pagesettingstoolong");

		}

		if ($newsettings_settings_check eq 1 && $altersettings eq "on"){

			# The new settings value is invalid, so return
			# an error.

			kiriwrite_error("pagesettingsinvalid");

		}

		# Define some values for later.

		my %database_info;
		my %edited_list;
		my %warning_list;
		my %page_info;
		my $page;
		my $warning;
		my $filename;
		my $page_name;
		my $pagefound = 0;
		my $pageedited = 0;
		my $warning_count = 0;

		tie(%edited_list, 'Tie::IxHash');
		tie(%warning_list, 'Tie::IxHash');

		# Check if the template filename is !skip and
		# set the alter template value to off if it
		# is.

		if ($newtemplate eq "!skip"){

			$altertemplate = "off";

		}

		# Check if all values are not selected and return
		# an error if they are.

		if ($altersection ne "on" && $altertemplate ne "on" && $altersettings ne "on"){

			# All values are not selected so return 
			# an error.

			kiriwrite_error("noeditvaluesselected");

		}

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Check if the database has read and write permissions.

		my $database_permissions = $kiriwrite_dbmodule->dbpermissions($database, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		%database_info = $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		};

		my $database_name = $database_info{"DatabaseName"};

		# Edit the selected pages.

		foreach $filename (@filelist){

			# Get the page information.

			%page_info = $kiriwrite_dbmodule->getpageinfo({ PageFilename => $filename });

			# Check if any errors occured.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so write a warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($kiriwrite_lang->{pages}->{databasepageerror}, $filename, $kiriwrite_dbmodule->geterror(1));

			} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page does not exist, so write a warning message.

 				$warning_list{$warning_count}{Message} = kiriwrite_language($kiriwrite_lang->{pages}->{databasepagedoesnotexist}, $filename);
 				$warning_count++;
				next;

			}

			# Check if the page section should be altered.

			if ($altersection eq "on"){

				# Change the section name.

				$page_info{"PageSection"} = $newsection;

			}

			# Check if the page template should be altered.

			if ($altertemplate eq "on"){

				# Change the page template filename.

				$page_info{"PageTemplate"} = $newtemplate;

			}

			# Check if the page settings should be altered.

			if ($altersettings eq "on"){

				# Change the page settings value.

				$page_info{"PageSettings"} = $newsettings;

			}

			# Edit the selected page.

			$kiriwrite_dbmodule->editpage({ PageFilename => $page_info{"PageFilename"}, PageNewFilename => $page_info{"PageFilename"}, PageNewName => $page_info{"PageName"}, PageNewDescription => $page_info{"PageDescription"}, PageNewSection => $page_info{"PageSection"}, PageNewTemplate => $page_info{"PageTemplate"}, PageNewContent => $page_info{"PageContent"}, PageNewSettings => $page_info{"PageSettings"} });

			# Check if any errors occured while editing the page.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so write a warning message
				# with the extended error information.

				$warning_list{$warning_count}{Message} = kiriwrite_language($kiriwrite_lang->{pages}->{databasepageerror}, $filename, $kiriwrite_dbmodule->geterror(1));
				$warning_count++;
				next;

			} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The pages does not exist in the database.

				$warning_list{$warning_count}{Message} = kiriwrite_language($kiriwrite_lang->{pages}->{databasepagedoesnotexist}, $filename);
				$warning_count++;
				next;

			} elsif ($kiriwrite_dbmodule->geterror eq "PageExists"){

				# A page already exists with the new filename.

				kiriwrite_error("pagefilenameexists");

			}

			# The page has been edited so write a message saying that the page
			# has been edited.

 			$edited_list{$pageedited}{Filename} 	= $page_info{"PageFilename"};
 			$edited_list{$pageedited}{Name}		= $page_info{"PageName"};
 
 			# Increment the counter of edited pages.
 
 			$pageedited++;

		}

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{multiedit}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();

		# Check if the counter of edited pages is 0 and if it is
		# then write a message saying that no pages were edited
		# else write a message listing all of the pages edited.

		if ($pageedited eq 0){

			$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{nopagesedited}, $database_name));

		} else {

			# Write out the message saying that the selected pages
			# were edited.

			$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{pagesedited}, $database_name));
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->startbox("datalist");

			foreach $page (keys %edited_list){

				# Check if the page name is not blank.

				if (!$edited_list{$page}{Name}){

					$kiriwrite_presmodule->additalictext($kiriwrite_lang->{blank}->{noname});
					$kiriwrite_presmodule->addtext(" (" . $edited_list{$page}{Filename} . ")");

				} else {

					$kiriwrite_presmodule->addtext($edited_list{$page}{Name});
					$kiriwrite_presmodule->addtext(" (" . $edited_list{$page}{Filename} . ")");

				}

				$kiriwrite_presmodule->addlinebreak();
			}

			$kiriwrite_presmodule->endbox();

		}

		# Check if any warnings have occured and write a message
		# if any warnings did occur.

		if (%warning_list){

			# One or several warnings have occured so 
			# write a message.

			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{editedpageswarnings});
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->startbox("datalist");
			foreach $warning (keys %warning_list) {
				$kiriwrite_presmodule->addtext($warning_list{$warning}{Message});
				$kiriwrite_presmodule->addlinebreak();
			}
			$kiriwrite_presmodule->endbox();

		}

		# Write a link going back to the page list for
		# the selected database.

		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($kiriwrite_lang->{pages}->{returnpagelist}, $database_name) });

		return $kiriwrite_presmodule->grab();

	} elsif ($confirm eq 0){

		# The action to edit the template has not been confirmed
		# so write a form out instead.

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Check if the database has read and write permissions.

		my $database_permissions = $kiriwrite_dbmodule->dbpermissions($database, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		my %database_info = $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		};

 		my $database_name	= $database_info{"DatabaseName"};

		# Define some variables for later.

		my %edit_list;
		my %template_list;
		my %template_info;
		my %page_info;
		my @templates_list;
		my @filenames;
		my $filelist_filename;
		my $filename;
		my $page;
		my $pageseek = 0;
		my $page_name;
		my $page_filename;
		my $template;
		my $template_filename;
		my $template_warning;
		my $templateseek = 0;

		tie(%edit_list, 'Tie::IxHash');
		tie(%template_list, 'Tie::IxHash');

		# Get the information about each page that is going
		# to be edited.

		foreach $filelist_filename (@filelist){

			%page_info = $kiriwrite_dbmodule->getpageinfo({ PageFilename => $filelist_filename });

			# Check if any errors occured.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

			} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page does not exist, so process the next page.

				next;

			}

			# Add the page name and file name to the list of
			# pages to edit.

			$edit_list{$pageseek}{Filename}	= $page_info{"PageFilename"};
			$edit_list{$pageseek}{Name}	= $page_info{"PageName"};

			# Increment the page seek counter and reset the
			# page found value.

			$pageseek++;

		}

		# Check if any pages were found in the database and return
		# an error if not.

		if ($pageseek eq 0){

			# No pages were found so return an error.

			kiriwrite_error("nopagesselected");

		}

		# Connect to the template database.

		$kiriwrite_dbmodule->connecttemplate();

		# Check if any errors had occured.

		if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseDoesNotExist"){

			# The template database does not exist so write a warning
			# message.

			$template_warning = $kiriwrite_lang->{pages}->{templatedatabasenotexistmultieditkeep};

		} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so
			# return an error.

			$template_warning = $kiriwrite_lang->{pages}->{templatedatabasepermissionsinvalidmultieditkeep};

		}

		if (!$template_warning){

			# Get the list of templates available.

			@templates_list = $kiriwrite_dbmodule->gettemplatelist();

			# Check if any errors had occured.

			if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

				# A database error occured while getting the list
				# of templates so write a warning message with the 
				# extended error information.

				$template_warning = kiriwrite_language($kiriwrite_lang->{pages}->{templatedatabaseerrormultieditkeep}, $kiriwrite_dbmodule->geterror(1));

			}

			if (!$template_warning){

				foreach $template_filename (@templates_list){

					# Get the template data.

					%template_info = $kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $template_filename });

					# Check if any error occured while getting the template information.

					if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

						# A database error has occured, so write a warning message with
						# the extended error information.

						$template_warning = kiriwrite_language($kiriwrite_lang->{pages}->{templatedatabaseerrormultieditkeep}, $kiriwrite_dbmodule->geterror(1));

					} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

						# The template does not exist, so process the next page.

						next;

					}

					# Add the template to the list of templates.

					$template_list{$templateseek}{Filename}	= $template_info{"TemplateFilename"};
					$template_list{$templateseek}{Name} 	= $template_info{"TemplateName"};

					$templateseek++;

				}

			}

		}

		# Disconnect from the template database.

		$kiriwrite_dbmodule->disconnecttemplate();

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# Write a form for editing the selected pages.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{multiedit}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addhiddendata("mode", "page");
		$kiriwrite_presmodule->addhiddendata("action", "multiedit");
		$kiriwrite_presmodule->addhiddendata("database", $database);
		$kiriwrite_presmodule->addhiddendata("count", $pageseek);
		$kiriwrite_presmodule->addhiddendata("confirm", 1);

		$pageseek = 1;

		foreach $page (keys %edit_list){
			$kiriwrite_presmodule->addhiddendata("name[" . $pageseek . "]", "on");
			$kiriwrite_presmodule->addhiddendata("id[" . $pageseek  . "]", $edit_list{$page}{Filename});
			$pageseek++;
		}

		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{multieditmessage}, $database_name));
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->startbox("datalist");

		foreach $page (keys %edit_list){
			if (!$edit_list{$page}{Name}){
				$kiriwrite_presmodule->additalictext("No Name");
				$kiriwrite_presmodule->addtext(" (" . $edit_list{$page}{Filename} . ")");
			} else {
				$kiriwrite_presmodule->addtext($edit_list{$page}{Name} . " (" . $edit_list{$page}{Filename} . ")");
			}

			$kiriwrite_presmodule->addlinebreak();
		}

		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{multieditmessagevalues});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

		$kiriwrite_presmodule->startheader();
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{alter}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{setting}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{value}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->endheader();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addcheckbox("altersection");
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagesection});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addinputbox("newsection", { Size => 64, MaxLength => 256 });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addcheckbox("altertemplate");
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagetemplate});
		$kiriwrite_presmodule->endcell();

		$kiriwrite_presmodule->addcell("tablecell2");

		if ($template_warning){

			$kiriwrite_presmodule->addhiddendata("newtemplate", "!skip");
			$kiriwrite_presmodule->addtext($template_warning);

		} else {

			$kiriwrite_presmodule->addselectbox("newtemplate");

			foreach $template (keys %template_list){

				$kiriwrite_presmodule->addoption($template_list{$template}{Name} . " (" . $template_list{$template}{Filename} . ")", { Value => $template_list{$template}{Filename}});

			}

			$kiriwrite_presmodule->addoption($kiriwrite_lang->{pages}->{usenotemplate}, { Value => "!none", Selected => 1 });
			$kiriwrite_presmodule->endselectbox();
		}

		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addcheckbox("altersettings");
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{pagesettings});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addradiobox("newsettings", { Description => $kiriwrite_lang->{pages}->{usepageandsection}, Value => 1 , Selected => 1});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addradiobox("newsettings", { Description => $kiriwrite_lang->{pages}->{usepagename}, Value => 2 });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addradiobox("newsettings", { Description => $kiriwrite_lang->{pages}->{usesectionname}, Value => 3 });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addradiobox("newsettings", { Description => $kiriwrite_lang->{pages}->{nopagesection}, Value => 0 });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->endtable();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{pages}->{editpagesbutton});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addreset($kiriwrite_lang->{common}->{clearvalues});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($kiriwrite_lang->{pages}->{returnpagelist}, $database_name) });
		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endform();

		return $kiriwrite_presmodule->grab();

	} else {

		# The confirm value is something else other than
		# 1 or 0, so return an error.

		kiriwrite_error("invalidvariable");

	}

}

sub kiriwrite_page_list{
#################################################################################
# kiriwrite_page_list: Lists pages from an database.				#
#										#
# Usage:									#
#										#
# kiriwrite_page_list([database]);						#
#										#
# database	Specifies the database to retrieve the pages from.		#
#################################################################################

	# Get the database file name from what was passed to the subroutine.

	my ($database_file) = @_;

	# Check if the database_file variable is empty, if it is then print out a
	# select box asking the user to select a database from the list.

	if (!$database_file) {

		# Define the variables required for this section.

		my %database_info;
		my @database_list;
		my @databasefilenames;
		my @databasenames;
		my $dbseek		= 0;
		my $dbfilename		= "";
		my $dbname		= "";
		my $data_file 		= "";
		my $data_file_length	= 0;
		my $data_file_friendly	= "";
		my $database_name	= "";
		my $file_permissions	= "";

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Open the data directory and get all of the databases.

		@database_list	= $kiriwrite_dbmodule->getdblist();

		# Check if any errors occured while trying to get the list of databases.

 		if ($kiriwrite_dbmodule->geterror eq "DataDirMissing"){

			# The database directory is missing so return an error.

			kiriwrite_error("datadirectorymissing");

		} elsif ($kiriwrite_dbmodule->geterror eq "DataDirInvalidPermissions"){

			# The database directory has invalid permissions set so return
			# an error.

			kiriwrite_error("datadirectoryinvalidpermissions");

		}

		# Get the information about each database (the short name and friendly name).

		foreach $data_file (@database_list){

			$kiriwrite_dbmodule->selectdb({ DatabaseName => $data_file });

			# Check if any errors occured while selecting the database.

			if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

				# The database does not exist, so process the next
				# database.

				next;

			} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

				# The database has invalid permissions set, so process
				# the next database.

				next;

			}

			# Get the database information.

			%database_info = $kiriwrite_dbmodule->getdatabaseinfo();

			# Check if any errors had occured while getting the database
			# information.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured, so process the next 
				# database.

				next;

			};

			# Set the database name.

			$database_name 		= $database_info{"DatabaseName"};

			# Check if the database name is undefined and if it is
			# then set it blank.

			if (!$database_name){
				$database_name = "";
			}

			# Append the database to the list of databases available.

			push(@databasefilenames, $data_file);
			push(@databasenames, $database_name);

		}

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# Write the page data.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{viewpages}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{pages}->{nodatabaseselected});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"});
		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addhiddendata("mode", "page");
		$kiriwrite_presmodule->addhiddendata("action", "view");
		$kiriwrite_presmodule->addselectbox("database");
		foreach $dbfilename (@databasefilenames){
			$dbname = $databasenames[$dbseek];
			$dbseek++;
			$kiriwrite_presmodule->addoption($dbname . " (" . $dbfilename . ")", { Value => $dbfilename });
		}
		$kiriwrite_presmodule->endselectbox();
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{pages}->{viewbutton});
		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endform();

		return $kiriwrite_presmodule->grab();

	} else {

		my %database_info;
		my %page_info;
		my @database_pages;
		my $pagemultioptions	= "";
		my $db_name		= "";
		my $tablestyle		= "";

		my $page_filename	= "";
		my $page_name		= "";
		my $page_description	= "";
		my $page_modified	= "";

		my $tablestyletype	= 0;
		my $page_count		= 0;
		my $db_file_notblank	= 0;

		tie(%database_info, 'Tie::IxHash');
		tie(%page_info, 'Tie::IxHash');

		# The database_file variable is not blank, so print out a list of pages from
		# the selected database.

		# Preform a variable check on the database filename to make sure that it is
		# valid before using it.

		kiriwrite_variablecheck($database_file, "filename", "", 0);
		kiriwrite_variablecheck($database_file, "maxlength", 32, 0);

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $database_file });

		# Check if any errors had occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		%database_info = $kiriwrite_dbmodule->getdatabaseinfo();

		$db_name = $database_info{"DatabaseName"};

		# Check if any errors had occured while getting the database
		# information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Get the list of pages.

		@database_pages = $kiriwrite_dbmodule->getpagelist();

		# Check if any errors had occured while getting the list of pages.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Check if there are any page names in the database array.

		if (@database_pages){

			# Write the start of the page.

			$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{pagelist}, $db_name), { Style => "pageheader" });
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
			$kiriwrite_presmodule->startbox();
			$kiriwrite_presmodule->addhiddendata("mode", "page");
			$kiriwrite_presmodule->addhiddendata("database", $database_file);
			$kiriwrite_presmodule->addhiddendata("type", "multiple");

			# Write the list of multiple selection options.

			$kiriwrite_presmodule->addreset($kiriwrite_lang->{common}->{selectnone});
			$kiriwrite_presmodule->addtext(" | ");
			$kiriwrite_presmodule->addbutton("action", { Value => "multidelete", Description => $kiriwrite_lang->{pages}->{deleteselectedbutton} });
			$kiriwrite_presmodule->addtext(" | ");
			$kiriwrite_presmodule->addbutton("action", { Value => "multimove", Description => $kiriwrite_lang->{pages}->{moveselectedbutton} });
			$kiriwrite_presmodule->addtext(" | ");
			$kiriwrite_presmodule->addbutton("action", { Value => "multicopy", Description => $kiriwrite_lang->{pages}->{copyselectedbutton} });
			$kiriwrite_presmodule->addtext(" | ");
			$kiriwrite_presmodule->addbutton("action", { Value => "multiedit", Description => $kiriwrite_lang->{pages}->{editselectedbutton} });

			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->endbox();

			# Write the table header.

			$kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });
			$kiriwrite_presmodule->startheader();
			$kiriwrite_presmodule->addheader("", { Style => "tablecellheader" });
			$kiriwrite_presmodule->addheader($kiriwrite_lang->{pages}->{pagefilename}, { Style => "tablecellheader" });
			$kiriwrite_presmodule->addheader($kiriwrite_lang->{pages}->{pagename}, { Style => "tablecellheader" });
			$kiriwrite_presmodule->addheader($kiriwrite_lang->{pages}->{pagedescription}, { Style => "tablecellheader" });
			$kiriwrite_presmodule->addheader($kiriwrite_lang->{pages}->{lastmodified}, { Style => "tablecellheader" });
			$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{options}, { Style => "tablecellheader" });
			$kiriwrite_presmodule->endheader();

			# Process each page filename and get the page information.

			foreach $page_filename (@database_pages){

				%page_info = $kiriwrite_dbmodule->getpageinfo({ PageFilename => $page_filename, Reduced => 1 });

				# Check if any errors have occured.

				if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

					# A database error has occured so return an error and
					# also the extended error information.

					kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

				} elsif ($kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

					# The page does not exist, so process the next page.

					next;

				}

				$page_count++;

				$page_filename 		= $page_info{"PageFilename"};
				$page_name		= $page_info{"PageName"};
				$page_description	= $page_info{"PageDescription"};
				$page_modified		= $page_info{"PageLastModified"};

				# Set the table cell style.

				if ($tablestyletype eq 0){

					$tablestyle = "tablecell1";
					$tablestyletype = 1;

				} else {

					$tablestyle = "tablecell2";
					$tablestyletype = 0;

				}

				# Write out the row of data.

				$kiriwrite_presmodule->startrow();
				$kiriwrite_presmodule->addcell($tablestyle);
				$kiriwrite_presmodule->addhiddendata("id[" . $page_count . "]", $page_filename);
				$kiriwrite_presmodule->addcheckbox("name[" . $page_count . "]");
				$kiriwrite_presmodule->endcell();
				$kiriwrite_presmodule->addcell($tablestyle);
				$kiriwrite_presmodule->addtext($page_filename);
				$kiriwrite_presmodule->endcell();
				$kiriwrite_presmodule->addcell($tablestyle);

				if (!$page_name){

					$kiriwrite_presmodule->additalictext($kiriwrite_lang->{blank}->{noname});

				} else {

					$kiriwrite_presmodule->addtext($page_name);

				}

				$kiriwrite_presmodule->endcell();
				$kiriwrite_presmodule->addcell($tablestyle);

				if (!$page_description){

					$kiriwrite_presmodule->additalictext($kiriwrite_lang->{blank}->{nodescription});

				} else {

					$kiriwrite_presmodule->addtext($page_description);

				}

				$kiriwrite_presmodule->endcell();
				$kiriwrite_presmodule->addcell($tablestyle);

				if (!$page_modified){

					$kiriwrite_presmodule->additalictext("No Date");

				} else {

					$kiriwrite_presmodule->addtext($page_modified);

				}

				$kiriwrite_presmodule->endcell();
				$kiriwrite_presmodule->addcell($tablestyle);
				$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"}  . "?mode=page&action=edit&database=" . $database_file . "&page=" . $page_filename, { Text => $kiriwrite_lang->{options}->{edit} });
				$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"}  . "?mode=page&action=delete&database=" . $database_file . "&page=" . $page_filename, { Text => $kiriwrite_lang->{options}->{delete} });
				$kiriwrite_presmodule->endcell();
				$kiriwrite_presmodule->endrow();

				# Increment the counter.

			}

		}

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		$kiriwrite_presmodule->endtable();
		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addhiddendata("count", $page_count);
		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endform();

		if (!@database_pages || !$page_count){

			# There were no values in the database pages array and 
			# the page count had not been incremented so write a
			# message saying that there were no pages in the
			# database.

			$kiriwrite_presmodule->clear();
			$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{pages}->{pagelist}, $db_name), { Style => "pageheader" });
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->startbox("errorbox");
			$kiriwrite_presmodule->enterdata($kiriwrite_lang->{pages}->{nopagesindatabase});
			$kiriwrite_presmodule->endbox();

		}

		return $kiriwrite_presmodule->grab();

	}

}

sub kiriwrite_template_add{
#################################################################################
# kiriwrite_template_add: Add a template to the template folder			#
#										#
# Usage:									#
#										#
# kiriwrite_template_add(filename, name, description, layout, confirm);		#
#										#
# filename	The filename of the new template.				#
# name		The name of the template.					#
# description	The description of the template.				#
# layout	The layout of the new template.					#
# confirm	Confirm the action of creating a new template.			#
#################################################################################

	# Get the variables that were passed to the subroutine.

	my ($templatefilename, $templatename, $templatedescription, $templatelayout, $confirm) = @_;

	# Check if the confirm value is blank and if it is then set confirm to 0.

	if (!$confirm){

		# The confirm value is blank, so set the value of confirm to 0.

		$confirm = 0;

	}

	if ($confirm eq 1){

		# Check (validate) each of the values.

		kiriwrite_variablecheck($templatename, "utf8", 0, 0);
		kiriwrite_variablecheck($templatedescription, "utf8", 0, 0);
		kiriwrite_variablecheck($templatelayout, "utf8", 0, 0);

		# Convert the values into proper UTF8 strings that can be used.

		$templatename 		= kiriwrite_utf8convert($templatename);
		$templatedescription 	= kiriwrite_utf8convert($templatedescription);
		$templatelayout		= kiriwrite_utf8convert($templatelayout);

		# Check the length of the converted UTF8 strings.

		my $templatefilename_length_check 	= kiriwrite_variablecheck($templatefilename, "maxlength", 64, 1);
		my $templatename_length_check	  	= kiriwrite_variablecheck($templatename, "maxlength", 512, 1);
		my $templatedescription_length_check 	= kiriwrite_variablecheck($templatedescription, "maxlength", 512, 1);
		kiriwrite_variablecheck($confirm, "maxlength", 1, 0);

		if ($templatefilename_length_check eq 1){

			# The template filename length is too long, so return an error.

			kiriwrite_error("templatefilenametoolong");

		}

		if ($templatename_length_check eq 1){

			# The template name length is too long, so return an error.

			kiriwrite_error("templatenametoolong");

		}


		if ($templatedescription_length_check eq 1){

			# The template description length is too long, so return an error.

			kiriwrite_error("templatedescriptiontoolong");

		}

 		# Check if the filename specified is a valid filename.

		kiriwrite_variablecheck($templatefilename, "filename", "", 0);

		# Connect to the template server.

		$kiriwrite_dbmodule->connect();

		# Connect to the template database.

		$kiriwrite_dbmodule->connecttemplate(1);

		# Check if any errors had occured.

		if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so
			# return an error.

			kiriwrite_error("templatedatabaseinvalidpermissions");

		}

		$kiriwrite_dbmodule->addtemplate({ TemplateFilename => $templatefilename, TemplateName => $templatename, TemplateDescription => $templatedescription, TemplateLayout => $templatelayout });

		if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

			# A database error has occured so return an error along
			# with the extended error information.

			kiriwrite_error("templatedatabaseerror", $kiriwrite_dbmodule->geterror(1));

		} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so return
			# an error.

			kiriwrite_error("templatedatabaseinvalidpermissions");

		} elsif ($kiriwrite_dbmodule->geterror eq "TemplatePageExists"){

			# The template page already exists so return an error.

			kiriwrite_error("templatefilenameexists");

		} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseUncreateable"){

			# The template databases is uncreatable so return an error.

			kiriwrite_error("templatedatabasenotcreated");

		}

		$kiriwrite_dbmodule->disconnecttemplate();

		# Disconnect from the template server.

		$kiriwrite_dbmodule->disconnect();

		# Print out the confirmation message.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{template}->{addedtemplate}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{template}->{addedtemplatemessage}, $templatename));
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=template", { Text => $kiriwrite_lang->{template}->{returntemplatelist} });
		return $kiriwrite_presmodule->grab();

	} else {
		# No confirmation was made, so print out a form for adding a template.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{template}->{addtemplate}, { Style => "pageheader" });
		$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addhiddendata("mode", "template");
		$kiriwrite_presmodule->addhiddendata("action", "add");
		$kiriwrite_presmodule->addhiddendata("confirm", 1);
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->starttable("", { CellSpacing => 0, CellPadding => 5 });

		$kiriwrite_presmodule->startheader();
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{setting}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{value}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->endheader();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{template}->{templatename});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("templatename", { Size => 64, MaxLength => 512 });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{template}->{templatedescription});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("templatedescription", { Size => 64, MaxLength => 512 });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{template}->{templatefilename});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("templatefilename", { Size => 32, MaxLength => 64 });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{template}->{templatelayout});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addtextbox("templatelayout", { Columns => 50, Rows => 10 });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->startbox("datalist");
		$kiriwrite_presmodule->addboldtext($kiriwrite_lang->{common}->{tags});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagecontent});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagetitle});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagename});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagedescription});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagesection});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pageautosection});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pageautotitle});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();
		$kiriwrite_presmodule->endtable();

		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{template}->{addtemplatebutton});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addreset($kiriwrite_lang->{common}->{clearvalues});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=template" , { Text => $kiriwrite_lang->{template}->{returntemplatelist} });

		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endform();

		return $kiriwrite_presmodule->grab();

	}


}

sub kiriwrite_template_edit{
#################################################################################
# kiriwrite_template_edit: Edit a template from the template folder.		#
#										#
# Usage:									#
#										#
# kiriwrite_template_edit(filename, [newfilename], [newname], [newdescription], #
#				[templatelayout], [confirm]);			#
#										#
# filename		The current filename of the template to edit.		#
# newfilename		The new filename of the template to edit.		#
# newname		The new name of the template being edited.		#
# newdescription	The new description of the template being edited.	#
# templatelayout	The modified/altered template layout.			#
# confirm		Confirms the action to edit a template and its		#
#			settings.						#
#################################################################################

	# Get all the variables that have been passed to the subroutine.

	my ($templatefilename, $templatenewfilename, $templatenewname, $templatenewdescription, $templatelayout, $confirm) = @_;

	# Check if the confirm variable is blank, if it is then
	# set confirm to '0'

	if (!$confirm){

		# confirm is uninitalised/blank, so set the value of confirm
		# to '0'

		$confirm = 0;

	}

	# Check if the template filename is blank and if it is, then return
	# an error.

	if (!$templatefilename){

		kiriwrite_error("templatefilenameblank");

	}

	# Connect to the database server.

	$kiriwrite_dbmodule->connect();

	# Check if any errors occured while connecting to the database server.

	if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

		# A database connection error has occured so return
		# an error.

		kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

	}

	if ($confirm eq 1){

		# Check certain strings to see if they UTF8 compiliant.

		kiriwrite_variablecheck($templatenewname, "utf8", 0, 0);
		kiriwrite_variablecheck($templatenewdescription, "utf8", 0, 0);
		kiriwrite_variablecheck($templatelayout, "utf8", 0, 0);

		# Convert the values into proper UTF8 strings.

		$templatenewname 	= kiriwrite_utf8convert($templatenewname);
		$templatenewdescription	= kiriwrite_utf8convert($templatenewdescription);
 		$templatelayout		= kiriwrite_utf8convert($templatelayout);

		# Check if the filenames recieved are valid filenames.

		kiriwrite_variablecheck($templatenewfilename, "maxlength", 64, 0);
		kiriwrite_variablecheck($templatenewdescription, "maxlength", 512, 0);
		kiriwrite_variablecheck($templatenewname, "maxlength", 512, 0);
		kiriwrite_variablecheck($templatefilename, "maxlength", 64, 0);
		kiriwrite_variablecheck($confirm, "maxlength", 1, 0);

		kiriwrite_variablecheck($templatefilename, "filename", "", 0);
		kiriwrite_variablecheck($templatenewfilename, "filename", "", 0);

		# Connect to the template database.

		$kiriwrite_dbmodule->connecttemplate();

		# Check if any errors had occured.

		if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so
			# return an error.

			kiriwrite_error("templatedatabaseinvalidpermissions");

		}

		# Edit the template.

		$kiriwrite_dbmodule->edittemplate({ TemplateFilename => $templatefilename, NewTemplateFilename => $templatenewfilename, NewTemplateName => $templatenewname, NewTemplateDescription => $templatenewdescription, NewTemplateLayout => $templatelayout });

		# Check if any error occured while editing the template.

		if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

			# A database error has occured, so return an error.

			kiriwrite_error("templatedatabaseerror", $kiriwrite_dbmodule->geterror(1));

		} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so return
			# an error.

			kiriwrite_error("templatedatabaseinvalidpermissions");

		} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

			# The template does not exist, so process the next template.

			kiriwrite_error("templatedoesnotexist");

		}

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# Disconnect from the template database.

		$kiriwrite_dbmodule->disconnecttemplate();

		# Append a link so that the user can return to the templates list.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{template}->{editedtemplate}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{template}->{editedtemplatemessage}, $templatenewname));
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=template", { Text => $kiriwrite_lang->{template}->{returntemplatelist} });

	} else {

		# Connect to the template database.

		$kiriwrite_dbmodule->connecttemplate();

		# Check if any errors had occured.

		if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so
			# return an error.

			kiriwrite_error("templatedatabaseinvalidpermissions");

		}

		# Get the template information.

		my %template_info = $kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $templatefilename });

		# Check if any error occured while getting the template information.

		if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

			# A database error has occured, so return an error.

			kiriwrite_error("templatedatabaseerror", $kiriwrite_dbmodule->geterror(1));

		} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

			# The template does not exist, so return an error.

			kiriwrite_error("templatedoesnotexist");

		}

		# Disconnect from the template database.

		$kiriwrite_dbmodule->disconnecttemplate();

		# Get the values from the query results.

		my $template_filename		= $template_info{"TemplateFilename"};
		my $template_name		= $template_info{"TemplateName"};
		my $template_description	= $template_info{"TemplateDescription"};
		my $template_layout		= $template_info{"TemplateLayout"};
		my $template_modified		= $template_info{"TemplateLastModified"};

		# Check if the values are undefined and set them blank
		# if they are.

		if (!$template_name){
			$template_name = "";
		}

		if (!$template_description){
			$template_description = "";
		}

		if (!$template_layout){
			$template_layout = "";
		}

		# Write out the form for editing an template with the current template 
		# settings put into the correct place.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{template}->{edittemplate}, { Style => "pageheader" });
 		$kiriwrite_presmodule->addlinebreak();
 		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addhiddendata("mode", "template");
		$kiriwrite_presmodule->addhiddendata("action", "edit");
		$kiriwrite_presmodule->addhiddendata("confirm", 1);
		$kiriwrite_presmodule->addhiddendata("template", $template_filename);
		$kiriwrite_presmodule->starttable("", { CellSpacing => 0, CellPadding => 5});

		$kiriwrite_presmodule->startheader();
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{setting}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{value}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->endheader();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{template}->{templatename});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("newname", { Size => 64, MaxLength => 512, Value => $template_name });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{template}->{templatedescription});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("newdescription", { Size => 64, MaxLength => 512, Value => $template_description });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{template}->{templatefilename});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("newfilename", { Size => 32, MaxLength => 64, Value => $template_filename });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{template}->{templatelayout});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addtextbox("newlayout", { Rows => 10, Columns => 50, Value => $template_layout});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->startbox("datalist");
		$kiriwrite_presmodule->addboldtext($kiriwrite_lang->{common}->{tags});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagecontent});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagetitle});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagename});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagedescription});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pagesection});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pageautosection});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{common}->{pageautotitle});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->endtable();

		$kiriwrite_presmodule->addlinebreak();

		$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{template}->{edittemplatebutton});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addreset($kiriwrite_lang->{common}->{restorecurrent});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=template", { Text => $kiriwrite_lang->{template}->{returntemplatelist} });

		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endform();

	}

	# Disconnect from the database server.

	$kiriwrite_dbmodule->disconnect();

	return $kiriwrite_presmodule->grab();

}

sub kiriwrite_template_delete{
#################################################################################
# kiriwrite_template_delete: Delete a template from the template folder.	#
#										#
# Usage:									#
#										#
# kiriwrite_template_delete(filename, confirm);					#
#										#
# filename	Specifies the filename of the database to delete.		#
# confirm	Confirms the action to delete a template.			#
#################################################################################

	# Get the parameters that were passed to the subroutine.

	my ($template_filename, $template_confirm) = @_;

	if (!$template_confirm){
		$template_confirm = 0;
	}

	# Check the length of the variables.
	kiriwrite_variablecheck($template_filename, "maxlength", 64, 0);
	kiriwrite_variablecheck($template_confirm, "maxlength", 1, 0);

	# Check if the template_name string is blank and if it is then
	# return an error (as the template_name string should not be
	# blank.

	if (!$template_filename){

		# The template_filename string really is blank, 
		# so return an error saying that an empty
		# filename was passed (to the subroutine).

		kiriwrite_error("templatefilenameblank");

	}

	# Check if the template_confirm string is blank and if it is, write
	# out a form asking the user to confirm the deletion.

	if ($template_confirm eq 1){

		# The action to delete the template from the template database has
		# been confirmed so delete the template.

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Check if the template database exists and the file permissions
		# are valid and return an error if they aren't.

		$kiriwrite_dbmodule->connecttemplate();

		if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseDoesNotExist"){

			# The template database does not exist so write a warning
			# message.

			kiriwrite_error("templatedatabasemissing");

		} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so
			# return an error.

			kiriwrite_error("templatedatabaseinvalidpermissions");

		}

		my %template_info = $kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $template_filename });

		# Check if any error occured while getting the template information.

		if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

			# A database error has occured, so return an error.

			kiriwrite_error("templatedatabaseerror", $kiriwrite_dbmodule->geterror(1));

		} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

			# The template does not exist, so return an error.

			kiriwrite_error("templatedoesnotexist");

		}

		# Delete the selected template.

		$kiriwrite_dbmodule->deletetemplate({ TemplateFilename => $template_filename });

		# Check if any error occured while deleting the template.

		if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

 			# A database error has occured, so return an error.

			kiriwrite_error("templatedatabaseerror", $kiriwrite_dbmodule->geterror(1));

		} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

			# The template does not exist, so process the next template.

			kiriwrite_error("templatedoesnotexist");

		}

		$kiriwrite_dbmodule->disconnecttemplate();

		# Get the deleted database name.

		my $database_template_name = $template_info{"TemplateName"};

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{template}->{deletedtemplate}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{template}->{deletedtemplatemessage}, $database_template_name) );
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=template", { Text => $kiriwrite_lang->{template}->{returntemplatelist} });

		return $kiriwrite_presmodule->grab();

	} elsif ($template_confirm eq 0) {

		# The template confirm value is 0 (previously blank and then set to 0), so
		# write out a form asking the user to confirm the deletion of the template.

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Connect to the template database.

		$kiriwrite_dbmodule->connecttemplate();

		if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseDoesNotExist"){

			# The template database does not exist so write a warning
			# message.

			kiriwrite_error("templatedatabasemissing");

		} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so
			# return an error.

			kiriwrite_error("templatedatabaseinvalidpermissions");

		}

		my %template_info = $kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $template_filename });

		if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

			# A database error has occured, so return an error.

			kiriwrite_error("templatedatabaseerror", $kiriwrite_dbmodule->geterror(1));

		} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

			# The template does not exist, so return an error.

			kiriwrite_error("templatedoesnotexist");

		}

		my $template_data_filename	= $template_info{"TemplateFilename"};
		my $template_data_name		= $template_info{"TemplateName"};

		$kiriwrite_dbmodule->disconnecttemplate();

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# Write out the confirmation form.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{template}->{deletetemplate}, { Style => "pageheader" });
		$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addhiddendata("mode", "template");
		$kiriwrite_presmodule->addhiddendata("template", $template_filename);
		$kiriwrite_presmodule->addhiddendata("action", "delete");
		$kiriwrite_presmodule->addhiddendata("confirm", 1);
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{template}->{deletetemplatemessage}, $template_data_name, $template_data_filename));
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{template}->{deletetemplatebutton});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=template", { Text => $kiriwrite_lang->{template}->{deletetemplatereturntolist} });
		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endform();

		return $kiriwrite_presmodule->grab();

	} else {

			kiriwrite_error("invalidvariable");

	}

}

sub kiriwrite_template_list{
#################################################################################
# kiriwrite_template_list: List the templates in the template folder.		#
#										#
# Usage:									#
#										#
# kiriwrite_template_list();							#
#################################################################################

	# Define certain values for later.

	my %template_info;

	my @templates_list;

	my $template;
	my $template_filename 		= "";
	my $template_filename_list	= "";
	my $template_name		= "";
	my $template_description 	= "";
	my $template_data		= "";

	my $template_count = 0;

	my $template_style = 0;
	my $template_stylename = "";

	my $templatewarning = "";

	# Connect to the database server.

	$kiriwrite_dbmodule->connect();

	# Check if any errors occured while connecting to the database server.

	if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

		# A database connection error has occured so return
		# an error.

		kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

	}

	# Connect to the template database.

	$kiriwrite_dbmodule->connecttemplate();

	# Check if any errors had occured.

	if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseDoesNotExist"){

		# The template database does not exist so write a warning
		# message.

		$templatewarning = $kiriwrite_lang->{template}->{templatedatabasedoesnotexist};

	} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

		# The template database has invalid permissions set so
		# return an error.

		kiriwrite_error("templatedatabaseinvalidpermissions");

	} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

		# A database error occured while getting the list of
		# templates so return an error with the extended
		# error information.

		kiriwrite_error("templatedatabaseerror", $kiriwrite_dbmodule->geterror(1));

	}

	# Get the list of template databases.

	if (!$templatewarning){

		@templates_list = $kiriwrite_dbmodule->gettemplatelist();

	}

	# Check if any errors had occured.

	if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

		# A database error occured while getting the list
		# of templates so return an error with the 
		# extended error information.

		kiriwrite_error("templatedatabaseerror", $kiriwrite_dbmodule->geterror(1));

	}

	# Check if any templates are in the database and if there isn't
	# then write a message saying that there are no templates in the
	# database.

	if (!@templates_list && !$templatewarning){
		$templatewarning = $kiriwrite_lang->{template}->{notemplatesavailable};
	}

	# Process the templates into a template list.

	$kiriwrite_presmodule->addtext($kiriwrite_lang->{template}->{viewtemplates}, { Style => "pageheader" });
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();

	if ($templatewarning){

		$kiriwrite_presmodule->startbox("errorbox");
		$kiriwrite_presmodule->addtext($templatewarning);
		$kiriwrite_presmodule->endbox();

	} else {

		$kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });
		$kiriwrite_presmodule->startheader();
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{template}->{templatefilename}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{template}->{templatename}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{template}->{templatedescription}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{options}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->endheader();

		foreach $template (@templates_list){

			# Get the template data.

			%template_info = $kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $template });

			# Check if any errors occured while trying to get the template
			# data.

			if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

				# A database error has occured, so return an error.

				kiriwrite_error("templatedatabaseerror", $kiriwrite_dbmodule->geterror(1));

			} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

				# The template does not exist, so process the next template.

				next;

			}

			$template_filename	= $template_info{"TemplateFileName"};
			$template_name		= $template_info{"TemplateName"};
			$template_description	= $template_info{"TemplateDescription"};

 			# Check what style the row of table cells should be.
 
 			if ($template_style eq 0){
 
 				$template_stylename = "tablecell1";
 				$template_style = 1;
 
 			} else {
 
 				$template_stylename = "tablecell2";
 				$template_style = 0;
 
 			}

			$kiriwrite_presmodule->startrow();
			$kiriwrite_presmodule->addcell($template_stylename);
			$kiriwrite_presmodule->addtext($template_info{"TemplateFilename"});

			# Check if the blank template value was set.

			if (!$template_info{"TemplateLayout"}){
				$kiriwrite_presmodule->additalictext(" " . "[Blank Template]");
			}

			$kiriwrite_presmodule->endcell();
			$kiriwrite_presmodule->addcell($template_stylename);

			# Check if the template name is blank and if it is
			# write a message to say there's no name for the
			# template.

			if (!$template_info{"TemplateName"}){
				$kiriwrite_presmodule->additalictext($kiriwrite_lang->{blank}->{noname});
			} else {
				$kiriwrite_presmodule->addtext($template_info{"TemplateName"});
			}

			$kiriwrite_presmodule->endcell();
			$kiriwrite_presmodule->addcell($template_stylename);

			# Check if the template description is blank and if
			# it is then write a message to say there's no
			# description for the template.

			if (!$template_info{"TemplateDescription"}){
				$kiriwrite_presmodule->additalictext($kiriwrite_lang->{blank}->{nodescription});
			} else {
				$kiriwrite_presmodule->addtext($template_info{"TemplateDescription"});
			}

			$kiriwrite_presmodule->endcell();
			$kiriwrite_presmodule->addcell($template_stylename);
			$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=template&action=edit&template=" . $template_info{"TemplateFilename"}, { Text => $kiriwrite_lang->{options}->{edit} });
			$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=template&action=delete&template=" . $template_info{"TemplateFilename"}, { Text => $kiriwrite_lang->{options}->{delete} });
			$kiriwrite_presmodule->endcell();
			$kiriwrite_presmodule->endrow();

		}

		$kiriwrite_presmodule->endtable();

	}

	# Disconnect from the database server.

	$kiriwrite_dbmodule->disconnect();

	$kiriwrite_dbmodule->disconnecttemplate();
	return $kiriwrite_presmodule->grab();


}

sub kiriwrite_database_add{
#################################################################################
# kiriwrite_database_add: Creates a new database.				#
# 										#
# Usage:									#
#										#
# kiriwrite_database_add(filename, name, description, notes, categories, 	#
#				[confirm]);					#
#										#
# filename	Specifies the filename for the database.			#
# name		Specifies a (friendly) name for the database.			#
# description	Specifies a description for the database.			#
# notes		Specifies the notes for the database.				#
# categories	Specifies the categories for the database.			#
# confirm	Confirms the action to create a database.			#
#################################################################################

	# Get the variables passed from the subroutine.

	my ($database_filename, $database_name, $database_description, $database_notes, $database_categories, $database_confirm) = @_;

	# Check if the confirm value is blank and if it is then
	# set the confirm value to 0.

	if (!$database_confirm){

		# The confirm value was blank so set the value to 0.

		$database_confirm = 0;

	}

	if ($database_confirm eq 1){

		# The action to create a new database is confirmed.

		# Validate the database name and database descriptions.

		my $database_name_check_utf8		= kiriwrite_variablecheck($database_name, "utf8", 0, 0);
		my $database_description_check_utf8	= kiriwrite_variablecheck($database_description, "utf8", 0, 0);
		my $database_notes_check_utf8		= kiriwrite_variablecheck($database_notes, "utf8", 0, 0);
		my $database_categories_check_utf8	= kiriwrite_variablecheck($database_categories, "utf8", 0, 0);

		# Convert the UTF8 strings before checking the length of the strings.

		$database_name			= kiriwrite_utf8convert($database_name);
		$database_description		= kiriwrite_utf8convert($database_description);
		$database_notes			= kiriwrite_utf8convert($database_notes);
		$database_categories		= kiriwrite_utf8convert($database_categories);

		my $database_name_check_blank		= kiriwrite_variablecheck($database_name, "blank", 0, 1);
		my $database_name_check_length 		= kiriwrite_variablecheck($database_name, "maxlength", 256, 1);
		my $database_description_check_length	= kiriwrite_variablecheck($database_description, "maxlength", 512, 1);
		my $database_filename_check_length	= kiriwrite_variablecheck($database_filename, "maxlength", 32, 1);
		my $database_categories_check_length	= kiriwrite_variablecheck($database_categories, "maxlength", 512, 1);

		# Check if values returned contains any values that would
		# result in a specific error message being returned.

		if ($database_name_check_length eq 1){

			# The length of the database name is too long, so return an error.
			kiriwrite_error("databasenametoolong");

		}

		if ($database_description_check_length eq 1){

			# The database description length is too long, so return an error.
			kiriwrite_error("databasedescriptiontoolong");

		}

		if ($database_name_check_blank eq 1){

			# The database name is blank, so return an error.
			kiriwrite_error("databasenameblank");

		}

		if ($database_filename_check_length eq 1){

			# The database filename is to long, so return an error.
			kiriwrite_error("databasefilenametoolong");

		}

		if ($database_categories_check_length eq 1){

			# The database categories is too long, so return an error.
			kiriwrite_error("databasecategoriestoolong");

		}

		# Check if the database filename is blank and if it is then
		# generate a filename.

		if ($database_filename eq ""){

			# Filename is blank so generate a file name from
			# the database name.

			$database_filename = kiriwrite_processfilename($database_name);

		} else {

			# Filename is not blank so don't generate a filename.

		}

		kiriwrite_variablecheck($database_filename, "filename", "", 0);
		kiriwrite_variablecheck($database_filename, "maxlength", 32, 0);

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		my $database_name_final = $database_name;

		# Create the database.

		$kiriwrite_dbmodule->adddatabase({ DatabaseFilename => $database_filename, DatabaseName => $database_name, DatabaseDescription => $database_description, DatabaseNotes => $database_notes, DatabaseCategories => $database_categories, VersionMajor => $kiriwrite_version{"major"}, VersionMinor => $kiriwrite_version{"minor"}, VersionRevision => $kiriwrite_version{"revision"} });

		# Check if any errors have occured.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseExists"){

			# A database with the filename given already exists, so
			# return an error.

			kiriwrite_error("fileexists");

		} elsif ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error with
			# the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{adddatabase}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{database}->{databaseadded} , $database_name_final));
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=db", { Text => $kiriwrite_lang->{database}->{databaselistreturnlink} });

		return $kiriwrite_presmodule->grab();

	}

	# There is confirm value is not 1, so write a form for creating a database to
	# store pages in.

	$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{adddatabase}, { Style => "pageheader" });
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
	$kiriwrite_presmodule->startbox();	
	$kiriwrite_presmodule->addhiddendata("mode", "db");
	$kiriwrite_presmodule->addhiddendata("action", "new");
	$kiriwrite_presmodule->addhiddendata("confirm", "1");
	$kiriwrite_presmodule->endbox();
	$kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

	$kiriwrite_presmodule->startheader();
	$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{setting}, { Style => "tablecellheader"});
	$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{value}, { Style => "tablecellheader"});
	$kiriwrite_presmodule->endheader();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databasename});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addinputbox("databasename", { Size => 64, MaxLength => 256 });
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databasedescription});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addinputbox("databasedescription", { Size => 64, MaxLength => 512 });
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databasecategories});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addinputbox("databasecategories", { Size => 64, MaxLength => 512 });
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databasenotes});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addtextbox("databasenotes", { Columns => 50, Rows => 10, WordWrap => 0 });
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databasefilename});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addinputbox("databasefilename", { Size => 32, MaxLength => 32 });
	$kiriwrite_presmodule->startlist();
	$kiriwrite_presmodule->additem($kiriwrite_lang->{database}->{adddatabaseautogenerate});
	$kiriwrite_presmodule->additem($kiriwrite_lang->{database}->{adddatabasenoextensions});
	$kiriwrite_presmodule->additem($kiriwrite_lang->{database}->{adddatabasecharacterlength});
	$kiriwrite_presmodule->additem($kiriwrite_lang->{database}->{adddatabasecharacters});
	$kiriwrite_presmodule->endlist();
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->endtable();
	$kiriwrite_presmodule->startbox();
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{database}->{adddatabasebutton});
	$kiriwrite_presmodule->addtext("|");
	$kiriwrite_presmodule->addreset($kiriwrite_lang->{database}->{clearvaluesbutton});
	$kiriwrite_presmodule->addtext("| ");
	$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=db", { Text => $kiriwrite_lang->{database}->{databaselistreturnlink} });
	$kiriwrite_presmodule->endbox();
	$kiriwrite_presmodule->endform();

	# Exit the subroutine taking the data in the pagadata variable with it.

	return $kiriwrite_presmodule->grab();

}

sub kiriwrite_database_edit{
#################################################################################
# kiriwrite_database_edit: Edits an database.					#
#										#
# Usage:									#
# 										#
# kiriwrite_database_edit(filename, newfilename, newname, newdescription, 	#
#				notes, categories, [confirm]);			#
#										#
# filename		Specifies the filename of the database.			#
# newfilename		Specifies the new filename of the database.		#
# newname		Specifies the new name of the database.			#
# newdescription	Specifies the new description of the database.		#
# notes			Specifies the new notes of the database.		#
# categories		Specifies the new categories of the database.		#
# confirm		Confirms the action to edit a database.			#
#################################################################################

	# First, get all the variables passed to the subroutine.

	my ($database_shortname, $database_newfilename, $database_newname, $database_newdescription, $database_notes, $database_categories, $database_confirm) = @_;

	# Check if the database confirm value is blank and if it is
	# set the confirm value to 0.

	if (!$database_confirm){

		$database_confirm = 0;

	}

	# Check if the database filename given is valid and return an error
	# if it isn't.

	kiriwrite_variablecheck($database_shortname, "filename", "", 0);

	# Check if the confirm variable has a value in it, if it has, check again to make sure it really is the correct value (Perl moans
	# if $database_confirm was used directly).

	if ($database_confirm eq 1){

		# Check if the new data passes the validation tests below. First, check the length of the variables.

		my $database_name_check_utf8		= kiriwrite_variablecheck($database_newname, "utf8", 0, 0);
		my $database_description_check_utf8	= kiriwrite_variablecheck($database_newdescription, "utf8", 0, 0);
		my $database_notes_check_utf8		= kiriwrite_variablecheck($database_notes, "utf8", 0, 0);
		my $database_categories_check_utf8	= kiriwrite_variablecheck($database_categories, "utf8", 0, 0);

		# Convert the UTF8 strings to make sure their length is accurate.

		$database_newname 		= kiriwrite_utf8convert($database_newname);
		$database_newdescription 	= kiriwrite_utf8convert($database_newdescription);
		$database_notes			= kiriwrite_utf8convert($database_notes);
		$database_categories		= kiriwrite_utf8convert($database_categories);

		# Preform the following tests.

		my $database_filename_check_length 	= kiriwrite_variablecheck($database_newfilename, "maxlength", 32, 1);
		my $database_filename_letnum		= kiriwrite_variablecheck($database_newfilename, "filename", 0, 0);
		my $database_name_check_length 		= kiriwrite_variablecheck($database_newname, "maxlength", 256, 1);
		my $database_description_check_length 	= kiriwrite_variablecheck($database_newdescription, "maxlength", 512, 1);
		my $database_categories_check_length	= kiriwrite_variablecheck($database_categories, "maxlength", 512, 1);
		my $database_name_check_blank 		= kiriwrite_variablecheck($database_newname, "blank", 0, 1);

		# Check if the data is valid and return a specific error if it doesn't.

		if ($database_name_check_length eq 1){

			# The length of the database name is too long, so return an error.
			kiriwrite_error("databasenametoolong");

		}

		if ($database_description_check_length eq 1){

			# The database description length is too long, so return an error.
			kiriwrite_error("databasedescriptiontoolong");

		}

		if ($database_name_check_blank eq 1){

			# The database name is blank, so return an error.
			kiriwrite_error("databasenameblank");

		}

		if ($database_filename_check_length eq 1){

			# The database filename is too long, so return an error.
			kiriwrite_error("databasefilenametoolong");

		}

		if ($database_categories_check_length eq 1){

			# The database categories is too long, so return an error.
			kiriwrite_error("databasecategoriestoolong");

		}

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Get the database.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $database_shortname });

		# Check if any errors had occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# FIX THIS!! >O

		$kiriwrite_dbmodule->editdatabase({ DatabaseNewFilename => $database_newfilename, DatabaseName => $database_newname , DatabaseDescription => $database_newdescription , DatabaseNotes => $database_notes, DatabaseCategories => $database_categories });

		# Check if any errors had occured while using the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		} elsif ($kiriwrite_dbmodule->geterror eq "DataDirInvalidPermissions"){

			# The database directory has invalid permissions set, so
			# return an error.

			kiriwrite_error("datadirectoryinvalidpermissions");

		} elsif ($kiriwrite_dbmodule->geterror eq "DatabaseExists"){

			# A database already exists with the new filename, so
			# return an error.

			kiriwrite_error("databasealreadyexists");

		} elsif ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error with
			# the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Disconnect from the server.

		$kiriwrite_dbmodule->disconnect();

		# Write out a message saying that the database has been updated.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{editeddatabase}, { Style => "pageheader" } );
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{database}->{databaseupdated}, $database_newname));
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=db", { Text => $kiriwrite_lang->{database}->{databaselistreturnlink} });

		return $kiriwrite_presmodule->grab();

	} else {

		my (%database_info);

		# Check if the database filename given is valid and return an error
		# if it isn't.

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $database_shortname });

		# Check if any errors had occured while setting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get the database information.

		%database_info = $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Get the values needed from the kiriwrite_database_info table.

		my $database_oldname 		= $database_info{"DatabaseName"};
		my $database_olddescription	= $database_info{"Description"};
		my $database_notes		= $database_info{"Notes"};
		my $database_categories		= $database_info{"Categories"};

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# Print out the form for editing a database's settings.

		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{database}->{editdatabase}, $database_oldname), { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addhiddendata("mode", "db");
		$kiriwrite_presmodule->addhiddendata("action", "edit");
		$kiriwrite_presmodule->addhiddendata("database", $database_shortname);
		$kiriwrite_presmodule->addhiddendata("confirm", "1");
		$kiriwrite_presmodule->endbox();

		$kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });
		$kiriwrite_presmodule->startheader();
		$kiriwrite_presmodule->addheader("Setting", { Style => "tablecellheader" });
		$kiriwrite_presmodule->addheader("Value", { Style => "tablecellheader" });
		$kiriwrite_presmodule->endheader();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databasename});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("databasename", { Size => 64, MaxLength => 256, Value => $database_oldname } );
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databasedescription});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("databasedescription", { Size => 64, MaxLength => 512, Value => $database_olddescription } );
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databasecategories});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("databasecategories", { Size => 64, MaxLength => 512, Value => $database_categories } );
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databasenotes});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addtextbox("databasenotes", { Columns => 50, Rows => 10, Value => $database_notes } );
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databasefilename});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("databasefilename", { Size => 32, MaxLength => 32, Value => $database_shortname } );
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->endtable();

		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{database}->{editdatabasebutton});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addreset($kiriwrite_lang->{common}->{restorecurrent});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=db", { Text => $kiriwrite_lang->{database}->{databaselistreturnlink} });
		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endform();

		return $kiriwrite_presmodule->grab();

	}

	# The interpreter should not be here. So return an error saying invalid variable.

	kiriwrite_error("invalidvariable");

}

sub kiriwrite_database_delete{
#################################################################################
# kiriwrite_database_delete: Deletes an database.				#
#										#
# Usage:									#
#										#
# kiriwrite_database_delete(filename, [confirm]);				#
#										#
# filename	Specifies the filename for the database to be deleted.		#
# confirm	Confirms the action to delete a database.			#
#################################################################################

	my ($database_filename, $database_confirm) = @_;

	# Check if the confirm value is blank and if it is then set the
	# confirm value to 0.

	if (!$database_confirm){

		$database_confirm = 0;

	}

	# Connect to the database server.

	$kiriwrite_dbmodule->connect();

	# Check if any errors occured while connecting to the database server.

	if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

		# A database connection error has occured so return
		# an error.

		kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

	}

	# Check if the database filename given is valid and return an error
	# if it isn't.

	kiriwrite_variablecheck($database_filename, "filename", "", 0);

	# Check if the request to delete a database has been confirmed. If it has, 
	# then delete the database itself.

	if ($database_confirm eq 1){
		# There is a value in the confirm variable of the HTTP query.

		# Select the database to delete and get the database name.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $database_filename });

		# Check if any error occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet") {

			# The database has invalid permissions set so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		my %database_info	= $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors have occured while getting the database
		# name.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error with
			# the extended error information.

			kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

		}

		my $database_name = $database_info{"DatabaseName"};

		# Delete the selected database.

		$kiriwrite_dbmodule->deletedatabase({ DatabaseName => $database_filename });

		# Check if any error occured while deleting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet") {

			# The database has invalid permissions set so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# Write a message saying that the database has been deleted.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{deleteddatabase}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{database}->{deleteddatabasemessage}, $database_name));
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=db", { Text => $kiriwrite_lang->{database}->{databaselistreturnlink} }); 

		return $kiriwrite_presmodule->grab();

	}

	# The action has not been confirmed, so write out a form asking the 
	# user to confirm.

	# Get the database name.

	$kiriwrite_dbmodule->selectdb({ DatabaseName => $database_filename });

	# Check if any error occured while selecting the database.

	if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

		# The database does not exist so return an error.

		kiriwrite_error("databasemissingfile");

	} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet") {

		# The database has invalid permissions set so return
		# an error.

		kiriwrite_error("databaseinvalidpermissions");


	}

	# Check if any errors have occured.

	my %database_info	= $kiriwrite_dbmodule->getdatabaseinfo();

	if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

		# A database error has occured so return an error with
		# the extended error information.

		kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

	}

	my $database_name = $database_info{"DatabaseName"};

	# Disconnect from the database server.

	$kiriwrite_dbmodule->disconnect();

	# Write out the form to ask the user to confirm the deletion of the 
	# selected database.

	$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{deletedatabase}, { Style => "pageheader" });
	$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
	$kiriwrite_presmodule->startbox();
	$kiriwrite_presmodule->addhiddendata("mode", "db");
	$kiriwrite_presmodule->addhiddendata("action", "delete");
	$kiriwrite_presmodule->addhiddendata("database", $database_filename);
	$kiriwrite_presmodule->addhiddendata("confirm", "1");
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{database}->{deletedatabasemessage}, $database_name));
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{database}->{deletedatabasebutton});
	$kiriwrite_presmodule->addtext(" | ");
	$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=db", { Text => $kiriwrite_lang->{database}->{deletedatabasereturn} });
	$kiriwrite_presmodule->endbox();
	$kiriwrite_presmodule->endform();

	return $kiriwrite_presmodule->grab();

}

sub kiriwrite_database_list{
#################################################################################
# kiriwrite_database_list: Lists the databases available.			#
#										#
# Usage:									#
# 										#
# kiriwrite_database_list();							#
#################################################################################

	# Connect to the database server.

	$kiriwrite_dbmodule->connect();

	# Check if any errors occured while connecting to the database server.

	if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

		# A database connection error has occured so return
		# an error.

		kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

	}

	# Get the list of available databases and process any errors that
	# might have occured.

	my @database_list = $kiriwrite_dbmodule->getdblist();

	if ($kiriwrite_dbmodule->geterror eq "DataDirMissing"){

		# The database directory is missing so return an error.

		kiriwrite_error("datadirectorymissing");

	} elsif ($kiriwrite_dbmodule->geterror eq "DataDirInvalidPermissions"){

		# The database directory has invalid permissions set so return
		# an error.

		kiriwrite_error("datadirectoryinvalidpermissions");

	}

	# Declare the following variables that are going to be used before using 
	# the foreach function.

	my ($database_info, %database_info);
	my @error_list;
	my @permissions_list;
	my $database_count = 0;
	my $database_filename = "";
	my $database_filename_friendly = "";
	my $database_filename_length = 0;
	my $database_name = "";
	my $database_description = "";
	my $database_permissions = "";
	my $nodescription = 0;
	my $noname = 0;
	my $data_file = "";
	my $table_style = 0;
	my $table_style_name = "";

	# Begin creating the table for the list of databases.

	$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databaselist}, { Style => "pageheader" });
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->starttable("", { CellPadding => "5", CellSpacing => "0" });
	$kiriwrite_presmodule->startheader();
	$kiriwrite_presmodule->addheader($kiriwrite_lang->{database}->{databasename}, { Style => "tablecellheader" });
	$kiriwrite_presmodule->addheader($kiriwrite_lang->{database}->{databasedescription}, { Style => "tablecellheader" });
	$kiriwrite_presmodule->addheader($kiriwrite_lang->{database}->{databaseoptions}, { Style => "tablecellheader" });
	$kiriwrite_presmodule->endheader();

	foreach $data_file (@database_list){

		# Select the database.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $data_file });

		# Check if any error occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so process the next
			# database.

			next;

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet") {

			# The database has invalid permissions settings, so
			# add the database to the list of databases with
			# invalid permissions set and process the next
			# database.

			push(@permissions_list, $data_file);
			next;

		}

		# Get information about the database.

		%database_info = $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any error occured while getting information from the
		# database.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured, add the database and specific
			# error message to the list of databases with errors and
			# process the next database.

			push(@error_list, $data_file . ": " . $kiriwrite_dbmodule->geterror(1));
			next;

		}

		$database_name		= $database_info{"DatabaseName"};
		$database_description 	= $database_info{"Description"};

		# Check the style to be used with.

		if ($table_style eq 0){

			# Use the first style and set the style value
			# to use the next style, the next time the
			# if statement is checked.

			$table_style_name = "tablecell1";
			$table_style = 1;
		} else {

			# Use the second style and set the style
			# value to use the first style, the next
			# time if statement is checked.

			$table_style_name = "tablecell2";
			$table_style = 0;
		}

		# Create a friendly name for the database.

		$database_filename_friendly = $data_file;

		# Append the database information to the table.

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell($table_style_name);

		if (!$database_name){
			$kiriwrite_presmodule->additalictext($kiriwrite_lang->{blank}->{noname});
		} else {
			$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database_filename_friendly, { Text => $database_name });
		}

		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell($table_style_name);

		if (!$database_description){
			$kiriwrite_presmodule->additalictext($kiriwrite_lang->{blank}->{nodescription});
		} else {
			$kiriwrite_presmodule->addtext($database_description);
		}

		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell($table_style_name);
		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=db&action=edit&database=" . $database_filename_friendly, { Text => $kiriwrite_lang->{options}->{edit} });
		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=compile&action=compile&type=single&database=" . $database_filename_friendly, { Text => $kiriwrite_lang->{options}->{compile} });
		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=db&action=delete&database=" . $database_filename_friendly, { Text => $kiriwrite_lang->{options}->{delete} });
		$kiriwrite_presmodule->endrow();

		$database_count++;
		$nodescription = 0;
		$noname = 0;

	}

	$kiriwrite_presmodule->endtable();

	# Disconnect from the database server.

	$kiriwrite_dbmodule->disconnect();

	# Check if there are no valid databases are if there is no
	# valid databases then write a message saying that no
	# valid databases are available.

	if ($database_count eq 0){

		$kiriwrite_presmodule->clear();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databaselist}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->startbox("errorbox");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{nodatabasesavailable});
		$kiriwrite_presmodule->endbox();

	}

	# Check if any databases with problems have appeared and if they
	# have, print out a message saying which databases have problems.

	if (@permissions_list){

		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databaseinvalidpermissions}, { Style => "smallpageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databaseinvalidpermissionstext});
		$kiriwrite_presmodule->addlinebreak();

		foreach $data_file (@permissions_list){
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addtext($data_file);
		}

		$kiriwrite_presmodule->addlinebreak();

	}

	if (@error_list){

		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databaseerrors}, { Style => "smallpageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databaseerrorstext});
		$kiriwrite_presmodule->addlinebreak();

		foreach $data_file (@error_list){
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addtext($data_file);
		}

		$kiriwrite_presmodule->addlinebreak();

	}

	return $kiriwrite_presmodule->grab();	# Return to the main part of the script with the processed information.

}


sub kiriwrite_filter_list{
#################################################################################
# kiriwrite_filter_list: Lists the filters that will be used when compiling a	#
# webpage.									#
#										#
# Usage:									#
#										#
# kiriwrite_filter_list();							#
#################################################################################

	my $filtersdb_notexist = 0;

	# Connect to the database server.

	$kiriwrite_dbmodule->connect();

	# Check if any errors occured while connecting to the database server.

	if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

		# A database connection error has occured so return
		# an error.

		kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

	}

	# Connect to the filter database.

	$kiriwrite_dbmodule->connectfilter();

	# Check if any error has occured while connecting to the filter
	# database.

	if ($kiriwrite_dbmodule->geterror eq "FilterDatabaseDoesNotExist"){

		# The filter database does not exist.

		$filtersdb_notexist = 1;

	} elsif ($kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

		# The filter database has invalid permissions set so return
		# an error.

		kiriwrite_error("filtersdbpermissions");

	} elsif ($kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

		# A database error has occured with the filter database.

		kiriwrite_error("filtersdbdatabaseerror", $kiriwrite_dbmodule->geterror(1));

	}

	# Define some variables required for processing the filters list.

	my %filter_list;
	my %filter_info;
	my @database_filters;
	my $blankfindfilter = 0;
	my $filterswarning = "";
	my $filter;
	my $filter_count = 0;
	my $filter_style = 0;
	my $filter_style_name = "";

	tie(%filter_list, 'Tie::IxHash');

	$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{viewfilters}, { Style => "pageheader" });
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();

	# If the filter database exists then get the list of filters,
	# otherwise write a message saying that the filter database
	# does not exist and will be created when a filter is added.

	if ($filtersdb_notexist eq 0){

		# Get the list of available filters.

		@database_filters	= $kiriwrite_dbmodule->getfilterlist();

		# Check if any errors occured while getting the list of filters.

		if ($kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error has occured with the filter database.

			kiriwrite_error("filtersdbdatabaseerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Process each filter getting the priority, find setting and
		# replace setting.

		foreach $filter (@database_filters){

			# Get the information about the filter.

			%filter_info = $kiriwrite_dbmodule->getfilterinfo({ FilterID => $filter });

			# Check if any errors occured while getting the filter information.

			if ($kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

				# A database error occured while using the filter database.

				kiriwrite_error("filtersdbdatabaseerror", $kiriwrite_dbmodule->geterror(1));

			} elsif ($kiriwrite_dbmodule->geterror eq "FilterDoesNotExist"){

				# The filter does not exist so process the next filter.

				next;

			}

			# Check if the find filter is blank.

			if (!$filter_info{"FilterFind"}){

				# The find filter is blank, so set the value to write a warning
				# message saying that a find filter given is blank.

				$blankfindfilter = 1;

			}

			$filter_list{$filter_count}{ID}		= $filter_info{"FilterID"};
			$filter_list{$filter_count}{Priority}	= $filter_info{"FilterPriority"};
			$filter_list{$filter_count}{Find}	= $filter_info{"FilterFind"};
			$filter_list{$filter_count}{Replace}	= $filter_info{"FilterReplace"};
			$filter_list{$filter_count}{Notes}	= $filter_info{"FilterNotes"};

			$filter_count++;

		}

		# Check if there are filters in the filter database and
		# write a message if there isn't.

		if ($filter_count eq 0){

			# There are no filters in the filter database.

			$filterswarning	= $kiriwrite_lang->{filter}->{nofiltersavailable};

		}

	}

	# Check if the database wasn't found and if it
	# wasn't then write a message saying that the
	# database will be created when a filter is
	# added.

	if ($filtersdb_notexist eq 1){

		# The filter database doesn't exist so write
		# a message.

		$filterswarning = $kiriwrite_lang->{filter}->{filterdatabasedoesnotexist};


	}

	# Check if there is a warning message and if
	# there is then write that warning message
	# else write the list of filters.

	if ($filterswarning){

		$kiriwrite_presmodule->startbox("errorbox");
		$kiriwrite_presmodule->addtext($filterswarning);
		$kiriwrite_presmodule->endbox();

	} else {

		# The filter database exists so write out the
		# list of filters.

		if ($blankfindfilter eq 1){

			$kiriwrite_presmodule->addboldtext($kiriwrite_lang->{filter}->{warningtitle});
			$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{blankfindfilters});
			$kiriwrite_presmodule->addtext();
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addlinebreak();

		}

		$kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

		$kiriwrite_presmodule->startheader();
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{filter}->{priority}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{filter}->{findsetting}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{filter}->{replacesetting}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{options}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->endheader();

		foreach $filter (keys %filter_list){

			# Check which style should be used.

			if ($filter_style eq 0){

				$filter_style_name = "tablecell1";
				$filter_style = 1;

			} else {

				$filter_style_name = "tablecell2";
				$filter_style = 0;

			}

			$kiriwrite_presmodule->startrow();
			$kiriwrite_presmodule->addcell($filter_style_name);
			$kiriwrite_presmodule->addtext($filter_list{$filter}{Priority});
			$kiriwrite_presmodule->endcell();
			$kiriwrite_presmodule->addcell($filter_style_name);

			# Check if the find filter is blank.

			if (!$filter_list{$filter}{Find}){

				# The find filter is blank.

				$kiriwrite_presmodule->additalictext($kiriwrite_lang->{filter}->{blankfindsetting});

			} else {

				# The find filter is not blank.

				$kiriwrite_presmodule->addtext($filter_list{$filter}{Find});

			}

			$kiriwrite_presmodule->endcell();
			$kiriwrite_presmodule->addcell($filter_style_name);

			# Check if the replace filter is blank.

			if (!$filter_list{$filter}{Replace}){

				# The replace filter is blank.

				$kiriwrite_presmodule->additalictext($kiriwrite_lang->{filter}->{blankreplacesetting});

			} else {

				# The replace filter is not blank.

				$kiriwrite_presmodule->addtext($filter_list{$filter}{Replace});

			}

			$kiriwrite_presmodule->endcell();
			$kiriwrite_presmodule->addcell($filter_style_name);
			$kiriwrite_presmodule->addlink("?mode=filter&action=edit&filter=" . $filter_list{$filter}{ID}, { Text => $kiriwrite_lang->{options}->{edit} });
			$kiriwrite_presmodule->addlink("?mode=filter&action=delete&filter=" . $filter_list{$filter}{ID}, { Text => $kiriwrite_lang->{options}->{delete} });
			$kiriwrite_presmodule->endcell();
			$kiriwrite_presmodule->endrow();

		}

		$kiriwrite_presmodule->endtable();

	}

	# Disconnect from the filter database.

	$kiriwrite_dbmodule->disconnectfilter();

	# Disconnect from the database server.

	$kiriwrite_dbmodule->disconnect();

	return $kiriwrite_presmodule->grab();

}

sub kiriwrite_filter_add{
#################################################################################
# kiriwrite_filter_add: Adds a filter to the filter list.			#
#										#
# Usage:									#
#										#
# kiriwrite_filter_add(filterfind, filterreplace, filterpriority, 		#
#			filternotes, [confirm]);				#
#										#
# filterfind		Specifies the new word(s) to find.			#
# filterreplace		Specifies the new word(s) to replace.			#
# filterpriority	Specifies the new priority to use.			#
# filternotes		Specifies the new notes to use.				#
# confirm		Confirms the action to add a filter.			#
#################################################################################

	# Get the values that have been passed to the subroutine.

	my ($filter_new_find, $filter_new_replace, $filter_new_priority, $filter_new_notes, $confirm) = @_;

	# Check the confirm value to make sure it is no more than
	# one character long.

	kiriwrite_variablecheck($confirm, "maxlength", 1, 0);

	if (!$confirm){

		# The confirm value is undefined, so set the
		# value of the confirm integer to '0'.

		$confirm = 0;

	}

	if ($confirm eq 1){

		# The confirm integer is '1', so add the word
		# to the filter list.

		# First, check the variables recieved are UTF8
		# copliant.

		kiriwrite_variablecheck($filter_new_find, "utf8", 0, 0);
		kiriwrite_variablecheck($filter_new_replace, "utf8", 0, 0);
		kiriwrite_variablecheck($filter_new_priority, "utf8", 0, 0);
		kiriwrite_variablecheck($filter_new_notes, "utf8", 0, 0);

		# Convert the UTF8 values so that the length can
		# checked properly.

		$filter_new_find 	= kiriwrite_utf8convert($filter_new_find);
		$filter_new_replace	= kiriwrite_utf8convert($filter_new_replace);
		$filter_new_priority	= kiriwrite_utf8convert($filter_new_priority);
		$filter_new_notes	= kiriwrite_utf8convert($filter_new_notes);

		# Check if the find filter is blank and return an error
		# if it is.

		if (!$filter_new_find){

			# The find filter given is blank so return an
			# error.

			kiriwrite_error("blankfindfilter");

		}

		if (!$filter_new_priority){

			# The filter priority is blank so set it
			# to 1.

			$filter_new_priority = 1;

		}

		# Check the length and contents of the values given
		# to make sure they are valid.

		my $filterfind_maxlength_check		= kiriwrite_variablecheck($filter_new_find, "maxlength", 1024, 1);
		my $filterreplace_maxlength_check	= kiriwrite_variablecheck($filter_new_replace, "maxlength", 1024, 1);
		my $filterpriority_maxlength_check	= kiriwrite_variablecheck($filter_new_priority, "maxlength", 5, 1);
		my $filterpriority_numbers_check	= kiriwrite_variablecheck($filter_new_priority, "numbers", 0, 1);

		# Check if the result of the tests to see if they
		# are valid.

		if ($filterfind_maxlength_check eq 1){

			# The find filter is too long, so return
			# an error.

			kiriwrite_error("findfiltertoolong");

		}

		if ($filterreplace_maxlength_check eq 1){

			# The replace filter is too long, so
			# return an error.

			kiriwrite_error("replacefiltertoolong");

		}

		if ($filterpriority_maxlength_check eq 1){

			# The length of the filter priority
			# given is too long, so return an
			# error.

			kiriwrite_error("filterprioritytoolong");

		}

		if ($filterpriority_numbers_check eq 1){

			# The priority of the filter given
			# contains characters other than
			# numbers.

			kiriwrite_error("filterpriorityinvalidchars");

		}

		# Check if the filter priority is less than 1
		# and more than 10000 and return an error
		# if it is.

		if ($filter_new_priority < 1 || $filter_new_priority > 50000){

			# The filter priority is less than 1 and
			# more than 10000, so return an error.

			kiriwrite_error("filterpriorityinvalid");

		}

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Connect to the filter database.

		$kiriwrite_dbmodule->connectfilter(1);

		# Check if any error has occured while connecting to the filter
		# database.

		if ($kiriwrite_dbmodule->geterror eq "FilterDatabaseDoesNotExist"){

			# The filter database does not exist.

			kiriwrite_error("filtersdbmissing");

		} elsif ($kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

			# The filter database has invalid permissions set so return
			# an error.

			kiriwrite_error("filtersdbpermissions");

		}

		# Add the filter to the filter database.

		$kiriwrite_dbmodule->addfilter({ FindFilter => $filter_new_find, ReplaceFilter => $filter_new_replace, Priority => $filter_new_priority, Notes => $filter_new_notes});

		# Check if any errors have occured while adding the filter.

		if ($kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

			# The filter database has invalid permissions set so return
			# an error.

			kiriwrite_error("filtersdbpermissions");

		} elsif ($kiriwrite_dbmodule->geterror eq "FilterDatabaseUncreatable"){

			# The filter database is uncreatable so return an error.

			kiriwrite_error("filterdatabase");

		} elsif ($kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error with the filter database has occured so return
			# an error with the extended error information.

			kiriwrite_error("filtersdbdatabaseerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Disconnect from the filter database.

		$kiriwrite_dbmodule->disconnectfilter();

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# Write out a message saying that the filter was added to the
		# filter database.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{filteradded}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{filteraddedmessage});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=filter", { Text => $kiriwrite_lang->{filter}->{returnfilterlist} });

 		return $kiriwrite_presmodule->grab();

	} elsif ($confirm ne 0) {

		# The confirm integer is another value (which
		# it shouldn't be) so return an error.

		kiriwrite_error("invalidvalue");

	}

	# The confirm integer was blank so print out a form
	# for adding a new filter.

	$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{addfilter}, { Style => "pageheader" });
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
	$kiriwrite_presmodule->startbox();
	$kiriwrite_presmodule->addhiddendata("mode", "filter");
	$kiriwrite_presmodule->addhiddendata("action", "add");
	$kiriwrite_presmodule->addhiddendata("confirm", 1);
	$kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

	$kiriwrite_presmodule->startheader();
	$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{setting}, { Style => "tablecellheader" });
	$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{value}, { Style => "tablecellheader" });
	$kiriwrite_presmodule->endheader();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{findfilter});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addinputbox("findword", { Size => 64, MaxLength => 1024 });
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{replacefilter});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addinputbox("replaceword", { Size => 64, MaxLength => 1024 });
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{priority});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addinputbox("priority", { Size => 5, MaxLength => 5 });
	$kiriwrite_presmodule->startlist();
	$kiriwrite_presmodule->additem($kiriwrite_lang->{filter}->{noprioritygiven});
	$kiriwrite_presmodule->endlist();
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{notes});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addtextbox("notes", { Columns => 50, Rows => 10 });
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->endtable();

	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{filter}->{addfilterbutton});
	$kiriwrite_presmodule->addtext(" | ");
	$kiriwrite_presmodule->addreset($kiriwrite_lang->{common}->{clearvalues});
	$kiriwrite_presmodule->addtext(" | ");
	$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=filter", { Text => $kiriwrite_lang->{filter}->{returnfilterlist} });

	$kiriwrite_presmodule->endbox();
	$kiriwrite_presmodule->endform();

	return $kiriwrite_presmodule->grab();

}

sub kiriwrite_filter_edit{
#################################################################################
# kiriwrite_filter_edit: Edits a filter from the filter list.			#
#										#
# Usage:									#
#										#
# kiriwrite_filter_edit(filternumber, newfilterfind, newfilterreplace,		#
#			newfilterpriority, newfilternotes, confirm);		#
#										#
# filterid		Specifies the filter number (line number) in the	#
#			filter database.					#
# newfilterfind		Specifies the new word to find.				#
# newfilterreplace	Specifies the new word to replace.			#
# newfilterpriority	Specifies the new filter priority.			#
# newfilternotes	Specifies the new filter notes.				#
# confirm		Confirms the action to edit a filter.			#
#################################################################################

	# Get the values that have been passed to the subroutine.

	my ($filter_id, $filter_new_find, $filter_new_replace, $filter_new_priority, $filter_new_notes, $confirm) = @_;

	# Check the confirm value to make sure it is no more than
	# one character long.

	kiriwrite_variablecheck($confirm, "maxlength", 1, 0);

	# Check if the confirm value is blank and if it is
	# srt the confirm value to 0.

	if (!$confirm){

		# The confirm value does not have any value
		# set so set it to 0.

		$confirm = 0;

	}

	# Check if the filter identification number is blank,
	# contains characters other than numbers and is more
	# than seven characters long.

	if (!$filter_id){

		# The filter identification number is blank,
		# so return an error.

		kiriwrite_error("filteridblank");

	}

	my $filter_id_numbers_check	= kiriwrite_variablecheck($filter_id, "numbers", 0, 1);

	if ($filter_id_numbers_check eq 1){

		# The filter identification number contains
		# characters other than numbers, so return
		# an error.

		kiriwrite_error("filteridinvalid");

	}

	my $filter_id_maxlength_check	= kiriwrite_variablecheck($filter_id, "maxlength", 7, 1);

	if ($filter_id_maxlength_check eq 1){

		# The filter identification number given
		# is more than seven characters long, so
		# return an error.

		kiriwrite_error("filteridtoolong");

	}

 	my $filter_priority;
 	my $filter_find;
 	my $filter_replace;
 	my $filter_notes;
 
	# Check if the action to edit a filter has been
	# confirmed.

	if ($confirm eq 1){

		# The action to edit a filter has been confirmed so
		# edit the selected filter.

		# First, check the variables recieved are UTF8
		# copliant.

		kiriwrite_variablecheck($filter_new_find, "utf8", 0, 0);
		kiriwrite_variablecheck($filter_new_replace, "utf8", 0, 0);
		kiriwrite_variablecheck($filter_new_priority, "utf8", 0, 0);
		kiriwrite_variablecheck($filter_new_notes, "utf8", 0, 0);

		# Convert the UTF8 values so that the length can
		# checked properly.

		$filter_find 		= kiriwrite_utf8convert($filter_new_find);
		$filter_replace		= kiriwrite_utf8convert($filter_new_replace);
		$filter_priority	= kiriwrite_utf8convert($filter_new_priority);
		$filter_notes		= kiriwrite_utf8convert($filter_new_notes);

		# Check if the find filter is blank and return an error
		# if it is.

		if (!$filter_new_find){

			# The find filter given is blank so return an
			# error.

			kiriwrite_error("blankfindfilter");

		}

		if (!$filter_new_priority){

			# The filter priority is blank so set it
			# to 1.

			$filter_new_priority = 1;

		}

		# Check the length and contents of the values given
		# to make sure they are valid.

		my $filterfind_maxlength_check		= kiriwrite_variablecheck($filter_new_find, "maxlength", 1024, 1);
		my $filterreplace_maxlength_check	= kiriwrite_variablecheck($filter_new_replace, "maxlength", 1024, 1);
		my $filterpriority_maxlength_check	= kiriwrite_variablecheck($filter_new_priority, "maxlength", 5, 1);
		my $filterpriority_numbers_check	= kiriwrite_variablecheck($filter_new_priority, "numbers", 0, 1);

		# Check if the result of the tests to see if they
		# are valid.

		if ($filterfind_maxlength_check eq 1){

			# The find filter is too long, so return
			# an error.

			kiriwrite_error("findfiltertoolong");

		}

		if ($filterreplace_maxlength_check eq 1){

			# The replace filter is too long, so
			# return an error.

			kiriwrite_error("replacefiltertoolong");

		}

		if ($filterpriority_maxlength_check eq 1){

			# The length of the filter priority
			# given is too long, so return an
			# error.

			kiriwrite_error("filterprioritytoolong");

		}

		if ($filterpriority_numbers_check eq 1){

			# The priority of the filter given
			# contains characters other than
			# numbers.

			kiriwrite_error("filterpriorityinvalidchars");

		}

		# Check if the filter priority is less than 1
		# and more than 10000 and return an error
		# if it is.

		if ($filter_new_priority < 1 || $filter_new_priority > 50000){

			# The filter priority is less than 1 and
			# more than 10000, so return an error.

			kiriwrite_error("filterpriorityinvalid");

		}

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Connect to the filter database.

		$kiriwrite_dbmodule->connectfilter();

		# Check if any error has occured while connecting to the filter
		# database.

		if ($kiriwrite_dbmodule->geterror eq "FilterDatabaseDoesNotExist"){

			# The filter database does not exist.

			kiriwrite_error("filtersdbmissing");

		} elsif ($kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

			# The filter database has invalid permissions set so return
			# an error.

			kiriwrite_error("filtersdbpermissions");

		} elsif ($kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error has occured with the filter database.

			kiriwrite_error("filtersdbdatabaseerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Edit the selected filter in the filter database.

		$kiriwrite_dbmodule->editfilter({ FilterID => $filter_id, NewFindFilter => $filter_new_find, NewReplaceFilter => $filter_new_replace, NewFilterPriority => $filter_new_priority, NewFilterNotes => $filter_new_notes });

		# Check if any errors occured while editing the filter.

		if ($kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

			# The filter database has invalid permissions set so return
			# an error.

			kiriwrite_error("filtersdbpermissions");

		} elsif ($kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error has occured while using the filter database
			# so return an error.

			kiriwrite_error("filtersdbdatabaseerror", $kiriwrite_dbmodule->geterror(1));

		} elsif ($kiriwrite_dbmodule->geterror eq "FilterDoesNotExist"){

			# The specified filter does not exist so return an error.

			kiriwrite_error("filterdoesnotexist");

		}

		# Disconnect from the filter database.

		$kiriwrite_dbmodule->disconnectfilter();

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# Write a message saying that the filter was edited.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{editedfilter}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{editedfiltermessage});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=filter", { Text => $kiriwrite_lang->{filter}->{returnfilterlist}});

		return $kiriwrite_presmodule->grab();

	} elsif ($confirm eq 0){

		# The action to edit a filter has not been confirmed
		# so write a form for editing the filter with.

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Connect to the filter database.

		$kiriwrite_dbmodule->connectfilter();

		# Check if any error has occured while connecting to the filter
		# database.

		if ($kiriwrite_dbmodule->geterror eq "FilterDatabaseDoesNotExist"){

			# The filter database does not exist.

			kiriwrite_error("filtersdbmissing");

		} elsif ($kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

			# The filter database has invalid permissions set so return
			# an error.

			kiriwrite_error("filtersdbpermissions");

		} elsif ($kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error has occured with the filter database.

			kiriwrite_error("filtersdbdatabaseerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Get information about the filter.

		my %filter_info = $kiriwrite_dbmodule->getfilterinfo({ FilterID => $filter_id });

		# Check if any errors occured while getting information about the filter.

		if ($kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error occured while using the filter database so
			# return an error.

			kiriwrite_error("filtersdbdatabaseerror", $kiriwrite_dbmodule->geterror(1));

		} elsif ($kiriwrite_dbmodule->geterror eq "FilterDoesNotExist"){

			# The filter does not exist so return an error.

			kiriwrite_error("filterdoesnotexist");

		}

		# Get the required information.

		$filter_priority	= $filter_info{"FilterPriority"};
		$filter_find		= $filter_info{"FilterFind"};
		$filter_replace		= $filter_info{"FilterReplace"};
		$filter_notes		= $filter_info{"FilterNotes"};

		# Disconnect from the filter database.

		$kiriwrite_dbmodule->disconnectfilter();

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# Write out the form.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{editfilter}, { Style => "pageheader" });
		$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addhiddendata("mode", "filter");
		$kiriwrite_presmodule->addhiddendata("action", "edit");
		$kiriwrite_presmodule->addhiddendata("filter", $filter_id);
		$kiriwrite_presmodule->addhiddendata("confirm", 1);

		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

		$kiriwrite_presmodule->startheader();
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{setting}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{value}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->endheader();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{findfilter});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("filterfind", { Size => 64, MaxLength => 1024, Value => $filter_find });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{replacefilter});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("filterreplace", { Size => 64, MaxLength => 1024, Value => $filter_replace });
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{priority});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addinputbox("priority", { Size => 5, MaxLength => 5, Value => $filter_priority });
		$kiriwrite_presmodule->startlist();
		$kiriwrite_presmodule->additem($kiriwrite_lang->{filter}->{noprioritygiven});
		$kiriwrite_presmodule->endlist();
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->startrow();
		$kiriwrite_presmodule->addcell("tablecell1");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{notes});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->addcell("tablecell2");
		$kiriwrite_presmodule->addtextbox("notes", { Columns => 50, Rows => 10});
		$kiriwrite_presmodule->endcell();
		$kiriwrite_presmodule->endrow();

		$kiriwrite_presmodule->endtable();

		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{filter}->{editfilterbutton});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addreset($kiriwrite_lang->{common}->{restorecurrent});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=filter", { Text => $kiriwrite_lang->{filter}->{returnfilterlist} });
		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endform();

		return $kiriwrite_presmodule->grab(); 

	} else {

		# A confirm value other than 0 or 1 has been
		# specified, so return an error.

		kiriwrite_error("invalidvalue");

	}

}

sub kiriwrite_filter_delete{
#################################################################################
# kiriwrite_filter_delete: Deletes a filter from the filter list.		#
# 										#
# Usage:									#
# 										#
# kiriwrite_filter_delete(filterid, confirm);					#
#										#
# filterid	Specifies the filter line number to delete.			#
# confirm	Confirms the deletion of the selected filter.			#
#################################################################################

	# Get the values that were passed to this subroutine.

	my ($filter_id, $confirm) = @_;

	# Check the confirm value to make sure it is no more than
	# one character long.

	kiriwrite_variablecheck($confirm, "maxlength", 1, 0);

	# Check if the confirm value is blank and if it is
	# srt the confirm value to 0.

	if (!$confirm){

		# The confirm value does not have any value
		# set so set it to 0.

		$confirm = 0;

	}

	# Check if the filter identification number is blank,
	# contains characters other than numbers and is more
	# than seven characters long.

	if (!$filter_id){

		# The filter identification number is blank,
		# so return an error.

		kiriwrite_error("filteridblank");

	}

	my $filter_id_numbers_check	= kiriwrite_variablecheck($filter_id, "numbers", 0, 1);

	if ($filter_id_numbers_check eq 1){

		# The filter identification number contains
		# characters other than numbers, so return
		# an error.

		kiriwrite_error("filteridinvalid");

	}

	my $filter_id_maxlength_check	= kiriwrite_variablecheck($filter_id, "maxlength", 7, 1);

	if ($filter_id_maxlength_check eq 1){

		# The filter identification number given
		# is more than seven characters long, so
		# return an error.

		kiriwrite_error("filteridtoolong");

	}

	# Define some values for later.

	my @database_filter;
	my $filter_exists = 0;

	# Check if the confirm integer has a value of '1'.

	if ($confirm eq 1){

		# The action to delete a filter has been confirmed.

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Connect to the filter database.

		$kiriwrite_dbmodule->connectfilter();

		# Check if any error has occured while connecting to the filter
		# database.

		if ($kiriwrite_dbmodule->geterror eq "FilterDatabaseDoesNotExist"){

			# The filter database does not exist.

			kiriwrite_error("filtersdbmissing");

		} elsif ($kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

			# The filter database has invalid permissions set so return
			# an error.

			kiriwrite_error("filtersdbpermissions");

		} elsif ($kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error has occured with the filter database.

			kiriwrite_error("filtersdbdatabaseerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Delete the filter from the filter database.

		$kiriwrite_dbmodule->deletefilter({ FilterID => $filter_id });

		# Check if any errors occured while deleting the filter.

		if ($kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error has occured while trying to delete a filter so
			# return an error.

			kiriwrite_error("filtersdbdatabaseerror", $kiriwrite_dbmodule->geterror(1));

		} elsif ($kiriwrite_dbmodule->geterror eq "FilterDoesNotExist"){

 			# The filter does not exist so return an error.
 
 			kiriwrite_error("filterdoesnotexist");

		}

		# Disconnect from the filter database.

		$kiriwrite_dbmodule->disconnectfilter();

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		# Write a message saying that the filter was deleted
		# from the filter database.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{deletedfilter}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{deletedfiltermessage});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=filter", { Text => $kiriwrite_lang->{filter}->{returnfilterlist} });

	} elsif ($confirm eq 0) {

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Connect to the filter database.

		$kiriwrite_dbmodule->connectfilter();

		# Check if any error has occured while connecting to the filter
		# database.

		if ($kiriwrite_dbmodule->geterror eq "FilterDatabaseDoesNotExist"){

			# The filter database does not exist.

			kiriwrite_error("filtersdbmissing");

		} elsif ($kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

			# The filter database has invalid permissions set so return
			# an error.

			kiriwrite_error("filtersdbpermissions");

		} elsif ($kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error has occured with the filter database.

			kiriwrite_error("filtersdbdatabaseerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Get information about the filter (to check if it exists).

		my %filter_info = $kiriwrite_dbmodule->getfilterinfo({ FilterID => $filter_id });

		# Check if any errors occured while getting information about the filter.

		if ($kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error occured while using the filter database so
			# return an error.

			kiriwrite_error("filtersdbdatabaseerror", $kiriwrite_dbmodule->geterror(1));

		} elsif ($kiriwrite_dbmodule->geterror eq "FilterDoesNotExist"){

			# The filter does not exist so return an error.

			kiriwrite_error("filterdoesnotexist");

		}

		# Disconnect from the filter database.

		$kiriwrite_dbmodule->disconnectfilter();

		# Disconnect from the database

		# The confirm integer is '0', so continue write out
		# a form asking the user to confirm the deletion
		# pf the filter.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{deletefilter}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{filter}->{deletefiltermessage});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addhiddendata("mode", "filter");
		$kiriwrite_presmodule->addhiddendata("action", "delete");
		$kiriwrite_presmodule->addhiddendata("filter", $filter_id);
		$kiriwrite_presmodule->addhiddendata("confirm", 1);
		$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{filter}->{deletefilterbutton});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=filter", { Text => $kiriwrite_lang->{filter}->{deletefilterreturn} });
 		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endform();

	} else {

		kiriwrite_error("invalidvalue");

	}

	return $kiriwrite_presmodule->grab();

}

sub kiriwrite_compile_makepages{
#################################################################################
# kiriwrite_compile_makepages: Compile the selected pages and place them in the #
# specified output directory.							#
#										#
# Usage:									#
#										#
# kiriwrite_compile_makepages(type, selectedlist, confirm);			#
#										#
# type		Specifies if single or multiple databases are to be compiled.	#
# confirm	Specifies if the action to compile the databases should really	#
#		be done.							#
# selectedlist	Specifies the databases to compile from as an array.		#
#################################################################################

	# Get the values that have been passed to the subroutine.

	my ($type, $confirm, @selectedlist) = @_;

	# Check if the confirm value is more than one
	# character long.

	kiriwrite_variablecheck($confirm, "maxlength", 1, 0);

	# Check if the confirm value is blank and if it
	# is then set the confirm value to 0.

	if (!$confirm){

		# The confirm value is blank, so set the
		# confirm value to 0.

		$confirm = 0;

	}

	# Check if there are any databases selected
	# and return an error if there isn't.

	if (!@selectedlist){

		# There are no databases in the array
		# so return an error.

		kiriwrite_error("nodatabaseselected");

	}

	# Check if the type given is no more than
	# 7 characters long.

	my $type_maxlength_check = kiriwrite_variablecheck($type, "maxlength", 8, 1);

	if ($type_maxlength_check eq 1){

		# The type length given is too long so
		# return an error.

		kiriwrite_error("variabletoolong");

	}

	# Check if the action to compile the databases
	# has been confirmed.

	if ($confirm eq 1){

		# The action to compile the datavases has
		# been confirmed.

		# Define some variables for later.

		my %database_info;
		my %filter_info;
		my %template_info;
		my %page_info;
		my %templatefiles;
		my @page_filenames;
		my @databaseinfo;
		my @databasepages;
		my @filterslist;
		my @findfilter;
		my @replacefilter;
		my @templateslist;
		my @pagedirectories;
		my @database_filters;
		my $warning_count 		= 0;
		my $error_count 		= 0;
		my $pages_count			= 0;
		my $filter;
		my $filters_count		= 0;
		my $filters_find_blank_warning	= 0;
		my $filter_find;
		my $filter_replace;
		my $database;
		my $database_name;
		my $page_filename;
		my $page_filename_check;
		my $page_filename_char		= "";
		my $page_filename_directory;
 		my $page_filename_length	= 0;
 		my $page_filename_seek 		= 0;
 		my $page_filename_dircount	= 0;
		my $page_filename_exists	= 0;
		my $page_filename_permissions	= 0;
 		my $page_directory_name;
 		my $page_directory_path;
		my $page_name;
		my $page_description;
		my $page_section;
		my $page_template;
		my $page_content;
		my $page_settings;
		my $page_lastmodified;
		my $page_title;
		my $page_final;
		my $page_autosection;
		my $page_autotitle;
		my $page;
		my $database_filename_check	= 0;
		my $database_maxlength_check	= 0;
		my $output_exists		= 0;
		my $output_permissions		= 0;
		my $filters_exists		= 0;
		my $filters_permissions		= 0;
		my $filters_skip		= 0;
  		my $template;
		my $templates_skip		= 0;
		my $information_prefix		= $kiriwrite_lang->{compile}->{informationprefix};
		my $error_prefix		= $kiriwrite_lang->{compile}->{errorprefix};
		my $warning_prefix		= $kiriwrite_lang->{compile}->{warningprefix};
		my $filehandle_page;

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{compile}->{compiledatabases}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->startbox("datalist");

		# Check if the output directory exists and has
		# valid permissions set.

		$output_exists		= kiriwrite_fileexists($kiriwrite_config{'directory_data_output'});

		if ($output_exists ne 0){

			# The output directory does not exist so
			# return an error.

			kiriwrite_error("outputdirectorymissing");

		}

		$output_permissions	= kiriwrite_filepermissions($kiriwrite_config{'directory_data_output'}, 1, 1);

		if ($output_permissions ne 0){

			# The output directory has invalid
			# permissions set so return an error.

			kiriwrite_error("outputdirectoryinvalidpermissions");

		}

		# Connect to the database server.

		$kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

		}

		# Connect to the filter database.

		$kiriwrite_dbmodule->connectfilter();

		# Check if any error has occured while connecting to the filter
		# database.

		if ($kiriwrite_dbmodule->geterror eq "FilterDatabaseDoesNotExist"){

			# The filter database does not exist so write a warning message.

 			$kiriwrite_presmodule->addtext($warning_prefix . $kiriwrite_lang->{compile}->{filterdatabasemissing});
 			$kiriwrite_presmodule->addlinebreak();
 			$filters_skip = 1;
 			$warning_count++;

		} elsif ($kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

			# The filter database has invalid permissions set so write a
			# an error message.

			$kiriwrite_presmodule->addtext($error_prefix . $kiriwrite_lang->{compile}->{filterdatabasepermissions});
			$kiriwrite_presmodule->addlinebreak();
			$filters_skip = 1;
			$error_count++;

		}

		# Load the filter database (if the filters skip
		# value isn't set to 1).

		if ($filters_skip eq 0){

			# Get the list of available filters.

			@database_filters	= $kiriwrite_dbmodule->getfilterlist();

			# Check if any errors occured while getting the list of filters.

			if ($kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

				# A database error has occured with the filter database.

				$kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($kiriwrite_lang->{compile}->{filterdatabaseerror}, $kiriwrite_dbmodule->geterror(1)));
				$kiriwrite_presmodule->addlinebreak();
				$error_count++;

			}

			# Check if the filters skip value is set to 0
			# before executing the query.

			if ($filters_skip eq 0){

				foreach $filter (@database_filters){

					# Get the filter information.

					%filter_info = $kiriwrite_dbmodule->getfilterinfo({ FilterID => $filter });

					# Check if any errors occured while getting the filter information.

					if ($kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

						# A database error occured while using the filter database.

						$kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($kiriwrite_lang->{compile}->{filterdatabaseerror}, $kiriwrite_dbmodule->geterror(1)));
						$kiriwrite_presmodule->addlinebreak();
						$error_count++;
						next;

					} elsif ($kiriwrite_dbmodule->geterror eq "FilterDoesNotExist"){

						# The filter does not exist so process the next filter.

						next;

					}

					# Check if the find filter is blank and
					# if it is then write a warning message.

					if (!$filter_info{"FilterFind"}){

						if ($filters_find_blank_warning ne 1){

							$kiriwrite_presmodule->addtext($warning_prefix . $kiriwrite_lang->{compile}->{findfilterblank});
							$kiriwrite_presmodule->addlinebreak();
							$filters_find_blank_warning = 1;
						}
						next;

					} else {

						# Add each find and replace filter.

						$findfilter[$filters_count]	= $filter_info{"FilterFind"};
						$replacefilter[$filters_count]	= $filter_info{"FilterReplace"};

					}

					$filters_count++;

				}

 				$kiriwrite_presmodule->addtext($information_prefix . $kiriwrite_lang->{compile}->{finishfilterdatabase});
 				$kiriwrite_presmodule->addlinebreak();

			}

		}

		# Disconnect from the filter database.

		$kiriwrite_dbmodule->disconnectfilter();

		# Connect to the template database.

		$kiriwrite_dbmodule->connecttemplate();

		# Check if any errors occured while connecting to the template database.

		if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseDoesNotExist"){

			# The template database does not exist so set the template
			# warning message.

 			$kiriwrite_presmodule->addtext($warning_prefix . $kiriwrite_lang->{compile}->{templatedatabasemissing});
 			$kiriwrite_presmodule->addlinebreak();
 			$templates_skip = 1;
 			$warning_count++;

		} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so write
			# the template warning message.
 
 			$kiriwrite_presmodule->addtext($error_prefix . $kiriwrite_lang->{compile}->{templatedatabasepermissions});
 			$kiriwrite_presmodule->addlinebreak();
 			$templates_skip = 1;
 			$error_count++;

		}

		# Check if the template skip value isn't set and if it isn't
		# then get the list of templates.

		if (!$templates_skip){

			@templateslist = $kiriwrite_dbmodule->gettemplatelist();

			# Check if any errors had occured.

			if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

				# A database error occured while getting the list
				# of templates so return a warning message with the 
				# extended error information.

				$kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($kiriwrite_lang->{compile}->{templatedatabaseerror}, $kiriwrite_dbmodule->geterror(1)));
				$templates_skip = 1;
				$error_count++;

			}

			# Check if the template skip value isn't set and if it isn't
			# then process each template.

			if (!$templates_skip){

				# Process each template.

				foreach $template (@templateslist){

					# Get information about the template.

					%template_info = $kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $template });

					# Check if any error occured while getting the template information.

					if ($kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

						# A database error has occured, so return an error.

						$kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($kiriwrite_lang->{compile}->{templatedatabaseerror}, $kiriwrite_dbmodule->geterror(1)));
						$error_count++;

					} elsif ($kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

						# The template does not exist, so process the next template.

						next;

					}

 					# Place each template file into the hash.

 					$templatefiles{$template_info{"TemplateFilename"}}{template} 	= $template_info{"TemplateLayout"};
 					$templatefiles{$template_info{"TemplateFilename"}}{valid} 	= 1;

				}

 				$kiriwrite_presmodule->addtext($information_prefix . $kiriwrite_lang->{compile}->{finishtemplatedatabase});
 				$kiriwrite_presmodule->addlinebreak();

			}

		}

		# Disconnect from the template database.

		$kiriwrite_dbmodule->disconnecttemplate();

		# Process each database.

		foreach $database (@selectedlist){

			# Check if the database filename and length
			# are valid.

			$kiriwrite_presmodule->addhorizontalline();

			$database_filename_check	= kiriwrite_variablecheck($database, "page_filename", "", 1);
			$database_maxlength_check	= kiriwrite_variablecheck($database, "maxlength", 32, 1);

			if ($database_filename_check ne 0){

				# The database filename is invalid, so process
				# the next database.

				$kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($kiriwrite_lang->{compile}->{databasefilenameinvalidcharacters}, $database));
				$kiriwrite_presmodule->addlinebreak();
				$error_count++;
				next;

			}

			if ($database_maxlength_check ne 0){

				# The database file is too long, so process the
				# next database.

				$kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($kiriwrite_lang->{compile}->{databasefilenametoolong}, $database));
				$kiriwrite_presmodule->addlinebreak();
				$error_count++;
				next;

			}

			# Select the database.

			$kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

			# Check if any errors had occured while selecting the database.

			if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

				# The database does not exist, so write a warning message.

				$kiriwrite_presmodule->addtext($warning_prefix . kiriwrite_language($kiriwrite_lang->{compile}->{databasemissing}, $database));
				$kiriwrite_presmodule->addlinebreak();
				$warning_count++;
				next;

			} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

				# The database has invalid permissions set, so write
				# an error message.

				$kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($kiriwrite_lang->{compile}->{databaseinvalidpermissions}, $database));
				$kiriwrite_presmodule->addlinebreak();
				$error_count++;
				next;

			}

			# Get information about the database.

			my %database_info = $kiriwrite_dbmodule->getdatabaseinfo();

			# Check if any error occured while getting the database information.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so write an error.

				$kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($kiriwrite_lang->{compile}->{databaseerror}, $database, $kiriwrite_dbmodule->geterror(1)));
				$kiriwrite_presmodule->addlinebreak();
				$error_count++;
				next;

			};

			# Get the database name.

			$database_name = $database_info{"DatabaseName"};

			$kiriwrite_presmodule->addtext($information_prefix . kiriwrite_language($kiriwrite_lang->{compile}->{compilingpages}, $database_name));
			$kiriwrite_presmodule->addlinebreak();

			# Get the list of pages in the database.

			@databasepages = $kiriwrite_dbmodule->getpagelist();

			# Check if any errors occured while getting the list of pages.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				$kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($kiriwrite_lang->{compile}->{databasepageerror}, $database, $kiriwrite_dbmodule->geterror(1)));
				$kiriwrite_presmodule->addlinebreak();
				$error_count++;
				next;

			}

			foreach $page (@databasepages) {

				# Get information about the page.

				%page_info = $kiriwrite_dbmodule->getpageinfo({ PageFilename => $page });

				$page_filename		= $page_info{"PageFilename"};
				$page_name		= $page_info{"PageName"};
				$page_description	= $page_info{"PageDescription"};
				$page_section		= $page_info{"PageSection"};
				$page_template		= $page_info{"PageTemplate"};
				$page_content		= $page_info{"PageContent"};
				$page_settings		= $page_info{"PageSettings"};
				$page_lastmodified	= $page_info{"PageLastModified"};

				# Check if the filename is valid.

				$page_filename_check = kiriwrite_variablecheck($page_filename, "page_filename", 0, 1);

				if ($page_filename_check ne 0){

					# The file name is not valid so write a
					# error and process the next page.

					$kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($kiriwrite_lang->{compile}->{invalidpagefilename}, $page_name));
					$kiriwrite_presmodule->addlinebreak();
					$error_count++;
					next;

				}

				# Check if the template with the filename does not exist
				# in the template files hash and write a message and
				# process the next page.

				if (!$templatefiles{$page_template}{valid} && $page_template ne "!none" && $templates_skip eq 0){

					$kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($kiriwrite_lang->{compile}->{templatefilemissing}, $page_template, $page_name, $page_filename));
					$kiriwrite_presmodule->addlinebreak();
					$error_count++;
					next;

					$page_final = $page_content;

				} elsif ($page_template eq "!none"){

					$page_final = $page_content;

				} else {

					$page_final = $templatefiles{$page_template}{template};

					if (!$page_final){
						$page_final = "";
					}

					$page_final =~ s/<kiriwrite:pagecontent>/$page_content/g;

				}

				# Create the combined page title (if needed).

				if ($page_settings eq 0 || $page_settings > 3){

					# Don't use page name or section name.

					$page_final =~ s/<kiriwrite:pagetitle>//g;

				} elsif ($page_settings eq 1){

					# Use the page name and section name.

					$page_autotitle = "(" . $page_section . " - " . $page_name . ")";
					$page_title = $page_section . " - " . $page_name;
					$page_final =~ s/<kiriwrite:pagetitle>/$page_title/g;

				} elsif ($page_settings eq 2){

					# Use the page name only.

					$page_autotitle = "(" . $page_name . ")";
					$page_final =~ s/<kiriwrite:pagetitle>/$page_name/g;

				} elsif ($page_settings eq 3){

					# Use the section name only.

					if ($page_section){
						$page_autotitle = "(" . $page_section . ")";
					}
					$page_final =~ s/<kiriwrite:pagetitle>/$page_section/g;

				}

				# Check if the section name is not blank and
				# place brackets inbetween if it is.

				if ($page_section){

					$page_autosection = "(" . $page_section . ")";

				}

				# Replace each <kiriwrite> value with the apporiate page
				# values.

				$page_final =~ s/<kiriwrite:pagename>/$page_name/g;
				$page_final =~ s/<kiriwrite:pagedescription>/$page_description/g;
				$page_final =~ s/<kiriwrite:pagesection>/$page_section/g;
				$page_final =~ s/<kiriwrite:autosection>/$page_autosection/g;
				$page_final =~ s/<kiriwrite:autotitle>/$page_autotitle/g;

				# Process the filters on the page data.

				if ($filters_skip eq 0){

					$filters_count = 0;

					foreach $filter_find (@findfilter){

						# Get the replace filter and process each
						# filter on the page.

						$filter_replace = $replacefilter[$filters_count];
						$page_final =~ s/$filter_find/$filter_replace/g;
						$filters_count++;

					}

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

					mkdir($kiriwrite_config{"directory_data_output"} . '/' . $page_directory_path);

				}

				# Check if the file already exists and if it does then check
				# the permissions of the file and return an error if the
				# permissions set are invalid.

				$page_filename_exists = kiriwrite_fileexists($kiriwrite_config{"directory_data_output"} . '/' . $page_filename);	

				if ($page_filename_exists eq 0){

					# The page filename exists, so check if the permissions given are
					# valid.

					$page_filename_permissions = kiriwrite_filepermissions($kiriwrite_config{"directory_data_output"} . '/' . $page_filename, 1, 1);

					if ($page_filename_permissions eq 1){

						# The file has invalid permissions set.

						$kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($kiriwrite_lang->{compile}->{pageinvalidpermissions}, $page_filename));
						$kiriwrite_presmodule->addlinebreak();
						$error_count++;

						# Reset certain values.

						$page_autotitle = "";
						$page_autosection = "";
						$page_filename_seek = 0;
						$page_filename_dircount = 0;

						$page_filename_directory = "";
						$page_directory_path = "";
						$page_directory_name = "";
						@pagedirectories = ();
						
						next;

					}

				}

				# Reset certain values.

				$page_autotitle = "";
				$page_autosection = "";
				$page_filename_seek = 0;
				$page_filename_dircount = 0;

				$page_filename_directory = "";
				$page_directory_path = "";
				$page_directory_name = "";
				@pagedirectories = ();

				# Write the file to the output directory.

				($page_filename) = $page_filename =~ m/^(.*)$/g;
				($kiriwrite_config{"directory_data_output"}) = $kiriwrite_config{"directory_data_output"} =~ m/^(.*)$/g;

				open($filehandle_page, "> ",  $kiriwrite_config{"directory_data_output"} . '/' . $page_filename) or ($kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($kiriwrite_lang->{compile}->{pagenotwritten}, $page_filename, $!)), $kiriwrite_presmodule->addlinebreak(), $error_count++, next);

				if (!$page_final){

					$page_final = "";

				}

				binmode $filehandle_page, ':utf8';
				print $filehandle_page $page_final;
				close($filehandle_page);

				# Write a message saying the page has been compiled. Check
				# to see if the page name is blank and write a message
				# saying there's no page name.

				if (!$page_name){
					$kiriwrite_presmodule->addtext($information_prefix . ' ');
					$kiriwrite_presmodule->additalictext($kiriwrite_lang->{blank}->{noname});
					$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{compile}->{compiledpageblankname}, $page_filename));
				} else {
					$kiriwrite_presmodule->addtext($information_prefix . kiriwrite_language($kiriwrite_lang->{compile}->{compiledpage}, $page_name, $page_filename));
				}


				$kiriwrite_presmodule->addlinebreak();
				$pages_count++;

			}

			# Write a message saying that the database has
			# been processed.

  			$kiriwrite_presmodule->addtext($information_prefix . kiriwrite_language($kiriwrite_lang->{compile}->{databasefinish}, $database_name));
			$kiriwrite_presmodule->addlinebreak();

		}

		# Disconnect from the database server.

		$kiriwrite_dbmodule->disconnect();

		$kiriwrite_presmodule->addhorizontalline();
		$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{compile}->{compileresults}, $pages_count, $error_count, $warning_count));
		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=compile", { Text => $kiriwrite_lang->{compile}->{returncompilelist} });

		return $kiriwrite_presmodule->grab();

	} elsif ($confirm eq 0){

		# The action to compile the databases has
		# not been confirmed so check what type
		# is being used.

		if ($type eq "single"){

			# The type is a single database selected so
			# process that database.

			# Define some variables for later.

			my %database_info; 
			my $database_filename_check;
			my $database_maxlength_check;
			my $databasefilename;
			my $database_name;

			# Check that the database name and length are
			# valid and return an error if they aren't.

			$databasefilename = $selectedlist[0];

			# Connect to the database server.

			$kiriwrite_dbmodule->connect();

			# Check if any errors occured while connecting to the database server.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

				# A database connection error has occured so return
				# an error.

				kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

			}

			# Select the database.

			$kiriwrite_dbmodule->selectdb({ DatabaseName => $databasefilename });

			# Check if any errors had occured while selecting the database.

			if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

				# The database does not exist, so return an error.

				kiriwrite_error("databasemissingfile");

			} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

				# The database has invalid permissions set, so return
				# an error.

				kiriwrite_error("databaseinvalidpermissions");

			}

			# Get information about the database.

			%database_info = $kiriwrite_dbmodule->getdatabaseinfo();

			# Check if any error occured while getting the database information.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				kiriwrite_error("databaseerror", $kiriwrite_dbmodule->geterror(1));

			};

			$database_name = $database_info{"DatabaseName"};

			# Disconnect from the database server.

			$kiriwrite_dbmodule->disconnect();

			# Write out a form asking the user to confirm if the
			# user wants to compile the selected database.

			$kiriwrite_presmodule->addtext($kiriwrite_lang->{compile}->{compiledatabase}, { Style => "pageheader" });
			$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
			$kiriwrite_presmodule->startbox();
			$kiriwrite_presmodule->addhiddendata("mode", "compile");
			$kiriwrite_presmodule->addhiddendata("action", "compile");
			$kiriwrite_presmodule->addhiddendata("type", "multiple");
			$kiriwrite_presmodule->addhiddendata("id[1]", $databasefilename);
			$kiriwrite_presmodule->addhiddendata("name[1]", "on");
			$kiriwrite_presmodule->addhiddendata("confirm", 1);
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addtext(kiriwrite_language($kiriwrite_lang->{compile}->{compiledatabasemessage}, $database_name));
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{compile}->{compiledatabasebutton});
			$kiriwrite_presmodule->addtext(" | ");
			$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=compile", { Text => $kiriwrite_lang->{compile}->{returncompilelist} });
			$kiriwrite_presmodule->endbox();
			$kiriwrite_presmodule->endform();

			return $kiriwrite_presmodule->grab();

		} elsif ($type eq "multiple"){

			# The type is multiple databases selected
			# so process each database.

			# Define some variables for later.

			my %database_list;
			my $databasename;
			my $database;
			my $database_filename_check;
			my $database_maxlength_check;
			my $database_count = 0;
			my $database_info_name;

			# Connect to the database server.

			$kiriwrite_dbmodule->connect();

			# Check if any errors occured while connecting to the database server.

			if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

				# A database connection error has occured so return
				# an error.

				kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

			}

			foreach $databasename (@selectedlist){

 				# Check	if the database is in the database
 				# directory and skip it if it isn't.
 
 				$database_filename_check 	= kiriwrite_variablecheck($databasename, "filename", "", 1);
 				$database_maxlength_check	= kiriwrite_variablecheck($databasename, "maxlength", 32, 1);
 
 				if ($database_filename_check ne 0 || $database_maxlength_check ne 0){
 
 					# The database filename given is invalid or
 					# the database filename given is too long
 					# so process the next database.
 
 					next;
 
 				}

				# Select the database to add the page to.

				$kiriwrite_dbmodule->selectdb({ DatabaseName => $databasename });

				# Check if any errors had occured while selecting the database.

				if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

					# The database does not exist, so process the next database.

					next;

				} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

					# The database has invalid permissions set, so process
					# the next database.

					next;

				}

				# Get information about the database.

				my %database_info = $kiriwrite_dbmodule->getdatabaseinfo();

				# Check if any error occured while getting the database information.

				if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

					# A database error has occured so process the next
					# database.

					next;

				};

				$database_list{$database_count}{Name} 		= $database_info{"DatabaseName"};
				$database_list{$database_count}{Filename}	= $databasename;

				$database_count++;

			}

			# Check if any databases are available to be compiled.

			if ($database_count eq 0){

				# No databases are available to be compiled.

				kiriwrite_error("nodatabaseselected");

			}

			# Write out the form for compiling the database.

			$kiriwrite_presmodule->addtext($kiriwrite_lang->{compile}->{compileselecteddatabases}, { Style => "pageheader" });
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
			$kiriwrite_presmodule->startbox();
			$kiriwrite_presmodule->addhiddendata("mode", "compile");
			$kiriwrite_presmodule->addhiddendata("action", "compile");
			$kiriwrite_presmodule->addhiddendata("type", "multiple");
			$kiriwrite_presmodule->addhiddendata("count", $database_count);
			$kiriwrite_presmodule->addhiddendata("confirm", 1);
			$kiriwrite_presmodule->addtext($kiriwrite_lang->{compile}->{compileselecteddatabasesmessage});
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->startbox("datalist");

			$database_count = 0;

			# write out the list of databases to compile.

			foreach $database (keys %database_list){

				$database_count++;

				$kiriwrite_presmodule->addhiddendata("id[" . $database_count . "]", $database_list{$database}{Filename});
				$kiriwrite_presmodule->addhiddendata("name[" . $database_count . "]", "on");

				# Check if the database name is undefined and if it is
				# then write a message saying the database name is blank.

				if (!$database_list{$database}{Name}){
					$kiriwrite_presmodule->additalictext($kiriwrite_lang->{compile}->{blankdatabasename});
				} else {
					$kiriwrite_presmodule->addtext($database_list{$database}{Name});
				}

				$kiriwrite_presmodule->addlinebreak();

			}

			$kiriwrite_presmodule->endbox();

			# Disconnect from the database server.

			$kiriwrite_dbmodule->disconnect();

			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{compile}->{compileselecteddatabasesbutton});
			$kiriwrite_presmodule->addtext(" | ");
			$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=compile", { Text => $kiriwrite_lang->{compile}->{returncompilelist} });
			$kiriwrite_presmodule->endbox();
			$kiriwrite_presmodule->endform();

			return $kiriwrite_presmodule->grab();

		} else {

			# The type is something else other than
			# single or multiple, so return an error.

			kiriwrite_error("invalidvariable");

		}

	} else {

		# The confirm value is neither 0 or 1, so
		# return an error.

		kiriwrite_error("invalidvariable");

	}

}

sub kiriwrite_compile_all{
#################################################################################
# kiriwrite_compile_all: Compile all of the databases in the database		#
# directory.									#
#										#
# Usage:									#
# 										#
# kiriwrite_compile_all();							#
#################################################################################

	# Connect to the database server.

	$kiriwrite_dbmodule->connect();

	# Check if any errors occured while connecting to the database server.

	if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

		# A database connection error has occured so return
		# an error.

		kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

	}

	# Get the list of available databases.

	my @database_list = $kiriwrite_dbmodule->getdblist();

	# Check if any errors occured while getting the databases.

	if ($kiriwrite_dbmodule->geterror eq "DataDirMissing"){

		# The database directory is missing so return an error.

		kiriwrite_error("datadirectorymissing");

	} elsif ($kiriwrite_dbmodule->geterror eq "DataDirInvalidPermissions"){

		# The database directory has invalid permissions set so return
		# an error.

		kiriwrite_error("datadirectoryinvalidpermissions");

	}

	# Define some variables for later.

	my $database;
	my $database_name_filename_check;
	my $database_count 		= 0;

	# Check the list of databases to compile to see if it is blank,
	# if it is then return an error.

	if (!@database_list){

		# The list of database is blank so return an error.

		kiriwrite_error("nodatabasesavailable");

	}

	# Write out a form for confirming the action to compile all of the databases.

	$kiriwrite_presmodule->addtext($kiriwrite_lang->{compile}->{compilealldatabases}, { Style => "pageheader" });
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();

	$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
	$kiriwrite_presmodule->startbox();
	$kiriwrite_presmodule->addhiddendata("mode", "compile");
	$kiriwrite_presmodule->addhiddendata("action", "compile");
	$kiriwrite_presmodule->addhiddendata("type", "multiple");

	foreach $database (@database_list){

		# Check if the database filename is blank.

		if ($database eq ""){

			# The database filename is blank so process
			# the next database.

			next;

		}

		# Check if the database filename is valid before
		# using the database.

		$database_name_filename_check 	= kiriwrite_variablecheck($database, "filename", 0, 1);

		if ($database_name_filename_check ne 0){

			# The database filename is invalid so process
			# the next database.

			next;

		}

		$database_count++;
		$kiriwrite_presmodule->addhiddendata("id[" . $database_count . "]", $database);
		$kiriwrite_presmodule->addhiddendata("name[" . $database_count . "]", "on");

	}

	$kiriwrite_presmodule->addhiddendata("count", $database_count);

	# Disconnect from the database server.

	$kiriwrite_dbmodule->disconnect();

	$kiriwrite_presmodule->addtext($kiriwrite_lang->{compile}->{compilealldatabasesmessage});
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();

	$kiriwrite_presmodule->addhiddendata("confirm", 1);
	$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{compile}->{compilealldatabasesbutton});
	$kiriwrite_presmodule->addtext(" | ");
	$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=compile", { Text => $kiriwrite_lang->{compile}->{returncompilelist} });
	$kiriwrite_presmodule->endbox();
	$kiriwrite_presmodule->endform();

	return $kiriwrite_presmodule->grab();

}

sub kiriwrite_selectedlist{
#################################################################################
# kiriwrite_page_selectedlist: Get the list of selected pages to use.		#
#										#
# Usage:									#
#										#
# kiriwrite_page_selectedlist();						#
#################################################################################

	# Load the required Perl modules.

	my $query = new CGI;

	my $count	= $query->param('count');

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

		$filename 		= $query->param('id[' . $seek . ']');
		$filename_list[$seek] 	= $filename;

	} until ($seek eq $count || $count eq 0);

	# Get the list of selected filenames.

	$seek = 0;

	do {

		# Get the values from name[]

		$seek++;

		$selected 	= $query->param('name[' . $seek . ']');

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

sub kiriwrite_compile_list{
#################################################################################
# kiriwrite_compile_list: Shows a list of databases that can be compiled.	#
#										#
# Usage:									#
#										#
# kiriwrite_compile_list();							#
#################################################################################

	# Define the following variables that are going to be used before using 
	# the foreach function.

	my %database_info;
	my %database_list;
	my $database_count = 0;
	my $database_filename = "";
	my $database_filename_friendly = "";
	my $database_permissions = "";
	my $database_name = "";
	my $database_description = "";
	my $data_file = "";
	my @permissions_list;
	my @error_list;
	my $table_style = 0;
	my $table_style_name = "";
	my $database;

	tie(%database_list, 'Tie::IxHash');

	# Connect to the database server.

	$kiriwrite_dbmodule->connect();

	# Check if any errors occured while connecting to the database server.

	if ($kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

		# A database connection error has occured so return
		# an error.

		kiriwrite_error("databaseconnectionerror", $kiriwrite_dbmodule->geterror(1));

	}

	# Get the list of available databases and process any errors that
	# might have occured.

	my @database_list = $kiriwrite_dbmodule->getdblist();

	if ($kiriwrite_dbmodule->geterror eq "DataDirMissing"){

		# The database directory is missing so return an error.

		kiriwrite_error("datadirectorymissing");

	} elsif ($kiriwrite_dbmodule->geterror eq "DataDirInvalidPermissions"){

		# The database directory has invalid permissions set so return
		# an error.

		kiriwrite_error("datadirectoryinvalidpermissions");

	}

	# Begin creating the table for the list of databases.

	foreach $data_file (@database_list){

		# Select the database.

		$kiriwrite_dbmodule->selectdb({ DatabaseName => $data_file });

		# Check if any error occured while selecting the database.

		if ($kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so process the next
			# database.

			next;

		} elsif ($kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet") {

			# The database has invalid permissions settings, so
			# add the database to the list of databases with
			# invalid permissions set and process the next
			# database.

			push(@permissions_list, $data_file);
			next;

		}

		# Get information about the database.

		%database_info = $kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any error occured while getting information from the
		# database.

		if ($kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured, add the database and specific
			# error message to the list of databases with errors and
			# process the next database.

			push(@error_list, $data_file . ": " . $kiriwrite_dbmodule->geterror(1));
			next;

		}

		$database_name		= $database_info{"DatabaseName"};
		$database_description 	= $database_info{"Description"};

		# Create a friendly name for the database.

		$database_filename_friendly = $data_file;

		# Append the database information to the table.

 		$database_list{$database_count}{Filename} 	= $database_filename_friendly;
 		$database_list{$database_count}{Name} 		= $database_name;
 		$database_list{$database_count}{Description} 	= $database_description;

		$database_count++;

	}

	# Check if there are no valid databases are if there is no
	# valid databases then write a message saying that no
	# valid databases are available.

	$kiriwrite_presmodule->addtext($kiriwrite_lang->{compile}->{compilepages}, { Style => "pageheader" });
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();

	if ($database_count eq 0){

		# There are no databases available for compiling so
		# write a message instead.

		$kiriwrite_presmodule->startbox("errorbox");
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{compile}->{nodatabasesavailable});
		$kiriwrite_presmodule->endbox();

	} else {

		$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
		$kiriwrite_presmodule->startbox();
		$kiriwrite_presmodule->addhiddendata("mode", "compile");
		$kiriwrite_presmodule->addhiddendata("action", "compile");
		$kiriwrite_presmodule->addhiddendata("type", "multiple");

		$kiriwrite_presmodule->addreset($kiriwrite_lang->{common}->{selectnone});
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{compile}->{compileselectedbutton});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addhiddendata("count", $database_count);
		$kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

		$kiriwrite_presmodule->startheader();
		$kiriwrite_presmodule->addheader("", { Style => "tablecellheader" });
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{database}->{databasename}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{database}->{databasedescription}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{options}, { Style => "tablecellheader" });
		$kiriwrite_presmodule->endheader();

		$database_count = 1;

		foreach $database (keys %database_list){

			# Check the style to be used with.

			if ($table_style eq 0){

				# Use the first style and set the style value
				# to use the next style, the next time the
				# if statement is checked.

				$table_style_name = "tablecell1";
				$table_style = 1;

			} else {

				# Use the second style and set the style
				# value to use the first style, the next
				# time if statement is checked.

				$table_style_name = "tablecell2";
				$table_style = 0;
			}

			# Add the template to the list of available
			# templates to compile.

			$kiriwrite_presmodule->startrow();
			$kiriwrite_presmodule->addcell($table_style_name);
			$kiriwrite_presmodule->addhiddendata("id[" . $database_count . "]", $database_list{$database}{Filename});
			$kiriwrite_presmodule->addcheckbox("name[" . $database_count . "]");
			$kiriwrite_presmodule->endcell();
			$kiriwrite_presmodule->addcell($table_style_name);

			if (!$database_list{$database}{Name}){
				$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=compile&action=compile&type=single&database=" . $database_list{$database}{Filename}, { Text => $kiriwrite_presmodule->additalictext($kiriwrite_lang->{blank}->{noname}) });
			} else {
				$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database_list{$database}{Filename}, { Text => $database_list{$database}{Name} });
			}

			$kiriwrite_presmodule->endcell();
			$kiriwrite_presmodule->addcell($table_style_name);

			if (!$database_list{$database}{Description}){
				$kiriwrite_presmodule->additalictext($kiriwrite_lang->{blank}->{nodescription});
			} else {
				$kiriwrite_presmodule->addtext($database_list{$database}{Description});
			}

			$kiriwrite_presmodule->endcell();
			$kiriwrite_presmodule->addcell($table_style_name);
			$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=compile&action=compile&type=single&database=" . $database_list{$database}{Filename}, { Text => $kiriwrite_lang->{options}->{compile} });
			$kiriwrite_presmodule->endcell();
			$kiriwrite_presmodule->endrow();

			$database_count++;

		}

		$kiriwrite_presmodule->endtable();
		$kiriwrite_presmodule->endbox();
		$kiriwrite_presmodule->endform();

	}

	# Disconnect from the database server.

	$kiriwrite_dbmodule->disconnect();

	# Check if any databases with problems have appeared and if they
	# have, print out a message saying which databases have problems.

	if (@permissions_list){

 		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databaseinvalidpermissions}, { Style => "smallpageheader" });
 		$kiriwrite_presmodule->addlinebreak();
 		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databaseinvalidpermissionstext});
 		$kiriwrite_presmodule->addlinebreak();
 
 		foreach $database (@permissions_list){
 
 			$kiriwrite_presmodule->addlinebreak();
 			$kiriwrite_presmodule->addtext($database);
 
 		}
 
 		$kiriwrite_presmodule->addlinebreak();
 		$kiriwrite_presmodule->addlinebreak();

	}

	if (@error_list){

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databaseerrors}, { Style => "smallpageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{database}->{databaseerrorstext});
		$kiriwrite_presmodule->addlinebreak();

		foreach $database (@error_list){

			$kiriwrite_presmodule->addlinebreak();
			$kiriwrite_presmodule->addtext($database);

		}

	}

	return $kiriwrite_presmodule->grab();

}

sub kiriwrite_compile_clean{
#################################################################################
# kiriwrite_compile_clean: Deletes the contents of the output directory.	#
#										#
# Usage:									#
#										#
# kiriwrite_compile_clean(confirm);						#
#										#
# confirm	Confirms the deletion of files from the output directory.	#
#################################################################################

	# Get the values passed to the subroutine.

	my ($confirm) = @_;

	# Define some variables for later.

	my $file_permissions;
	my $output_directory_exists;
	my $output_directory_permissions;
	my $warning_message;

	# Check if the output directory exists.

	$output_directory_exists	 = kiriwrite_fileexists($kiriwrite_config{"directory_data_output"});

	if ($output_directory_exists eq 1){

		# The output directory does not exist so return
		# an error.

		kiriwrite_error("outputdirectorymissing");

	}

	# Check if the output directory has invalid
	# permissions set.

	$output_directory_permissions	= kiriwrite_filepermissions($kiriwrite_config{"directory_data_output"});

	if ($output_directory_permissions eq 1){

		# The output directory has invalid permissions
		# set, so return an error.

		kiriwrite_error("outputdirectoryinvalidpermissions");

	}

	if ($confirm) {

		if ($confirm eq 1){

			# The action to clean the output directory has been
			# confirmed.

			# Remove the list of files and directories from the
			# output directory.

			$file_permissions = kiriwrite_compile_clean_helper($kiriwrite_config{"directory_data_output"}, 1);

			$kiriwrite_presmodule->addtext($kiriwrite_lang->{compile}->{cleanoutputdirectory}, { Style => "pageheader" });

			if ($file_permissions eq 1){

				$kiriwrite_presmodule->addlinebreak();
				$kiriwrite_presmodule->addlinebreak();
				$kiriwrite_presmodule->addtext($kiriwrite_lang->{compile}->{somecontentnotremoved});
				$kiriwrite_presmodule->addlinebreak();
				$kiriwrite_presmodule->addlinebreak();

			} else {

				$kiriwrite_presmodule->addlinebreak();
				$kiriwrite_presmodule->addlinebreak();
				$kiriwrite_presmodule->addtext($kiriwrite_lang->{compile}->{contentremoved});
				$kiriwrite_presmodule->addlinebreak();
				$kiriwrite_presmodule->addlinebreak();

			}

			$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=compile", { Text => $kiriwrite_lang->{compile}->{returncompilelist} });

			return $kiriwrite_presmodule->grab();

		} else {

			# A value other than 1 is set for the confirm value
			# (which it shouldn't be) so return an error.

			kiriwrite_error("invalidvariable");

		}

	}

	# Print out a form for cleaning the output directory.

	$kiriwrite_presmodule->addtext($kiriwrite_lang->{compile}->{cleanoutputdirectory}, { Style => "pageheader" });
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
	$kiriwrite_presmodule->startbox();
	$kiriwrite_presmodule->addhiddendata("mode", "compile");
	$kiriwrite_presmodule->addhiddendata("action", "clean");
	$kiriwrite_presmodule->addhiddendata("confirm", 1);
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{compile}->{cleanoutputdirectorymessage});
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{compile}->{cleanoutputdirectorybutton});
	$kiriwrite_presmodule->addtext(" | ");
	$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=compile", { Text => $kiriwrite_lang->{compile}->{returncompilelist}});
	$kiriwrite_presmodule->endbox();
	$kiriwrite_presmodule->endform();

	return $kiriwrite_presmodule->grab();

}

sub kiriwrite_compile_clean_helper{
#################################################################################
# kiriwrite_compile_clean_helper: Helper for cleaning out the output directory.	#
# This command sometimes is called recursively (when a directory is found).	#
#										#
# Usage:									#
#										#
# kiriwrite_compile_clean_helper(directory, removedirectory, [permissions]);	#
#										#
# directory		Specifies the directory to remove files (and		#
#			sub-directories) from.					#
# keepdirectory		Keeps the directory itself after all files have been	#
#			removed.						#
# permissions		Used recursively for error checking.			#
#################################################################################

	# Get the values passed to the subroutine.

	my ($directory, $directory_keep, $permissions) = @_;

	# Check if the directory_keep is only one charater long.

	my $directory_file = "";
	my @directory_list;
	my $file_permissions = 0;
	my $debug = 0;

	# Check if the file permissions value is blank.

	if (!$permissions){

		# The file permissions value is blank.

		$permissions = 0;

	}

	# Open the directory specified, read the contents of
	# the directory and then close the directory.

	opendir(DIRECTORY, $directory);
	@directory_list = readdir(DIRECTORY);
	closedir(DIRECTORY);

	# Remove each file and directory.

	foreach $directory_file (@directory_list){

		# Check if the filename is '.' or '..' and if it
		# is skip those files.

		if ($directory_file eq "." || $directory_file eq ".."){

			# The filename is '.' or '..' so skip processing
			# these files.

		} else {

			# Check if the permissions on the file or directory has
			# valid permissions set.

			$file_permissions = kiriwrite_filepermissions($directory . '/' . $directory_file, 1, 1);

			if ($file_permissions eq 1){

				# The file or directory has invalid permissions set.

				$permissions = 1;
				next;

			}

			# Check if the filename is a directory.

			if (-d $directory . '/' . $directory_file){

				# The filename is a directory so send the directory name
				# and this subroutine again (recursively).

				kiriwrite_compile_clean_helper($directory . '/' . $directory_file, 0, $permissions);

			} else {

				# The file is not a directory but an actual file so
				# remove as normal (in terms of the Perl language).

				($directory) = $directory =~ m/^(.*)$/g;
				($directory_file) = $directory_file =~ m/^(.*)$/g;

				# Check if the directory is undefined and if it is then
				# set it to blank.

				if (!$directory){
					$directory = "";
				}

				if (!$directory_file){
					$directory_file = "";
				}

				unlink($directory . '/' . $directory_file);

			}

		}

	}

	# Check if the directory should be kept.

	if ($directory_keep eq 1){

		# The directory_keep value is set as 1 so the directory
		# specified should be kept.

	} elsif ($directory_keep eq 0) {

		# The directory_keep value is set as 0 so remove the
		# directory specified.

		($directory) = $directory =~ m/^(.*)$/g;
		rmdir($directory);

	} else {

		# A value other than 0 or 1 was specified so return
		# an error,

		kiriwrite_error('invalidvalue');

	}

	return $permissions;

}

sub kiriwrite_settings_view{
#################################################################################
# kiriwrite_options_view: Writes out the list of options and variables.		#
#										#
# Usage:									#
#										#
# kiriwrite_settings_view();							#
#################################################################################

	# Get the settings.

	my $settings_directory_db		= $kiriwrite_config{"directory_data_db"};
	my $settings_directory_output		= $kiriwrite_config{"directory_data_output"};
	my $settings_noncgi_images		= $kiriwrite_config{"directory_noncgi_images"};
	my $settings_system_datetime		= $kiriwrite_config{"system_datetime"};
	my $settings_system_language		= $kiriwrite_config{"system_language"};
	my $settings_system_presentation	= $kiriwrite_config{"system_presmodule"};
	my $settings_system_database		= $kiriwrite_config{"system_dbmodule"};

	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{viewsettings}, { Style => "pageheader" });
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{currentsettings});
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

	$kiriwrite_presmodule->startheader();
	$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{setting}, { Style => "tablecellheader" });
	$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{value}, { Style => "tablecellheader" });
	$kiriwrite_presmodule->endheader();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecellheader");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{directories});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecellheader");
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{databasedirectory});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addtext($settings_directory_db);
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{outputdirectory});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addtext($settings_directory_output);
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{imagesuripath});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addtext($settings_noncgi_images);
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecellheader");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{date});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecellheader");
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{dateformat});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addtext($settings_system_datetime);
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecellheader");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{language});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecellheader");
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{systemlanguage});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addtext($settings_system_language);
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecellheader");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{modules});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecellheader");
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{presentationmodule});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addtext($settings_system_presentation);
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{databasemodule});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addtext($settings_system_database);
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->endtable();

	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{altersettings});

	return $kiriwrite_presmodule->grab();

}

sub kiriwrite_settings_edit{
#################################################################################
# kiriwrite_settings_edit: Edits the options.					#
#										#
# Usage:									#
#										#
# kiriwrite_settings_edit(options);						#
#										#
# options		Specifies the following options in any order.		#
#										#
# DatabaseDirectory	Specifies the new database directory to use.		#
# OutputDirectory	Specifies the new output directory to use.		#
# ImagesURIPath		Specifies the new URI path for images.			#
# DateTimeFormat	Specifies the new date and time format.			#
# SystemLanguage	Specifies the new language to use for Kiriwrite.	#
# PrsentationModule	Specifies the new presentation module to use for	#
#			Kiriwrite.						#
# DatabaseModule	Specifies the new database module to use for Kiriwrite.	#
#										#
# Options for server-based database modules.					#
#										#
# DatabaseServer	Specifies the database server to use.			#
# DaravasePort		Specifies the port the database server is running on.	#
# DatabaseProtocol	Specifies the protocol the database server is using.	#
# DatabaseSQLDatabase	Specifies the SQL database name to use.			#
# DatabaseUsername	Specifies the database server username.			#
# DatabasePasswordKeep	Keeps the current password in the configuration file.	#
# DatabasePassword	Specifies the password for the database server username.#
# DatabaseTablePrefix	Specifies the prefix used for tables.			#
#################################################################################

	# Get the values that have been passed to the subroutine.

	my ($passedoptions) = @_;

	# Get the values from the hash.

	my $settings_dbdirectory		= $passedoptions->{"DatabaseDirectory"};
	my $settings_outputdirectory		= $passedoptions->{"OutputDirectory"};
	my $settings_imagesuri			= $passedoptions->{"ImagesURIPath"};
	my $settings_datetimeformat		= $passedoptions->{"DateTimeFormat"};
	my $settings_languagesystem		= $passedoptions->{"SystemLanguage"};
	my $settings_presmodule			= $passedoptions->{"PresentationModule"};
	my $settings_dbmodule			= $passedoptions->{"DatabaseModule"};

	my $settings_database_server		= $passedoptions->{"DatabaseServer"};
	my $settings_database_port		= $passedoptions->{"DatabasePort"};
	my $settings_database_protocol		= $passedoptions->{"DatabaseProtocol"};
	my $settings_database_sqldatabase	= $passedoptions->{"DatabaseSQLDatabase"};
	my $settings_database_username		= $passedoptions->{"DatabaseUsername"};
	my $settings_database_passwordkeep	= $passedoptions->{"DatabasePasswordKeep"};
	my $settings_database_password		= $passedoptions->{"DatabasePassword"};
	my $settings_database_tableprefix	= $passedoptions->{"DatabaseTablePrefix"};

	my $confirm				= $passedoptions->{"Confirm"};

	if (!$confirm){

		# If the confirm value is blank, then set the confirm
		# value to 0.

		$confirm = 0;

	}

	if ($confirm eq "1"){

		# The action to edit the settings has been confirmed.
		# Start by checking each variable about to be placed
		# in the settings file is valid.

		# Deinfe some variables for later.

		my @kiriwrite_new_settings;

		# Check the length of the directory names.

		kiriwrite_variablecheck($settings_dbdirectory, "maxlength", 64, 0);
		kiriwrite_variablecheck($settings_outputdirectory, "maxlength", 64, 0);
		kiriwrite_variablecheck($settings_imagesuri, "maxlength", 512, 0);
		kiriwrite_variablecheck($settings_datetimeformat, "maxlength", 32, 0);

		kiriwrite_variablecheck($settings_languagesystem, "language_filename", "", 0);

		# Check the module names to see if they're valid.

		my $kiriwrite_presmodule_modulename_check 	= kiriwrite_variablecheck($settings_presmodule, "module", 0, 1);
		my $kiriwrite_dbmodule_modulename_check		= kiriwrite_variablecheck($settings_dbmodule, "module", 0, 1);

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

		# Check if the directory names only contain letters and numbers and
		# return a specific error if they don't.

		my $kiriwrite_dbdirectory_check 	= kiriwrite_variablecheck($settings_dbdirectory, "directory", 0, 1);
		my $kiriwrite_outputdirectory_check 	= kiriwrite_variablecheck($settings_outputdirectory, "directory", 0, 1);
		kiriwrite_variablecheck($settings_datetimeformat, "datetime", 0, 0);

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

		# Check if the presentation module with the filename given exists.

		my $presmodule_exists = kiriwrite_fileexists("Modules/Presentation/" . $settings_presmodule . ".pm");

		if ($presmodule_exists eq 1){

			# The presentation module does not exist so return an error.

			kiriwrite_error("presmodulemissing");

		}

		# Check if the database module with the filename given exists.

		my $dbmodule_exists = kiriwrite_fileexists("Modules/Database/" . $settings_dbmodule . ".pm");

		if ($dbmodule_exists eq 1){

			# The database module does not exist so return an error.

			kiriwrite_error("dbmodulemissing");

		}

		# Check if the language filename given exists.

		my $languagefile_exists = kiriwrite_fileexists("lang/" . $settings_languagesystem . ".xml");

		if ($languagefile_exists eq 1){

			# The language filename given does not exist so return an error.

			kiriwrite_error("languagefilenamemissing");		

		}

		# Check the database server options to see if they are valid.

		my $kiriwrite_databaseserver_length_check		= kiriwrite_variablecheck($settings_database_server, "maxlength", 128, 1);
		my $kiriwrite_databaseserver_lettersnumbers_check	= kiriwrite_variablecheck($settings_database_server, "lettersnumbers", 0, 1);
		my $kiriwrite_databaseport_length_check			= kiriwrite_variablecheck($settings_database_port, "maxlength", 5, 1);
		my $kiriwrite_databaseport_numbers_check		= kiriwrite_variablecheck($settings_database_port, "numbers", 0, 1);
		my $kiriwrite_databaseport_port_check			= kiriwrite_variablecheck($settings_database_port, "port", 0, 1);
		my $kiriwrite_databaseprotocol_length_check		= kiriwrite_variablecheck($settings_database_protocol, "maxlength", 5, 1);
		my $kiriwrite_databaseprotocol_protocol_check		= kiriwrite_variablecheck($settings_database_protocol, "serverprotocol", 0, 1);
		my $kiriwrite_databasename_length_check			= kiriwrite_variablecheck($settings_database_sqldatabase, "maxlength", 32, 1);
		my $kiriwrite_databasename_lettersnumbers_check		= kiriwrite_variablecheck($settings_database_sqldatabase, "lettersnumbers", 0, 1);
		my $kiriwrite_databaseusername_length_check		= kiriwrite_variablecheck($settings_database_username, "maxlength", 16, 1);
		my $kiriwrite_databaseusername_lettersnumbers_check	= kiriwrite_variablecheck($settings_database_username, "lettersnumbers", 0, 1);
		my $kiriwrite_databasepassword_length_check		= kiriwrite_variablecheck($settings_database_password, "maxlength", 64, 1);
		my $kiriwrite_databasetableprefix_length_check		= kiriwrite_variablecheck($settings_database_tableprefix, "maxlength", 16, 1);
		my $kiriwrite_databasetableprefix_lettersnumbers_check	= kiriwrite_variablecheck($settings_database_tableprefix, "lettersnumbers", 0, 1);

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

		# Check if the current password should be kept.

		if ($settings_database_passwordkeep eq "on"){

			# The current password in the configuration file should be used.

			$settings_database_password 	= $kiriwrite_config{"database_password"};

		}

		# Write the new settings to the XML file.

		kiriwrite_output_xml("kiriwrite.xml", "config", { DatabaseDirectory => $settings_dbdirectory, OutputDirectory => $settings_outputdirectory, ImagesURIPath => $settings_imagesuri, DateTimeFormat => $settings_datetimeformat, SystemLanguage => $settings_languagesystem, PresentationModule => $settings_presmodule, DatabaseModule => $settings_dbmodule, DatabaseServer => $settings_database_server, DatabasePort => $settings_database_port, DatabaseProtocol => $settings_database_protocol, DatabaseSQLDatabase => $settings_database_sqldatabase, DatabaseUsername => $settings_database_username, DatabasePassword => $settings_database_password, DatabaseTablePrefix => $settings_database_tableprefix });

		# Write a confirmation message.

		$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{settingsedited}, { Style => "pageheader" });
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{settingseditedmessage});
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlinebreak();
		$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=settings", { Text => $kiriwrite_lang->{setting}->{returnsettingslist} });

		return $kiriwrite_presmodule->grab();

	}

	# Get the list of languages available.

	my %language_list;
	my @language_directory 		= "";
	my $language;
	my $language_filename 		= "";
	my $language_file_xml 		= "";
	my $language_file_systemname 	= "";
	my $language_file_localname 	= "";
	my $language_file_seek 		= 0;
	my $language_flie_dot 		= 0;
	my $language_file_length 	= 0;
	my $language_file_count		= 0;
	my $language_file_char		= "";
	my $language_file_friendly 	= "";
	my $language_config		= $kiriwrite_config{"system_language"};

	tie(%language_list, 'Tie::IxHash');

	opendir(LANGUAGEDIR, "lang");
	@language_directory = grep /m*\.xml$/, readdir(LANGUAGEDIR);
	closedir(LANGUAGEDIR);

	# Process each language by loading the XML configuration file
	# used for each language and then get the System name and 
	# the local name of the language.

	foreach $language_filename (@language_directory){

		# Load the language file currently selected.

		$language_file_xml = $xsl->XMLin("lang" . '/' . $language_filename, SuppressEmpty => 1);

		# Get the system name and the local name of the language.

		$language_file_localname = $language_file_xml -> {about} -> {name};

		# Check if either the system name or the local name of the language
		# is blank and if it is, then don't add the language to the list.

		if ($language_file_localname eq ""){

			# The system name or the local name is blank so don't add
			# the language to the list.
		
		} else {

			# Get the 'friendly' name of the language file name (basically
			# remove the .xml part from the filename.

			$language_file_length = length($language_filename);

			do {

				# Get a character from the language filename and currently
				# set by the seek counter.

				$language_file_char = substr($language_filename, $language_file_seek, 1);

				# Check if the character is a dot and if it is then set the
				# last dot value to the seek counter value.

				if ($language_file_char eq "."){

					# Current chatacter is a dot so set the last dot value 
					# to what is currently the seek counter.

					$language_flie_dot = $language_file_seek;

				} else {

					# Current character is not a dot, so do nothing.

				}

				# Increment the seek counter.

				$language_file_seek++;

			} until ($language_file_seek eq $language_file_length);

			# Reset the seek counter.

			$language_file_seek = 0;

			# Process the file name again and this time process the file
			# name until it reaches the last dot found.

			do {

				# Get the character the seek counter is currently set at.

				$language_file_char = substr($language_filename, $language_file_seek, 1);

				# Append the character to the friendly file name.

				$language_file_friendly = $language_file_friendly . $language_file_char;

				# Increment the seek counter.
	
				$language_file_seek++;

			} until ($language_file_seek eq $language_flie_dot);

			# Append the language to the available languages list.

			$language_list{$language_file_count}{Filename} = $language_file_friendly;
			$language_list{$language_file_count}{Name} = $language_file_localname;
			$language_file_count++;

			# Reset certain counters and values before continuing.

			$language_file_seek 	= 0;
			$language_flie_dot	= 0;
			$language_file_length	= 0;
			$language_file_char	= "";
			$language_file_friendly	= "";

		}

	}

	# Get the list of presentation modules available.

	my %presmodule_list;
	my @presmodule_directory;
	my $presmodule;
	my $presmodule_file 		= "";
	my $presmodule_char 		= "";
	my $presmodule_dot 		= 0;
	my $presmodule_firstdot		= 0;
	my $presmodule_firstdotfound	= "";
	my $presmodule_seek 		= 0;
	my $presmodule_length 		= 0;
	my $presmodule_count		= 0;
	my $presmodule_friendly 	= "";
	my $presmodule_selectlist 	= "";
	my $presmodule_config		= $kiriwrite_config{"system_presmodule"};

	# Open and get the list of presentation modules (perl modules) by filtering
	# out the 

	opendir(OUTPUTSYSTEMDIR, "Modules/Presentation");
	@presmodule_directory = grep /m*\.pm$/, readdir(OUTPUTSYSTEMDIR);
	closedir(OUTPUTSYSTEMDIR);

	# Process each presentation module and add them to the list of available
	# presentation modules.

	foreach $presmodule_file (@presmodule_directory){

		# Get the length of the presentation module (perl module) filename.

		$presmodule_length = length($presmodule_file);

		# Get the friendly name of the Perl module (by getting rid of the
		# .pm part of the filename).

		do {

			$presmodule_char = substr($presmodule_file, $presmodule_seek, 1);

			# Check if the current character is a dot and if it is then
			# set the last dot found number to the current seek number.

			if ($presmodule_char eq "."){

				# Put the seek value as the last dot found number.

				$presmodule_dot = $presmodule_seek;

			}

			# Increment the seek counter.

			$presmodule_seek++;

		} until ($presmodule_seek eq $presmodule_length);

		# Reset the seek counter as it is going to be used again.

		$presmodule_seek = 0;

		# Get the friendly name of the Perl module by the processing the file
		# name to the last dot the previous 'do' tried to find.

		do {

			# Get the character the seek counter is currently set at.

			$presmodule_char = substr($presmodule_file, $presmodule_seek, 1);

			# Append the character to the friendly name of the presentation module.

			$presmodule_friendly = $presmodule_friendly . $presmodule_char;

			# Increment the seek counter.

			$presmodule_seek++;

		} until ($presmodule_seek eq $presmodule_dot);

		# Append the option to tbe list of available presentation modules.

		$presmodule_list{$presmodule_count}{Filename} = $presmodule_friendly;

		# Reset the following values.

		$presmodule_seek 	= 0;
		$presmodule_length	= 0;
		$presmodule_char	= "";
		$presmodule_friendly	= "";
		$presmodule_count++;

	}

	# Get the list of database modules available.

	my %dbmodule_list;
	my @dbmodule_directory;
	my $dbmodule;
	my $dbmodule_file 		= "";
	my $dbmodule_char 		= "";
	my $dbmodule_dot 		= 0;
	my $dbmodule_firstdot		= 0;
	my $dbmodule_firstdotfound	= "";
	my $dbmodule_seek 		= 0;
	my $dbmodule_length 		= 0;
	my $dbmodule_count		= 0;
	my $dbmodule_friendly 		= "";
	my $dbmodule_selectlist 	= "";
	my $dbmodule_config		= $kiriwrite_config{"system_dbmodule"};

	# Open and get the list of presentation modules (perl modules) by filtering
	# out the 

	opendir(DATABASEDIR, "Modules/Database");
	@dbmodule_directory = grep /m*\.pm$/, readdir(DATABASEDIR);
	closedir(DATABASEDIR);

	# Process each presentation module and add them to the list of available
	# presentation modules.

	foreach $dbmodule_file (@dbmodule_directory){

		# Get the length of the database module (perl module) filename.

		$dbmodule_length = length($dbmodule_file);

		# Get the friendly name of the Perl module (by getting rid of the
		# .pm part of the filename).

		do {

			$dbmodule_char = substr($dbmodule_file, $dbmodule_seek, 1);

			# Check if the current character is a dot and if it is then
			# set the last dot found number to the current seek number.

			if ($dbmodule_char eq "."){

				# Put the seek value as the last dot found number.

				$dbmodule_dot = $dbmodule_seek;

			}

			# Increment the seek counter.

			$dbmodule_seek++;

		} until ($dbmodule_seek eq $dbmodule_length);

		# Reset the seek counter as it is going to be used again.

		$dbmodule_seek = 0;

		# Get the friendly name of the Perl module by the processing the file
		# name to the last dot the previous 'do' tried to find.

		do {

			# Get the character the seek counter is currently set at.

			$dbmodule_char = substr($dbmodule_file, $dbmodule_seek, 1);

			# Append the character to the friendly name of the presentation module.

			$dbmodule_friendly = $dbmodule_friendly . $dbmodule_char;

			# Increment the seek counter.

			$dbmodule_seek++;

		} until ($dbmodule_seek eq $dbmodule_dot);

		# Append the option to tbe list of available database modules.

		$dbmodule_list{$dbmodule_count}{Filename} = $dbmodule_friendly;

		# Reset the following values.

		$dbmodule_seek 	= 0;
		$dbmodule_length	= 0;
		$dbmodule_char		= "";
		$dbmodule_friendly	= "";
		$dbmodule_count++;

	}

	# Get the directory settings.

	my $directory_settings_database 	= $kiriwrite_config{"directory_data_db"};
	my $directory_settings_output	 	= $kiriwrite_config{"directory_data_output"};
	my $directory_settings_imagesuri 	= $kiriwrite_config{"directory_noncgi_images"};
	my $datetime_setting			= $kiriwrite_config{"system_datetime"};

	my $database_server			= $kiriwrite_config{"database_server"};
	my $database_port			= $kiriwrite_config{"database_port"};
	my $database_protocol			= $kiriwrite_config{"database_protocol"};
	my $database_sqldatabase		= $kiriwrite_config{"database_sqldatabase"};
	my $database_username			= $kiriwrite_config{"database_username"};
	my $database_passwordhash		= $kiriwrite_config{"database_passwordhash"};
	my $database_password			= $kiriwrite_config{"database_password"};
	my $database_prefix			= $kiriwrite_config{"database_tableprefix"};

	# Print out a form for editing the settings.

	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{editsettings}, { Style => "pageheader" });
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addboldtext($kiriwrite_lang->{setting}->{warning});
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{warningmessage});
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();

	$kiriwrite_presmodule->startform($kiriwrite_env{"script_filename"}, "POST");
	$kiriwrite_presmodule->startbox();
	$kiriwrite_presmodule->addhiddendata("mode", "settings");
	$kiriwrite_presmodule->addhiddendata("action", "edit");
	$kiriwrite_presmodule->addhiddendata("confirm", 1);

	$kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

	$kiriwrite_presmodule->startheader();
	$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{setting}, { Style => "tablecellheader" });
	$kiriwrite_presmodule->addheader($kiriwrite_lang->{common}->{value}, { Style => "tablecellheader" });
	$kiriwrite_presmodule->endheader();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecellheader");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{directories});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecellheader");
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{databasedirectory});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addinputbox("databasedir", { Size => 32, MaxLength => 64, Value => $directory_settings_database });
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{outputdirectory});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addinputbox("outputdir", { Size => 32, MaxLength => 64, Value => $directory_settings_output });
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{imagesuripath});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addinputbox("imagesuripath", { Size => 32, MaxLength => 64, Value => $directory_settings_imagesuri });
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecellheader");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{date});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecellheader");
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{dateformat});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addinputbox("datetime", { Size => 32, MaxLength => 64, Value => $datetime_setting });
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->startbox("datalist");

	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{singleday});
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{doubleday});
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{singlemonth});
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{doublemonth});
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{singleyear});
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{doubleyear});
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{singlehour});
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{doublehour});
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{singleminute});
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{doubleminute});
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{singlesecond});
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{doublesecond});
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{othercharacters});
	$kiriwrite_presmodule->endbox();
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecellheader");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{language});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecellheader");
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{systemlanguage});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");

	$kiriwrite_presmodule->addselectbox("language");

	# Process the list of available languages.

	foreach $language (keys %language_list){

		# Check if the language filename matches the filename in the configuration
		# file.

		if ($language_list{$language}{Filename} eq $language_config){

			$kiriwrite_presmodule->addoption($language_list{$language}{Name}, { Value => $language_list{$language}{Filename} , Selected => 1 });

		} else {

			$kiriwrite_presmodule->addoption($language_list{$language}{Name}, { Value => $language_list{$language}{Filename} });

		}

	}

	$kiriwrite_presmodule->endselectbox();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecellheader");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{modules});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecellheader");
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{presentationmodule});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");

	$kiriwrite_presmodule->addselectbox("presmodule");

	# Process the list of available presentation modules.

	foreach $presmodule (keys %presmodule_list){

		# Check if the presentation module fileanme matches the filename in the 
		# configuration file.

		if ($presmodule_list{$presmodule}{Filename} eq $presmodule_config){

			$kiriwrite_presmodule->addoption($presmodule_list{$presmodule}{Filename}, { Value => $presmodule_list{$presmodule}{Filename} , Selected => 1 });

		} else {

 			$kiriwrite_presmodule->addoption($presmodule_list{$presmodule}{Filename}, { Value => $presmodule_list{$presmodule}{Filename} });

		}

	}

	$kiriwrite_presmodule->endselectbox();

	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{databasemodule});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");

	# Process the list of available database modules.

	$kiriwrite_presmodule->addselectbox("dbmodule");

	foreach $dbmodule (keys %dbmodule_list){

		# Check if the database module fileanme matches the filename in the 
		# configuration file.

		if ($dbmodule_list{$dbmodule}{Filename} eq $dbmodule_config){

			$kiriwrite_presmodule->addoption($dbmodule_list{$dbmodule}{Filename}, { Value => $dbmodule_list{$dbmodule}{Filename} , Selected => 1 });

		} else {

 			$kiriwrite_presmodule->addoption($dbmodule_list{$dbmodule}{Filename}, { Value => $dbmodule_list{$dbmodule}{Filename} });

		}


	}

	$kiriwrite_presmodule->endselectbox();

	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{databaseserver});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addinputbox("database_server", { Size => 32, MaxLength => 128, Value => $database_server });
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{databaseport});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addinputbox("database_port", { Size => 5, MaxLength => 5, Value => $database_port });
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{databaseprotocol});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");

	# Check if TCP is being used.

	$kiriwrite_presmodule->addselectbox("database_protocol");

	if ($database_protocol eq "tcp"){

		# The TCP protocol is selected so have the TCP option selected.

		$kiriwrite_presmodule->addoption("TCP", { Value => "tcp", Selected => 1});

	} else {

		# The TCP protocol is not selected.

		$kiriwrite_presmodule->addoption("TCP", { Value => "tcp"});

	} 

	# Check if UDP is being used.

	if ($database_protocol eq "udp"){

		# The UDP protocol is selected so have the UDP option selected.

		$kiriwrite_presmodule->addoption("UDP", { Value => "udp", Selected => 1});

	} else {

		# The UDP protocol is not selected.

		$kiriwrite_presmodule->addoption("UDP", { Value => "udp"});

	}

	$kiriwrite_presmodule->endselectbox();

	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{databasename});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addinputbox("database_sqldatabase", { Size => 32, MaxLength => 32, Value => $database_sqldatabase });
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{databaseusername});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addinputbox("database_username", { Size => 16, MaxLength => 16, Value => $database_username });
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{databasepassword});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addinputbox("database_password", { Size => 16, MaxLength => 64, Password => 1 });
	$kiriwrite_presmodule->addtext(" ");
	$kiriwrite_presmodule->addcheckbox("database_password_keep", { OptionDescription => "Keep the current password", Checked => 1 });
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->startrow();
	$kiriwrite_presmodule->addcell("tablecell1");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{setting}->{tableprefix});
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->addcell("tablecell2");
	$kiriwrite_presmodule->addinputbox("database_tableprefix", { Size => 16, MaxLength => 16, Value => $database_prefix });
	$kiriwrite_presmodule->endcell();
	$kiriwrite_presmodule->endrow();

	$kiriwrite_presmodule->endtable();

	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addsubmit($kiriwrite_lang->{setting}->{changesettingsbutton});
	$kiriwrite_presmodule->addtext(" | ");
	$kiriwrite_presmodule->addreset($kiriwrite_lang->{common}->{restorecurrent});
	$kiriwrite_presmodule->addtext(" | ");
	$kiriwrite_presmodule->addlink($kiriwrite_env{"script_filename"} . "?mode=settings", { Text => $kiriwrite_lang->{setting}->{returnsettingslist} });
	$kiriwrite_presmodule->endbox();
	$kiriwrite_presmodule->endform();

	return $kiriwrite_presmodule->grab();

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

	use XML::Simple qw(XMLin);
	$xsl = XML::Simple->new();

	# Check if the Kiriwrite configuration file exists before using it and
	# return an critical error if it doesn't exist.

	my $kiriwrite_conf_exist = kiriwrite_fileexists("kiriwrite.xml");

	if ($kiriwrite_conf_exist eq 1){

		# The configuration really does not exist so return an critical error.

		kiriwrite_critical("configfilemissing");

	}

	# Check if the Kiriwrite configuration file has valid permission settings
	# before using it and return an critical error if it doesn't have the
	# valid permission settings.

	my $kiriwrite_conf_permissions = kiriwrite_filepermissions("kiriwrite.xml", 1, 0);

	if ($kiriwrite_conf_permissions eq 1){

		# The permission settings for the Kiriwrite configuration file are
		# invalid, so return an critical error.

		kiriwrite_critical("configfileinvalidpermissions");

	}

	# Converts the XML file into meaningful data for later on in this subroutine.

	my $kiriwrite_conf_file = 'kiriwrite.xml';
	my $kiriwrite_conf_data = $xsl->XMLin($kiriwrite_conf_file, SuppressEmpty => 1);

	# Go and fetch the settings and place them into a hash (that is global).

	%kiriwrite_config = (

		"directory_data_db"		=> $kiriwrite_conf_data->{settings}->{directories}->{database},
		"directory_data_output"		=> $kiriwrite_conf_data->{settings}->{directories}->{output},
		"directory_noncgi_images"	=> $kiriwrite_conf_data->{settings}->{directories}->{images},

		"system_language"		=> $kiriwrite_conf_data->{settings}->{language}->{lang},
		"system_presmodule"		=> $kiriwrite_conf_data->{settings}->{system}->{presentation},
		"system_dbmodule"		=> $kiriwrite_conf_data->{settings}->{system}->{database},
		"system_datetime"		=> $kiriwrite_conf_data->{settings}->{system}->{datetime},

		"database_server"		=> $kiriwrite_conf_data->{settings}->{database}->{server},
		"database_port"			=> $kiriwrite_conf_data->{settings}->{database}->{port},
		"database_protocol"		=> $kiriwrite_conf_data->{settings}->{database}->{protocol},
		"database_sqldatabase"		=> $kiriwrite_conf_data->{settings}->{database}->{database},
		"database_username"		=> $kiriwrite_conf_data->{settings}->{database}->{username},
		"database_password"		=> $kiriwrite_conf_data->{settings}->{database}->{password},
		"database_tableprefix"		=> $kiriwrite_conf_data->{settings}->{database}->{prefix}

	);

	# Do a validation check on all of the variables that were loaded into the global configuration hash.

	kiriwrite_variablecheck($kiriwrite_config{"directory_data_db"}, "maxlength", 64, 0);
	kiriwrite_variablecheck($kiriwrite_config{"directory_data_output"}, "maxlength", 64, 0);
	kiriwrite_variablecheck($kiriwrite_config{"directory_noncgi_images"}, "maxlength", 512, 0);
	kiriwrite_variablecheck($kiriwrite_config{"directory_data_template"}, "maxlength", 64, 0);

	my $kiriwrite_config_language_filename = kiriwrite_variablecheck($kiriwrite_config{"system_language"}, "language_filename", "", 1);
	my $kiriwrite_config_presmodule_filename = kiriwrite_variablecheck($kiriwrite_config{"system_presmodule"}, "module", 0, 1);
	my $kiriwrite_config_dbmodule_filename = kiriwrite_variablecheck($kiriwrite_config{"system_dbmodule"}, "module", 0, 1);

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

	# Check if the language file does exist before loading it and return an critical error
	# if it does not exist.

	my $kiriwrite_config_language_fileexists = kiriwrite_fileexists("lang/" . $kiriwrite_config{"system_language"} . ".xml");

	if ($kiriwrite_config_language_fileexists eq 1){

		# Language file does not exist so return an critical error.

		kiriwrite_critical("languagefilemissing");

	}

	# Check if the language file has valid permission settings and return an critical error if
	# the language file has invalid permissions settings.

	my $kiriwrite_config_language_filepermissions = kiriwrite_filepermissions("lang/" . $kiriwrite_config{"system_language"} . ".xml", 1, 0);

	if ($kiriwrite_config_language_filepermissions eq 1){

		# Language file contains invalid permissions so return an critical error.

		kiriwrite_critical("languagefilepermissions");

	}

	# Load the language file.

	$kiriwrite_lang = $xsl->XMLin("lang/" . $kiriwrite_config{"system_language"} . ".xml", SuppressEmpty => 1);

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

		# Check if the string is a valid UTF8 string.

  		if ($variable_data =~ m/^(
			[\x09\x0A\x0D\x20-\x7E]              # ASCII
			| [\xC2-\xDF][\x80-\xBF]             # non-overlong 2-byte
			|  \xE0[\xA0-\xBF][\x80-\xBF]        # excluding overlongs
			| [\xE1-\xEC\xEE\xEF][\x80-\xBF]{2}  # straight 3-byte
			|  \xED[\x80-\x9F][\x80-\xBF]        # excluding surrogates
			|  \xF0[\x90-\xBF][\x80-\xBF]{2}     # planes 1-3
			| [\xF1-\xF3][\x80-\xBF]{3}          # planes 4-15
			|  \xF4[\x80-\x8F][\x80-\xBF]{2}     # plane 16
		)*$/x){

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

	print header(-Expires=>'Sunday, 01-Jan-06 00:00:00 GMT', -charset=>'utf-8');
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

	my ($kiriwrite_error, %kiriwrite_error);

	%kiriwrite_error = (

		# Catch all error message.
		"generic"			=> $kiriwrite_lang->{error}->{generic},

		# Standard error messages.
		"blankfilename"			=> $kiriwrite_lang->{error}->{blankfilename},
		"blankvariable"			=> $kiriwrite_lang->{error}->{blankvariable},
		"fileexists"			=> $kiriwrite_lang->{error}->{fileexists},
		"internalerror"			=> $kiriwrite_lang->{error}->{internalerror},
		"invalidoption"			=> $kiriwrite_lang->{error}->{invalidoption},
		"invalidaction"			=> $kiriwrite_lang->{error}->{invalidaction},
		"invalidfilename"		=> $kiriwrite_lang->{error}->{invalidfilename},
		"invalidmode"			=> $kiriwrite_lang->{error}->{invalidmode},
		"invalidutf8"			=> $kiriwrite_lang->{error}->{invalidutf8},
		"invalidvariable"		=> $kiriwrite_lang->{error}->{invalidvariable},
		"variabletoolong"		=> $kiriwrite_lang->{error}->{variabletoolong},

		# Specific error messages.
		"blankcompiletype"		=> $kiriwrite_lang->{error}->{blankcompiletype},
		"blankdatabasepageadd"		=> $kiriwrite_lang->{error}->{blankdatabasepageadd},
		"blankdirectory"		=> $kiriwrite_lang->{error}->{blankdirectory},
		"blankfindfilter"		=> $kiriwrite_lang->{error}->{blankfindfilter},
		"blankdatetimeformat"		=> $kiriwrite_lang->{error}->{blankdatetimeformat},
		"databaseconnectionerror"	=> $kiriwrite_lang->{error}->{databaseconnectionerror},
		"databasecategoriestoolong"	=> $kiriwrite_lang->{error}->{databasecategoriestoolong},
		"databasecopysame"		=> $kiriwrite_lang->{error}->{databasecopysame},
		"databasealreadyexists"		=> $kiriwrite_lang->{error}->{databasealreadyexists},
		"datadirectorymissing"		=> $kiriwrite_lang->{error}->{datadirectorymissing},
		"datadirectoryinvalidpermissions"	=> $kiriwrite_lang->{error}->{datadirectoryinvalidpermissions},
		"databasedescriptiontoolong"	=> $kiriwrite_lang->{error}->{databasedescriptiontoolong},
		"databasefilenameinvalid"	=> $kiriwrite_lang->{error}->{databasefilenameinvalid},
		"databasefilenametoolong"	=> $kiriwrite_lang->{error}->{databasefilenametoolong},
		"databaseerror"	=> $kiriwrite_lang->{error}->{databaseerror},
		"databaseinvalidpermissions"	=> $kiriwrite_lang->{error}->{databaseinvalidpermissions},
		"databasenameinvalid"		=> $kiriwrite_lang->{error}->{databasenameinvalid},
		"databasenametoolong"		=> $kiriwrite_lang->{error}->{databasenametoolong},
		"databasenameblank"		=> $kiriwrite_lang->{error}->{databasenameblank},
		"databasemissingfile"		=> $kiriwrite_lang->{error}->{databasemissingfile},
		"databasemovemissingfile"	=> $kiriwrite_lang->{error}->{databasemovemissingfile},
		"databasenorename"		=> $kiriwrite_lang->{error}->{databasenorename},
		"databasemovesame"		=> $kiriwrite_lang->{error}->{databasemovesame},
		"dbmoduleblank"			=> $kiriwrite_lang->{error}->{dbmoduleblank},
		"dbmoduleinvalid"		=> $kiriwrite_lang->{error}->{dbmoduleinvalid},
		"dbdirectoryblank"		=> $kiriwrite_lang->{error}->{dbdirectoryblank},
		"dbdirectoryinvalid"		=> $kiriwrite_lang->{error}->{dbdirectoryinvalid},
		"dbmodulemissing"		=> $kiriwrite_lang->{error}->{dbmodulemissing},
		"filtersdatabasenotcreated"	=> $kiriwrite_lang->{error}->{filtersdatabasenotcreated},
		"filtersdbdatabaseerror"	=> $kiriwrite_lang->{error}->{filtersdbdatabaseerror},
		"filtersdbpermissions"		=> $kiriwrite_lang->{error}->{filtersdbpermissions},
		"filtersdbmissing"		=> $kiriwrite_lang->{error}->{filtersdbmissing},
		"filteridblank"			=> $kiriwrite_lang->{error}->{filteridblank},
		"filterdoesnotexist"		=> $kiriwrite_lang->{error}->{filterdoesnotexist},
		"filteridinvalid"		=> $kiriwrite_lang->{error}->{filteridinvalid},
		"filteridtoolong"		=> $kiriwrite_lang->{error}->{filteridtoolong},
		"findfiltertoolong"		=> $kiriwrite_lang->{error}->{findfiltertoolong},
		"filterpriorityinvalid"		=> $kiriwrite_lang->{error}->{filterpriorityinvalid},
		"filterpriorityinvalidchars"	=> $kiriwrite_lang->{error}->{filterpriorityinvalidchars},
		"filterprioritytoolong"		=> $kiriwrite_lang->{error}->{filterprioritytoolong},
		"invalidcompiletype"		=> $kiriwrite_lang->{error}->{invalidcompiletype},
		"invalidpagenumber"		=> $kiriwrite_lang->{error}->{invalidpagenumber},
		"nopagesselected"		=> $kiriwrite_lang->{error}->{nopagesselected},
		"invaliddirectory"		=> $kiriwrite_lang->{error}->{invaliddirectory},
		"invaliddatetimeformat"		=> $kiriwrite_lang->{error}->{invaliddatetimeformat},
		"invalidlanguagefilename"	=> $kiriwrite_lang->{error}->{invalidlanguagefilename},
		"languagefilenamemissing"	=> $kiriwrite_lang->{error}->{languagefilenamemissing},
		"moduleblank"			=> $kiriwrite_lang->{error}->{moduleblank},
		"moduleinvalid"			=> $kiriwrite_lang->{error}->{moduleinvalid},
		"newcopydatabasedatabaseerror"	=> $kiriwrite_lang->{error}->{newcopydatabasedatabaseerror},
		"newcopydatabasedoesnotexist"	=> $kiriwrite_lang->{error}->{newcopydatabasedoesnotexist},
		"newcopydatabasefileinvalidpermissions"	=> $kiriwrite_lang->{error}->{newcopydatabasefileinvalidpermissions},
		"newmovedatabasedatabaseerror"	=> $kiriwrite_lang->{error}->{newmovedatabasedatabaseerror},
		"newmovedatabasedoesnotexist"	=> $kiriwrite_lang->{error}->{newmovedatabasedoesnotexist},
		"newmovedatabasefileinvalidpermissions"	=> $kiriwrite_lang->{error}->{newmovedatabasefileinvalidpermissions},
		"nodatabasesavailable"		=> $kiriwrite_lang->{error}->{nodatabasesavailable},
		"nodatabaseselected"		=> $kiriwrite_lang->{error}->{nodatabaseselected},
		"noeditvaluesselected"		=> $kiriwrite_lang->{error}->{noeditvaluesselected},
		"oldcopydatabasedatabaseerror"	=> $kiriwrite_lang->{error}->{oldcopydatabasedatabaseerror},
		"oldcopydatabasedoesnotexist"	=> $kiriwrite_lang->{error}->{oldcopydatabasedoesnotexist},
		"oldcopydatabasefileinvalidpermissions"	=> $kiriwrite_lang->{error}->{oldcopydatabasefileinvalidpermissions},
		"oldmovedatabasedatabaseerror"	=> $kiriwrite_lang->{error}->{oldmovedatabasedatabaseerror},
		"oldmovedatabasedoesnotexist"	=> $kiriwrite_lang->{error}->{oldmovedatabasedoesnotexist},
		"oldmovedatabasefileinvalidpermissions"	=> $kiriwrite_lang->{error}->{oldmovedatabasefileinvalidpermissions},
		"outputdirectoryblank"		=> $kiriwrite_lang->{error}->{outputdirectoryblank},
		"outputdirectoryinvalid"	=> $kiriwrite_lang->{error}->{outputdirectoryinvalid},
		"outputdirectorymissing"	=> $kiriwrite_lang->{error}->{outputdirectorymissing},
		"outputdirectoryinvalidpermissions"	=> $kiriwrite_lang->{error}->{outputdirectoryinvalidpermissions},
		"presmoduleblank"		=> $kiriwrite_lang->{error}->{presmoduleblank},
		"presmoduleinvalid"		=> $kiriwrite_lang->{error}->{presmoduleinvalid},
		"presmodulemissing"		=> $kiriwrite_lang->{error}->{presmodulemissing},
		"pagefilenamedoesnotexist"	=> $kiriwrite_lang->{error}->{pagefilenamedoesnotexist},
		"pagefilenameexists"		=> $kiriwrite_lang->{error}->{pagefilenameexists},
		"pagefilenameinvalid"		=> $kiriwrite_lang->{error}->{pagefilenameinvalid},
		"pagefilenametoolong"		=> $kiriwrite_lang->{error}->{pagefilenametoolong},
		"pagefilenameblank"		=> $kiriwrite_lang->{error}->{pagefilenameblank},
		"pagetitletoolong"		=> $kiriwrite_lang->{error}->{pagetitletoolong},
		"pagedescriptiontoolong"	=> $kiriwrite_lang->{error}->{pagedescriptiontoolong},
		"pagesectiontoolong"		=> $kiriwrite_lang->{error}->{pagesectiontoolong},
		"pagedatabasefilenametoolong"	=> $kiriwrite_lang->{error}->{pagedatabasefilenametoolong},
		"pagesettingstoolong"		=> $kiriwrite_lang->{error}->{pagesettingstoolong},
		"pagesettingsinvalid"		=> $kiriwrite_lang->{error}->{pagesettingsinvalid},
		"pagetemplatefilenametoolong"	=> $kiriwrite_lang->{error}->{pagetemplatefilenametoolong},
		"replacefiltertoolong"		=> $kiriwrite_lang->{error}->{replacefiltertoolong},
		"servernameinvalid"		=> $kiriwrite_lang->{error}->{servernameinvalid},
		"servernametoolong"		=> $kiriwrite_lang->{error}->{servernametoolong},
		"serverdatabasenameinvalid"	=> $kiriwrite_lang->{error}->{serverdatabasenameinvalid},
		"serverdatabasenametoolong"	=> $kiriwrite_lang->{error}->{serverdatabasenametoolong},
		"serverdatabaseusernameinvalid"	=> $kiriwrite_lang->{error}->{serverdatabaseusernameinvalid},
		"serverdatabaseusernametoolong"	=> $kiriwrite_lang->{error}->{serverdatabaseusernametoolong},
		"serverdatabasepasswordtoolong"	=> $kiriwrite_lang->{error}->{serverdatabasepasswordtoolong},
		"serverdatabasetableprefixinvalid"	=> $kiriwrite_lang->{error}->{serverdatabasetableprefixinvalid},
		"serverdatabasetableprefixtoolong"	=> $kiriwrite_lang->{error}->{serverdatabasetableprefixtoolong},
		"serverportnumberinvalid"	=> $kiriwrite_lang->{error}->{serverportnumberinvalid},
		"serverportnumberinvalidcharacters"	=> $kiriwrite_lang->{error}->{serverportnumberinvalidcharacters},
		"serverportnumbertoolong"	=> $kiriwrite_lang->{error}->{serverportnumbertoolong},
		"serverprotocolnametoolong"	=> $kiriwrite_lang->{error}->{serverprotocolnametoolong},
		"serverprotocolinvalid"		=> $kiriwrite_lang->{error}->{serverprotocolinvalid},
		"templatenameblank"		=> $kiriwrite_lang->{error}->{templatenameblank},
		"templatefilenameexists"	=> $kiriwrite_lang->{error}->{templatefilenameexists},
		"templatefilenameinvalid"	=> $kiriwrite_lang->{error}->{templatefilenameinvalid},
		"templatedatabaseerror"		=> $kiriwrite_lang->{error}->{templatedatabaseerror},
		"templatedatabaseinvalidpermissions"	=> $kiriwrite_lang->{error}->{templatedatabaseinvalidpermissions},
		"templatedatabaseinvalidformat"	=> $kiriwrite_lang->{error}->{templatedatabaseinvalidformat},
		"templatedirectoryblank"	=> $kiriwrite_lang->{error}->{templatedirectoryblank},
		"templatedirectoryinvalid"	=> $kiriwrite_lang->{error}->{templatedirectoryinvalid},
		"templatedatabasenotcreated"	=> $kiriwrite_lang->{error}->{templatedatabasenotcreated},
		"templatefilenametoolong"	=> $kiriwrite_lang->{error}->{templatefilenametoolong},
		"templatenametoolong"		=> $kiriwrite_lang->{error}->{templatenametoolong},
		"templatedescriptiontoolong"	=> $kiriwrite_lang->{error}->{templatedescriptiontoolong},
		"templatedatabasemissing"	=> $kiriwrite_lang->{error}->{templatedatabasemissing},
		"templatedoesnotexist"		=> $kiriwrite_lang->{error}->{templatedoesnotexist},
		"templatefilenameblank"		=> $kiriwrite_lang->{error}->{templatefilenameblank},

	);

	# Check if the specified error is blank and if it is
	# use the generic error messsage.

	if (!$kiriwrite_error{$error_type}){
		$error_type = "generic";
	}

	$kiriwrite_presmodule->clear();

	$kiriwrite_presmodule->startbox("errorbox");
	$kiriwrite_presmodule->addtext($kiriwrite_lang->{error}->{error}, { Style => "errorheader" });
	$kiriwrite_presmodule->addlinebreak();
	$kiriwrite_presmodule->addtext($kiriwrite_error{$error_type}, { Style => "errortext" });

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
	);

	if (!$error_list{$error_type}){

		$error_type = "generic";

	}

	print header();
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

		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=db", { Text => $kiriwrite_lang->{database}->{submenu}->{viewdatabases} });
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=db&action=new", { Text => $kiriwrite_lang->{database}->{submenu}->{adddatabase} });

	} elsif ($menutype eq "pages"){
		# If the menu type is pages then print out the pages sub-menu.

		# First, fetch the database name from the HTTP query string.

		my $query = new CGI;
		my $db_filename = $query->param('database');

		# Check if a value has been placed in the db_filename string.

		if (!$db_filename){

			# As the database filename is blank, don't add an option to add a page.

		} else {

			# A database file has been specified so add an option to add a page to
			# the selected database.

			$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=page&action=add&database="  . $db_filename, { Text => $kiriwrite_lang->{pages}->{submenu}->{addpage} });

		}

	} elsif ($menutype eq "filter"){

		# If the menu type is filters then print out the filter sub-menu.

		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=filter", { Text => $kiriwrite_lang->{filter}->{submenu}->{showfilters} });
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=filter&action=add", { Text => $kiriwrite_lang->{filter}->{submenu}->{addfilter} });

	} elsif ($menutype eq "settings"){

		# If the menu type is options then print out the options sub-menu.

		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=settings", { Text => $kiriwrite_lang->{setting}->{submenu}->{viewsettings} });
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=settings&action=edit", { Text => $kiriwrite_lang->{setting}->{submenu}->{editsettings} });

	} elsif ($menutype eq "template"){

		# If the menu type is template then print out the template sub-menu.

		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=template", { Text => $kiriwrite_lang->{template}->{submenu}->{showtemplates} });
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=template&action=add", { Text => $kiriwrite_lang->{template}->{submenu}->{addtemplate} });

	} elsif ($menutype eq "compile"){

		# If the menu type is compile then print out the compile sub-menu.

		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=compile", { Text => $kiriwrite_lang->{compile}->{submenu}->{listdatabases} });
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=compile&action=all", { Text => $kiriwrite_lang->{compile}->{submenu}->{compileall} });
		$kiriwrite_presmodule->addtext(" | ");
		$kiriwrite_presmodule->addlink($kiriwrite_env{'script_filename'} . "?mode=compile&action=clean", { Text => $kiriwrite_lang->{compile}->{submenu}->{cleanoutputdirectory} });

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

	binmode STDOUT, ':utf8';

	print $pageoutput;

	return;

}

sub kiriwrite_output_xml{
#################################################################################
# kiriwrite_output_xml: Outputs several types of data to an XML file		#
#										#
# Usage:									#
#										#
# kiriwrite_output_xml(filename, type, settings);				#
#										#
# filename	Specifies the filename of the XML file.				#
# type		Specifies the type of the XML file to be written.		#
# settings		Specifies the following settings in any order.		#
#										#
# Settings for Kiriwrite configuration files:					#
#										#
# DatabaseDirectory	Specifies the new database directory to use.		#
# OutputDirectory	Specifies the new output directory to use.		#
# ImagesURIPath		Specifies the new URI path for images.			#
# DateTimeFormat	Specifies the new date and time format.			#
# SystemLanguage	Specifies the new language to use for Kiriwrite.	#
# PrsentationModule	Specifies the new presentation module to use for	#
#			Kiriwrite.						#
# DatabaseModule	Specifies the new database module to use for Kiriwrite.	#
# DatabaseServer	Specifies the database server to use.			#
# DaravasePort		Specifies the port the database server is running on.	#
# DatabaseProtocol	Specifies the protocol the database server is using.	#
# DatabaseSQLDatabase	Specifies the SQL database name to use.			#
# DatabaseUsername	Specifies the database server username.			#
# DatabasePassword	Specifies the password for the database server username.#
# DatabaseTablePrefix	Specifies the table prefix to use.			#
#################################################################################

	# Get the variables passed from the subroutine.

	my $xml_filename 	= shift;
	my $xml_type		= shift;
	my ($passedsettings)	= @_;

	# Check if filename is blank, if it is then return an error.

	if ($xml_filename eq ""){
		# Filename is blank, return an error.
		kiriwrite_error("blankfilename");
	}

	# Validate the XML filename to make sure nothing supicious is being passed.

	kiriwrite_variablecheck($xml_filename, "maxlength", 64, 0);
	kiriwrite_variablecheck($xml_filename, "filename", "", 0);

	# Check what type of XML data to output.

	if ($xml_type eq "config") {

		# The type of XML data to output is a Kiriwrite configuration file.

		# Get the data from the hash.

		my $settings_databasedir		= $passedsettings->{"DatabaseDirectory"};
		my $settings_outputdir			= $passedsettings->{"OutputDirectory"};
		my $settings_imagesuri			= $passedsettings->{"ImagesURIPath"};
		my $settings_datetime			= $passedsettings->{"DateTimeFormat"};
		my $settings_systemlanguage		= $passedsettings->{"SystemLanguage"};
		my $settings_presmodule			= $passedsettings->{"PresentationModule"};
		my $settings_dbmodule			= $passedsettings->{"DatabaseModule"};

		my $settings_database_server		= $passedsettings->{"DatabaseServer"};
		my $settings_database_port		= $passedsettings->{"DatabasePort"};
		my $settings_database_protocol		= $passedsettings->{"DatabaseProtocol"};
		my $settings_database_sqldatabase	= $passedsettings->{"DatabaseSQLDatabase"};
		my $settings_database_username		= $passedsettings->{"DatabaseUsername"};
		my $settings_database_password		= $passedsettings->{"DatabasePassword"};
		my $settings_database_tableprefix	= $passedsettings->{"DatabaseTablePrefix"};

		# Convert the password to make sure it can be read properly.

		if ($settings_database_password){

			$settings_database_password =~ s/\0//g;
			$settings_database_password =~ s/</&lt;/g;
			$settings_database_password =~ s/>/&gt;/g;

		}

		# Convert the less than and greater than characters are there and
		# convert them.

		if ($settings_imagesuri){

			$settings_imagesuri =~ s/</&lt;/g;
			$settings_imagesuri =~ s/>/&gt;/g;

		}

		# Check if the database password value is undefined and if it is then
		# set it blank.

		if (!$settings_database_password){

			$settings_database_password = "";

 		}

		# Create the XML data layout.

		my $xmldata = "<?xml version=\"1.0\"?>\r\n\r\n<kiriwrite-config>\r\n";

		$xmldata = $xmldata . "<!-- This file was automatically generated by Kiriwrite, please feel free to edit to your own needs. -->\r\n";
		$xmldata = $xmldata . "\t<settings>\r\n\t\t<directories>\r\n";

		$xmldata = $xmldata . "\t\t\t<database>" . $settings_databasedir . "</database>\r\n";
		$xmldata = $xmldata . "\t\t\t<output>" . $settings_outputdir  . "</output>\r\n";
		$xmldata = $xmldata . "\t\t\t<images>" . $settings_imagesuri . "</images>\r\n";
		$xmldata = $xmldata . "\t\t</directories>\r\n";

		$xmldata = $xmldata . "\t\t<language>\r\n";
		$xmldata = $xmldata . "\t\t\t<lang>" . $settings_systemlanguage . "</lang>\r\n";
		$xmldata = $xmldata . "\t\t</language>\r\n";

		$xmldata = $xmldata . "\t\t<system>\r\n";
		$xmldata = $xmldata . "\t\t\t<presentation>" . $settings_presmodule . "</presentation>\r\n";
		$xmldata = $xmldata . "\t\t\t<database>" . $settings_dbmodule . "</database>\r\n";
		$xmldata = $xmldata . "\t\t\t<datetime>" . $settings_datetime . "</datetime>\r\n";
		$xmldata = $xmldata . "\t\t</system>\r\n";

		$xmldata = $xmldata . "\t\t<database>\r\n";
		$xmldata = $xmldata . "\t\t\t<server>" . $settings_database_server . "</server>\r\n";
		$xmldata = $xmldata . "\t\t\t<port>" . $settings_database_port . "</port>\r\n";
		$xmldata = $xmldata . "\t\t\t<protocol>" . $settings_database_protocol . "</protocol>\r\n";
		$xmldata = $xmldata . "\t\t\t<database>" . $settings_database_sqldatabase . "</database>\r\n";
		$xmldata = $xmldata . "\t\t\t<username>" . $settings_database_username . "</username>\r\n";
		$xmldata = $xmldata . "\t\t\t<password>" . $settings_database_password . "</password>\r\n";
		$xmldata = $xmldata . "\t\t\t<prefix>" . $settings_database_tableprefix . "</prefix>\r\n";
		$xmldata = $xmldata . "\t\t</database>\r\n";

		$xmldata = $xmldata . "\t</settings>\r\n";

		$xmldata = $xmldata . "</kiriwrite-config>";

		# Open the Kiriwrite XML configuration file and write the new settings to the
		# configuration file.

		open(my $filehandle_xmlconfig, "> ", "kiriwrite.xml");
		print $filehandle_xmlconfig $xmldata;
		close($filehandle_xmlconfig);

	} else {

		# The type of XML data is something else that is not supported by
		# Kiriwrite, so return an error.

		kiriwrite_error("invalidoption");

	}

	return;

}

#################################################################################
# End listing the functions needed. 						#
#################################################################################

#################################################################################
# Begin proper script execution.						#
#################################################################################

kiriwrite_settings_load;	# Load the configuration options.

my $query = new CGI;		# Easily fetch variables from the HTTP string.



# Check if a mode has been specified and if a mode has been specified, continue
# and work out what mode has been specified.

if ($query->param('mode')){
	my $http_query_mode = $query->param('mode');

	if ($http_query_mode eq "db"){

		# If mode is 'db' (database), then check what action is required.

		if ($query->param('action')){
			# An action has been specified, so find out what action has been specified.

			my $http_query_action = $query->param('action');

			if ($http_query_action eq "edit"){
				# The edit action (which mean edit the settings for the selected database) has been specified,
				# get the database name and check if the action to edit an database has been confirmed.

				if ($query->param('database')){
					# If there is a value in the database variable check if it is a valid database. Otherwise,
					# return an error.

					my $http_query_database = $query->param('database');
				
					# Check if a value for confirm has been specified, if there is, check if it is the correct
					# value, otherwise return an error.

					if ($query->param('confirm')){
						# A value for confirm has been specified, find out what value it is. If the value is correct
						# then edit the database settings, otherwise return an error.

						my $http_query_confirm = $query->param('confirm');

						if ($http_query_confirm eq 1){
							# Value is correct, collect the variables to pass onto the database variable.
	
							# Get the variables from the HTTP query.
	
							my $newdatabasename 		= $query->param('databasename');
							my $newdatabasedescription 	= $query->param('databasedescription');
							my $newdatabasefilename 	= $query->param('databasefilename');
							my $databaseshortname 		= $query->param('database');
							my $databasenotes		= $query->param('databasenotes');
							my $databasecategories		= $query->param('databasecategories');

							# Check the permissions of the database configuration file and return
							# an error if the database permissions are invalid.
	
							# Pass the variables to the database editing subroutine.

							my $pagedata = kiriwrite_database_edit($databaseshortname, $newdatabasefilename, $newdatabasename, $newdatabasedescription, $databasenotes, $databasecategories, 1);
	
							kiriwrite_output_header;
							kiriwrite_output_page($kiriwrite_lang->{database}->{editdatabasetitle}, $pagedata, "database");
							exit;
	
						} else {
							# Value is incorrect, return and error.
							kiriwrite_error("invalidvariable");
						} 

					}

					# Display the form for editing an database.
					my $pagedata = kiriwrite_database_edit($http_query_database);

					kiriwrite_output_header;
					kiriwrite_output_page($kiriwrite_lang->{database}->{editdatabasetitle}, $pagedata, "database");
					exit;

				} else {

					# If there is no value in the database variable, then return an error.
					kiriwrite_error("invalidvariable");

				}

			} elsif ($http_query_action eq "delete"){

				# Action equested is to delete a database, find out if the user has already confirmed deletion of the database
				# and if the deletion of the database has been confirmed, delete the database.

				if ($query->param('confirm')){

					# User has confirmed to delete a database, pass the parameters to the kiriwrite_database_delete
					# subroutine.

					my $database_filename = $query->param('database');
					my $database_confirm = $query->param('confirm');
					my $pagedata = kiriwrite_database_delete($database_filename, $database_confirm);

					kiriwrite_output_header;
					kiriwrite_output_page($kiriwrite_lang->{database}->{deleteddatabase}, $pagedata, "database");

					exit;

				}

				# User has clicked on the delete link (thus hasn't confirmed the action to delete a database).

				my $database_filename = $query->param('database');
				my $pagedata = kiriwrite_database_delete($database_filename);

				kiriwrite_output_header;
				kiriwrite_output_page($kiriwrite_lang->{database}->{deletedatabase}, $pagedata, "database");

				exit;

			} elsif ($http_query_action eq "new"){

				# Action requested is to create a new database, find out if the user has already entered the information needed
				# to create a database and see if the user has confirmed the action, otherwise printout a form for adding a
				# database.

				my $http_query_confirm = $query->param('confirm');

				# Check if the confirm value is correct.

				if ($http_query_confirm){
					if ($http_query_confirm eq 1){

						# User has confirmed to create a database, pass the parameters to the 
						# kiriwrite_database_add subroutine.

						my $http_query_confirm = $query->param('confirm');

						my $database_name 		= $query->param('databasename');
						my $database_description 	= $query->param('databasedescription');
						my $database_filename 		= $query->param('databasefilename');
						my $database_notes		= $query->param('databasenotes');
						my $database_categories		= $query->param('databasecategories');

						my $pagedata = kiriwrite_database_add($database_filename, $database_name, $database_description, $database_notes, $database_categories, $http_query_confirm);

						kiriwrite_output_header;
						kiriwrite_output_page($kiriwrite_lang->{database}->{adddatabase}, $pagedata, "database");
						exit;

					} else {

						# The confirm value is something else other than 1 (which it shouldn't be), so
						# return an error.

					}
				}

				# User has clicked on the 'Add Database' link.

				my $pagedata = kiriwrite_database_add;

				kiriwrite_output_header;
				kiriwrite_output_page($kiriwrite_lang->{database}->{adddatabase}, $pagedata, "database");
				exit;

			} else {
				# Another option has been specified, so return an error.

 				kiriwrite_error("invalidaction");
			}
		}

		# No action has been specified, do the default action of displaying a list
		# of databases.

		my $pagedata = kiriwrite_database_list;

		kiriwrite_output_header;		# Output the header to browser/console/stdout.
		kiriwrite_output_page("", $pagedata, "database");	# Output the page to browser/console/stdout.
		exit;					# End the script.

	} elsif ($http_query_mode eq "page"){

		# If mode is 'page', then check what action is required.

		if ($query->param('action')){
			my $http_query_action = $query->param('action');

			# Check if the action requested matches with one of the options below. If it does,
			# go to that section, otherwise return an error.

			if ($http_query_action eq "view"){

				# The action selected was to view pages from a database, 

				my $database_name 	= $query->param('database');
				my $pagedata 		= kiriwrite_page_list($database_name);

				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang->{pages}->{viewingdatabase}, $pagedata, "pages");	# Output the page to browser/console/stdout.
				exit;			# End the script.

			} elsif ($http_query_action eq "add"){

				# The action selected was to add a page to the selected database.

				my $http_query_confirm	= $query->param('confirm');

				if (!$http_query_confirm){

					$http_query_confirm = 0;

				}

				if ($http_query_confirm eq 1){
		
					my $http_query_database		= $query->param('database');
					my $http_query_filename 	= $query->param('pagefilename');
					my $http_query_name 		= $query->param('pagename');
					my $http_query_description 	= $query->param('pagedescription');
					my $http_query_section		= $query->param('pagesection');
					my $http_query_template		= $query->param('pagetemplate');
					my $http_query_settings		= $query->param('pagesettings');
					my $http_query_content		= $query->param('pagecontent');
			
					my $pagedata			= kiriwrite_page_add($http_query_database, $http_query_filename, $http_query_name, $http_query_description, $http_query_section, $http_query_template, $http_query_settings, $http_query_content, $http_query_confirm);

					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{pages}->{addpage}, $pagedata, "pages");	# Output the page to browser/console/stdout.
					exit;				# End the script.

				}
		
				my $http_query_database	= $query->param('database');
				my $pagedata		= kiriwrite_page_add($http_query_database);

				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang->{pages}->{addpage}, $pagedata, "pages");	# Output the page to browser/console/stdout.
				exit;				# End the script.

			} elsif ($http_query_action eq "edit"){
			 
				# The action selected was to edit a page from a database.

				my $http_query_confirm = $query->param('confirm');

				if (!$http_query_confirm){

					$http_query_confirm = 0;

				}

				if ($http_query_confirm eq 1){

					# Get the needed values from the HTTP query.

					my $http_query_database 	= $query->param('database');
					my $http_query_filename		= $query->param('page');
					my $http_query_newfilename	= $query->param('pagefilename');
					my $http_query_name		= $query->param('pagename');
					my $http_query_description	= $query->param('pagedescription');
					my $http_query_section		= $query->param('pagesection');
					my $http_query_template		= $query->param('pagetemplate');
					my $http_query_settings		= $query->param('pagesettings');
					my $http_query_content		= $query->param('pagecontent');

					# Pass the values to the editing pages subroutine.

					my $pagedata = kiriwrite_page_edit($http_query_database, $http_query_filename, $http_query_newfilename, $http_query_name, $http_query_description, $http_query_section, $http_query_template, $http_query_settings, $http_query_content, $http_query_confirm);

					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{pages}->{editpagetitle}, $pagedata, "pages");	# Output the page to browser/console/stdout.
					exit;				# End the script.

				}

				# Get the needed values from the HTTP query.

				my $http_query_database = $query->param('database');
				my $http_query_filename	= $query->param('page');

				# Pass the values to the editing pages subroutine.

				my $pagedata = kiriwrite_page_edit($http_query_database, $http_query_filename);

				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang->{pages}->{editpagetitle}, $pagedata, "pages");	# Output the page to browser/console/stdout.
				exit;				# End the script.


			} elsif ($http_query_action eq "delete"){

				# The action selected was to delete a page from a database.

				my $http_query_database	= $query->param('database');
				my $http_query_page	= $query->param('page');
				my $http_query_confirm 	= $query->param('confirm');

				my $pagedata = "";
				my $selectionlist = "";

				if ($http_query_confirm){

					# The action has been confirmed, so try to delete the selected page
					# from the database.

					$pagedata = kiriwrite_page_delete($http_query_database, $http_query_page, $http_query_confirm);

					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{pages}->{deletepagetitle}, $pagedata, "pages"); # Output the page to browser/console/stdout.
					exit;				# End the script.

				}

				$pagedata = kiriwrite_page_delete($http_query_database, $http_query_page);

				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang->{pages}->{deletepagetitle}, $pagedata, "pages"); # Output the page to browser/console/stdout.
				exit;				# End the script.


			} elsif ($http_query_action eq "multidelete"){

				# The action selected was to delete multiple pages from a
				# database.

				my $http_query_database	= $query->param('database');
				my $http_query_confirm 	= $query->param('confirm');

				my @filelist;
				my $pagedata;

				if ($http_query_confirm){

					# The action to delete multiple pages from the selected
					# database has been confirmed.

					@filelist	= kiriwrite_selectedlist();
					$pagedata 	= kiriwrite_page_multidelete($http_query_database, $http_query_confirm, @filelist);

					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{pages}->{deletemultiplepages}, $pagedata, "pages"); # Output the page to browser/console/stdout.
					exit;				# End the script.

				}

				# Get the list of selected pages and pass them to the
				# multiple page delete subroutine.

				@filelist	= kiriwrite_selectedlist();
				$pagedata 	= kiriwrite_page_multidelete($http_query_database, $http_query_confirm, @filelist);

				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang->{pages}->{deletemultiplepages}, $pagedata, "pages"); # Output the page to browser/console/stdout.
				exit;				# End the script.

			} elsif ($http_query_action eq "multimove"){

				# The action selected was to move multiple pages from a
				# database.

				my $http_query_database		= $query->param('database');
				my $http_query_newdatabase	= $query->param('newdatabase');
				my $http_query_confirm		= $query->param('confirm');

				my @filelist;
				my $pagedata;

				if ($http_query_confirm){

					# The action to move multiple pages from the selected
					# database has been confirmed.

					@filelist	= kiriwrite_selectedlist();
					$pagedata	= kiriwrite_page_multimove($http_query_database, $http_query_newdatabase, $http_query_confirm, @filelist);

					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{pages}->{movepages}, $pagedata, "pages"); # Output the page to browser/console/stdout.
					exit;				# End the script.

				}

				# Get the list of selected pages and pass them to the
				# multiple page move subroutine.

				@filelist	= kiriwrite_selectedlist();
				$pagedata	= kiriwrite_page_multimove($http_query_database, $http_query_newdatabase, $http_query_confirm, @filelist);

				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang->{pages}->{movepages}, $pagedata, "pages"); # Output the page to browser/console/stdout.
				exit;				# End the script.

			} elsif ($http_query_action eq "multicopy"){

				# The action selected was to copy multiple pages from a
				# database.

				my $http_query_database		= $query->param('database');
				my $http_query_newdatabase	= $query->param('newdatabase');
				my $http_query_confirm		= $query->param('confirm');

				my @filelist;
				my $pagedata;

				if ($http_query_confirm){

					# The action to copy multiple pages from the selected
					# database has been confirmed.

					@filelist	= kiriwrite_selectedlist();
					$pagedata	= kiriwrite_page_multicopy($http_query_database, $http_query_newdatabase, $http_query_confirm, @filelist);

					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{pages}->{copypages}, $pagedata, "pages"); # Output the page to browser/console/stdout.
					exit;				# End the script.

				}

				# Get the list of selected pages and pass them to the
				# multiple page copy subroutine.

				@filelist	= kiriwrite_selectedlist();
				$pagedata	= kiriwrite_page_multicopy($http_query_database, $http_query_newdatabase, $http_query_confirm, @filelist);

				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang->{pages}->{copypages}, $pagedata, "pages"); # Output the page to browser/console/stdout.
				exit;				# End the script.

			} elsif ($http_query_action eq "multiedit"){

				# The action selected was to edit multiple pages from a
				# database.

				my $http_query_database		= $query->param('database');
				my $http_query_newsection	= $query->param('newsection');
				my $http_query_altersection	= $query->param('altersection');
				my $http_query_newtemplate	= $query->param('newtemplate');
				my $http_query_altertemplate	= $query->param('altertemplate');
				my $http_query_newsettings	= $query->param('newsettings');
				my $http_query_altersettings	= $query->param('altersettings');
				my $http_query_confirm		= $query->param('confirm');

				my @filelist;
				my $pagedata;

				if (!$http_query_confirm){

					@filelist 	= kiriwrite_selectedlist();
					$pagedata	= kiriwrite_page_multiedit($http_query_database, $http_query_newsection, $http_query_altersection, $http_query_newtemplate, $http_query_altertemplate, $http_query_newsettings, $http_query_altersettings, $http_query_confirm, @filelist);

					kiriwrite_output_header;	# Output the header to browser/console/stdout.
 					kiriwrite_output_page($kiriwrite_lang->{pages}->{multiedit}, $pagedata, "pages"); # Output the page to browser/console/stdout.
					exit;

				}

				# Get the list of selected pages and pass them to the
				# multiple page edit subroutine.

				@filelist 	= kiriwrite_selectedlist();
				$pagedata	= kiriwrite_page_multiedit($http_query_database, $http_query_newsection, $http_query_altersection, $http_query_newtemplate, $http_query_altertemplate, $http_query_newsettings, $http_query_altersettings, $http_query_confirm, @filelist);

				kiriwrite_output_header;	# Output the header to browser/console/stdout.
 				kiriwrite_output_page($kiriwrite_lang->{pages}->{multiedit}, $pagedata, "pages"); # Output the page to browser/console/stdout.
				exit;				# End the script.

			} else {
				kiriwrite_error("invalidaction");
			}

		} else {

			# If there the action option is left blank, then print out a form where the database
			# can be selected to view pages from.

			my $pagedata = kiriwrite_page_list;

			kiriwrite_output_header;	# Output the header to browser/console/stdout.
			kiriwrite_output_page($kiriwrite_lang->{pages}->{databaseselecttitle}, $pagedata, "pages");	# Output the page to browser/console/stdout.
			exit;				# End the script.

		}

		# No action has been specified, do the default action of listing pages from
		# the first database found in the directory.

	} elsif ($http_query_mode eq "filter"){

		# If there's a value for action in the HTTP query, then
		# get that value that is in the HTTP query.

		if ($query->param('action')){

			# There is a value for action in the HTTP query,
			# so get the value from it.

			my $http_query_action = $query->param('action');

			if ($http_query_action eq "add"){

				# The action the user requested is to add a filter to the
				# filter database.

				# Check if there is a value in confirm and if there is
				# then pass it on to the new find and replace words
				# to add to the filter database.

				my $http_query_confirm = $query->param('confirm');

				if ($http_query_confirm){

					# There is a value in http_query_confirm, so pass on the
					# new find and replace words so that they can be added
					# to the filter database.

					my $http_query_findwords 	= $query->param('findword');
					my $http_query_replacewords 	= $query->param('replaceword');
					my $http_query_priority		= $query->param('priority');
					my $http_query_notes		= $query->param('notes');
				
					my $pagedata = kiriwrite_filter_add($http_query_findwords, $http_query_replacewords, $http_query_priority, $http_query_notes, $http_query_confirm);

					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{filter}->{addfilter}, $pagedata, "filter"); # Output the page to browser/console/stdout.
					exit;				# End the script.

				}

				my $pagedata = kiriwrite_filter_add();

				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang->{filter}->{addfilter}, $pagedata, "filter"); # Output the page to browser/console/stdout.
				exit;				# End the script.

			} elsif ($http_query_action eq "edit"){

				# The action the user requested is to edit an filter from
				# the filter database.

				my $http_query_number = $query->param('filter');
				my $http_query_confirm = $query->param('confirm');

				if ($http_query_confirm){

					# There is a value in http_query_confirm, so pass on the
					# new find and replace words so that the filter database
					# can be edited.

					my $http_query_findwords 	= $query->param('filterfind');
					my $http_query_replacewords 	= $query->param('filterreplace');
					my $http_query_priority		= $query->param('priority');
					my $http_query_notes		= $query->param('notes');

					my $pagedata = kiriwrite_filter_edit($http_query_number, $http_query_findwords, $http_query_replacewords, $http_query_priority, $http_query_notes, $http_query_confirm);

					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{filter}->{editfilter}, $pagedata, "filter");	# Output the page to browser/console/stdout.
					exit;				# End the script.

				}

				my $pagedata = kiriwrite_filter_edit($http_query_number);

				kiriwrite_output_header;		# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang->{filter}->{editfilter}, $pagedata, "filter");	# Output the page to browser/console/stdout.
				exit;					# End the script.

			} elsif ($http_query_action eq "delete"){

				# The action the user requested is to delete an filter
				# from the filter database.

				my $http_query_number = $query->param('filter');
				my $http_query_confirm = $query->param('confirm');

				if ($http_query_confirm){

					my $pagedata = kiriwrite_filter_delete($http_query_number, $http_query_confirm);

					kiriwrite_output_header;		# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{filter}->{deletefilter}, $pagedata, "filter"); # Output the page to browser/console/stdout.
					exit;					# End the script

				}

				my $pagedata = kiriwrite_filter_delete($http_query_number);

				kiriwrite_output_header;		# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang->{filter}->{deletefilter}, $pagedata, "filter");	# Output the page to browser/console/stdout.
				exit;					# End the script.

			} else {

				# Another action was requested that was not one of 
				# the ones prcedding this catch all, so return
				# an error saying that an invalid option was
				# specified.

				kiriwrite_error("invalidaction");

			}

		} else {

			my $pagedata = kiriwrite_filter_list();

			kiriwrite_output_header;	# Output the header to browser/console/stdout.
			kiriwrite_output_page($kiriwrite_lang->{filter}->{viewfilters}, $pagedata, "filter"); # Output the page to browser/console/stdout.
			exit;				# End the script.

		}



	} elsif ($http_query_mode eq "template"){

		# Check if an action has been specified in the HTTP query.

		if ($query->param('action')){

			# An action has been specified in the HTTP query.

			my $http_query_action = $query->param('action');

			if ($http_query_action eq "delete"){
				# Get the required parameters from the HTTP query.

				my $http_query_template	= $query->param('template');
				my $http_query_confirm	= $query->param('confirm');

				# Check if a value for confirm has been specified (it shouldn't)
				# be blank.

				if (!$http_query_confirm){
					# The confirm parameter of the HTTP query is blank, so
					# write out a form asking the user to confirm the deletion
					# of the selected template.

					my $pagedata = kiriwrite_template_delete($http_query_template);

					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{template}->{deletetemplate}, $pagedata, "template");	# Output the page to browser/console/stdout.
					exit;				# End the script.

				} else {

					my $pagedata = kiriwrite_template_delete($http_query_template, $http_query_confirm);

					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{template}->{deletetemplate}, $pagedata, "template");	# Output the page to browser/console/stdout.
					exit;				# End the script.

				}

			} elsif ($http_query_action eq "add") {

				# Get the variables from the HTTP query in preperation for processing.

				my $http_query_confirm	= $query->param('confirm');
				my $http_query_templatelayout	= $query->param('templatelayout');
				my $http_query_templatename	= $query->param('templatename');
				my $http_query_templatedescription = $query->param('templatedescription');
				my $http_query_templatefilename = $query->param('templatefilename');

				# Check if there is a confirmed value in the http_query_confirm variable.

				if (!$http_query_confirm){

					# Since there is no confirm value, print out a form for creating a new
					# template.

					my $pagedata = kiriwrite_template_add();

					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{template}->{addtemplate}, $pagedata, "template");	# Output the page to browser/console/stdout.
					exit;				# End the script.

				} else {

					# A value in the http_query_confirm value is specified, so pass the
					# variables onto the kiriwrite_template_add subroutine.

					my $pagedata = kiriwrite_template_add($http_query_templatefilename, $http_query_templatename, $http_query_templatedescription, $http_query_templatelayout, $http_query_confirm);

					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{template}->{addtemplate}, $pagedata, "template");	# Output the page to browser/console/stdout.
					exit;				# End the script.

				}

			} elsif ($http_query_action eq "edit") {

				# Get the required parameters from the HTTP query.

				my $http_query_templatefile 	= $query->param('template');
				my $http_query_confirm 		= $query->param('confirm');

				# Check to see if http_query_confirm has a value of '1' in it and
				# if it does, edit the template using the settings providied.

				if (!$http_query_confirm){

					# Since there is no confirm value, open the template configuration
					# file and the template file itself then print out the data on to
					# the form.

					my $pagedata = kiriwrite_template_edit($http_query_templatefile);
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{template}->{edittemplate}, $pagedata, "template");	# Output the page to browser/console/stdout.
					exit;				# End the script.

				} elsif ($http_query_confirm eq 1) {

					# Since there is a confirm value of 1, the user has confirm the
					# action of editing of a template so get the other variables 
					# that were also sent and pass the variables to the subroutine.

					my $http_query_newfilename 	= $query->param('newfilename');
					my $http_query_newname		= $query->param('newname');
					my $http_query_newdescription	= $query->param('newdescription');
					my $http_query_newlayout	= $query->param('newlayout');

					my $pagedata = kiriwrite_template_edit($http_query_templatefile, $http_query_newfilename, $http_query_newname, $http_query_newdescription, $http_query_newlayout, $http_query_confirm);
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{template}->{edittemplate}, $pagedata, "template");	# Output the page to browser/console/stdout.
					exit;				# End the script.

				} else {

					# Another confirm value is there instead of '0' or '1'. Return
					# an error saying it is invalid.

					kiriwrite_error("invalidvariable");

				}

			} else {

				# Another action was specified and was not one of the ones above, so
				# return an error.

				kiriwrite_error("invalidaction");

			}

		} else {

			# If the action option is left blank, then print out a form where the list
			# of templates are available.

			my $pagedata = kiriwrite_template_list;

			kiriwrite_output_header;	# Output the header to browser/console/stdout.
			kiriwrite_output_page($kiriwrite_lang->{template}->{viewtemplates}, $pagedata, "template");	# Output the page to browser/console/stdout.
			exit;				# End the script.

		}

	} elsif ($http_query_mode eq "compile"){

		# The mode selected is to compile pages from databases.

		# If the action option is left blank, then print out a form where the list
		# of databases to compile are available.

		if ($query->param('action')){

			my $http_query_action = $query->param('action');

			if ($http_query_action eq "compile"){

				# The specified action is to compile the pages, check if the
				# action to compile the page has been confirmed.

				my $http_query_confirm 	= $query->param('confirm');
				my $http_query_type	= $query->param('type');

				# If it is blank, set the confirm value to 0.

				if (!$http_query_confirm){

					# The http_query_confirm variable is uninitalised, so place a
					# '0' (meaning an unconfirmed action).

					$http_query_confirm = 0;

				}

				# If the compile type is blank then return an error.

				if (!$http_query_type){

					# Compile type is blank so return an error.

					kiriwrite_error("blankcompiletype");

				}

				if ($http_query_type eq "multiple"){

					if ($http_query_confirm eq 1){

						# The action to compile the pages has been confirmed so
						# compile the pages.

						my @selectedlist = kiriwrite_selectedlist();
						my $pagedata = kiriwrite_compile_makepages($http_query_type, $http_query_confirm, @selectedlist);

						kiriwrite_output_header;	# Output the header to browser/console/stdout.
						kiriwrite_output_page($kiriwrite_lang->{compile}->{compilepages}, $pagedata, "compile"); # Output the page to browser/console/stdout.
						exit;				# End the script.

					} else {

						# The action to compile the pages has not been confirmed
						# so write a form asking the user to confirm the action
						# of compiling the pages.

						my @selectedlist = kiriwrite_selectedlist();
						my $pagedata = kiriwrite_compile_makepages($http_query_type, $http_query_confirm, @selectedlist);

						kiriwrite_output_header;	# Output the header to browser/console/stdout.
						kiriwrite_output_page($kiriwrite_lang->{compile}->{compileselecteddatabases}, $pagedata, "compile"); # Output the page to browser/console/stdout.
						exit;				# End the script.

					}

				} elsif ($http_query_type eq "single"){

					my $http_query_database	= $query->param('database');
					my @selectedlist;
					$selectedlist[0] = $http_query_database;
					my $pagedata = kiriwrite_compile_makepages($http_query_type, $http_query_confirm, @selectedlist);

					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{compile}->{compiledatabase}, $pagedata, "compile");
					exit;				# End the script.

				} else {

					kiriwrite_error("invalidcompiletype");

				}

			} elsif ($http_query_action eq "all"){

				# The selected action is to compile all of the databases
				# in the database directory. Check if the action to
				# compile all of the databases has been confirmed.

				my $http_query_confirm = $query->param('confirm');

				if (!$http_query_confirm){

					# The http_query_confirm variable is uninitalised, so place a
					# '0' (meaning an unconfirmed action).

					$http_query_confirm = 0;

				}

				if ($http_query_confirm eq 1){

					# The action to compile all the databases has been confirmed.

				}

				my $pagedata = kiriwrite_compile_all();

				kiriwrite_output_header;			# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang->{compile}->{compilealldatabases}, $pagedata, "compile");
				exit;

			} elsif ($http_query_action eq "clean") {

				# The selected action is to clean the output directory.
				# Check if the action to clean the output directory
				# has been confirmed.

				my $http_query_confirm = $query->param('confirm');

				if (!$http_query_confirm){

					# The http_query_confirm variable is uninitalised, so place a
					# '0' (meaning an unconfirmed action).

					$http_query_confirm = 0;

				}

				if ($http_query_confirm eq 1){

					# The action to clean the output directory has been confirmed.

					my $pagedata = kiriwrite_compile_clean($http_query_confirm);

					kiriwrite_output_header;		# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{compile}->{cleanoutputdirectory}, $pagedata, "compile");	# Output the page to browser/console/stdout.
					exit;					# End the script.
			
				}

				# The action to clean the output directory is not
				# confirmed, so write a page asking the user
				# to confirm cleaning the output directory.

				my $pagedata = kiriwrite_compile_clean();

				kiriwrite_output_header;		# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang->{compile}->{cleanoutputdirectory}, $pagedata, "compile");	# Output the page to browser/console/stdout.
				exit;					# End the script.

			} else {

				# The action specified was something else other than those
				# above, so return an error.

				kiriwrite_error("invalidaction");

			}
		}

		my $pagedata = kiriwrite_compile_list;

		kiriwrite_output_header;		# Output the header to browser/console/stdout.
		kiriwrite_output_page($kiriwrite_lang->{compile}->{compilepages}, $pagedata, "compile");	# Output the page to browser/console/stdout.
		exit;					# End the script.

	} elsif ($http_query_mode eq "settings"){

		# The mode selected is view (and change settings).

		# If the action value has been left blank, then view the list of
		# current settings.

		if ($query->param('action')){
			my $http_query_action = $query->param('action');

			if ($http_query_action eq "edit"){

				# The action specified is to edit the settings. Check if the action
				# to edit the settings has been confirmed.

				my $http_query_confirm = $query->param('confirm');

				if (!$http_query_confirm){

					# The confirm value is blank, so set it to 0.

					$http_query_confirm = 0;

				}

				if ($http_query_confirm eq 1){

					# The action to edit the settings has been confirmed. Get the
					# required settings from the HTTP query.

					my $http_query_database		= $query->param('databasedir');
					my $http_query_output		= $query->param('outputdir');
					my $http_query_imagesuri	= $query->param('imagesuripath');
					my $http_query_datetimeformat	= $query->param('datetime');
					my $http_query_systemlanguage	= $query->param('language');
					my $http_query_presmodule	= $query->param('presmodule');
					my $http_query_dbmodule		= $query->param('dbmodule');

					my $http_query_database_server		= $query->param('database_server');
					my $http_query_database_port		= $query->param('database_port');
					my $http_query_database_protocol	= $query->param('database_protocol');
					my $http_query_database_sqldatabase	= $query->param('database_sqldatabase');
					my $http_query_database_username	= $query->param('database_username');
					my $http_query_database_passwordkeep	= $query->param('database_password_keep');
					my $http_query_database_password	= $query->param('database_password');
					my $http_query_database_tableprefix	= $query->param('database_tableprefix');

					my $pagedata = kiriwrite_settings_edit({ DatabaseDirectory => $http_query_database, OutputDirectory => $http_query_output, ImagesURIPath => $http_query_imagesuri, DateTimeFormat => $http_query_datetimeformat, SystemLanguage => $http_query_systemlanguage, PresentationModule => $http_query_presmodule, DatabaseModule => $http_query_dbmodule, DatabaseServer => $http_query_database_server, DatabasePort => $http_query_database_port, DatabaseProtocol => $http_query_database_protocol, DatabaseSQLDatabase => $http_query_database_sqldatabase, DatabaseUsername => $http_query_database_username, DatabasePasswordKeep => $http_query_database_passwordkeep, DatabasePassword => $http_query_database_password, DatabaseTablePrefix => $http_query_database_tableprefix, Confirm => 1 });

					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang->{setting}->{editsettings}, $pagedata, "settings");	# Output the page to browser/console/stdout.
					exit;				# End the script.

				}

				# The action to edit the settings has not been confirmed.

				my $pagedata = kiriwrite_settings_edit;

				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang->{setting}->{editsettings}, $pagedata, "settings");	# Output the page to browser/console/stdout.
				exit;				# End the script.

			} else {

				# The action specified was something else other than those
				# above, so return an error.

				kiriwrite_error("invalidaction");

			}

		}

		# No action has been specified, so print out the list of settings currently being used.

		my $pagedata = kiriwrite_settings_view;

		kiriwrite_output_header;		# Output the header to browser/console/stdout.
		kiriwrite_output_page($kiriwrite_lang->{setting}->{viewsettings}, $pagedata, "settings");	# Output the page to browser/console/stdout.
		exit;					# End the script.

	} else {
		# Another mode has been specified than the ones above, so return an error saying that
		# an invalid option was specified.

		kiriwrite_error("invalidmode");
	}

} else {

	# No mode has been specified, so print the default "first-run" view of the
	# database list.

	my $pagedata = kiriwrite_database_list;

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