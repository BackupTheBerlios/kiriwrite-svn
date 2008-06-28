package Modules::System::Page;

use Modules::System::Common;
use strict;
use warnings;
use Exporter;

our @ISA = qw(Exporter);
our @EXPORT = qw(kiriwrite_page_list kiriwrite_page_add kiriwrite_page_edit kiriwrite_page_delete kiriwrite_page_multidelete kiriwrite_page_multimove kiriwrite_page_multicopy kiriwrite_page_multiedit);

sub kiriwrite_page_list{
#################################################################################
# kiriwrite_page_list: Lists pages from an database.				#
#										#
# Usage:									#
#										#
# kiriwrite_page_list([database], [browsernumber]);				#
#										#
# database	Specifies the database to retrieve the pages from.		#
# browsenumber	Specifies which list of pages to look at.			#
#################################################################################

	# Get the database file name from what was passed to the subroutine.

	my ($database_file, $page_browsenumber) = @_;

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

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Open the data directory and get all of the databases.

		@database_list	= $main::kiriwrite_dbmodule->getdblist();

		# Check if any errors occured while trying to get the list of databases.

 		if ($main::kiriwrite_dbmodule->geterror eq "DataDirMissing"){

			# The database directory is missing so return an error.

			kiriwrite_error("datadirectorymissing");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "DataDirInvalidPermissions"){

			# The database directory has invalid permissions set so return
			# an error.

			kiriwrite_error("datadirectoryinvalidpermissions");

		}

		# Get the information about each database (the short name and friendly name).

		foreach $data_file (@database_list){

			$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $data_file });

			# Check if any errors occured while selecting the database.

			if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

				# The database does not exist, so process the next
				# database.

				next;

			} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

				# The database has invalid permissions set, so process
				# the next database.

				next;

			}

			# Get the database information.

			%database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

			# Check if any errors had occured while getting the database
			# information.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

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

		$main::kiriwrite_dbmodule->disconnect();

		# Write the page data.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{viewpages}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{nodatabaseselected});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"});
		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addhiddendata("mode", "page");
		$main::kiriwrite_presmodule->addhiddendata("action", "view");
		$main::kiriwrite_presmodule->addselectbox("database");
		foreach $dbfilename (@databasefilenames){
			$dbname = $databasenames[$dbseek];
			$dbseek++;
			$main::kiriwrite_presmodule->addoption($dbname . " (" . $dbfilename . ")", { Value => $dbfilename });
		}
		$main::kiriwrite_presmodule->endselectbox();
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{pages}{viewbutton});
		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->endform();

		return $main::kiriwrite_presmodule->grab();

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
		my $page_split		= $main::kiriwrite_config{"display_pagecount"};
		my $page_list		= 0;
		my $page_list_count	= 0;

		tie(%database_info, 'Tie::IxHash');
		tie(%page_info, 'Tie::IxHash');

		# The database_file variable is not blank, so print out a list of pages from
		# the selected database.

		# Preform a variable check on the database filename to make sure that it is
		# valid before using it.

		kiriwrite_variablecheck($database_file, "filename", "", 0);
		kiriwrite_variablecheck($database_file, "maxlength", 32, 0);

		if (!$page_browsenumber || $page_browsenumber eq 0){

			$page_browsenumber = 1;

		}

		# Check if the page browse number is valid and if it isn't
		# then return an error.

		my $kiriwrite_browsenumber_length_check		= kiriwrite_variablecheck($page_browsenumber, "maxlength", 7, 1);
		my $kiriwrite_browsenumber_number_check		= kiriwrite_variablecheck($page_browsenumber, "numbers", 0, 1);

		if ($kiriwrite_browsenumber_length_check eq 1){

			# The browse number was too long so return
			# an error.

			kiriwrite_error("browsenumbertoolong");

		}

		if ($kiriwrite_browsenumber_number_check eq 1){

			# The browse number wasn't a number so
			# return an error.

			kiriwrite_error("browsenumberinvalid");

		}

		# Connect to the database server.

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database_file });

		# Check if any errors had occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		%database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

		$db_name = $database_info{"DatabaseName"};

		# Check if any errors had occured while getting the database
		# information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Get the count of pages in the database.

		my $page_total_count = $main::kiriwrite_dbmodule->getpagecount();

		# Check if any errors had occured while getting the count of
		# pages in the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Work out the total amount of page browse numbers.

		if ($page_total_count ne 0){

			if ($page_total_count eq $page_split){

				$page_list = int(($page_total_count / $page_split));

			} else {

				$page_list = int(($page_total_count / $page_split) + 1);

			}

		}

		my $start_from = ($page_browsenumber - 1) * $page_split;

		# Get the list of pages.

		@database_pages = $main::kiriwrite_dbmodule->getpagelist({ StartFrom => $start_from, Limit => $page_split });

		# Check if any errors had occured while getting the list of pages.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Check if there are any page names in the database array.

		if (@database_pages){

			# Write the start of the page.

			$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{pagelist}, $db_name), { Style => "pageheader" });
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
			$main::kiriwrite_presmodule->startbox();
			$main::kiriwrite_presmodule->addhiddendata("mode", "page");
			$main::kiriwrite_presmodule->addhiddendata("database", $database_file);
			$main::kiriwrite_presmodule->addhiddendata("type", "multiple");

			# Write out the page browsing list.

			$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{showlistpage});
			$main::kiriwrite_presmodule->addselectbox("browsenumber");

			# Write out the list of available pages to browse.
			
			while ($page_list_count ne $page_list){

				$page_list_count++;

				if ($page_list_count eq 1 && !$page_browsenumber){

					$main::kiriwrite_presmodule->addoption($page_list_count, { Value => $page_list_count, Selected => 1 });

				} else {

					if ($page_browsenumber eq $page_list_count){

						$main::kiriwrite_presmodule->addoption($page_list_count, { Value => $page_list_count, Selected => 1 });

					} else {

						$main::kiriwrite_presmodule->addoption($page_list_count, { Value => $page_list_count });

					}

				}

			}

			$main::kiriwrite_presmodule->endselectbox();
			$main::kiriwrite_presmodule->addbutton("action", { Value => "view", Description => $main::kiriwrite_lang{pages}{show} });


			if ($page_list ne $page_browsenumber){

				$main::kiriwrite_presmodule->addtext(" | ");
				$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database_file . "&browsenumber=" . ($page_browsenumber + 1), { Text => $main::kiriwrite_lang{pages}{nextpage} });

			}

			# Check if the page browse number is not blank and
			# not set as 0 and hide the Previous page link if
			# it is.

			if ($page_browsenumber > 1){

				$main::kiriwrite_presmodule->addtext(" | ");
				$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database_file . "&browsenumber=" . ($page_browsenumber - 1), { Text => $main::kiriwrite_lang{pages}{previouspage} });

			}

			$main::kiriwrite_presmodule->addlinebreak();

			# Write the list of multiple selection options.

			$main::kiriwrite_presmodule->addreset($main::kiriwrite_lang{common}{selectnone});
			$main::kiriwrite_presmodule->addtext(" | ");
			$main::kiriwrite_presmodule->addbutton("action", { Value => "multidelete", Description => $main::kiriwrite_lang{pages}{deleteselectedbutton} });
			$main::kiriwrite_presmodule->addtext(" | ");
			$main::kiriwrite_presmodule->addbutton("action", { Value => "multimove", Description => $main::kiriwrite_lang{pages}{moveselectedbutton} });
			$main::kiriwrite_presmodule->addtext(" | ");
			$main::kiriwrite_presmodule->addbutton("action", { Value => "multicopy", Description => $main::kiriwrite_lang{pages}{copyselectedbutton} });
			$main::kiriwrite_presmodule->addtext(" | ");
			$main::kiriwrite_presmodule->addbutton("action", { Value => "multiedit", Description => $main::kiriwrite_lang{pages}{editselectedbutton} });

			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->endbox();

			# Write the table header.

			$main::kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });
			$main::kiriwrite_presmodule->startheader();
			$main::kiriwrite_presmodule->addheader("", { Style => "tablecellheader" });
			$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{pages}{pagefilename}, { Style => "tablecellheader" });
			$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{pages}{pagename}, { Style => "tablecellheader" });
			$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{pages}{pagedescription}, { Style => "tablecellheader" });
			$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{pages}{lastmodified}, { Style => "tablecellheader" });
			$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{options}, { Style => "tablecellheader" });
			$main::kiriwrite_presmodule->endheader();

			# Process each page filename and get the page information.

			foreach $page_filename (@database_pages){

				%page_info = $main::kiriwrite_dbmodule->getpageinfo({ PageFilename => $page_filename, Reduced => 1 });

				# Check if any errors have occured.

				if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

					# A database error has occured so return an error and
					# also the extended error information.

					kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

				} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

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

				$main::kiriwrite_presmodule->startrow();
				$main::kiriwrite_presmodule->addcell($tablestyle);
				$main::kiriwrite_presmodule->addhiddendata("id[" . $page_count . "]", $page_filename);
				$main::kiriwrite_presmodule->addcheckbox("name[" . $page_count . "]");
				$main::kiriwrite_presmodule->endcell();
				$main::kiriwrite_presmodule->addcell($tablestyle);
				$main::kiriwrite_presmodule->addtext($page_filename);
				$main::kiriwrite_presmodule->endcell();
				$main::kiriwrite_presmodule->addcell($tablestyle);

				if (!$page_name){

					$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{blank}{noname});

				} else {

					$main::kiriwrite_presmodule->addtext($page_name);

				}

				$main::kiriwrite_presmodule->endcell();
				$main::kiriwrite_presmodule->addcell($tablestyle);

				if (!$page_description){

					$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{blank}{nodescription});

				} else {

					$main::kiriwrite_presmodule->addtext($page_description);

				}

				$main::kiriwrite_presmodule->endcell();
				$main::kiriwrite_presmodule->addcell($tablestyle);

				if (!$page_modified){

					$main::kiriwrite_presmodule->additalictext("No Date");

				} else {

					$main::kiriwrite_presmodule->addtext($page_modified);

				}

				$main::kiriwrite_presmodule->endcell();
				$main::kiriwrite_presmodule->addcell($tablestyle);
				$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"}  . "?mode=page&action=edit&database=" . $database_file . "&page=" . $page_filename, { Text => $main::kiriwrite_lang{options}{edit} });
				$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"}  . "?mode=page&action=delete&database=" . $database_file . "&page=" . $page_filename, { Text => $main::kiriwrite_lang{options}{delete} });
				$main::kiriwrite_presmodule->endcell();
				$main::kiriwrite_presmodule->endrow();

				# Increment the counter.

			}

		}

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		$main::kiriwrite_presmodule->endtable();
		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addhiddendata("count", $page_count);
		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->endform();

		if (!@database_pages && $page_browsenumber > 1){

			# There were no values given for the page browse
			# number given so write a message saying that
			# there were no pages for the page browse number
			# given.

			$main::kiriwrite_presmodule->clear();
			$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{pagelist}, $db_name), { Style => "pageheader" });
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->startbox("errorbox");
			$main::kiriwrite_presmodule->enterdata($main::kiriwrite_lang{pages}{nopagesinpagebrowse});
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database_file, { Text => $main::kiriwrite_lang{pages}{returntofirstpagebrowse} });
			$main::kiriwrite_presmodule->endbox();	

		} elsif (!@database_pages || !$page_count){

			# There were no values in the database pages array and 
			# the page count had not been incremented so write a
			# message saying that there were no pages in the
			# database.

			$main::kiriwrite_presmodule->clear();
			$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{pagelist}, $db_name), { Style => "pageheader" });
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->startbox("errorbox");
			$main::kiriwrite_presmodule->enterdata($main::kiriwrite_lang{pages}{nopagesindatabase});
			$main::kiriwrite_presmodule->endbox();

		}

		return $main::kiriwrite_presmodule->grab();

	}

}

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

		# Connect to the database server.

		$main::kiriwrite_dbmodule->connect();

		# Check if the database has write permissions.

		my $database_permissions = $main::kiriwrite_dbmodule->dbpermissions($pagedatabase, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Select the database to add the page to.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $pagedatabase });

		# Check if any errors had occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		my %database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any error occured while getting the database information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		};

		# Add the page to the selected database.

		$main::kiriwrite_dbmodule->addpage({ PageFilename => $pagefilename, PageName => $pagetitle, PageDescription => $pagedescription, PageSection => $pagesection, PageTemplate => $pagetemplate, PageContent => $pagefiledata, PageSettings => $pagesettings });

		# Check if any errors occured while adding the page.

		if ($main::kiriwrite_dbmodule->geterror eq "PageExists"){

			# A page with the filename given already exists so
			# return an error.

			kiriwrite_error("pagefilenameexists");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error
			# with extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		my $database_name = $database_info{"DatabaseName"};

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{addpage}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{pageaddedmessage}, $pagetitle, $database_name));
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $pagedatabase, { Text => kiriwrite_language($main::kiriwrite_lang{pages}{returnpagelist}, $database_name) });

		return $main::kiriwrite_presmodule->grab();

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

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $pagedatabase });

		# Check if any errors had occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Check if the database has write permissions.

		my $database_permissions = $main::kiriwrite_dbmodule->dbpermissions($pagedatabase, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		%database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any error occured while getting the database information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		};

		# Connect to the template database.

		$main::kiriwrite_dbmodule->connecttemplate();

		# Check if any errors occured while connecting to the template database.

		if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseDoesNotExist"){

			# The template database does not exist so set the template
			# warning message.

			$template_warningmessage = $main::kiriwrite_lang{pages}{notemplatedatabase};
 			$template_warning = 1;

		} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so write
			# the template warning message.

 			$template_warningmessage = $main::kiriwrite_lang{pages}{templatepermissionserror};
 			$template_warning = 1;

		}

		if ($template_warning eq 0){

			# Get the list of templates available.

			@templates_list = $main::kiriwrite_dbmodule->gettemplatelist();

			# Check if any errors had occured.

			if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

				# A database error occured while getting the list
				# of templates so return a warning message with the 
				# extended error information.

				$template_warningmessage = kiriwrite_language($main::kiriwrite_lang{pages}{templatedatabaseerror}, $main::kiriwrite_dbmodule->geterror(1));
				$template_warning = 1;

			}

			if ($template_warning eq 0){

				# Check to see if there are any templates in the templates
				# list array.

				my $template_filename = "";
				my $template_name = "";

				foreach $template (@templates_list){

					# Get information about the template.

					%template_info = $main::kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $template });

					# Check if any error occured while getting the template information.

					if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

						# A database error has occured, so return an error.

						kiriwrite_error("templatedatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

					} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

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

					$template_warningmessage = $main::kiriwrite_lang->{pages}->{notemplatesavailable};

				}

			}

		}

 		my $database_name 	= $database_info{"DatabaseName"};

		# Disconnect from the template database.

		$main::kiriwrite_dbmodule->disconnecttemplate();

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		# write out the form for adding a page.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{addpage}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");#
		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addhiddendata("mode", "page");
		$main::kiriwrite_presmodule->addhiddendata("action", "add");
 		$main::kiriwrite_presmodule->addhiddendata("database", $pagedatabase);
		$main::kiriwrite_presmodule->addhiddendata("confirm", "1");
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

		$main::kiriwrite_presmodule->startheader();
		$main::kiriwrite_presmodule->addcell("tablecellheader");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{common}{setting});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecellheader");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{common}{value});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endheader();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{database});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addtext($database_name);
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagename});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("pagename", { Size => 64, MaxLength => 512 });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagedescription});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("pagedescription", { Size => 64, MaxLength => 512 });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagesection});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("pagesection", { Size => 64, MaxLength => 256 });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagetemplate});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");

		# Check if the template warning value has been set
		# and write the error message in place of the templates
		# list if it is.

		if ($template_warning eq 1){

			$main::kiriwrite_presmodule->addhiddendata("pagetemplate", "!none");
			$main::kiriwrite_presmodule->addtext($template_warningmessage);

		} else {

			my $template_file;
			my $page_filename;
			my $page_name;

			$main::kiriwrite_presmodule->addselectbox("pagetemplate");

			foreach $template_file (keys %template_list){

				$page_filename 	= $template_list{$template_file}{Filename};
				$page_name	= $template_list{$template_file}{Name};
				$main::kiriwrite_presmodule->addoption($page_name . " (" . $page_filename . ")", { Value => $page_filename });
				$template_count++;

				$template_count = 0;
			}

			$main::kiriwrite_presmodule->addoption($main::kiriwrite_lang{pages}{usenotemplate}, { Value => "!none", Selected => 1 });
			$main::kiriwrite_presmodule->endselectbox();

		}

		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagefilename});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("pagefilename", { Size => 64, MaxLength => 256 });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagecontent});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addtextbox("pagecontent", { Columns => $main::kiriwrite_config{"display_textareacols"}, Rows => $main::kiriwrite_config{"display_textarearows"} });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startbox("datalist");
		$main::kiriwrite_presmodule->addboldtext($main::kiriwrite_lang{common}{tags});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{common}{pagetitle});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{common}{pagename});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{common}{pagedescription});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{common}{pagesection});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{common}{pageautosection});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{common}{pageautotitle});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagesettings});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addradiobox("pagesettings", { Description => $main::kiriwrite_lang{pages}{usepageandsection}, Value => "1", Selected => 1, LineBreak => 1});
		$main::kiriwrite_presmodule->addradiobox("pagesettings", { Description => $main::kiriwrite_lang{pages}{usepagename}, Value => "2", Selected => 0, LineBreak => 1});
		$main::kiriwrite_presmodule->addradiobox("pagesettings", { Description => $main::kiriwrite_lang{pages}{usesectionname}, Value => "3", Selected => 0, LineBreak => 1});
		$main::kiriwrite_presmodule->addradiobox("pagesettings", { Description => $main::kiriwrite_lang{pages}{nopagesection}, Value => "0", Selected => 0, LineBreak => 1});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->endtable();

		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{pages}{addpagebutton});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addreset($main::kiriwrite_lang{common}{clearvalues});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $pagedatabase, { Text => kiriwrite_language($main::kiriwrite_lang{pages}{returnpagelist}, $database_name) });
		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->endform();


		return $main::kiriwrite_presmodule->grab();

	} else {

		# The confirm value is something else than '1' or '0' so
		# return an error.

		kiriwrite_error("invalidvalue");

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

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors had occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Check if the database has write permissions.

		my $database_permissions = $main::kiriwrite_dbmodule->dbpermissions($database, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get the database information.

		my %database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		};

		my $database_name = $database_info{"DatabaseName"};

		# Edit the selected page.

		$main::kiriwrite_dbmodule->editpage({ PageFilename => $pagefilename, PageNewFilename => $pagenewfilename, PageNewName => $pagenewtitle, PageNewDescription => $pagenewdescription, PageNewSection => $pagenewsection, PageNewTemplate => $pagenewtemplate, PageNewContent => $pagenewcontent, PageNewSettings => $pagenewsettings });

		# Check if any errors occured while editing the page.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

			# The pages does not exist in the database.

			kiriwrite_error("pagefilenamedoesnotexist");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "PageExists"){

			# A page already exists with the new filename.

			kiriwrite_error("pagefilenameexists");

		}

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{editedpage}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{editedpagemessage}, $pagenewtitle));
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($main::kiriwrite_lang{pages}{returnpagelist}, $database_name) });

		return $main::kiriwrite_presmodule->grab();

	} elsif ($confirm eq 0) {

		# Connect to the database server.

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors had occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get the information about the database.

		my %database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		};

		my $database_name = $database_info{"DatabaseName"};

		# Get the page info.

		my %page_info = $main::kiriwrite_dbmodule->getpageinfo({ PageFilename => $pagefilename });

		# Check if any errors occured while getting the page information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

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

		$main::kiriwrite_dbmodule->connecttemplate();

		# Check if any errors occured while connecting to the template database.

		if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseDoesNotExist"){

			# The template database does not exist so set the template
			# warning message.

			$template_warning = $main::kiriwrite_lang{pages}{notemplatedatabasekeep};

		} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so write
			# the template warning message.

 			$template_warning = $main::kiriwrite_lang{pages}{templatepermissionserrorkeep};

		}

		if (!$template_warning){

			# Get the list of available templates.

			@template_filenames = $main::kiriwrite_dbmodule->gettemplatelist();

			# Check if any errors had occured.

			if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

				# A database error occured while getting the list
				# of templates so return an error with the 
				# extended error information.

				$template_warning = kiriwrite_language($main::kiriwrite_lang{pages}{templatedatabaseerrorkeep} , $main::kiriwrite_dbmodule->geterror(1));

			}

			if (!$template_warning){

				foreach $template_filename (@template_filenames){

					# Get the information about each template.

					%template_info = $main::kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $template_filename });

					# Check if any errors occured while getting the template information.

					if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

						# A template database error has occured so return a warning message
						# with the extended error information.

						$template_warning = kiriwrite_language($main::kiriwrite_lang{pages}{templatedatabaseerrorkeep} , $main::kiriwrite_dbmodule->geterror(1));
						last;

					} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

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

		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{editpage}, $data_name), { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();

		$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addhiddendata("mode", "page");
		$main::kiriwrite_presmodule->addhiddendata("action", "edit");
		$main::kiriwrite_presmodule->addhiddendata("database", $database);
		$main::kiriwrite_presmodule->addhiddendata("page", $pagefilename);
		$main::kiriwrite_presmodule->addhiddendata("confirm", 1);
		$main::kiriwrite_presmodule->endbox();

		$main::kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

		$main::kiriwrite_presmodule->startheader();
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{setting}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{value}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->endheader();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{database});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addtext($database_name);
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagename});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("pagename", { Size => 64, MaxLength => 512, Value => $data_name });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagedescription});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("pagedescription", { Size => 64, MaxLength => 512, Value => $data_description });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagesection});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("pagesection", { Size => 64, MaxLength => 256, Value => $data_section });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagetemplate});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");

		# Check if any template warnings have occured.

		if ($template_warning){

			$main::kiriwrite_presmodule->addtext($template_warning);
			$main::kiriwrite_presmodule->addlinebreak();

		}

		$main::kiriwrite_presmodule->addselectbox("pagetemplate");

		# Process the list of templates, select one if the
		# template filename for the page matches, else give
		# an option for the user to keep the current template
		# filename.

		$template_count = 0;

		foreach $template_file (keys %template_list){

			if ($template_list{$template_count}{Selected}){

				$main::kiriwrite_presmodule->addoption($template_list{$template_count}{Name} . " (" . $template_list{$template_count}{Filename} . ")", { Value => $template_list{$template_count}{Filename}, Selected => 1 });

			} else {

				$main::kiriwrite_presmodule->addoption($template_list{$template_count}{Name} . " (" . $template_list{$template_count}{Filename} . ")", { Value => $template_list{$template_count}{Filename} });

			}

			$template_count++;

		}

		if ($data_template eq "!none"){

			$main::kiriwrite_presmodule->addoption($main::kiriwrite_lang{pages}{usenotemplate}, { Value => "!none", Selected => 1 });
			$template_found = 1;

		} else {

			$main::kiriwrite_presmodule->addoption($main::kiriwrite_lang{pages}{usenotemplate}, { Value => "!none" });

		}

		if ($template_found eq 0 && $data_template ne "!none"){

			# The template with the filename given was not found.

			$main::kiriwrite_presmodule->addoption(kiriwrite_language($main::kiriwrite_lang{pages}{keeptemplatefilename}, $data_template), { Value => $data_template, Selected => 1, Style => "warningoption" });

		}

		# Disconnect from the template database.

		$main::kiriwrite_dbmodule->disconnecttemplate();

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		$main::kiriwrite_presmodule->endselectbox();

		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagefilename});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("pagefilename", { Size => 64, MaxLength => 256, Value => $data_filename });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagecontent});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addtextbox("pagecontent", { Columns => $main::kiriwrite_config{"display_textareacols"}, Rows => $main::kiriwrite_config{"display_textarearows"},  Value => $data_content });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startbox("datalist");
		$main::kiriwrite_presmodule->addboldtext($main::kiriwrite_lang{common}{tags});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{common}{pagetitle});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{common}{pagename});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{common}{pagedescription});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{common}{pagesection});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{common}{pageautosection});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{common}{pageautotitle});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagesettings});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");

		# Check if the page settings value is set to a 
		# certain number and select that option based
		# on the number else set the value to 0.

		if ($data_settings eq 1){
			$main::kiriwrite_presmodule->addradiobox("pagesettings", { Description => $main::kiriwrite_lang{pages}{usepageandsection}, Value => "1", Selected => 1, LineBreak => 1});
		} else {
			$main::kiriwrite_presmodule->addradiobox("pagesettings", { Description => $main::kiriwrite_lang{pages}{usepageandsection}, Value => "1", LineBreak => 1});
		}

		if ($data_settings eq 2){
			$main::kiriwrite_presmodule->addradiobox("pagesettings", { Description => $main::kiriwrite_lang{pages}{usepagename}, Value => "2", Selected => 1, LineBreak => 1});
		} else {
			$main::kiriwrite_presmodule->addradiobox("pagesettings", { Description => $main::kiriwrite_lang{pages}{usepagename}, Value => "2", LineBreak => 1});
		}

		if ($data_settings eq 3){
			$main::kiriwrite_presmodule->addradiobox("pagesettings", { Description => $main::kiriwrite_lang{pages}{usesectionname}, Value => "3", Selected => 1, LineBreak => 1});
		} else {
			$main::kiriwrite_presmodule->addradiobox("pagesettings", { Description => $main::kiriwrite_lang{pages}{usesectionname}, Value => "3", LineBreak => 1});
		}

		if ($data_settings eq 0 || ($data_settings ne 1 && $data_settings ne 2 && $data_settings ne 3)){
			$main::kiriwrite_presmodule->addradiobox("pagesettings", { Description => $main::kiriwrite_lang{pages}{nopagesection}, Value => "0", Selected => 1, LineBreak => 1});
		} else {
			$main::kiriwrite_presmodule->addradiobox("pagesettings", { Description => $main::kiriwrite_lang{pages}{nopagesection}, Value => "0", LineBreak => 1});
		}

		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();
		$main::kiriwrite_presmodule->endtable();

		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{pages}{editpagebutton});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addreset($main::kiriwrite_lang{common}{restorecurrent});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($main::kiriwrite_lang{pages}{returnpagelist}, $database_name) } );
		$main::kiriwrite_presmodule->endbox();

		$main::kiriwrite_presmodule->endform();

		return $main::kiriwrite_presmodule->grab();

	} else {

		# The confirm value is a value other than '0' and '1' so
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

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Select the database to delete the page from.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors had occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Check if the database has write permissions.

		my $database_permissions = $main::kiriwrite_dbmodule->dbpermissions($database, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get the information about the database.

		my %database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any error occured while getting the database information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Get the information about the page that is going to be deleted.

		my %page_info = $main::kiriwrite_dbmodule->getpageinfo({ PageFilename => $page });

		# Check if any errors occured while getting the page information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

			# The page does not exist, so return an error.

			kiriwrite_error("pagefilenamedoesnotexist");

		}

		# Delete the page from the database.

		$main::kiriwrite_dbmodule->deletepage({ PageFilename => $page });

		# Check if any errors occured while deleting the page from the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

			# The page does not exist, so return an error.

			kiriwrite_error("pagefilenamedoesnotexist");

		}

		# Get the database name and page name.

		my $database_name 	= $database_info{"DatabaseName"};
		my $page_name		= $page_info{"PageName"};

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		# Write out a message saying that the selected page from
		# the database has been deleted.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagedeleted}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{pagedeletedmessage}, $page_name, $database_name));
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($main::kiriwrite_lang{pages}{returnpagelist}, $database_name)});

		return $main::kiriwrite_presmodule->grab();

	} elsif ($confirm eq 0){

		# Connect to the database server.

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors had occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		my %database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors occured while getting the database information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Get information about the page that is going to be deleted.

		my %page_info = $main::kiriwrite_dbmodule->getpageinfo({ PageFilename => $page });

		# Check if any errors occured while getting the page information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

			# The page does not exist, so return an error.

			kiriwrite_error("pagefilenamedoesnotexist");

		}

		my $database_name 	= $database_info{"DatabaseName"};
		my $page_name		= $page_info{"PageName"};

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		# Write a message asking the user to confirm the deletion of the
		# page.

		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{deletepage}, $page_name), { Style => "pageheader" });
		$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addhiddendata("mode", "page");
		$main::kiriwrite_presmodule->addhiddendata("action", "delete");
		$main::kiriwrite_presmodule->addhiddendata("database", $database);
		$main::kiriwrite_presmodule->addhiddendata("page", $page);
		$main::kiriwrite_presmodule->addhiddendata("confirm", "1");
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{deletepagemessage}, $page_name, $database_name));
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{pages}{deletepagebutton});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($main::kiriwrite_lang{pages}{deletepagesreturnlink}, $database_name)});
		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->endform();

		return $main::kiriwrite_presmodule->grab();

	} else {

		# Another page deletion type was specified, so return an error.

		kiriwrite_error("invalidoption");

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

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Check if the database has read and write permissions.

		my $database_permissions = $main::kiriwrite_dbmodule->dbpermissions($database, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		my %database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

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

			%page_info = $main::kiriwrite_dbmodule->getpageinfo({ PageFilename => $filelist_filename });

			# Check if any errors occured.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

			} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page does not exist, so process the next page.

				next;

			}

			# Add the page to the list of deleted pages.

			$deleted_list{$page_count}{Filename}	= $page_info{"PageFilename"};
			$deleted_list{$page_count}{Name}	= $page_info{"PageName"};

			# Delete the page.

			$main::kiriwrite_dbmodule->deletepage({ PageFilename => $filelist_filename });

			# Check if any errors occured while deleting the page from the database.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

			} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page does not exist, so process the next page.

				next;

			}

			$page_found = 0;
			$page_count++;

		}

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{selectedpagesdeleted}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{selectedpagesdeletedmessage}, $database_name));
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startbox("datalist");

		foreach $page (keys %deleted_list){

			if (!$deleted_list{$page}{Name}){
				$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{blank}{noname});
				$main::kiriwrite_presmodule->addtext(" (" . $deleted_list{$page}{Filename} . ")");

			} else {
				$main::kiriwrite_presmodule->addtext($deleted_list{$page}{Name} . " (" . $deleted_list{$page}{Filename} . ")");
			}

			$main::kiriwrite_presmodule->addlinebreak();
		}

		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($main::kiriwrite_lang{pages}{returnpagelist}, $database_name)});

		return $main::kiriwrite_presmodule->grab();

	} elsif ($confirm eq 0){

		# The action to delete multiple pages from the database has
		# not been confirmed, so write a form asking the user to confirm
		# the deletion of those pages.

		# Connect to the database server.

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Check if the database has read and write permissions.

		my $database_permissions = $main::kiriwrite_dbmodule->dbpermissions($database, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		my %database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

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

			%page_info = $main::kiriwrite_dbmodule->getpageinfo({ PageFilename => $filelist_filename });

			# Check if any errors occured.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

			} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

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

		$main::kiriwrite_dbmodule->disconnect();

		# Check if any files were selected and return
		# an error if there wasn't.

		if ($pageseek eq 0){

			# No pages were selected so return an error.

			kiriwrite_error("nopagesselected");

		}

		# Write the form for displaying pages.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{deletemultiplepages}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addhiddendata("mode", "page");
		$main::kiriwrite_presmodule->addhiddendata("action", "multidelete");
		$main::kiriwrite_presmodule->addhiddendata("database", $database);
		$main::kiriwrite_presmodule->addhiddendata("confirm", "1");
		$main::kiriwrite_presmodule->addhiddendata("count", $pageseek);

		$pageseek = 1;

		foreach $page (keys %delete_list){

			$main::kiriwrite_presmodule->addhiddendata("name[" . $pageseek . "]", "on");
			$main::kiriwrite_presmodule->addhiddendata("id[" . $pageseek . "]", $delete_list{$page}{Filename});

			$pageseek++;

		}

		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{deletemultiplemessage}, $database_name));
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startbox("datalist");

		foreach $page (keys %delete_list){

			if (!$delete_list{$page}{Name}){
				$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{blank}{noname});
				$main::kiriwrite_presmodule->addtext(" (" . $delete_list{$page}{Filename} . ")");
			} else {
				$main::kiriwrite_presmodule->addtext($delete_list{$page}{Name} . " (" . $delete_list{$page}{Filename} . ")");
			}
			$main::kiriwrite_presmodule->addlinebreak();

		}

		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{pages}{deletepagesbutton});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($main::kiriwrite_lang{pages}{deletepagesreturnlink}, $database_name)});
		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->endform();

		return $main::kiriwrite_presmodule->grab();

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

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Select the database the pages are going to be moved from.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors had occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("oldmovedatabasedoesnotexist");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("oldmovedatabasefileinvalidpermissions");

		}

		# Check if the database has read and write permissions.

		my $database_permissions = $main::kiriwrite_dbmodule->dbpermissions($database, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("oldmovedatabasefileinvalidpermissions");

		}

		# Select the database the pages are going to be moved to.

		$main::kiriwrite_dbmodule->selectseconddb({ DatabaseName => $newdatabase });

		# Check if any errors had occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("newmovedatabasedoesnotexist");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("newmovedatabasefileinvalidpermissions");

		}

		# Check if the database has read and write permissions.

		$database_permissions = $main::kiriwrite_dbmodule->dbpermissions($newdatabase, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("newmovedatabasefileinvalidpermissions");

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

		my %olddatabase_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("oldmovedatabasedatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		};

		$olddatabase_name = $olddatabase_info{"DatabaseName"};

		# Get information about the database that the selected pages are moving to.

		my %newdatabase_info = $main::kiriwrite_dbmodule->getseconddatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("newmovedatabasedatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		};

		$newdatabase_name = $newdatabase_info{"DatabaseName"};

		# Get each file in the old database, get the page values,
		# put them into the new database and delete the pages
		# from the old database.

		foreach $filename (@filelist){

			# Get the page information.

			%page_info = $main::kiriwrite_dbmodule->getpageinfo({ PageFilename => $filename });

			# Check if any errors occured.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so write a warning message and
				# also the extended error information.

				$warning_list{$warning_count}{Message} = kiriwrite_language($main::kiriwrite_lang{pages}{databasepageerror}, $filename, $main::kiriwrite_dbmodule->geterror(1));
				$warning_count++;
				next;

			} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page does not exist, so process the next page.

				$warning_list{$warning_count}{Message} = kiriwrite_language($main::kiriwrite_lang{pages}{pagedoesnotexist}, $filename);
				$warning_count++;
				next;

			}

			# Move the selected page.

			$main::kiriwrite_dbmodule->movepage({ PageFilename => $filename });

			# Check if any errors occured while moving the page.

			if ($main::kiriwrite_dbmodule->geterror eq "OldDatabaseError"){

				# A database error has occured while moving the pages from
				# the old database, so write a warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($main::kiriwrite_lang{pages}{databasemovefrompageerror}, $filename, $main::kiriwrite_dbmodule->geterror(1));
				$warning_count++;
				next;

			} elsif ($main::kiriwrite_dbmodule->geterror eq "NewDatabaseError"){

				# A database error has occured while moving the pages to
				# the new database, so write a warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($main::kiriwrite_lang{pages}{databasemovetopageerror}, $filename, $main::kiriwrite_dbmodule->geterror(1));
				$warning_count++;
				next;

			} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page with the filename given in the database that
				# the page is to be moved from doesn't exist so write
				# a warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($main::kiriwrite_lang{pages}{databasemovefrompagenotexist}, $filename);
				$warning_count++;
				next;

			} elsif ($main::kiriwrite_dbmodule->geterror eq "PageAlreadyExists"){

				# The page with the filename given in the database that
				# the page is to be moved to already exists so write a
				# warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($main::kiriwrite_lang{pages}{databasemovetopageexists}, $filename);
				$warning_count++;
				next;

			}

			$moved_list{$move_count}{Filename} 	= $page_info{"PageFilename"};
			$moved_list{$move_count}{Name} 		= $page_info{"PageName"};

			$move_count++;

		}

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		# Write out a message saying that the pages were moved (if any)
		# to the new database (and any warnings given).

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{movepages}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();

		if (%moved_list){

			$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{movedpagesmessage}, $olddatabase_name, $newdatabase_name));
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();

			$main::kiriwrite_presmodule->startbox("datalist");
			foreach $page (keys %moved_list){
				if (!$moved_list{$page}{Name}){
					$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{blank}{noname});
					$main::kiriwrite_presmodule->addtext(" (" . $moved_list{$page}{Filename} . ")");
				} else {
					$main::kiriwrite_presmodule->addtext($moved_list{$page}{Name} . " (" . $moved_list{$page}{Filename} . ")");
				}

				$main::kiriwrite_presmodule->addlinebreak();
			}
			$main::kiriwrite_presmodule->endbox();

		} else {

			$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{nopagesmoved}, $olddatabase_name, $newdatabase_name));
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();

		}

		if (%warning_list){

			$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{errormessages});
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->startbox("datalist");
			foreach $warning (keys %warning_list){
				$main::kiriwrite_presmodule->addtext($warning_list{$warning}{Message});
				$main::kiriwrite_presmodule->addlinebreak();
			}
			$main::kiriwrite_presmodule->endbox();

		}

		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($main::kiriwrite_lang{pages}{returnpagelist}, $olddatabase_name)}); 
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $newdatabase, { Text => kiriwrite_language($main::kiriwrite_lang{pages}{viewpagelist}, $newdatabase_name)});

		return $main::kiriwrite_presmodule->grab();

	} elsif ($confirm eq 0) {

		# The action to move several pages from one database
		# to another has not been confirmed so write a form.

		# Connect to the database server.

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Check if the database has read and write permissions.

		my $database_permissions = $main::kiriwrite_dbmodule->dbpermissions($database, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		my %database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

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

			%page_info = $main::kiriwrite_dbmodule->getpageinfo({ PageFilename => $filelist_filename });

			# Check if any errors occured.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

			} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

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

		my @database_list	= $main::kiriwrite_dbmodule->getdblist();

		# Check if any errors occured while trying to get the list of databases.

 		if ($main::kiriwrite_dbmodule->geterror eq "DataDirMissing"){

			# The database directory is missing so return an error.

			kiriwrite_error("datadirectorymissing");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "DataDirInvalidPermissions"){

			# The database directory has invalid permissions set so return
			# an error.

			kiriwrite_error("datadirectoryinvalidpermissions");

		}

		# Get the information about each database (the short name and friendly name).

		foreach $data_file (@database_list){

			$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $data_file });

			# Check if any errors occured while selecting the database.

			if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

				# The database does not exist, so process the next
				# database.

				next;

			} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

				# The database has invalid permissions set, so process
				# the next database.

				next;

			}

			# Get the database information.

			%database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

			# Check if any errors had occured while getting the database
			# information.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

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

		$main::kiriwrite_dbmodule->disconnect();

		# Write out the form.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{movepages}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addhiddendata("mode", "page");
		$main::kiriwrite_presmodule->addhiddendata("action", "multimove");
		$main::kiriwrite_presmodule->addhiddendata("database", $database);
		$main::kiriwrite_presmodule->addhiddendata("count", $pageseek);
		$main::kiriwrite_presmodule->addhiddendata("confirm", "1");

		# Write the page form data.

		$pageseek = 1;

		foreach $page (keys %move_list){
			$main::kiriwrite_presmodule->addhiddendata("name[" . $pageseek . "]", "on");
			$main::kiriwrite_presmodule->addhiddendata("id[" . $pageseek . "]", $move_list{$page}{Filename});
			$pageseek++;
		}

		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{movepagesmessage}, $database_name));
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startbox("datalist");

		foreach $page (keys %move_list){
			if (!$move_list{$page}{Name}){
				$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{blank}{noname});
				$main::kiriwrite_presmodule->addtext(" (" . $move_list{$page}{Filename} . ")");
			} else {
				$main::kiriwrite_presmodule->addtext($move_list{$page}{Name} . " (" . $move_list{$page}{Filename} . ")");
			}
			$main::kiriwrite_presmodule->addlinebreak();
		}

		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{movepagesto});

		$main::kiriwrite_presmodule->addselectbox("newdatabase");

		foreach $db_name (keys %db_list){
			$main::kiriwrite_presmodule->addoption($db_list{$db_name}{Name} . " (" . $db_list{$db_name}{Filename} . ")", { Value => $db_list{$db_name}{Filename}});
		}

		$main::kiriwrite_presmodule->endselectbox();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{pages}{movepagesbutton});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($main::kiriwrite_lang{pages}{returnpagelist}, $database_name)});
		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->endform();

		return $main::kiriwrite_presmodule->grab();

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

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Select the database the pages are going to be copied from.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors had occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("oldcopydatabasedoesnotexist");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("oldcopydatabasefileinvalidpermissions");

		}

		# Select the database the pages are going to be copied to.

		$main::kiriwrite_dbmodule->selectseconddb({ DatabaseName => $newdatabase });

		# Check if any errors had occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("newcopydatabasedoesnotexist");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("newcopydatabasefileinvalidpermissions");

		}

		# Check if the database has read and write permissions.

		my $database_permissions = $main::kiriwrite_dbmodule->dbpermissions($newdatabase, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("newcopydatabasefileinvalidpermissions");

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

		my %olddatabase_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("oldcopydatabasedatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		};

		$olddatabase_name = $olddatabase_info{"DatabaseName"};

		# Get information about the database that the selected pages are moving to.

		my %newdatabase_info = $main::kiriwrite_dbmodule->getseconddatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("newcopydatabasedatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

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

			%page_info = $main::kiriwrite_dbmodule->getpageinfo({ PageFilename => $filename });

			# Check if any errors occured.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				$warning_list{$warning_count}{Message} = kiriwrite_language($main::kiriwrite_lang{pages}{databasepageerror}, $filename, $main::kiriwrite_dbmodule->geterror(1));
				$warning_count++;
				next;

			} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page does not exist, so process the next page.

				$warning_list{$warning_count}{Message} = kiriwrite_language($main::kiriwrite_lang{pages}{databasecopyfrompageerror}, $filename);
				$warning_count++;
				next;

			}

			$main::kiriwrite_dbmodule->copypage({ PageFilename => $filename });

			# Check if any errors occured while copying the page.

			if ($main::kiriwrite_dbmodule->geterror eq "OldDatabaseError"){

				# A database error has occured while copying the pages from
				# the old database, so write a warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($main::kiriwrite_lang{pages}{databasecopyfromdatabaseerror}, $filename,  $main::kiriwrite_dbmodule->geterror(1));
				$warning_count++;
				next;

			} elsif ($main::kiriwrite_dbmodule->geterror eq "NewDatabaseError"){

				# A database error has occured while copying the pages to
				# the new database, so write a warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($main::kiriwrite_lang{pages}{databasecopytodatabaseerror}, $filename, $main::kiriwrite_dbmodule->geterror(1));
				$warning_count++;
				next;

			} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page with the filename given in the database that
				# the page is to be copied from doesn't exist so write
				# a warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($main::kiriwrite_lang{pages}{databasecopyfrompagenotexist}, $filename);
				$warning_count++;
				next;

			} elsif ($main::kiriwrite_dbmodule->geterror eq "PageAlreadyExists"){

				# The page with the filename given in the database that
				# the page is to be copied to already exists so write a
				# warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($main::kiriwrite_lang{pages}{databasecopytopageexists}, $filename);
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

		$main::kiriwrite_dbmodule->disconnect();

		# Write out a message saying that the pages were moved (if any)
		# to the new database (and any warnings given).

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{copypages}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();

		if (%copied_list){

			$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{copypagesresultmessage}, $olddatabase_name, $newdatabase_name));
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->startbox("datalist");
			foreach $page (keys %copied_list){
				if (!$copied_list{$page}{Name}){
					$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{blank}{noname});
					$main::kiriwrite_presmodule->addtext(" (" . $copied_list{$page}{Filename} . ")");
				} else {
					$main::kiriwrite_presmodule->addtext($copied_list{$page}{Name} . " (" . $copied_list{$page}{Filename} . ")");
				}
				$main::kiriwrite_presmodule->addlinebreak();
			}
			$main::kiriwrite_presmodule->endbox();

		} else {

			$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{nopagescopied}, $olddatabase_name, $newdatabase_name));

		}

		if (%warning_list){

			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{copypageswarnings});
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->startbox("datalist");
			foreach $warning (keys %warning_list){
				$main::kiriwrite_presmodule->addtext($warning_list{$warning}{Message});
				$main::kiriwrite_presmodule->addlinebreak();
			}
			$main::kiriwrite_presmodule->endbox();

		}

		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($main::kiriwrite_lang{pages}{returnpagelist}, $olddatabase_name)});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $newdatabase, { Text => kiriwrite_language($main::kiriwrite_lang{pages}{viewpagelist}, $newdatabase_name)});

		return $main::kiriwrite_presmodule->grab();

	} elsif ($confirm eq 0) {

		# The action to copy several pages from one database
		# to another has not been confirmed so write a form.

		# Connect to the database server.

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Select the database to copy the pages from.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		my %database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

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

			%page_info = $main::kiriwrite_dbmodule->getpageinfo({ PageFilename => $filename });

			# Check if any errors occured.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

			} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

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

		my @database_list	= $main::kiriwrite_dbmodule->getdblist();

		# Check if any errors occured while trying to get the list of databases.

 		if ($main::kiriwrite_dbmodule->geterror eq "DataDirMissing"){

			# The database directory is missing so return an error.

			kiriwrite_error("datadirectorymissing");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "DataDirInvalidPermissions"){

			# The database directory has invalid permissions set so return
			# an error.

			kiriwrite_error("datadirectoryinvalidpermissions");

		}

		# Process each database to get the database name.

		foreach $data_file (@database_list){

			$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $data_file });

			# Check if any errors occured while selecting the database.

			if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

				# The database does not exist, so process the next
				# database.

				next;

			} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

				# The database has invalid permissions set, so process
				# the next database.

				next;

			}

			# Get the database information.

			%database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

			# Check if any errors had occured while getting the database
			# information.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

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

		$main::kiriwrite_dbmodule->disconnect();

		# Write out the form.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{copypages}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addhiddendata("mode", "page");
		$main::kiriwrite_presmodule->addhiddendata("action", "multicopy");
		$main::kiriwrite_presmodule->addhiddendata("database", $database);
		$main::kiriwrite_presmodule->addhiddendata("count", $pageseek);
		$main::kiriwrite_presmodule->addhiddendata("confirm", 1);

		$pageseek = 1;

		foreach $page (keys %copy_list){
			$main::kiriwrite_presmodule->addhiddendata("name[" . $pageseek . "]", "on");
			$main::kiriwrite_presmodule->addhiddendata("id[" . $pageseek . "]", $copy_list{$page}{Filename});
			$pageseek++;
		}

		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{copypagesmessage}, $database_name));

		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();

		$main::kiriwrite_presmodule->startbox("datalist");

		foreach $page (keys %copy_list){
			if (!$copy_list{$page}{Name}){
				$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{blank}{noname});
				$main::kiriwrite_presmodule->addtext(" (" . $copy_list{$page}{Filename} . ")");
			} else {
				$main::kiriwrite_presmodule->addtext($copy_list{$page}{Name} . " (" . $copy_list{$page}{Filename} . ")");
			}
			$main::kiriwrite_presmodule->addlinebreak();
		}

		$main::kiriwrite_presmodule->endbox();

		$main::kiriwrite_presmodule->addlinebreak();

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{copypagesto});
		$main::kiriwrite_presmodule->addselectbox("newdatabase");

		foreach $dbname (keys %db_list){
			$main::kiriwrite_presmodule->addoption($db_list{$dbname}{Name} . " (" . $db_list{$dbname}{Filename} . ")", { Value => $db_list{$dbname}{Filename}});
		}

		$main::kiriwrite_presmodule->endselectbox();

		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{pages}{copypagesbutton});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($main::kiriwrite_lang{pages}{returnpagelist}, $database_name) });

		$main::kiriwrite_presmodule->endbox();		
		$main::kiriwrite_presmodule->endform();

		return $main::kiriwrite_presmodule->grab();

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

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Check if the database has read and write permissions.

		my $database_permissions = $main::kiriwrite_dbmodule->dbpermissions($database, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		%database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		};

		my $database_name = $database_info{"DatabaseName"};

		# Edit the selected pages.

		foreach $filename (@filelist){

			# Get the page information.

			%page_info = $main::kiriwrite_dbmodule->getpageinfo({ PageFilename => $filename });

			# Check if any errors occured.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so write a warning message.

				$warning_list{$warning_count}{Message} = kiriwrite_language($main::kiriwrite_lang{pages}{databasepageerror}, $filename, $main::kiriwrite_dbmodule->geterror(1));

			} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The page does not exist, so write a warning message.

 				$warning_list{$warning_count}{Message} = kiriwrite_language($main::kiriwrite_lang{pages}{databasepagedoesnotexist}, $filename);
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

			$main::kiriwrite_dbmodule->editpage({ PageFilename => $page_info{"PageFilename"}, PageNewFilename => $page_info{"PageFilename"}, PageNewName => $page_info{"PageName"}, PageNewDescription => $page_info{"PageDescription"}, PageNewSection => $page_info{"PageSection"}, PageNewTemplate => $page_info{"PageTemplate"}, PageNewContent => $page_info{"PageContent"}, PageNewSettings => $page_info{"PageSettings"} });

			# Check if any errors occured while editing the page.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so write a warning message
				# with the extended error information.

				$warning_list{$warning_count}{Message} = kiriwrite_language($main::kiriwrite_lang{pages}{databasepageerror}, $filename, $main::kiriwrite_dbmodule->geterror(1));
				$warning_count++;
				next;

			} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

				# The pages does not exist in the database.

				$warning_list{$warning_count}{Message} = kiriwrite_language($main::kiriwrite_lang{pages}{databasepagedoesnotexist}, $filename);
				$warning_count++;
				next;

			} elsif ($main::kiriwrite_dbmodule->geterror eq "PageExists"){

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

		$main::kiriwrite_dbmodule->disconnect();

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{multiedit}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();

		# Check if the counter of edited pages is 0 and if it is
		# then write a message saying that no pages were edited
		# else write a message listing all of the pages edited.

		if ($pageedited eq 0){

			$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{nopagesedited}, $database_name));

		} else {

			# Write out the message saying that the selected pages
			# were edited.

			$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{pagesedited}, $database_name));
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->startbox("datalist");

			foreach $page (keys %edited_list){

				# Check if the page name is not blank.

				if (!$edited_list{$page}{Name}){

					$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{blank}{noname});
					$main::kiriwrite_presmodule->addtext(" (" . $edited_list{$page}{Filename} . ")");

				} else {

					$main::kiriwrite_presmodule->addtext($edited_list{$page}{Name});
					$main::kiriwrite_presmodule->addtext(" (" . $edited_list{$page}{Filename} . ")");

				}

				$main::kiriwrite_presmodule->addlinebreak();
			}

			$main::kiriwrite_presmodule->endbox();

		}

		# Check if any warnings have occured and write a message
		# if any warnings did occur.

		if (%warning_list){

			# One or several warnings have occured so 
			# write a message.

			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{editedpageswarnings});
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->startbox("datalist");
			foreach $warning (keys %warning_list) {
				$main::kiriwrite_presmodule->addtext($warning_list{$warning}{Message});
				$main::kiriwrite_presmodule->addlinebreak();
			}
			$main::kiriwrite_presmodule->endbox();

		}

		# Write a link going back to the page list for
		# the selected database.

		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($main::kiriwrite_lang{pages}{returnpagelist}, $database_name) });

		return $main::kiriwrite_presmodule->grab();

	} elsif ($confirm eq 0){

		# The action to edit the template has not been confirmed
		# so write a form out instead.

		# Connect to the database server.

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

		# Check if any errors occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Check if the database has read and write permissions.

		my $database_permissions = $main::kiriwrite_dbmodule->dbpermissions($database, 1, 1);

		if ($database_permissions eq 1){

			# The database permissions are invalid so return an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get information about the database.

		my %database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

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

			%page_info = $main::kiriwrite_dbmodule->getpageinfo({ PageFilename => $filelist_filename });

			# Check if any errors occured.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

			} elsif ($main::kiriwrite_dbmodule->geterror eq "PageDoesNotExist"){

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

		$main::kiriwrite_dbmodule->connecttemplate();

		# Check if any errors had occured.

		if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseDoesNotExist"){

			# The template database does not exist so write a warning
			# message.

			$template_warning = $main::kiriwrite_lang{pages}{templatedatabasenotexistmultieditkeep};

		} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so
			# return an error.

			$template_warning = $main::kiriwrite_lang{pages}{templatedatabasepermissionsinvalidmultieditkeep};

		}

		if (!$template_warning){

			# Get the list of templates available.

			@templates_list = $main::kiriwrite_dbmodule->gettemplatelist();

			# Check if any errors had occured.

			if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

				# A database error occured while getting the list
				# of templates so write a warning message with the 
				# extended error information.

				$template_warning = kiriwrite_language($main::kiriwrite_lang{pages}{templatedatabaseerrormultieditkeep}, $main::kiriwrite_dbmodule->geterror(1));

			}

			if (!$template_warning){

				foreach $template_filename (@templates_list){

					# Get the template data.

					%template_info = $main::kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $template_filename });

					# Check if any error occured while getting the template information.

					if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

						# A database error has occured, so write a warning message with
						# the extended error information.

						$template_warning = kiriwrite_language($main::kiriwrite_lang{pages}{templatedatabaseerrormultieditkeep}, $main::kiriwrite_dbmodule->geterror(1));

					} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

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

		$main::kiriwrite_dbmodule->disconnecttemplate();

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		# Write a form for editing the selected pages.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{multiedit}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addhiddendata("mode", "page");
		$main::kiriwrite_presmodule->addhiddendata("action", "multiedit");
		$main::kiriwrite_presmodule->addhiddendata("database", $database);
		$main::kiriwrite_presmodule->addhiddendata("count", $pageseek);
		$main::kiriwrite_presmodule->addhiddendata("confirm", 1);

		$pageseek = 1;

		foreach $page (keys %edit_list){
			$main::kiriwrite_presmodule->addhiddendata("name[" . $pageseek . "]", "on");
			$main::kiriwrite_presmodule->addhiddendata("id[" . $pageseek  . "]", $edit_list{$page}{Filename});
			$pageseek++;
		}

		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{pages}{multieditmessage}, $database_name));
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startbox("datalist");

		foreach $page (keys %edit_list){
			if (!$edit_list{$page}{Name}){
				$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{blank}{noname});
				$main::kiriwrite_presmodule->addtext(" (" . $edit_list{$page}{Filename} . ")");
			} else {
				$main::kiriwrite_presmodule->addtext($edit_list{$page}{Name} . " (" . $edit_list{$page}{Filename} . ")");
			}

			$main::kiriwrite_presmodule->addlinebreak();
		}

		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{multieditmessagevalues});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

		$main::kiriwrite_presmodule->startheader();
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{alter}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{setting}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{value}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->endheader();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addcheckbox("altersection");
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagesection});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addinputbox("newsection", { Size => 64, MaxLength => 256 });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addcheckbox("altertemplate");
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagetemplate});
		$main::kiriwrite_presmodule->endcell();

		$main::kiriwrite_presmodule->addcell("tablecell2");

		if ($template_warning){

			$main::kiriwrite_presmodule->addhiddendata("newtemplate", "!skip");
			$main::kiriwrite_presmodule->addtext($template_warning);

		} else {

			$main::kiriwrite_presmodule->addselectbox("newtemplate");

			foreach $template (keys %template_list){

				$main::kiriwrite_presmodule->addoption($template_list{$template}{Name} . " (" . $template_list{$template}{Filename} . ")", { Value => $template_list{$template}{Filename}});

			}

			$main::kiriwrite_presmodule->addoption($main::kiriwrite_lang{pages}{usenotemplate}, { Value => "!none", Selected => 1 });
			$main::kiriwrite_presmodule->endselectbox();
		}

		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addcheckbox("altersettings");
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{pages}{pagesettings});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addradiobox("newsettings", { Description => $main::kiriwrite_lang{pages}{usepageandsection}, Value => 1 , Selected => 1});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addradiobox("newsettings", { Description => $main::kiriwrite_lang{pages}{usepagename}, Value => 2 });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addradiobox("newsettings", { Description => $main::kiriwrite_lang{pages}{usesectionname}, Value => 3 });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addradiobox("newsettings", { Description => $main::kiriwrite_lang{pages}{nopagesection}, Value => 0 });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->endtable();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{pages}{editpagesbutton});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addreset($main::kiriwrite_lang{common}{clearvalues});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database, { Text => kiriwrite_language($main::kiriwrite_lang{pages}{returnpagelist}, $database_name) });
		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->endform();

		return $main::kiriwrite_presmodule->grab();

	} else {

		# The confirm value is something else other than
		# 1 or 0, so return an error.

		kiriwrite_error("invalidvariable");

	}

}

1;