package Modules::System::Filter;

use Modules::System::Common;
use strict;
use warnings;
use Exporter;

our @ISA = qw(Exporter);
our @EXPORT = qw(kiriwrite_filter_list kiriwrite_filter_add kiriwrite_filter_edit kiriwrite_filter_delete);

sub kiriwrite_filter_list{
#################################################################################
# kiriwrite_filter_list: Lists the filters that will be used when compiling a	#
# webpage.									#
#										#
# Usage:									#
#										#
# kiriwrite_filter_list([browsenumber]);					#
#										#
# browsenumber	Specifies the page browse number to use.			#
#################################################################################

	my $filter_browsenumber = shift;

	my $filtersdb_notexist = 0;

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

		# The filter database does not exist.

		$filtersdb_notexist = 1;

	} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

		# The filter database has invalid permissions set so return
		# an error.

		kiriwrite_error("filtersdbpermissions");

	} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

		# A database error has occured with the filter database.

		kiriwrite_error("filtersdbdatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

	}

	# Define some variables required for processing the filters list.

	my %filter_list;
	my %filter_info;
	my @database_filters;
	my $blankfindfilter = 0;
	my $filterswarning = "";
	my $filter;
	my $filter_split = $main::kiriwrite_config{"display_filtercount"};
	my $filter_list = 0;
	my $filter_count = 0;
	my $filter_style = 0;
	my $filter_list_count = 0;
	my $filter_total_count;
	my $filter_style_name = "";

	tie(%filter_list, 'Tie::IxHash');

	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{viewfilters}, { Style => "pageheader" });
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();

	# If the filter database exists then get the list of filters,
	# otherwise write a message saying that the filter database
	# does not exist and will be created when a filter is added.

	if ($filtersdb_notexist eq 0){

		if (!$filter_browsenumber || $filter_browsenumber eq 0){

			$filter_browsenumber = 1;

		}

		# Check if the filter browse number is valid and if it isn't
		# then return an error.

		my $kiriwrite_browsenumber_length_check		= kiriwrite_variablecheck($filter_browsenumber, "maxlength", 7, 1);
		my $kiriwrite_browsenumber_number_check		= kiriwrite_variablecheck($filter_browsenumber, "numbers", 0, 1);

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

		# Get the total count of filters in the filter database.

		my $filter_total_count	= $main::kiriwrite_dbmodule->getfiltercount();

		# Check if any errors occured while getting the count of filters.

		if ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error has occured with the filter database.

			kiriwrite_error("filtersdbdatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		if ($filter_total_count ne 0){

			if ($filter_total_count eq $filter_split){

				$filter_list = int(($filter_total_count / $filter_split));

			} else {

				$filter_list = int(($filter_total_count / $filter_split) + 1);

			}

		}

		my $start_from = ($filter_browsenumber - 1) * $filter_split;

		# Get the list of available filters.

		@database_filters	= $main::kiriwrite_dbmodule->getfilterlist({ StartFrom => $start_from, Limit => $filter_split });

		# Check if any errors occured while getting the list of filters.

		if ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error has occured with the filter database.

			kiriwrite_error("filtersdbdatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Process each filter getting the priority, find setting and
		# replace setting.

		foreach $filter (@database_filters){

			# Get the information about the filter.

			%filter_info = $main::kiriwrite_dbmodule->getfilterinfo({ FilterID => $filter });

			# Check if any errors occured while getting the filter information.

			if ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

				# A database error occured while using the filter database.

				kiriwrite_error("filtersdbdatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

			} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDoesNotExist"){

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
			$filter_list{$filter_count}{Enabled}	= $filter_info{"FilterEnabled"};
			$filter_list{$filter_count}{Notes}	= $filter_info{"FilterNotes"};

			$filter_count++;

		}

		# Check if there are filters in the filter database and
		# write a message if there isn't.

	}

	# Check if the database wasn't found and if it
	# wasn't then write a message saying that the
	# database will be created when a filter is
	# added.

	if ($filtersdb_notexist eq 1){

		# The filter database doesn't exist so write
		# a message.

		$main::kiriwrite_presmodule->clear();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{viewfilters}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startbox("errorbox");
		$main::kiriwrite_presmodule->enterdata($main::kiriwrite_lang{filter}{filterdatabasedoesnotexist});
		$main::kiriwrite_presmodule->endbox();

		# Disconnect from the filter database.

		$main::kiriwrite_dbmodule->disconnectfilter();

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();
		return $main::kiriwrite_presmodule->grab();

	}

	# Check if there is a warning message and if
	# there is then write that warning message
	# else write the list of filters.

	if ($filterswarning){

		$main::kiriwrite_presmodule->startbox("errorbox");
		$main::kiriwrite_presmodule->addtext($filterswarning);
		$main::kiriwrite_presmodule->endbox();

	} elsif ($filter_count) {

		# The filter database exists so write out the
		# list of filters.

		if ($blankfindfilter eq 1){

			$main::kiriwrite_presmodule->addboldtext($main::kiriwrite_lang{filter}{warningtitle});
			$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{blankfindfilters});
			$main::kiriwrite_presmodule->addtext();
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addlinebreak();

		}

		# Start a form for using the filter browsing list with.

		$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "GET");
		$main::kiriwrite_presmodule->addhiddendata("mode", "filter");

		# Write out the filter browsing list.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{showlistpage});
		$main::kiriwrite_presmodule->addselectbox("browsenumber");

		# Write out the list of available pages to browse.
		
		while ($filter_list_count ne $filter_list){

			$filter_list_count++;

			if ($filter_list_count eq 1 && !$filter_browsenumber){

				$main::kiriwrite_presmodule->addoption($filter_list_count, { Value => $filter_list_count, Selected => 1 });

			} else {

				if ($filter_browsenumber eq $filter_list_count){

					$main::kiriwrite_presmodule->addoption($filter_list_count, { Value => $filter_list_count, Selected => 1 });

				} else {

					$main::kiriwrite_presmodule->addoption($filter_list_count, { Value => $filter_list_count });

				}

			}

		}

		$main::kiriwrite_presmodule->endselectbox();
		$main::kiriwrite_presmodule->addbutton("action", { Value => "view", Description => $main::kiriwrite_lang{filter}{show} });

		if ($filter_list ne $filter_browsenumber){

			$main::kiriwrite_presmodule->addtext(" | ");
			$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=filter&action=view&browsenumber=" . ($filter_browsenumber + 1), { Text => $main::kiriwrite_lang{filter}{nextpage} });

		}

		# Check if the filter browse number is not blank and
		# not set as 0 and hide the Previous page link if
		# it is.

		if ($filter_browsenumber > 1){

			$main::kiriwrite_presmodule->addtext(" | ");
			$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=filter&action=view&browsenumber=" . ($filter_browsenumber - 1), { Text => $main::kiriwrite_lang{filter}{previouspage} });

		}

		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();

		$main::kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

		$main::kiriwrite_presmodule->startheader();
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{filter}{priority}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{filter}{findsetting}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{filter}{replacesetting}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{options}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->endheader();

		foreach $filter (keys %filter_list){

			# Check which style should be used.

			if ($filter_style eq 0){

				$filter_style_name = "tablecell1";
				$filter_style = 1;

			} else {

				$filter_style_name = "tablecell2";
				$filter_style = 0;

			}

			# Check if the filter is disabled.

			if (!$filter_list{$filter}{Enabled}){

				$filter_style_name = "tablecelldisabled";

			}

			$main::kiriwrite_presmodule->startrow();
			$main::kiriwrite_presmodule->addcell($filter_style_name);
			$main::kiriwrite_presmodule->addtext($filter_list{$filter}{Priority});
			$main::kiriwrite_presmodule->endcell();
			$main::kiriwrite_presmodule->addcell($filter_style_name);

			# Check if the find filter is blank.

			if (!$filter_list{$filter}{Find}){

				# The find filter is blank.

				$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{filter}{blankfindsetting});

			} else {

				# The find filter is not blank.

				$main::kiriwrite_presmodule->addtext($filter_list{$filter}{Find});

			}

			$main::kiriwrite_presmodule->endcell();
			$main::kiriwrite_presmodule->addcell($filter_style_name);

			# Check if the replace filter is blank.

			if (!$filter_list{$filter}{Replace}){

				# The replace filter is blank.

				$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{filter}{blankreplacesetting});

			} else {

				# The replace filter is not blank.

				$main::kiriwrite_presmodule->addtext($filter_list{$filter}{Replace});

			}

			$main::kiriwrite_presmodule->endcell();
			$main::kiriwrite_presmodule->addcell($filter_style_name);
			$main::kiriwrite_presmodule->addlink("?mode=filter&action=edit&filter=" . $filter_list{$filter}{ID}, { Text => $main::kiriwrite_lang{options}{edit} });
			$main::kiriwrite_presmodule->addlink("?mode=filter&action=delete&filter=" . $filter_list{$filter}{ID}, { Text => $main::kiriwrite_lang{options}{delete} });
			$main::kiriwrite_presmodule->endcell();
			$main::kiriwrite_presmodule->endrow();

		}

		$main::kiriwrite_presmodule->endtable();
		$main::kiriwrite_presmodule->endform();

	}

	if (!$filter_total_count){

		$filter_total_count = "";

	}

	if ($filter_browsenumber > 1 && !@database_filters){

		# There were no values given for the page browse
		# number given so write a message saying that
		# there were no pages for the page browse number
		# given.

		$main::kiriwrite_presmodule->clear();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{viewfilters}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startbox("errorbox");
		$main::kiriwrite_presmodule->enterdata($main::kiriwrite_lang{filter}{nofiltersinpagebrowse});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=filter", { Text => $main::kiriwrite_lang{filter}{returntofirstpagebrowse} });
		$main::kiriwrite_presmodule->endbox();

	} elsif (!@database_filters || !$filter_count || $filter_total_count eq 0){

		# There are no filters in the filter database.

		$main::kiriwrite_presmodule->clear();
		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{filter}{viewfilters}), { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startbox("errorbox");
		$main::kiriwrite_presmodule->enterdata($main::kiriwrite_lang{filter}{nofiltersavailable});
		$main::kiriwrite_presmodule->endbox();

	}

	# Disconnect from the filter database.

	$main::kiriwrite_dbmodule->disconnectfilter();

	# Disconnect from the database server.

	$main::kiriwrite_dbmodule->disconnect();

	return $main::kiriwrite_presmodule->grab();

}

