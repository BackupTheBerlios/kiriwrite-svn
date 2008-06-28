#!/usr/bin/perl -Tw

#################################################################################
# Kiriwrite (kiriwrite.pl/kiriwrite.cgi)					#
# Main program script			     					#
#										#
# Version: 0.4.0								#
# mod_perl 2.x compatabile version						#
#										#
# Copyright (C) 2005-2008 Steve Brokenshire <sbrokenshire@xestia.co.uk>		#
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

use strict;
use warnings;

use utf8;
use CGI::Lite;
use Tie::IxHash;

binmode STDOUT, ':utf8';

# This is commented out because it uses a fair bit of CPU usage.

#use CGI::Carp('fatalsToBrowser'); 	# Output errors to the browser.

# Declare global variables for Kiriwrite settings and languages.

our ($kiriwrite_config, %kiriwrite_config, %kiriwrite_lang, $kiriwrite_lang, $kiriwrite_version, %kiriwrite_version, $kiriwrite_env, %kiriwrite_env, $kiriwrite_presmodule, $kiriwrite_dbmodule, $form_data, $kiriwrite_script_name, $kiriwrite_env_path);

# If you are using mod_perl please change these settings to the correct
# directory where this script is being run from.

use lib '.';
chdir('.');

# Load the common functions module.

use Modules::System::Common;

# Setup the version information for Kiriwrite.

%kiriwrite_version = (
	"major" 	=> 0,
	"minor" 	=> 4,
	"revision" 	=> 0
);

kiriwrite_initalise;		# Initalise the Kiriwrite enviroment.
kiriwrite_settings_load;	# Load the configuration options.

my $query_lite = new CGI::Lite;

# Check if a mode has been specified and if a mode has been specified, continue
# and work out what mode has been specified.

$form_data = $query_lite->parse_form_data;

