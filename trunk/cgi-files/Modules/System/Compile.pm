package Modules::System::Compile;

use Modules::System::Common;
use strict;
use warnings;
use Exporter;

our @ISA = qw(Exporter);
our @EXPORT = qw(kiriwrite_compile_makepages kiriwrite_compile_all kiriwrite_compile_list kiriwrite_compile_clean kiriwrite_compile_clean_helper);

sub kiriwrite_compile_makepages{
#################################################################################
# kiriwrite_compile_makepages: Compile the selected pages and place them in the #
# specified output directory.							#
#										#
# Usage:									#
#										#
# kiriwrite_compile_makepages(type, selectedlist, override, overridetemplate,	#
#				confirm);					#
#										#
# type			Specifies if single or multiple databases are to be 	#
#			compiled.						#
# confirm		Specifies if the action to compile the databases should #
#			really be done.						#
# override		Specifies if the template should be overriden.		#
# overridetemplate	Specifies the name of the template to override with.	#
# selectedlist		Specifies the databases to compile from as an array.	#
#################################################################################

	# Get the values that have been passed to the subroutine.

	my ($type, $confirm, $override, $override_template, @selectedlist) = @_;

	# Check if the confirm value is more than one
	# character long.

	kiriwrite_variablecheck($confirm, "maxlength", 1, 0);

	# Check if the value for enabling the override feature
	# is "on" or blank and if it is something else then
	# return an error.

	if (!$override){

		$override = "off";

	}

	if ($override eq "on"){
	} elsif (!$override || $override eq "off"){
	} else {

		# The override value is invalid so return an error.

		kiriwrite_error("overridetemplatevalueinvalid");

	}

	# Check if the override template filename is valid and
	# return an error if it isn't.

	kiriwrite_variablecheck($override_template, "utf8", 0, 0);
	$override_template	= kiriwrite_utf8convert($override_template);
	my $kiriwrite_overridetemplatefilename_length_check 	= kiriwrite_variablecheck($override_template, "maxlength", 64, 1);
	my $kiriwrite_overridetemplatefilename_filename_check 	= kiriwrite_variablecheck($override_template, "filename", "", 1);

	if ($kiriwrite_overridetemplatefilename_length_check eq 1){

		# The override template filename given is too long
		# so return an error.

		kiriwrite_error("overridetemplatetoolong");

	}

	if ($kiriwrite_overridetemplatefilename_filename_check eq 2 && $override_template ne "!none"){

		# The override template filename is invalid so
		# return an error.

		kiriwrite_error("overridetemplateinvalid");

	}

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
		my $information_prefix		= $main::kiriwrite_lang{compile}{informationprefix};
		my $error_prefix		= $main::kiriwrite_lang{compile}{errorprefix};
		my $warning_prefix		= $main::kiriwrite_lang{compile}{warningprefix};
		my $filehandle_page;

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{compile}{compiledatabases}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startbox("datalist");

		# Check if the output directory exists and has
		# valid permissions set.

		$output_exists		= kiriwrite_fileexists($main::kiriwrite_config{'directory_data_output'});

		if ($output_exists ne 0){

			# The output directory does not exist so
			# return an error.

			kiriwrite_error("outputdirectorymissing");

		}

		$output_permissions	= kiriwrite_filepermissions($main::kiriwrite_config{'directory_data_output'}, 1, 1);

		if ($output_permissions ne 0){

			# The output directory has invalid
			# permissions set so return an error.

			kiriwrite_error("outputdirectoryinvalidpermissions");

		}

		# Connect to the database server.

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Connect to the filter database.

		$main::kiriwrite_dbmodule->connectfilter();

		# Check if any error has occured while connecting to the filter
		# database.

		if ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseDoesNotExist"){

			# The filter database does not exist so write a warning message.

 			$main::kiriwrite_presmodule->addtext($warning_prefix . $main::kiriwrite_lang{compile}{filterdatabasemissing});
 			$main::kiriwrite_presmodule->addlinebreak();
 			$filters_skip = 1;
 			$warning_count++;

		} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

			# The filter database has invalid permissions set so write a
			# an error message.

			$main::kiriwrite_presmodule->addtext($error_prefix . $main::kiriwrite_lang{compile}{filterdatabasepermissions});
			$main::kiriwrite_presmodule->addlinebreak();
			$filters_skip = 1;
			$error_count++;

		}

		# Load the filter database (if the filters skip
		# value isn't set to 1).

		if ($filters_skip eq 0){

			# Get the list of available filters.

			@database_filters	= $main::kiriwrite_dbmodule->getfilterlist();

			# Check if any errors occured while getting the list of filters.

			if ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

				# A database error has occured with the filter database.

				$main::kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($main::kiriwrite_lang{compile}{filterdatabaseerror}, $main::kiriwrite_dbmodule->geterror(1)));
				$main::kiriwrite_presmodule->addlinebreak();
				$error_count++;

			}

			# Check if the filters skip value is set to 0
			# before executing the query.

			if ($filters_skip eq 0){

				foreach $filter (@database_filters){

					# Get the filter information.

					%filter_info = $main::kiriwrite_dbmodule->getfilterinfo({ FilterID => $filter, Reduced => 1 });

					# Check if the filter is enabled and if it isn't then process
					# the next filter.

					if (!$filter_info{"FilterEnabled"}){

						# The filter is not enabled so process the next filter.

						next;

					}

					# Check if any errors occured while getting the filter information.

					if ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

						# A database error occured while using the filter database.

						$main::kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($main::kiriwrite_lang{compile}{filterdatabaseerror}, $main::kiriwrite_dbmodule->geterror(1)));
						$main::kiriwrite_presmodule->addlinebreak();
						$error_count++;
						next;

					} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDoesNotExist"){

						# The filter does not exist so process the next filter.

						next;

					}

					# Check if the find filter is blank and
					# if it is then write a warning message.

					if (!$filter_info{"FilterFind"}){

						if ($filters_find_blank_warning ne 1){

							$main::kiriwrite_presmodule->addtext($warning_prefix . $main::kiriwrite_lang{compile}{findfilterblank});
							$main::kiriwrite_presmodule->addlinebreak();
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

 				$main::kiriwrite_presmodule->addtext($information_prefix . $main::kiriwrite_lang{compile}{finishfilterdatabase});
 				$main::kiriwrite_presmodule->addlinebreak();

			}

		}

		# Disconnect from the filter database.

		$main::kiriwrite_dbmodule->disconnectfilter();

		# Connect to the template database.

		$main::kiriwrite_dbmodule->connecttemplate();

		# Check if any errors occured while connecting to the template database.

		if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseDoesNotExist"){

			# The template database does not exist so set the template
			# warning message.

 			$main::kiriwrite_presmodule->addtext($warning_prefix . $main::kiriwrite_lang{compile}{templatedatabasemissing});
 			$main::kiriwrite_presmodule->addlinebreak();
 			$templates_skip = 1;
 			$warning_count++;

		} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so write
			# the template warning message.
 
 			$main::kiriwrite_presmodule->addtext($error_prefix . $main::kiriwrite_lang{compile}{templatedatabasepermissions});
 			$main::kiriwrite_presmodule->addlinebreak();
 			$templates_skip = 1;
 			$error_count++;

		}

		# Check if the template skip value isn't set and if it isn't
		# then get the list of templates.

		if (!$templates_skip){

			@templateslist = $main::kiriwrite_dbmodule->gettemplatelist();

			# Check if any errors had occured.

			if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

				# A database error occured while getting the list
				# of templates so return a warning message with the 
				# extended error information.

				$main::kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($main::kiriwrite_lang{compile}{templatedatabaseerror}, $main::kiriwrite_dbmodule->geterror(1)));
				$templates_skip = 1;
				$error_count++;

			}

			# Check if the template skip value isn't set and if it isn't
			# then process each template.

			if (!$templates_skip){

				# Process each template.

				foreach $template (@templateslist){

					# Get information about the template.

					%template_info = $main::kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $template });

					# Check if any error occured while getting the template information.

					if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

						# A database error has occured, so return an error.

						$main::kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($main::kiriwrite_lang{compile}{templatedatabaseerror}, $main::kiriwrite_dbmodule->geterror(1)));
						$error_count++;

					} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

						# The template does not exist, so process the next template.

						next;

					}

 					# Place each template file into the hash.

 					$templatefiles{$template_info{"TemplateFilename"}}{template} 	= $template_info{"TemplateLayout"};
 					$templatefiles{$template_info{"TemplateFilename"}}{valid} 	= 1;

				}

 				$main::kiriwrite_presmodule->addtext($information_prefix . $main::kiriwrite_lang{compile}{finishtemplatedatabase});
 				$main::kiriwrite_presmodule->addlinebreak();

			}

		}

		# Disconnect from the template database.

		$main::kiriwrite_dbmodule->disconnecttemplate();

		# Process each database.

		foreach $database (@selectedlist){

			# Check if the database filename and length
			# are valid.

			$main::kiriwrite_presmodule->addhorizontalline();

			$database_filename_check	= kiriwrite_variablecheck($database, "page_filename", "", 1);
			$database_maxlength_check	= kiriwrite_variablecheck($database, "maxlength", 32, 1);

			if ($database_filename_check ne 0){

				# The database filename is invalid, so process
				# the next database.

				$main::kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($main::kiriwrite_lang{compile}{databasefilenameinvalidcharacters}, $database));
				$main::kiriwrite_presmodule->addlinebreak();
				$error_count++;
				next;

			}

			if ($database_maxlength_check ne 0){

				# The database file is too long, so process the
				# next database.

				$main::kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($main::kiriwrite_lang{compile}{databasefilenametoolong}, $database));
				$main::kiriwrite_presmodule->addlinebreak();
				$error_count++;
				next;

			}

			# Select the database.

			$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database });

			# Check if any errors had occured while selecting the database.

			if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

				# The database does not exist, so write a warning message.

				$main::kiriwrite_presmodule->addtext($warning_prefix . kiriwrite_language($main::kiriwrite_lang{compile}{databasemissing}, $database));
				$main::kiriwrite_presmodule->addlinebreak();
				$warning_count++;
				next;

			} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

				# The database has invalid permissions set, so write
				# an error message.

				$main::kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($main::kiriwrite_lang{compile}{databaseinvalidpermissions}, $database));
				$main::kiriwrite_presmodule->addlinebreak();
				$error_count++;
				next;

			}

			# Get information about the database.

			my %database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

			# Check if any error occured while getting the database information.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so write an error.

				$main::kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($main::kiriwrite_lang{compile}{databaseerror}, $database, $main::kiriwrite_dbmodule->geterror(1)));
				$main::kiriwrite_presmodule->addlinebreak();
				$error_count++;
				next;

			};

			# Get the database name.

			$database_name = $database_info{"DatabaseName"};

			$main::kiriwrite_presmodule->addtext($information_prefix . kiriwrite_language($main::kiriwrite_lang{compile}{compilingpages}, $database_name));
			$main::kiriwrite_presmodule->addlinebreak();

			# Get the list of pages in the database.

			@databasepages = $main::kiriwrite_dbmodule->getpagelist();

			# Check if any errors occured while getting the list of pages.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				$main::kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($main::kiriwrite_lang{compile}{databasepageerror}, $database, $main::kiriwrite_dbmodule->geterror(1)));
				$main::kiriwrite_presmodule->addlinebreak();
				$error_count++;
				next;

			}

			foreach $page (@databasepages) {

				# Get information about the page.

				%page_info = $main::kiriwrite_dbmodule->getpageinfo({ PageFilename => $page });

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

					$main::kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($main::kiriwrite_lang{compile}{invalidpagefilename}, $page_name));
					$main::kiriwrite_presmodule->addlinebreak();
					$error_count++;
					next;

				}

				# Check if the template with the filename does not exist
				# in the template files hash and write a message and
				# process the next page.

				if ($override eq "on"){

					$page_template = $override_template;

				}

				if (!$templatefiles{$page_template}{valid} && $page_template ne "!none" && $templates_skip eq 0){

					$main::kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($main::kiriwrite_lang{compile}{templatefilemissing}, $page_template, $page_name, $page_filename));
					$main::kiriwrite_presmodule->addlinebreak();
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

						$main::kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($main::kiriwrite_lang{compile}{pageinvalidpermissions}, $page_filename));
						$main::kiriwrite_presmodule->addlinebreak();
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
				($main::kiriwrite_config{"directory_data_output"}) = $main::kiriwrite_config{"directory_data_output"} =~ m/^(.*)$/g;

				open($filehandle_page, "> ",  $main::kiriwrite_config{"directory_data_output"} . '/' . $page_filename) or ($main::kiriwrite_presmodule->addtext($error_prefix . kiriwrite_language($main::kiriwrite_lang{compile}{pagenotwritten}, $page_filename, $!)), $main::kiriwrite_presmodule->addlinebreak(), $error_count++, next);

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
					$main::kiriwrite_presmodule->addtext($information_prefix . ' ');
					$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{blank}{noname} . ' ');
					$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{compile}{compiledpageblankname}, $page_filename));
				} else {
					$main::kiriwrite_presmodule->addtext($information_prefix . kiriwrite_language($main::kiriwrite_lang{compile}{compiledpage}, $page_name, $page_filename));
				}


				$main::kiriwrite_presmodule->addlinebreak();
				$pages_count++;

			}

			# Write a message saying that the database has
			# been processed.

  			$main::kiriwrite_presmodule->addtext($information_prefix . kiriwrite_language($main::kiriwrite_lang{compile}{databasefinish}, $database_name));
			$main::kiriwrite_presmodule->addlinebreak();

		}

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		$main::kiriwrite_presmodule->addhorizontalline();
		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{compile}{compileresults}, $pages_count, $error_count, $warning_count));
		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=compile", { Text => $main::kiriwrite_lang{compile}{returncompilelist} });

		return $main::kiriwrite_presmodule->grab();

	} elsif ($confirm eq 0){

		# The action to compile the databases has
		# not been confirmed so check what type
		# is being used.

		# Get the list of templates for overwriting the
		# template if needed.

		my $templateoverride_skip 	= 0;
		my $templatedbwarning		= "";
		my @template_list;
		my $template_filename;
		my $template_file;
		my %template_info;
		my %template_dblist;
		tie(%template_dblist, "Tie::IxHash");

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

			$main::kiriwrite_dbmodule->connect();

			# Check if any errors occured while connecting to the database server.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

				# A database connection error has occured so return
				# an error.

				kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

			}

			# Select the database.

			$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $databasefilename });

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

			# Check if any error occured while getting the database information.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

				# A database error has occured so return an error and
				# also the extended error information.

				kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

			};

			$database_name = $database_info{"DatabaseName"};

			$main::kiriwrite_dbmodule->connecttemplate();

			# Check if any errors occured while connecting to the
			# template database.

			if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseDoesNotExist"){

				# The template database does not exist so skip processing
				# the list of templates in the template database.

				$templateoverride_skip = 1;
				$templatedbwarning = $main::kiriwrite_lang{compile}{templatedbmissing};

			} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

				# The template database has invalid permissions set so
				# skip processing the list of templates in the
				# template database.

				$templateoverride_skip = 1;
				$templatedbwarning = $main::kiriwrite_lang{compile}{templatedbinvalidpermissions};

			}

			# Get the list of available templates if no errors had
			# occured.

			if ($templateoverride_skip ne 1){

				@template_list = $main::kiriwrite_dbmodule->gettemplatelist();

				# Check if any errors occured while getting the list of templates.

				if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

					# A template database error has occured so skip processing the
					# list of templates in the template database.

					$templateoverride_skip = 1;
					$templatedbwarning = $main::kiriwrite_lang{compile}{templatedberror};

				}

				if ($templateoverride_skip ne 1){

					foreach $template_file (@template_list){

						%template_info = $main::kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $template_file });
						
						if ($main::kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

							next;

						} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

							next;

						}

						$template_dblist{$template_file} = $template_info{"TemplateName"};

					}

				}

			}

			# Disconnect from the template database and database server.

			$main::kiriwrite_dbmodule->disconnecttemplate();
			$main::kiriwrite_dbmodule->disconnect();

			# Write out a form asking the user to confirm if the
			# user wants to compile the selected database.

			$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{compile}{compiledatabase}, { Style => "pageheader" });
			$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
			$main::kiriwrite_presmodule->startbox();
			$main::kiriwrite_presmodule->addhiddendata("mode", "compile");
			$main::kiriwrite_presmodule->addhiddendata("action", "compile");
			$main::kiriwrite_presmodule->addhiddendata("type", "multiple");
			$main::kiriwrite_presmodule->addhiddendata("id[1]", $databasefilename);
			$main::kiriwrite_presmodule->addhiddendata("name[1]", "on");
			$main::kiriwrite_presmodule->addhiddendata("confirm", 1);
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{compile}{compiledatabasemessage}, $database_name));
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();

			if ($templateoverride_skip eq 1){

				# Add message saying why template can't be overridden.
				$main::kiriwrite_presmodule->addtext($templatedbwarning);

			} else {

				# Add overwrite template data.
				$main::kiriwrite_presmodule->addcheckbox("enableoverride", { OptionDescription => $main::kiriwrite_lang{compile}{overridetemplate}, LineBreak => 1 });
				$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{compile}{replacecurrenttemplate});
				$main::kiriwrite_presmodule->addselectbox("overridetemplate");

				foreach $template_file (keys %template_dblist){

					$main::kiriwrite_presmodule->addoption($template_dblist{$template_file} . " (" . $template_file . ")", { Value => $template_file });

				}

				$main::kiriwrite_presmodule->addoption($main::kiriwrite_lang{compile}{dontusetemplate}, { Value => "!none" });
				$main::kiriwrite_presmodule->endselectbox();

			}

			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{compile}{compiledatabasebutton});
			$main::kiriwrite_presmodule->addtext(" | ");
			$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=compile", { Text => $main::kiriwrite_lang{compile}{returncompilelist} });
			$main::kiriwrite_presmodule->endbox();
			$main::kiriwrite_presmodule->endform();

			return $main::kiriwrite_presmodule->grab();

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

			$main::kiriwrite_dbmodule->connect();

			# Check if any errors occured while connecting to the database server.

			if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

				# A database connection error has occured so return
				# an error.

				kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

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

				$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $databasename });

				# Check if any errors had occured while selecting the database.

				if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

					# The database does not exist, so process the next database.

					next;

				} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

					# The database has invalid permissions set, so process
					# the next database.

					next;

				}

				# Get information about the database.

				my %database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

				# Check if any error occured while getting the database information.

				if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

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

			$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{compile}{compileselecteddatabases}, { Style => "pageheader" });
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
			$main::kiriwrite_presmodule->startbox();
			$main::kiriwrite_presmodule->addhiddendata("mode", "compile");
			$main::kiriwrite_presmodule->addhiddendata("action", "compile");
			$main::kiriwrite_presmodule->addhiddendata("type", "multiple");
			$main::kiriwrite_presmodule->addhiddendata("count", $database_count);
			$main::kiriwrite_presmodule->addhiddendata("confirm", 1);
			$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{compile}{compileselecteddatabasesmessage});
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->startbox("datalist");

			$database_count = 0;

			# write out the list of databases to compile.

			foreach $database (keys %database_list){

				$database_count++;

				$main::kiriwrite_presmodule->addhiddendata("id[" . $database_count . "]", $database_list{$database}{Filename});
				$main::kiriwrite_presmodule->addhiddendata("name[" . $database_count . "]", "on");

				# Check if the database name is undefined and if it is
				# then write a message saying the database name is blank.

				if (!$database_list{$database}{Name}){
					$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{compile}{blankdatabasename});
				} else {
					$main::kiriwrite_presmodule->addtext($database_list{$database}{Name});
				}

				$main::kiriwrite_presmodule->addlinebreak();

			}

			$main::kiriwrite_presmodule->endbox();

			$main::kiriwrite_presmodule->addlinebreak();

			$main::kiriwrite_dbmodule->connecttemplate();

			# Check if any errors occured while connecting to the
			# template database.

			if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseDoesNotExist"){

				# The template database does not exist so skip processing
				# the list of templates in the template database.

				$templateoverride_skip = 1;
				$templatedbwarning = $main::kiriwrite_lang{compile}{templatedbmissing};

			} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

				# The template database has invalid permissions set so
				# skip processing the list of templates in the
				# template database.

				$templateoverride_skip = 1;
				$templatedbwarning = $main::kiriwrite_lang{compile}{templatedbinvalidpermissions};

			}

			# Get the list of available templates if no errors had
			# occured.

			if ($templateoverride_skip ne 1){

				@template_list = $main::kiriwrite_dbmodule->gettemplatelist();

				# Check if any errors occured while getting the list of templates.

				if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

					# A template database error has occured so skip processing the
					# list of templates in the template database.

					$templateoverride_skip = 1;
					$templatedbwarning = $main::kiriwrite_lang{compile}{templatedberror};

				}

				if ($templateoverride_skip ne 1){

					foreach $template_file (@template_list){

						%template_info = $main::kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $template_file });
						
						if ($main::kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

							next;

						} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

							next;

						}

						$template_dblist{$template_file} = $template_info{"TemplateName"};

					}

				}

			}

			if ($templateoverride_skip eq 1){

				# Add message saying why template can't be overridden.
				$main::kiriwrite_presmodule->addtext($templatedbwarning);

			} else {

				# Add overwrite template data.
				$main::kiriwrite_presmodule->addcheckbox("enableoverride", { OptionDescription => $main::kiriwrite_lang{compile}{overridetemplate}, LineBreak => 1 });
				$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{compile}{replacecurrenttemplate});
				$main::kiriwrite_presmodule->addselectbox("overridetemplate");

				foreach $template_file (keys %template_dblist){

					$main::kiriwrite_presmodule->addoption($template_dblist{$template_file} . " (" . $template_file . ")", { Value => $template_file });

				}

				$main::kiriwrite_presmodule->addoption($main::kiriwrite_lang{compile}{dontusetemplate}, { Value => "!none" });
				$main::kiriwrite_presmodule->endselectbox();

			}

			# Disconnect from the template database and database server.

			$main::kiriwrite_dbmodule->disconnecttemplate();
			$main::kiriwrite_dbmodule->disconnect();

			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{compile}{compileselecteddatabasesbutton});
			$main::kiriwrite_presmodule->addtext(" | ");
			$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=compile", { Text => $main::kiriwrite_lang{compile}{returncompilelist} });
			$main::kiriwrite_presmodule->endbox();
			$main::kiriwrite_presmodule->endform();

			return $main::kiriwrite_presmodule->grab();

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

	$main::kiriwrite_dbmodule->connect();

	# Check if any errors occured while connecting to the database server.

	if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

		# A database connection error has occured so return
		# an error.

		kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

	}

	# Get the list of available databases.

	my @database_list = $main::kiriwrite_dbmodule->getdblist();

	# Check if any errors occured while getting the databases.

	if ($main::kiriwrite_dbmodule->geterror eq "DataDirMissing"){

		# The database directory is missing so return an error.

		kiriwrite_error("datadirectorymissing");

	} elsif ($main::kiriwrite_dbmodule->geterror eq "DataDirInvalidPermissions"){

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

	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{compile}{compilealldatabases}, { Style => "pageheader" });
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();

	$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
	$main::kiriwrite_presmodule->startbox();
	$main::kiriwrite_presmodule->addhiddendata("mode", "compile");
	$main::kiriwrite_presmodule->addhiddendata("action", "compile");
	$main::kiriwrite_presmodule->addhiddendata("type", "multiple");

	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{compile}{compilealldatabasesmessage});
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();

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
		$main::kiriwrite_presmodule->addhiddendata("id[" . $database_count . "]", $database);
		$main::kiriwrite_presmodule->addhiddendata("name[" . $database_count . "]", "on");

	}

	$main::kiriwrite_presmodule->addhiddendata("count", $database_count);

	my $templateoverride_skip 	= 0;
	my $templatedbwarning		= "";
	my @template_list;
	my $template_filename;
	my %template_info;
	my %template_dblist;
	my $template_file;
	tie(%template_dblist, "Tie::IxHash");

	$main::kiriwrite_dbmodule->connecttemplate();

	# Check if any errors occured while connecting to the
	# template database.

	if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseDoesNotExist"){

		# The template database does not exist so skip processing
		# the list of templates in the template database.

		$templateoverride_skip = 1;
		$templatedbwarning = $main::kiriwrite_lang{compile}{templatedbmissing};

	} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

		# The template database has invalid permissions set so
		# skip processing the list of templates in the
		# template database.

		$templateoverride_skip = 1;
		$templatedbwarning = $main::kiriwrite_lang{compile}{templatedbinvalidpermissions};

	}

	# Get the list of available templates if no errors had
	# occured.

	if ($templateoverride_skip ne 1){

		@template_list = $main::kiriwrite_dbmodule->gettemplatelist();

		# Check if any errors occured while getting the list of templates.

		if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

			# A template database error has occured so skip processing the
			# list of templates in the template database.

			$templateoverride_skip = 1;
			$templatedbwarning = $main::kiriwrite_lang{compile}{templatedberror};

		}

		if ($templateoverride_skip ne 1){

			foreach $template_file (@template_list){

				%template_info = $main::kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $template_file });
				
				if ($main::kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

					next;

				} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

					next;

				}

				$template_dblist{$template_file} = $template_info{"TemplateName"};

			}

		}

	}

	if ($templateoverride_skip eq 1){

		# Add message saying why template can't be overridden.
		$main::kiriwrite_presmodule->addtext($templatedbwarning);

	} else {

		# Add overwrite template data.
		$main::kiriwrite_presmodule->addcheckbox("enableoverride", { OptionDescription => $main::kiriwrite_lang{compile}{overridetemplate}, LineBreak => 1 });
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{compile}{replacecurrenttemplate});
		$main::kiriwrite_presmodule->addselectbox("overridetemplate");

		foreach $template_file (keys %template_dblist){

			$main::kiriwrite_presmodule->addoption($template_dblist{$template_file} . " (" . $template_file . ")", { Value => $template_file });

		}

		$main::kiriwrite_presmodule->addoption($main::kiriwrite_lang{compile}{dontusetemplate}, { Value => "!none" });
		$main::kiriwrite_presmodule->endselectbox();

	}

	# Disconnect from the template database and database server.

	$main::kiriwrite_dbmodule->disconnecttemplate();
	$main::kiriwrite_dbmodule->disconnect();

	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();

	$main::kiriwrite_presmodule->addhiddendata("confirm", 1);
	$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{compile}{compilealldatabasesbutton});
	$main::kiriwrite_presmodule->addtext(" | ");
	$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=compile", { Text => $main::kiriwrite_lang{compile}{returncompilelist} });
	$main::kiriwrite_presmodule->endbox();
	$main::kiriwrite_presmodule->endform();

	return $main::kiriwrite_presmodule->grab();

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

	$main::kiriwrite_dbmodule->connect();

	# Check if any errors occured while connecting to the database server.

	if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

		# A database connection error has occured so return
		# an error.

		kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

	}

	# Get the list of available databases and process any errors that
	# might have occured.

	my @database_list = $main::kiriwrite_dbmodule->getdblist();

	if ($main::kiriwrite_dbmodule->geterror eq "DataDirMissing"){

		# The database directory is missing so return an error.

		kiriwrite_error("datadirectorymissing");

	} elsif ($main::kiriwrite_dbmodule->geterror eq "DataDirInvalidPermissions"){

		# The database directory has invalid permissions set so return
		# an error.

		kiriwrite_error("datadirectoryinvalidpermissions");

	}

	# Begin creating the table for the list of databases.

	foreach $data_file (@database_list){

		# Select the database.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $data_file });

		# Check if any error occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so process the next
			# database.

			next;

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet") {

			# The database has invalid permissions settings, so
			# add the database to the list of databases with
			# invalid permissions set and process the next
			# database.

			push(@permissions_list, $data_file);
			next;

		}

		# Get information about the database.

		%database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any error occured while getting information from the
		# database.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured, add the database and specific
			# error message to the list of databases with errors and
			# process the next database.

			push(@error_list, $data_file . ": " . $main::kiriwrite_dbmodule->geterror(1));
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

	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{compile}{compilepages}, { Style => "pageheader" });
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();

	if ($database_count eq 0){

		# There are no databases available for compiling so
		# write a message instead.

		$main::kiriwrite_presmodule->startbox("errorbox");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{compile}{nodatabasesavailable});
		$main::kiriwrite_presmodule->endbox();

	} else {

		$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addhiddendata("mode", "compile");
		$main::kiriwrite_presmodule->addhiddendata("action", "compile");
		$main::kiriwrite_presmodule->addhiddendata("type", "multiple");

		$main::kiriwrite_presmodule->addreset($main::kiriwrite_lang{common}{selectnone});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{compile}{compileselectedbutton});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addhiddendata("count", $database_count);
		$main::kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

		$main::kiriwrite_presmodule->startheader();
		$main::kiriwrite_presmodule->addheader("", { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{database}{databasename}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{database}{databasedescription}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{options}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->endheader();

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

			$main::kiriwrite_presmodule->startrow();
			$main::kiriwrite_presmodule->addcell($table_style_name);
			$main::kiriwrite_presmodule->addhiddendata("id[" . $database_count . "]", $database_list{$database}{Filename});
			$main::kiriwrite_presmodule->addcheckbox("name[" . $database_count . "]");
			$main::kiriwrite_presmodule->endcell();
			$main::kiriwrite_presmodule->addcell($table_style_name);

			if (!$database_list{$database}{Name}){
				$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=compile&action=compile&type=single&database=" . $database_list{$database}{Filename}, { Text => $main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{blank}{noname}) });
			} else {
				$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database_list{$database}{Filename}, { Text => $database_list{$database}{Name} });
			}

			$main::kiriwrite_presmodule->endcell();
			$main::kiriwrite_presmodule->addcell($table_style_name);

			if (!$database_list{$database}{Description}){
				$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{blank}{nodescription});
			} else {
				$main::kiriwrite_presmodule->addtext($database_list{$database}{Description});
			}

			$main::kiriwrite_presmodule->endcell();
			$main::kiriwrite_presmodule->addcell($table_style_name);
			$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=compile&action=compile&type=single&database=" . $database_list{$database}{Filename}, { Text => $main::kiriwrite_lang{options}{compile} });
			$main::kiriwrite_presmodule->endcell();
			$main::kiriwrite_presmodule->endrow();

			$database_count++;

		}

		$main::kiriwrite_presmodule->endtable();
		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->endform();

	}

	# Disconnect from the database server.

	$main::kiriwrite_dbmodule->disconnect();

	# Check if any databases with problems have appeared and if they
	# have, print out a message saying which databases have problems.

	if (@permissions_list){

 		$main::kiriwrite_presmodule->addlinebreak();

 		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databaseinvalidpermissions}, { Style => "smallpageheader" });
 		$main::kiriwrite_presmodule->addlinebreak();
 		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databaseinvalidpermissionstext});
 		$main::kiriwrite_presmodule->addlinebreak();
 
 		foreach $database (@permissions_list){
 
 			$main::kiriwrite_presmodule->addlinebreak();
 			$main::kiriwrite_presmodule->addtext($database);
 
 		}

 		$main::kiriwrite_presmodule->addlinebreak();
 
	}

	if (@error_list){

 		$main::kiriwrite_presmodule->addlinebreak();

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databaseerrors}, { Style => "smallpageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databaseerrorstext});
		$main::kiriwrite_presmodule->addlinebreak();

		foreach $database (@error_list){

			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addtext($database);

		}

	}

	return $main::kiriwrite_presmodule->grab();

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

	$output_directory_exists	 = kiriwrite_fileexists($main::kiriwrite_config{"directory_data_output"});

	if ($output_directory_exists eq 1){

		# The output directory does not exist so return
		# an error.

		kiriwrite_error("outputdirectorymissing");

	}

	# Check if the output directory has invalid
	# permissions set.

	$output_directory_permissions	= kiriwrite_filepermissions($main::kiriwrite_config{"directory_data_output"});

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

			$file_permissions = kiriwrite_compile_clean_helper($main::kiriwrite_config{"directory_data_output"}, 1);

			$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{compile}{cleanoutputdirectory}, { Style => "pageheader" });

			if ($file_permissions eq 1){

				$main::kiriwrite_presmodule->addlinebreak();
				$main::kiriwrite_presmodule->addlinebreak();
				$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{compile}{somecontentnotremoved});
				$main::kiriwrite_presmodule->addlinebreak();
				$main::kiriwrite_presmodule->addlinebreak();

			} else {

				$main::kiriwrite_presmodule->addlinebreak();
				$main::kiriwrite_presmodule->addlinebreak();
				$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{compile}{contentremoved});
				$main::kiriwrite_presmodule->addlinebreak();
				$main::kiriwrite_presmodule->addlinebreak();

			}

			$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=compile", { Text => $main::kiriwrite_lang{compile}{returncompilelist} });

			return $main::kiriwrite_presmodule->grab();

		} else {

			# A value other than 1 is set for the confirm value
			# (which it shouldn't be) so return an error.

			kiriwrite_error("invalidvariable");

		}

	}

	# Print out a form for cleaning the output directory.

	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{compile}{cleanoutputdirectory}, { Style => "pageheader" });
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
	$main::kiriwrite_presmodule->startbox();
	$main::kiriwrite_presmodule->addhiddendata("mode", "compile");
	$main::kiriwrite_presmodule->addhiddendata("action", "clean");
	$main::kiriwrite_presmodule->addhiddendata("confirm", 1);
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{compile}{cleanoutputdirectorymessage});
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{compile}{cleanoutputdirectorybutton});
	$main::kiriwrite_presmodule->addtext(" | ");
	$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=compile", { Text => $main::kiriwrite_lang{compile}{returncompilelist}});
	$main::kiriwrite_presmodule->endbox();
	$main::kiriwrite_presmodule->endform();

	return $main::kiriwrite_presmodule->grab();

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