sub kiriwrite_filter_add{
#################################################################################
# kiriwrite_filter_add: Adds a filter to the filter list.			#
#										#
# Usage:									#
#										#
# kiriwrite_filter_add(options);						#
#										#
# options	Specifies the following options as a hash (in any order).	#
#										#
# FindFilter	Specifies the find filter setting.				#
# ReplaceFilter	Specifies the replace filter setting.				#
# Priority	Specifies the priority of the filter.				#
# Enabled	Specifies if the filter should be enabled.			#
# Notes		Specifies some notes about the filter.				#
# Confirm	Specifies if the filter should be added.			#
#################################################################################

	# Get the values that have been passed to the subroutine.

	my ($options) = @_;

	my $confirm	= $options->{"Confirm"};

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

		# Get the values from the hashref.

		my $filter_new_find	= $options->{"FindFilter"};
		my $filter_new_replace	= $options->{"ReplaceFilter"};
		my $filter_new_priority	= $options->{"Priority"};
		my $filter_new_enabled	= $options->{"Enabled"};
		my $filter_new_notes	= $options->{"Notes"};

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

		# Check if the enabled value is either "on" or
		# blank and return an error if it is something
		# else.

		if (!$filter_new_enabled || $filter_new_enabled ne "off"){

		} else {

			# FINISH THIS.

		}

		# Check if the new filter should be enabled.

		my $filter_enable = 0;

		if (!$filter_new_enabled){

			$filter_new_enabled = "off";

		}

		if ($filter_new_enabled eq "on"){
			
			# The filter is enabled.

			$filter_enable = 1;

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

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Connect to the filter database.

		$main::kiriwrite_dbmodule->connectfilter(1);

		# Check if any error has occured while connecting to the filter
		# database.

		if ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseDoesNotExist"){

			# The filter database does not exist.

			kiriwrite_error("filtersdbmissing");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

			# The filter database has invalid permissions set so return
			# an error.

			kiriwrite_error("filtersdbpermissions");

		}

		# Add the filter to the filter database.

		$main::kiriwrite_dbmodule->addfilter({ FindFilter => $filter_new_find, ReplaceFilter => $filter_new_replace, Priority => $filter_new_priority, Enabled => $filter_enable, Notes => $filter_new_notes});

		# Check if any errors have occured while adding the filter.

		if ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

			# The filter database has invalid permissions set so return
			# an error.

			kiriwrite_error("filtersdbpermissions");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseUncreatable"){

			# The filter database is uncreatable so return an error.

			kiriwrite_error("filterdatabase");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error with the filter database has occured so return
			# an error with the extended error information.

			kiriwrite_error("filtersdbdatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Disconnect from the filter database.

		$main::kiriwrite_dbmodule->disconnectfilter();

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		# Write out a message saying that the filter was added to the
		# filter database.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{filteradded}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{filteraddedmessage});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=filter", { Text => $main::kiriwrite_lang{filter}{returnfilterlist} });

 		return $main::kiriwrite_presmodule->grab();

	} elsif ($confirm ne 0) {

		# The confirm integer is another value (which
		# it shouldn't be) so return an error.

		kiriwrite_error("invalidvalue");

	}

	# The confirm integer was blank so print out a form
	# for adding a new filter.

	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{addfilter}, { Style => "pageheader" });
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
	$main::kiriwrite_presmodule->startbox();
	$main::kiriwrite_presmodule->addhiddendata("mode", "filter");
	$main::kiriwrite_presmodule->addhiddendata("action", "add");
	$main::kiriwrite_presmodule->addhiddendata("confirm", 1);
	$main::kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

	$main::kiriwrite_presmodule->startheader();
	$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{setting}, { Style => "tablecellheader" });
	$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{value}, { Style => "tablecellheader" });
	$main::kiriwrite_presmodule->endheader();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{findfilter});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("findword", { Size => 64, MaxLength => 1024 });
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{replacefilter});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("replaceword", { Size => 64, MaxLength => 1024 });
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{priority});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("priority", { Size => 5, MaxLength => 5 });
	$main::kiriwrite_presmodule->startlist();
	$main::kiriwrite_presmodule->additem($main::kiriwrite_lang{filter}{noprioritygiven});
	$main::kiriwrite_presmodule->endlist();
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{notes});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addtextbox("notes", { Columns => $main::kiriwrite_config{"display_textareacols"}, Rows => $main::kiriwrite_config{"display_textarearows"} });
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addcheckbox("enabled", { OptionDescription => $main::kiriwrite_lang{filter}{enabled}, Checked => 1 });
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->endtable();

	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{filter}{addfilterbutton});
	$main::kiriwrite_presmodule->addtext(" | ");
	$main::kiriwrite_presmodule->addreset($main::kiriwrite_lang{common}{clearvalues});
	$main::kiriwrite_presmodule->addtext(" | ");
	$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=filter", { Text => $main::kiriwrite_lang{filter}{returnfilterlist} });

	$main::kiriwrite_presmodule->endbox();
	$main::kiriwrite_presmodule->endform();

	return $main::kiriwrite_presmodule->grab();

}