if ($form_data->{'mode'}){
	my $http_query_mode = $form_data->{'mode'};

	if ($http_query_mode eq "db"){

		use Modules::System::Database;

		if ($form_data->{'action'}){
		# An action has been specified, so find out what action has been specified.

		my $http_query_action = $form_data->{'action'};
	
			if ($http_query_action eq "edit"){
				# The edit action (which mean edit the settings for the selected database) has been specified,
				# get the database name and check if the action to edit an database has been confirmed.
		
				if ($form_data->{'database'}){
					# If there is a value in the database variable check if it is a valid database. Otherwise,
					# return an error.
		
					my $http_query_database = $form_data->{'database'};
				
					# Check if a value for confirm has been specified, if there is, check if it is the correct
					# value, otherwise return an error.
		
					if ($form_data->{'confirm'}){
						# A value for confirm has been specified, find out what value it is. If the value is correct
						# then edit the database settings, otherwise return an error.
		
						my $http_query_confirm = $form_data->{'confirm'};
		
						if ($http_query_confirm eq 1){
							# Value is correct, collect the variables to pass onto the database variable.
		
							# Get the variables from the HTTP query.
		
							my $newdatabasename 		= $form_data->{'databasename'};
							my $newdatabasedescription 	= $form_data->{'databasedescription'};
							my $newdatabasefilename 	= $form_data->{'databasefilename'};
							my $databaseshortname 		= $form_data->{'database'};
							my $databasenotes		= $form_data->{'databasenotes'};
							my $databasecategories		= $form_data->{'databasecategories'};
		
							# Pass the variables to the database editing subroutine.
		
							my $pagedata = kiriwrite_database_edit($databaseshortname, $newdatabasefilename, $newdatabasename, $newdatabasedescription, $databasenotes, $databasecategories, 1);
		
							kiriwrite_output_header;
							kiriwrite_output_page($kiriwrite_lang{database}{editdatabasetitle}, $pagedata, "database");
							exit;
		
						} else {
							# Value is incorrect, return and error.
							kiriwrite_error("invalidvariable");
						} 
		
					}
		
					# Display the form for editing an database.
					my $pagedata = kiriwrite_database_edit($http_query_database);
		
					kiriwrite_output_header;
					kiriwrite_output_page($kiriwrite_lang{database}{editdatabasetitle}, $pagedata, "database");
					exit;
		
				} else {
		
					# If there is no value in the database variable, then return an error.
					kiriwrite_error("invalidvariable");
		
				}
		
			} elsif ($http_query_action eq "delete"){
		
				# Action equested is to delete a database, find out if the user has already confirmed deletion of the database
				# and if the deletion of the database has been confirmed, delete the database.
		
				if ($form_data->{'confirm'}){
		
					# User has confirmed to delete a database, pass the parameters to the kiriwrite_database_delete
					# subroutine.
		
					my $database_filename 	= $form_data->{'database'};
					my $database_confirm 	= $form_data->{'confirm'};
					my $pagedata = kiriwrite_database_delete($database_filename, $database_confirm);
		
					kiriwrite_output_header;
					kiriwrite_output_page($kiriwrite_lang->{database}->{deleteddatabase}, $pagedata, "database");
		
					exit;
		
				}
		
				# User has clicked on the delete link (thus hasn't confirmed the action to delete a database).
		
				my $database_filename = $form_data->{'database'};
				my $pagedata = kiriwrite_database_delete($database_filename);
		
				kiriwrite_output_header;
				kiriwrite_output_page($kiriwrite_lang->{database}->{deletedatabase}, $pagedata, "database");
		
				exit;
		
			} elsif ($http_query_action eq "new"){
		
				# Action requested is to create a new database, find out if the user has already entered the information needed
				# to create a database and see if the user has confirmed the action, otherwise printout a form for adding a
				# database.
		
				my $http_query_confirm = $form_data->{'confirm'};
		
				# Check if the confirm value is correct.
		
				if ($http_query_confirm){
					if ($http_query_confirm eq 1){
		
						# User has confirmed to create a database, pass the parameters to the 
						# kiriwrite_database_add subroutine.
		
						my $http_query_confirm = $form_data->{'confirm'};
		
						my $database_name 		= $form_data->{'databasename'};
						my $database_description 	= $form_data->{'databasedescription'};
						my $database_filename 		= $form_data->{'databasefilename'};
						my $database_notes		= $form_data->{'databasenotes'};
						my $database_categories		= $form_data->{'databasecategories'};
		
						my $pagedata = kiriwrite_database_add($database_filename, $database_name, $database_description, $database_notes, $database_categories, $http_query_confirm);
		
						kiriwrite_output_header;
						kiriwrite_output_page($kiriwrite_lang{database}{adddatabase}, $pagedata, "database");
						exit;
		
					} else {
		
						# The confirm value is something else other than 1 (which it shouldn't be), so
						# return an error.
		
					}
				}
	
				# User has clicked on the 'Add Database' link.
	
				my $pagedata = kiriwrite_database_add();
	
				kiriwrite_output_header;
				kiriwrite_output_page($main::kiriwrite_lang{database}{adddatabase}, $pagedata, "database");
				exit;
	
			} else {
				# Another option has been specified, so return an error.
	
				kiriwrite_error("invalidaction");
			}

		} else {

			# No action has been specified, do the default action of displaying a list
			# of databases.
		
			my $pagedata = kiriwrite_database_list();
		
			kiriwrite_output_header;		# Output the header to browser/console/stdout.
			kiriwrite_output_page("", $pagedata, "database");	# Output the page to browser/console/stdout.
			exit;					# End the script.

		}

	} elsif ($http_query_mode eq "page"){

		use Modules::System::Page;

		if ($form_data->{'action'}){
			my $http_query_action = $form_data->{'action'};
		
			# Check if the action requested matches with one of the options below. If it does,
			# go to that section, otherwise return an error.

			if ($http_query_action eq "view"){
		
				# The action selected was to view pages from a database, 
		
				my $http_query_database		= $form_data->{'database'};
				my $http_query_browsenumber	= $form_data->{'browsenumber'};
				my $pagedata 		= kiriwrite_page_list($http_query_database, $http_query_browsenumber);
		
				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang->{pages}->{viewingdatabase}, $pagedata, "pages", $http_query_database);	# Output the page to browser/console/stdout.
				exit;			# End the script.
		
			} elsif ($http_query_action eq "add"){
		
				# The action selected was to add a page to the selected database.
		
				my $http_query_confirm	= $form_data->{'confirm'};
		
				if (!$http_query_confirm){
		
					$http_query_confirm = 0;
		
				}
		
				if ($http_query_confirm eq 1){
		
					my $http_query_database		= $form_data->{'database'};
					my $http_query_filename 	= $form_data->{'pagefilename'};
					my $http_query_name 		= $form_data->{'pagename'};
					my $http_query_description 	= $form_data->{'pagedescription'};
					my $http_query_section		= $form_data->{'pagesection'};
					my $http_query_template		= $form_data->{'pagetemplate'};
					my $http_query_settings		= $form_data->{'pagesettings'};
					my $http_query_content		= $form_data->{'pagecontent'};
			
					my $pagedata			= kiriwrite_page_add($http_query_database, $http_query_filename, $http_query_name, $http_query_description, $http_query_section, $http_query_template, $http_query_settings, $http_query_content, $http_query_confirm);
		
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{pages}{addpage}, $pagedata, "pages");	# Output the page to browser/console/stdout.
					exit;				# End the script.
		
				}
		
				my $http_query_database	= $form_data->{'database'};
				my $pagedata		= kiriwrite_page_add($http_query_database);
		
				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang{pages}{addpage}, $pagedata, "pages");	# Output the page to browser/console/stdout.
				exit;				# End the script.
		
			}  elsif ($http_query_action eq "edit"){
				
				# The action selected was to edit a page from a database.
		
				my $http_query_confirm = $form_data->{'confirm'};
		
				if (!$http_query_confirm){
		
					$http_query_confirm = 0;
		
				}
		
				if ($http_query_confirm eq 1){
		
					# Get the needed values from the HTTP query.
		
					my $http_query_database 	= $form_data->{'database'};
					my $http_query_filename		= $form_data->{'page'};
					my $http_query_newfilename	= $form_data->{'pagefilename'};
					my $http_query_name		= $form_data->{'pagename'};
					my $http_query_description	= $form_data->{'pagedescription'};
					my $http_query_section		= $form_data->{'pagesection'};
					my $http_query_template		= $form_data->{'pagetemplate'};
					my $http_query_settings		= $form_data->{'pagesettings'};
					my $http_query_content		= $form_data->{'pagecontent'};
		
					# Pass the values to the editing pages subroutine.
		
					my $pagedata = kiriwrite_page_edit($http_query_database, $http_query_filename, $http_query_newfilename, $http_query_name, $http_query_description, $http_query_section, $http_query_template, $http_query_settings, $http_query_content, $http_query_confirm);
		
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{pages}{editpagetitle}, $pagedata, "pages");	# Output the page to browser/console/stdout.
					exit;				# End the script.
		
				}
		
				# Get the needed values from the HTTP query.
		
				my $http_query_database = $form_data->{'database'};
				my $http_query_filename	= $form_data->{'page'};
		
				# Pass the values to the editing pages subroutine.
		
				my $pagedata = kiriwrite_page_edit($http_query_database, $http_query_filename);
		
				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang{pages}{editpagetitle}, $pagedata, "pages");	# Output the page to browser/console/stdout.
				exit;				# End the script.

			
			} elsif ($http_query_action eq "delete"){
		
				# The action selected was to delete a page from a database.
		
				my $http_query_database	= $form_data->{'database'};
				my $http_query_page	= $form_data->{'page'};
				my $http_query_confirm 	= $form_data->{'confirm'};
		
				my $pagedata = "";
				my $selectionlist = "";
		
				if ($http_query_confirm){
		
					# The action has been confirmed, so try to delete the selected page
					# from the database.
		
					$pagedata = kiriwrite_page_delete($http_query_database, $http_query_page, $http_query_confirm);
		
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{pages}{deletepagetitle}, $pagedata, "pages"); # Output the page to browser/console/stdout.
					exit;				# End the script.
		
				}
		
				$pagedata = kiriwrite_page_delete($http_query_database, $http_query_page);
		
				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang{pages}{deletepagetitle}, $pagedata, "pages"); # Output the page to browser/console/stdout.
				exit;				# End the script.

			} elsif ($http_query_action eq "multidelete"){

				# The action selected was to delete multiple pages from a
				# database.
		
				my $http_query_database	= $form_data->{'database'};
				my $http_query_confirm 	= $form_data->{'confirm'};
		
				my @filelist;
				my $pagedata;

				if ($http_query_confirm eq 1){
		
					# The action to delete multiple pages from the selected
					# database has been confirmed.
		
					@filelist	= kiriwrite_selectedlist($form_data);
					$pagedata 	= kiriwrite_page_multidelete($http_query_database, $http_query_confirm, @filelist);
		
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{pages}{deletemultiplepages}, $pagedata, "pages"); # Output the page to browser/console/stdout.
					exit;				# End the script.
		
				}
		
				# Get the list of selected pages and pass them to the
				# multiple page delete subroutine.
		
				@filelist	= kiriwrite_selectedlist($form_data);
				$pagedata 	= kiriwrite_page_multidelete($http_query_database, $http_query_confirm, @filelist);
		
				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang{pages}{deletemultiplepages}, $pagedata, "pages"); # Output the page to browser/console/stdout.
				exit;				# End the script.

			} elsif ($http_query_action eq "multimove"){

				# The action selected was to move multiple pages from a
				# database.
		
				my $http_query_database		= $form_data->{'database'};
				my $http_query_newdatabase	= $form_data->{'newdatabase'};
				my $http_query_confirm		= $form_data->{'confirm'};
		
				my @filelist;
				my $pagedata;
		
				if ($http_query_confirm){
		
					# The action to move multiple pages from the selected
					# database has been confirmed.
		
					@filelist	= kiriwrite_selectedlist($form_data);
					$pagedata	= kiriwrite_page_multimove($http_query_database, $http_query_newdatabase, $http_query_confirm, @filelist);
		
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{pages}{movepages}, $pagedata, "pages"); # Output the page to browser/console/stdout.
					exit;				# End the script.
		
				}
		
				# Get the list of selected pages and pass them to the
				# multiple page move subroutine.
		
				@filelist	= kiriwrite_selectedlist($form_data);
				$pagedata	= kiriwrite_page_multimove($http_query_database, $http_query_newdatabase, $http_query_confirm, @filelist);
		
				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang{pages}{movepages}, $pagedata, "pages"); # Output the page to browser/console/stdout.
				exit;				# End the script.

			} elsif ($http_query_action eq "multicopy"){

				# The action selected was to copy multiple pages from a
				# database.
		
				my $http_query_database		= $form_data->{'database'};
				my $http_query_newdatabase	= $form_data->{'newdatabase'};
				my $http_query_confirm		= $form_data->{'confirm'};
		
				my @filelist;
				my $pagedata;
		
				if ($http_query_confirm){
		
					# The action to copy multiple pages from the selected
					# database has been confirmed.
		
					@filelist	= kiriwrite_selectedlist($form_data);
					$pagedata	= kiriwrite_page_multicopy($http_query_database, $http_query_newdatabase, $http_query_confirm, @filelist);
		
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{pages}{copypages}, $pagedata, "pages"); # Output the page to browser/console/stdout.
					exit;				# End the script.
		
				}
		
				# Get the list of selected pages and pass them to the
				# multiple page copy subroutine.
		
				@filelist	= kiriwrite_selectedlist($form_data);
				$pagedata	= kiriwrite_page_multicopy($http_query_database, $http_query_newdatabase, $http_query_confirm, @filelist);
		
				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang{pages}{copypages}, $pagedata, "pages"); # Output the page to browser/console/stdout.
				exit;				# End the script.

			} elsif ($http_query_action eq "multiedit"){

				# The action selected was to edit multiple pages from a
				# database.
		
				my $http_query_database		= $form_data->{'database'};
				my $http_query_newsection	= $form_data->{'newsection'};
				my $http_query_altersection	= $form_data->{'altersection'};
				my $http_query_newtemplate	= $form_data->{'newtemplate'};
				my $http_query_altertemplate	= $form_data->{'altertemplate'};
				my $http_query_newsettings	= $form_data->{'newsettings'};
				my $http_query_altersettings	= $form_data->{'altersettings'};
				my $http_query_confirm		= $form_data->{'confirm'};
		
				my @filelist;
				my $pagedata;
		
				if (!$http_query_confirm){
		
					@filelist 	= kiriwrite_selectedlist($form_data);
					$pagedata	= kiriwrite_page_multiedit($http_query_database, $http_query_newsection, $http_query_altersection, $http_query_newtemplate, $http_query_altertemplate, $http_query_newsettings, $http_query_altersettings, $http_query_confirm, @filelist);
		
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{pages}{multiedit}, $pagedata, "pages"); # Output the page to browser/console/stdout.
					exit;
		
				}
		
				# Get the list of selected pages and pass them to the
				# multiple page edit subroutine.
		
				@filelist 	= kiriwrite_selectedlist($form_data);
				$pagedata	= kiriwrite_page_multiedit($http_query_database, $http_query_newsection, $http_query_altersection, $http_query_newtemplate, $http_query_altertemplate, $http_query_newsettings, $http_query_altersettings, $http_query_confirm, @filelist);
		
				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang{pages}{multiedit}, $pagedata, "pages"); # Output the page to browser/console/stdout.
				exit;				# End the script.

			} else {
				kiriwrite_error("invalidaction");
			}

		} else {

			# If there the action option is left blank, then print out a form where the database
			# can be selected to view pages from.
		
			my $pagedata = kiriwrite_page_list();
		
			kiriwrite_output_header;	# Output the header to browser/console/stdout.
			kiriwrite_output_page($kiriwrite_lang{pages}{databaseselecttitle}, $pagedata, "");	# Output the page to browser/console/stdout.
			exit;				# End the script.

		}

	} elsif ($http_query_mode eq "template"){

		use Modules::System::Template;

		if ($form_data->{'action'}){
		
			# An action has been specified in the HTTP query.
		
			my $http_query_action = $form_data->{'action'};
		
			if ($http_query_action eq "delete"){
				# Get the required parameters from the HTTP query.
		
				my $http_query_template	= $form_data->{'template'};
				my $http_query_confirm	= $form_data->{'confirm'};
		
				# Check if a value for confirm has been specified (it shouldn't)
				# be blank.
		
				if (!$http_query_confirm){
					# The confirm parameter of the HTTP query is blank, so
					# write out a form asking the user to confirm the deletion
					# of the selected template.
		
					my $pagedata = kiriwrite_template_delete($http_query_template);
		
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{template}{deletetemplate}, $pagedata, "template");	# Output the page to browser/console/stdout.
					exit;				# End the script.
		
				} else {
		
					my $pagedata = kiriwrite_template_delete($http_query_template, $http_query_confirm);
		
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{template}{deletetemplate}, $pagedata, "template");	# Output the page to browser/console/stdout.
					exit;				# End the script.
		
				}
		
			} elsif ($http_query_action eq "add") {
		
				# Get the variables from the HTTP query in preperation for processing.
		
				my $http_query_confirm		= $form_data->{'confirm'};
				my $http_query_templatelayout	= $form_data->{'templatelayout'};
				my $http_query_templatename	= $form_data->{'templatename'};
				my $http_query_templatedescription = $form_data->{'templatedescription'};
				my $http_query_templatefilename	= $form_data->{'templatefilename'};
		
				# Check if there is a confirmed value in the http_query_confirm variable.
		
				if (!$http_query_confirm){
		
					# Since there is no confirm value, print out a form for creating a new
					# template.
		
					my $pagedata = kiriwrite_template_add();
		
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{template}{addtemplate}, $pagedata, "template");	# Output the page to browser/console/stdout.
					exit;				# End the script.
		
				} else {
		
					# A value in the http_query_confirm value is specified, so pass the
					# variables onto the kiriwrite_template_add subroutine.
		
					my $pagedata = kiriwrite_template_add($http_query_templatefilename, $http_query_templatename, $http_query_templatedescription, $http_query_templatelayout, $http_query_confirm);
		
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{template}{addtemplate}, $pagedata, "template");	# Output the page to browser/console/stdout.
					exit;				# End the script.
		
				}
		
			} elsif ($http_query_action eq "edit") {
		
				# Get the required parameters from the HTTP query.
		
				my $http_query_templatefile 	= $form_data->{'template'};
				my $http_query_confirm 		= $form_data->{'confirm'};
		
				# Check to see if http_query_confirm has a value of '1' in it and
				# if it does, edit the template using the settings providied.
		
				if (!$http_query_confirm){
		
					# Since there is no confirm value, open the template configuration
					# file and the template file itself then print out the data on to
					# the form.
		
					my $pagedata = kiriwrite_template_edit($http_query_templatefile);
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{template}{edittemplate}, $pagedata, "template");	# Output the page to browser/console/stdout.
					exit;				# End the script.
		
				} elsif ($http_query_confirm eq 1) {
		
					# Since there is a confirm value of 1, the user has confirm the
					# action of editing of a template so get the other variables 
					# that were also sent and pass the variables to the subroutine.
		
					my $http_query_newfilename 	= $form_data->{'newfilename'};
					my $http_query_newname		= $form_data->{'newname'};
					my $http_query_newdescription	= $form_data->{'newdescription'};
					my $http_query_newlayout	= $form_data->{'newlayout'};
		
					my $pagedata = kiriwrite_template_edit($http_query_templatefile, $http_query_newfilename, $http_query_newname, $http_query_newdescription, $http_query_newlayout, $http_query_confirm);
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{template}{edittemplate}, $pagedata, "template");	# Output the page to browser/console/stdout.
					exit;				# End the script.
		
				} else {
		
					# Another confirm value is there instead of '0' or '1'. Return
					# an error saying it is invalid.
		
					kiriwrite_error("invalidvariable");
		
				}
		
			} elsif ($http_query_action eq "view"){
		
				# Get the required parameters from the HTTP query.
		
				my $http_query_browsenumber	= $form_data->{'browsenumber'};
		
				my $pagedata = kiriwrite_template_list($http_query_browsenumber);
		
				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang{template}{viewtemplates}, $pagedata, "template");	# Output the page to browser/console/stdout.
				exit;				# End the script.
		
			} else {
		
				# Another action was specified and was not one of the ones above, so
				# return an error.
		
				kiriwrite_error("invalidaction");
		
			}
		
		} else {
		
			# If the action option is left blank, then print out a form where the list
			# of templates are available.
		
			my $pagedata = kiriwrite_template_list();
		
			kiriwrite_output_header;	# Output the header to browser/console/stdout.
			kiriwrite_output_page($kiriwrite_lang{template}{viewtemplates}, $pagedata, "template");	# Output the page to browser/console/stdout.
			exit;				# End the script.
		
		}

	} elsif ($http_query_mode eq "filter"){

		use Modules::System::Filter;

		if ($form_data->{'action'}){
		
			# There is a value for action in the HTTP query,
			# so get the value from it.
		
			my $http_query_action = $form_data->{'action'};
		
			if ($http_query_action eq "add"){
		
				# The action the user requested is to add a filter to the
				# filter database.
		
				# Check if there is a value in confirm and if there is
				# then pass it on to the new find and replace words
				# to add to the filter database.
		
				my $http_query_confirm = $form_data->{'confirm'};
		
				if ($http_query_confirm){
		
					# There is a value in http_query_confirm, so pass on the
					# new find and replace words so that they can be added
					# to the filter database.
		
					my $http_query_findwords 	= $form_data->{'findword'};
					my $http_query_replacewords 	= $form_data->{'replaceword'};
					my $http_query_priority		= $form_data->{'priority'};
					my $http_query_enabled		= $form_data->{'enabled'};
					my $http_query_notes		= $form_data->{'notes'};
				
					my $pagedata = kiriwrite_filter_add({ FindFilter => $http_query_findwords, ReplaceFilter => $http_query_replacewords, Priority => $http_query_priority, Enabled => $http_query_enabled, Notes => $http_query_notes, Confirm => $http_query_confirm });
					#my $pagedata = kiriwrite_filter_add($http_query_findwords, $http_query_replacewords, $http_query_priority, $http_query_notes, $http_query_confirm);
		
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{filter}{addfilter}, $pagedata, "filter"); # Output the page to browser/console/stdout.
					exit;				# End the script.
		
				}
		
				my $pagedata = kiriwrite_filter_add();
		
				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang{filter}{addfilter}, $pagedata, "filter"); # Output the page to browser/console/stdout.
				exit;				# End the script.
		
			} elsif ($http_query_action eq "edit"){
		
				# The action the user requested is to edit an filter from
				# the filter database.
		
				my $http_query_number 	= $form_data->{'filter'};
				my $http_query_confirm 	= $form_data->{'confirm'};
		
				if ($http_query_confirm){
		
					# There is a value in http_query_confirm, so pass on the
					# new find and replace words so that the filter database
					# can be edited.
		
					my $http_query_findwords 	= $form_data->{'filterfind'};
					my $http_query_replacewords 	= $form_data->{'filterreplace'};
					my $http_query_priority		= $form_data->{'priority'};
					my $http_query_notes		= $form_data->{'notes'};
					my $http_query_enabled		= $form_data->{'enabled'};
		
					my $pagedata = kiriwrite_filter_edit({ FilterID => $http_query_number, NewFindFilter => $http_query_findwords, NewReplaceFilter => $http_query_replacewords, NewPriority => $http_query_priority, NewEnabled => $http_query_enabled, NewFilterNotes => $http_query_notes, Confirm => $http_query_confirm });
		
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{filter}{editfilter}, $pagedata, "filter");	# Output the page to browser/console/stdout.
					exit;				# End the script.
		
				}
		
				my $pagedata = kiriwrite_filter_edit({ FilterID => $http_query_number });
		
				kiriwrite_output_header;		# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang{filter}{editfilter}, $pagedata, "filter");	# Output the page to browser/console/stdout.
				exit;					# End the script.
		
			} elsif ($http_query_action eq "delete"){
		
				# The action the user requested is to delete an filter
				# from the filter database.
		
				my $http_query_number = $form_data->{'filter'};
				my $http_query_confirm = $form_data->{'confirm'};
		
				if ($http_query_confirm){
		
					my $pagedata = kiriwrite_filter_delete($http_query_number, $http_query_confirm);
		
					kiriwrite_output_header;		# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{filter}{deletefilter}, $pagedata, "filter"); # Output the page to browser/console/stdout.
					exit;					# End the script
		
				}
		
				my $pagedata = kiriwrite_filter_delete($http_query_number);
		
				kiriwrite_output_header;		# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang{filter}{deletefilter}, $pagedata, "filter");	# Output the page to browser/console/stdout.
				exit;					# End the script.
		
			} elsif ($http_query_action eq "view"){
		
				# The action the user requested is to view the list
				# filters on the filter database.
		
				my $http_query_browsenumber = $form_data->{'browsenumber'};
		
				my $pagedata = kiriwrite_filter_list($http_query_browsenumber);
		
				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang{filter}{viewfilters}, $pagedata, "filter"); # Output the page to browser/console/stdout.
				exit;				# End the script.
		
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
			kiriwrite_output_page($kiriwrite_lang{filter}{viewfilters}, $pagedata, "filter"); # Output the page to browser/console/stdout.
			exit;				# End the script.
		
		}

	} elsif ($http_query_mode eq "compile"){

		use Modules::System::Compile;

		if ($form_data->{'action'}){
		
			my $http_query_action = $form_data->{'action'};
		
			if ($http_query_action eq "compile"){
		
				# The specified action is to compile the pages, check if the
				# action to compile the page has been confirmed.
		
				my $http_query_confirm 	= $form_data->{'confirm'};
				my $http_query_type	= $form_data->{'type'};
		
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
		
						my $http_query_override		= $form_data->{'enableoverride'};
						my $http_query_overridetemplate	= $form_data->{'overridetemplate'};
		
						my @selectedlist = kiriwrite_selectedlist($form_data);
						my $pagedata = kiriwrite_compile_makepages($http_query_type, $http_query_confirm, $http_query_override, $http_query_overridetemplate, @selectedlist);
		
						kiriwrite_output_header;	# Output the header to browser/console/stdout.
						kiriwrite_output_page($kiriwrite_lang{compile}{compilepages}, $pagedata, "compile"); # Output the page to browser/console/stdout.
						exit;				# End the script.
		
					} else {
		
						# The action to compile the pages has not been confirmed
						# so write a form asking the user to confirm the action
						# of compiling the pages.
		
						my @selectedlist = kiriwrite_selectedlist($form_data);
						my $pagedata = kiriwrite_compile_makepages($http_query_type, $http_query_confirm, "", "", @selectedlist);
		
						kiriwrite_output_header;	# Output the header to browser/console/stdout.
						kiriwrite_output_page($kiriwrite_lang{compile}{compileselecteddatabases}, $pagedata, "compile"); # Output the page to browser/console/stdout.
						exit;				# End the script.
		
					}
		
				} elsif ($http_query_type eq "single"){
		
					my $http_query_database	= $form_data->{'database'};
					my @selectedlist;
					$selectedlist[0] = $http_query_database;
					my $pagedata = kiriwrite_compile_makepages($http_query_type, $http_query_confirm, "", "", @selectedlist);
		
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{compile}{compiledatabase}, $pagedata, "compile");
					exit;				# End the script.
		
				} else {
		
					kiriwrite_error("invalidcompiletype");
		
				}
		
			} elsif ($http_query_action eq "all"){
		
				# The selected action is to compile all of the databases
				# in the database directory. Check if the action to
				# compile all of the databases has been confirmed.
		
				my $http_query_confirm = $form_data->{'confirm'};
		
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
				kiriwrite_output_page($kiriwrite_lang{compile}{compilealldatabases}, $pagedata, "compile");
				exit;
		
			} elsif ($http_query_action eq "clean") {
		
				# The selected action is to clean the output directory.
				# Check if the action to clean the output directory
				# has been confirmed.
		
				my $http_query_confirm = $form_data->{'confirm'};
		
				if (!$http_query_confirm){
		
					# The http_query_confirm variable is uninitalised, so place a
					# '0' (meaning an unconfirmed action).
		
					$http_query_confirm = 0;
		
				}
		
				if ($http_query_confirm eq 1){
		
					# The action to clean the output directory has been confirmed.
		
					my $pagedata = kiriwrite_compile_clean($http_query_confirm);
		
					kiriwrite_output_header;		# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{compile}{cleanoutputdirectory}, $pagedata, "compile");	# Output the page to browser/console/stdout.
					exit;					# End the script.
			
				}
		
				# The action to clean the output directory is not
				# confirmed, so write a page asking the user
				# to confirm cleaning the output directory.
		
				my $pagedata = kiriwrite_compile_clean();
		
				kiriwrite_output_header;		# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang{compile}{cleanoutputdirectory}, $pagedata, "compile");	# Output the page to browser/console/stdout.
				exit;					# End the script.
		
			} else {
		
				# The action specified was something else other than those
				# above, so return an error.
		
				kiriwrite_error("invalidaction");
		
			}
		}
		
		my $pagedata = kiriwrite_compile_list();
		
		kiriwrite_output_header;		# Output the header to browser/console/stdout.
		kiriwrite_output_page($kiriwrite_lang{compile}{compilepages}, $pagedata, "compile");	# Output the page to browser/console/stdout.
		exit;					# End the script.
		
	} elsif ($http_query_mode eq "settings"){

		use Modules::System::Settings;

		if ($form_data->{'action'}){
			my $http_query_action = $form_data->{'action'};
		
			if ($http_query_action eq "edit"){
		
				# The action specified is to edit the settings. Check if the action
				# to edit the settings has been confirmed.
		
				my $http_query_confirm = $form_data->{'confirm'};
		
				if (!$http_query_confirm){
		
					# The confirm value is blank, so set it to 0.
		
					$http_query_confirm = 0;
		
				}
		
				if ($http_query_confirm eq 1){
		
					# The action to edit the settings has been confirmed. Get the
					# required settings from the HTTP query.
		
					my $http_query_database		= $form_data->{'databasedir'};
					my $http_query_output		= $form_data->{'outputdir'};
					my $http_query_imagesuri	= $form_data->{'imagesuripath'};
					my $http_query_datetimeformat	= $form_data->{'datetime'};
					my $http_query_systemlanguage	= $form_data->{'language'};
					my $http_query_presmodule	= $form_data->{'presmodule'};
					my $http_query_dbmodule		= $form_data->{'dbmodule'};
					my $http_query_textareacols	= $form_data->{'textareacols'};
					my $http_query_textarearows	= $form_data->{'textarearows'};
					my $http_query_pagecount	= $form_data->{'pagecount'};
					my $http_query_filtercount	= $form_data->{'filtercount'};
					my $http_query_templatecount	= $form_data->{'templatecount'};
		
					my $http_query_database_server		= $form_data->{'database_server'};
					my $http_query_database_port		= $form_data->{'database_port'};
					my $http_query_database_protocol	= $form_data->{'database_protocol'};
					my $http_query_database_sqldatabase	= $form_data->{'database_sqldatabase'};
					my $http_query_database_username	= $form_data->{'database_username'};
					my $http_query_database_passwordkeep	= $form_data->{'database_password_keep'};
					my $http_query_database_password	= $form_data->{'database_password'};
					my $http_query_database_tableprefix	= $form_data->{'database_tableprefix'};
		
					my $pagedata = kiriwrite_settings_edit({ DatabaseDirectory => $http_query_database, OutputDirectory => $http_query_output, ImagesURIPath => $http_query_imagesuri, DateTimeFormat => $http_query_datetimeformat, SystemLanguage => $http_query_systemlanguage, PresentationModule => $http_query_presmodule, TextAreaCols => $http_query_textareacols, TextAreaRows => $http_query_textarearows, PageCount => $http_query_pagecount, FilterCount => $http_query_filtercount, TemplateCount => $http_query_templatecount, DatabaseModule => $http_query_dbmodule, DatabaseServer => $http_query_database_server, DatabasePort => $http_query_database_port, DatabaseProtocol => $http_query_database_protocol, DatabaseSQLDatabase => $http_query_database_sqldatabase, DatabaseUsername => $http_query_database_username, DatabasePasswordKeep => $http_query_database_passwordkeep, DatabasePassword => $http_query_database_password, DatabaseTablePrefix => $http_query_database_tableprefix, Confirm => 1 });
		
					kiriwrite_output_header;	# Output the header to browser/console/stdout.
					kiriwrite_output_page($kiriwrite_lang{setting}{editsettings}, $pagedata, "settings");	# Output the page to browser/console/stdout.
					exit;				# End the script.
		
				}
		
				# The action to edit the settings has not been confirmed.
		
				my $pagedata = kiriwrite_settings_edit();
		
				kiriwrite_output_header;	# Output the header to browser/console/stdout.
				kiriwrite_output_page($kiriwrite_lang{setting}{editsettings}, $pagedata, "settings");	# Output the page to browser/console/stdout.
				exit;				# End the script.
		
			} else {
		
				# The action specified was something else other than those
				# above, so return an error.
		
				kiriwrite_error("invalidaction");
		
			}
		
		}
		
		# No action has been specified, so print out the list of settings currently being used.
		
		my $pagedata = kiriwrite_settings_view();
		
		kiriwrite_output_header;		# Output the header to browser/console/stdout.
		kiriwrite_output_page($kiriwrite_lang{setting}{viewsettings}, $pagedata, "settings");	# Output the page to browser/console/stdout.
		exit;					# End the script.

	} else {

		# An invalid mode has been specified so return
		# an error.

		kiriwrite_error("invalidmode");

	}
	
} else {

	# No mode has been specified, so print the default "first-run" view of the
	# database list.

	use Modules::System::Database;

	my $pagedata = kiriwrite_database_list();

	kiriwrite_output_header;		# Output the header to browser/console/stdout.
	kiriwrite_output_page("", $pagedata, "database");	# Output the page to browser/console/stdout.
	exit;					# End the script.		

}

__END__