sub kiriwrite_filter_edit{
#################################################################################
# kiriwrite_filter_edit: Edits a filter from the filter list.			#
#										#
# Usage:									#
#										#
# kiriwrite_filter_edit(options);						#
#										#
# options		Specifies the following options as hash (in any order).	#
#										#
# FilterID		Specifies the filter number in the filter database.	#
# NewFindFilter		Specifies the new find filter.				#
# NewReplaceFilter	Specifies the new replace filter.			#
# NewPriority		Specifies the new priority.				#
# NewEnabled		Specifies the new enable setting.			#
# NewFilterNotes	Specifies the new filter notes.				#
# Confirm		Confirms the action to edit a filter.			#
#################################################################################

	# Get the values that have been passed to the subroutine.

	my ($options) = @_;
	#my ($filter_id, $filter_new_find, $filter_new_replace, $filter_new_priority, $filter_new_notes, $confirm) = @_;

	my $filter_id		= $options->{"FilterID"};
	my $confirm = $options->{"Confirm"};

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
	my $filter_enabled;
 	my $filter_notes;
 
	# Check if the action to edit a filter has been
	# confirmed.

	if ($confirm eq 1){

		# The action to edit a filter has been confirmed so
		# edit the selected filter.

		# Get the values from the hashref.

		my $filter_new_find	= $options->{"NewFindFilter"};
		my $filter_new_replace	= $options->{"NewReplaceFilter"};
		my $filter_new_priority	= $options->{"NewPriority"};
		my $filter_new_notes	= $options->{"NewFilterNotes"};
		my $filter_new_enabled	= $options->{"NewEnabled"};

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

		# Check to see if the filter should be enabled.

		my $filter_enable = 0;

		if (!$filter_new_enabled){

			$filter_new_enabled = "off";

		}

		if ($filter_new_enabled eq "on"){
			
			# The filter is enabled.

			$filter_enable = 1;

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

			# The filter database does not exist.

			kiriwrite_error("filtersdbmissing");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

			# The filter database has invalid permissions set so return
			# an error.

			kiriwrite_error("filtersdbpermissions");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error has occured with the filter database.

			kiriwrite_error("filtersdbdatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Edit the selected filter in the filter database.

		$main::kiriwrite_dbmodule->editfilter({ FilterID => $filter_id, NewFindFilter => $filter_new_find, NewReplaceFilter => $filter_new_replace, NewFilterPriority => $filter_new_priority, NewEnabled => $filter_enable, NewFilterNotes => $filter_new_notes });

		# Check if any errors occured while editing the filter.

		if ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

			# The filter database has invalid permissions set so return
			# an error.

			kiriwrite_error("filtersdbpermissions");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error has occured while using the filter database
			# so return an error.

			kiriwrite_error("filtersdbdatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDoesNotExist"){

			# The specified filter does not exist so return an error.

			kiriwrite_error("filterdoesnotexist");

		}

		# Disconnect from the filter database.

		$main::kiriwrite_dbmodule->disconnectfilter();

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		# Write a message saying that the filter was edited.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{editedfilter}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{editedfiltermessage});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=filter", { Text => $main::kiriwrite_lang{filter}{returnfilterlist}});

		return $main::kiriwrite_presmodule->grab();

	} elsif ($confirm eq 0){

		# The action to edit a filter has not been confirmed
		# so write a form for editing the filter with.

		# Connect to the database server.

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

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

			# The filter database does not exist.

			kiriwrite_error("filtersdbmissing");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

			# The filter database has invalid permissions set so return
			# an error.

			kiriwrite_error("filtersdbpermissions");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error has occured with the filter database.

			kiriwrite_error("filtersdbdatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Get information about the filter.

		my %filter_info = $main::kiriwrite_dbmodule->getfilterinfo({ FilterID => $filter_id });

		# Check if any errors occured while getting information about the filter.

		if ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error occured while using the filter database so
			# return an error.

			kiriwrite_error("filtersdbdatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDoesNotExist"){

			# The filter does not exist so return an error.

			kiriwrite_error("filterdoesnotexist");

		}

		# Get the required information.

		$filter_priority	= $filter_info{"FilterPriority"};
		$filter_find		= $filter_info{"FilterFind"};
		$filter_replace		= $filter_info{"FilterReplace"};
		$filter_enabled		= $filter_info{"FilterEnabled"};
		$filter_notes		= $filter_info{"FilterNotes"};

		# Disconnect from the filter database.

		$main::kiriwrite_dbmodule->disconnectfilter();

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		# Write out the form.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{editfilter}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addhiddendata("mode", "filter");
		$main::kiriwrite_presmodule->addhiddendata("action", "edit");
		$main::kiriwrite_presmodule->addhiddendata("filter", $filter_id);
		$main::kiriwrite_presmodule->addhiddendata("confirm", 1);

		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

		$main::kiriwrite_presmodule->startheader();
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{setting}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{value}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->endheader();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{findfilter});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("filterfind", { Size => 64, MaxLength => 1024, Value => $filter_find });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{replacefilter});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("filterreplace", { Size => 64, MaxLength => 1024, Value => $filter_replace });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{priority});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("priority", { Size => 5, MaxLength => 5, Value => $filter_priority });
		$main::kiriwrite_presmodule->startlist();
		$main::kiriwrite_presmodule->additem($main::kiriwrite_lang{filter}{noprioritygiven});
		$main::kiriwrite_presmodule->endlist();
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{notes});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addtextbox("notes", { Columns => $main::kiriwrite_config{"display_textareacols"}, Rows => $main::kiriwrite_config{"display_textarearows"}, Value => $filter_notes});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");

		if ($filter_enabled eq 1){

			$main::kiriwrite_presmodule->addcheckbox("enabled", { OptionDescription => $main::kiriwrite_lang{filter}{enabled}, Checked => 1 });

		} else {

			$main::kiriwrite_presmodule->addcheckbox("enabled", { OptionDescription => $main::kiriwrite_lang{filter}{enabled} });

		}
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->endtable();

		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{filter}{editfilterbutton});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addreset($main::kiriwrite_lang{common}{restorecurrent});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=filter", { Text => $main::kiriwrite_lang{filter}{returnfilterlist} });
		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->endform();

		return $main::kiriwrite_presmodule->grab(); 

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

			# The filter database does not exist.

			kiriwrite_error("filtersdbmissing");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

			# The filter database has invalid permissions set so return
			# an error.

			kiriwrite_error("filtersdbpermissions");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error has occured with the filter database.

			kiriwrite_error("filtersdbdatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Delete the filter from the filter database.

		$main::kiriwrite_dbmodule->deletefilter({ FilterID => $filter_id });

		# Check if any errors occured while deleting the filter.

		if ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error has occured while trying to delete a filter so
			# return an error.

			kiriwrite_error("filtersdbdatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDoesNotExist"){

 			# The filter does not exist so return an error.
 
 			kiriwrite_error("filterdoesnotexist");

		}

		# Disconnect from the filter database.

		$main::kiriwrite_dbmodule->disconnectfilter();

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		# Write a message saying that the filter was deleted
		# from the filter database.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{deletedfilter}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{deletedfiltermessage});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=filter", { Text => $main::kiriwrite_lang{filter}{returnfilterlist} });

	} elsif ($confirm eq 0) {

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

			# The filter database does not exist.

			kiriwrite_error("filtersdbmissing");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseInvalidPermissionsSet"){

			# The filter database has invalid permissions set so return
			# an error.

			kiriwrite_error("filtersdbpermissions");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error has occured with the filter database.

			kiriwrite_error("filtersdbdatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Get information about the filter (to check if it exists).

		my %filter_info = $main::kiriwrite_dbmodule->getfilterinfo({ FilterID => $filter_id });

		# Check if any errors occured while getting information about the filter.

		if ($main::kiriwrite_dbmodule->geterror eq "FilterDatabaseError"){

			# A database error occured while using the filter database so
			# return an error.

			kiriwrite_error("filtersdbdatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		} elsif ($main::kiriwrite_dbmodule->geterror eq "FilterDoesNotExist"){

			# The filter does not exist so return an error.

			kiriwrite_error("filterdoesnotexist");

		}

		# Disconnect from the filter database.

		$main::kiriwrite_dbmodule->disconnectfilter();

		# Disconnect from the database

		# The confirm integer is '0', so continue write out
		# a form asking the user to confirm the deletion
		# pf the filter.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{deletefilter}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{filter}{deletefiltermessage});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addhiddendata("mode", "filter");
		$main::kiriwrite_presmodule->addhiddendata("action", "delete");
		$main::kiriwrite_presmodule->addhiddendata("filter", $filter_id);
		$main::kiriwrite_presmodule->addhiddendata("confirm", 1);
		$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{filter}{deletefilterbutton});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=filter", { Text => $main::kiriwrite_lang{filter}{deletefilterreturn} });
 		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->endform();

	} else {

		kiriwrite_error("invalidvalue");

	}

	return $main::kiriwrite_presmodule->grab();

}

1; 
