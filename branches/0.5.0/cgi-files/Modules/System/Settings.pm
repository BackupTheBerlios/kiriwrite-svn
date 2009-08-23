package Modules::System::Settings;

use Modules::System::Common;
use strict;
use warnings;
use Exporter;

our @ISA = qw(Exporter);
our @EXPORT = qw(kiriwrite_settings_view kiriwrite_settings_edit kiriwrite_output_config); 

sub kiriwrite_settings_view{
#################################################################################
# kiriwrite_options_view: Writes out the list of options and variables.		#
#										#
# Usage:									#
#										#
# kiriwrite_settings_view();							#
#################################################################################

	# Get the settings.

	my $settings_directory_db		= $main::kiriwrite_config{"directory_data_db"};
	my $settings_directory_output		= $main::kiriwrite_config{"directory_data_output"};
	my $settings_noncgi_images		= $main::kiriwrite_config{"directory_noncgi_images"};
	my $settings_display_textareacols	= $main::kiriwrite_config{"display_textareacols"};
	my $settings_display_textarearows	= $main::kiriwrite_config{"display_textarearows"};
	my $settings_display_pagecount		= $main::kiriwrite_config{"display_pagecount"};
	my $settings_display_templatecount	= $main::kiriwrite_config{"display_templatecount"};
	my $settings_display_filtercount	= $main::kiriwrite_config{"display_filtercount"};
	my $settings_system_datetime		= $main::kiriwrite_config{"system_datetime"};
	my $settings_system_language		= $main::kiriwrite_config{"system_language"};
	my $settings_system_presentation	= $main::kiriwrite_config{"system_presmodule"};
	my $settings_system_database		= $main::kiriwrite_config{"system_dbmodule"};
	my $settings_system_output		= $main::kiriwrite_config{"system_outputmodule"};


	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{viewsettings}, { Style => "pageheader" });
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{currentsettings});
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

	$main::kiriwrite_presmodule->startheader();
	$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{setting}, { Style => "tablecellheader" });
	$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{value}, { Style => "tablecellheader" });
	$main::kiriwrite_presmodule->endheader();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{directories});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{databasedirectory});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addtext($settings_directory_db);
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{outputdirectory});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addtext($settings_directory_output);
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{imagesuripath});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addtext($settings_noncgi_images);
	$main::kiriwrite_presmodule->endcell();
	$main::main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{display});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{textareacols});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addtext($settings_display_textareacols);
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{textarearows});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addtext($settings_display_textarearows);
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{pagecount});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addtext($settings_display_pagecount);
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{templatecount});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addtext($settings_display_templatecount);
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{filtercount});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addtext($settings_display_filtercount);
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{date});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{dateformat});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addtext($settings_system_datetime);
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{language});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{systemlanguage});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addtext($settings_system_language);
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{modules});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{presentationmodule});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addtext($settings_system_presentation);
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{outputmodule});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addtext($settings_system_output);
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{databasemodule});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addtext($settings_system_database);
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->endtable();

	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{altersettings});

	return $main::kiriwrite_presmodule->grab();

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
# OutputModule		Specifies the new output module to use for Kiriwrite.	#
# TextAreaCols		Specifies the width of the text area.			#
# TextAreaRows		Specifies the height of the text area.			#
# PageCount		Specifies the amount of pages that should be viewed.	#
# FilterCount		Specifies the amount of filters that should be viewed.	#
# TemplateCount		Specifies the amount of templates that should be viewed.#
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
	my $settings_outputmodule		= $passedoptions->{"OutputModule"};
	my $settings_dbmodule			= $passedoptions->{"DatabaseModule"};
	my $settings_textareacols		= $passedoptions->{"TextAreaCols"};
	my $settings_textarearows		= $passedoptions->{"TextAreaRows"};
	my $settings_pagecount			= $passedoptions->{"PageCount"};
	my $settings_filtercount		= $passedoptions->{"FilterCount"};
	my $settings_templatecount		= $passedoptions->{"TemplateCount"};

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
		my $kiriwrite_outputmodule_modulename_check	= kiriwrite_variablecheck($settings_outputmodule, "module", 0, 1);

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

		if ($kiriwrite_outputmodule_modulename_check eq 1){

			# The output module name is blank, so return
			# an error.

			kiriwrite_error("outputmoduleblank");

		}

		if ($kiriwrite_outputmodule_modulename_check eq 2){

			# The output module name is invalid, so return
			# an error.

			kiriwrite_error("outputmoduleinvalid");

		}

		# Check if the directory names only contain letters and numbers and
		# return a specific error if they don't.

		my $kiriwrite_dbdirectory_check 	= kiriwrite_variablecheck($settings_dbdirectory, "directory", 0, 1);
		my $kiriwrite_outputdirectory_check 	= kiriwrite_variablecheck($settings_outputdirectory, "directory", 0, 1);
		kiriwrite_variablecheck($settings_datetimeformat, "datetime", 0, 0);

		my $kiriwrite_textarearows_maxlength 		= kiriwrite_variablecheck($settings_textarearows, "maxlength", 3, 1);
		my $kiriwrite_textarearows_number 		= kiriwrite_variablecheck($settings_textarearows, "numbers", 0, 1);
		my $kiriwrite_textareacols_maxlength		= kiriwrite_variablecheck($settings_textareacols, "maxlength", 3, 1);
		my $kiriwrite_textareacols_number 		= kiriwrite_variablecheck($settings_textareacols, "numbers", 0, 1);

		my $kiriwrite_pagecount_maxlength		= kiriwrite_variablecheck($settings_pagecount, "maxlength", 4, 1);
		my $kiriwrite_pagecount_number	 		= kiriwrite_variablecheck($settings_pagecount, "numbers", 0, 1);
		my $kiriwrite_filtercount_maxlength		= kiriwrite_variablecheck($settings_filtercount, "maxlength", 4, 1);
		my $kiriwrite_filtercount_number		= kiriwrite_variablecheck($settings_filtercount, "numbers", 0, 1);
		my $kiriwrite_templatecount_maxlength		= kiriwrite_variablecheck($settings_templatecount, "maxlength", 4, 1);
		my $kiriwrite_templatecount_number		= kiriwrite_variablecheck($settings_templatecount, "numbers", 0, 1);

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

		if (!$settings_textarearows){

			# The text area row value is blank so return an
			# error.

			kiriwrite_error("textarearowblank");

		}

		if ($kiriwrite_textarearows_maxlength eq 1){

			# The text area row value is too long, so return
			# an error.

			kiriwrite_error("textarearowtoolong");

		}

		if ($kiriwrite_textarearows_number eq 1){

			# The text area row value is invalid, so return
			# an error.

			kiriwrite_error("textarearowinvalid");

		}

		if (!$settings_textareacols){

			# The text area column value is blank so return
			# an error.

			kiriwrite_error("textareacolblank");

		}

		if ($kiriwrite_textareacols_maxlength eq 1){

			# The text area column value is too long, so return
			# an error.

			kiriwrite_error("textareacoltoolong");

		}

		if ($kiriwrite_textareacols_number eq 1){

			# The text area column value is invalid, so return
			# an error.

			kiriwrite_error("textareacolinvalid");

		}

		if ($kiriwrite_pagecount_maxlength eq 1){

			# The page count value is too long, so return
			# an error.

			kiriwrite_error("pagecounttoolong");

		}

		if ($kiriwrite_pagecount_number eq 1){

			# The page count value is invalid, so return
			# an error.

			kiriwrite_error("pagecountinvalid");

		}

		if ($kiriwrite_filtercount_maxlength eq 1){

			# The filter count value is too long, so return
			# an error.

			kiriwrite_error("filtercounttoolong");

		}

		if ($kiriwrite_filtercount_number eq 1){

			# The filter count value is invalid, so return
			# an error.

			kiriwrite_error("filtercountinvalid");

		}

		if ($kiriwrite_templatecount_maxlength eq 1){

			# The template count value is too long, so return
			# an error.

			kiriwrite_error("templatecounttoolong");

		}

		if ($kiriwrite_templatecount_number eq 1){

			# The template count value is invalid, so return
			# an error.

			kiriwrite_error("templatecountinvalid");

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

		my $languagefile_exists = kiriwrite_fileexists("lang/" . $settings_languagesystem . ".lang");

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

			$settings_database_password 	= $main::kiriwrite_config{"database_password"};

		}

		# Write the new settings to the configuration file.

		kiriwrite_output_config({ DatabaseDirectory => $settings_dbdirectory, OutputDirectory => $settings_outputdirectory, ImagesURIPath => $settings_imagesuri, DateTimeFormat => $settings_datetimeformat, SystemLanguage => $settings_languagesystem, PresentationModule => $settings_presmodule, OutputModule => $settings_outputmodule, TextAreaCols => $settings_textareacols, TextAreaRows => $settings_textarearows, PageCount => $settings_pagecount, FilterCount => $settings_filtercount, TemplateCount => $settings_templatecount, DatabaseModule => $settings_dbmodule, DatabaseServer => $settings_database_server, DatabasePort => $settings_database_port, DatabaseProtocol => $settings_database_protocol, DatabaseSQLDatabase => $settings_database_sqldatabase, DatabaseUsername => $settings_database_username, DatabasePassword => $settings_database_password, DatabaseTablePrefix => $settings_database_tableprefix });

		# Write a confirmation message.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{settingsedited}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{settingseditedmessage});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=settings", { Text => $main::kiriwrite_lang{setting}{returnsettingslist} });

		return $main::kiriwrite_presmodule->grab();

	}

	# Get the list of languages available.

	my %language_list;
	my @language_directory 		= "";
	my $language;
	my ($language_file, %language_file);
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
	my $language_config		= $main::kiriwrite_config{"system_language"};
	my @lang_data;
	my $kiriwrite_languagefilehandle;

	tie(%language_list, 'Tie::IxHash');

	opendir(LANGUAGEDIR, "lang");
	@language_directory = grep /m*\.lang$/, readdir(LANGUAGEDIR);
	closedir(LANGUAGEDIR);

	# Process each language by loading the language file
	# used for each language and then get the System name and 
	# the local name of the language.

	foreach $language_filename (@language_directory){

		# Load the language file currently selected.

		open($kiriwrite_languagefilehandle, "lang/" . $main::kiriwrite_config{"system_language"} . ".lang");
		@lang_data = <$kiriwrite_languagefilehandle>;
		%language_file = kiriwrite_processconfig(@lang_data);
		close($kiriwrite_languagefilehandle);

		# Get the system name and the local name of the language.

		$language_file_localname = $language_file{about}{name};

		# Check if either the system name or the local name of the language
		# is blank and if it is, then don't add the language to the list.

		if (!$language_file_localname){

			# The system name or the local name is blank so don't add
			# the language to the list.
		
		} else {

			# Get the 'friendly' name of the language file name (basically
			# remove the .lang part from the filename.

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

		undef $language_file;

	}

	# Get the list of presentation modules available.

	my %presmodule_list;
	my @presmodule_directory;
	my $presmodule;
	my $presmodule_file 		= "";
	my $presmodule_count		= 0;
	my $presmodule_config		= $main::kiriwrite_config{"system_presmodule"};

	# Open and get the list of presentation modules (perl modules) by getting
	# only files which end in .pm.

	opendir(OUTPUTSYSTEMDIR, "Modules/Presentation");
	@presmodule_directory = grep /m*\.pm$/, readdir(OUTPUTSYSTEMDIR);
	closedir(OUTPUTSYSTEMDIR);

	foreach $presmodule_file (@presmodule_directory){

		# Remove the .pm suffix.

		$presmodule_file =~ s/.pm$//;
		$presmodule_list{$presmodule_count}{Filename} = $presmodule_file;
		$presmodule_count++;

	}

	# Get the list of database modules available.

	my %dbmodule_list;
	my @dbmodule_directory;
	my $dbmodule;
	my $dbmodule_file 		= "";
	my $dbmodule_count		= 0;
	my $dbmodule_config		= $main::kiriwrite_config{"system_dbmodule"};

	# Open and get the list of database modules (perl modules) by getting
	# only files which end in .pm.

	opendir(DATABASEDIR, "Modules/Database");
	@dbmodule_directory = grep /m*\.pm$/, readdir(DATABASEDIR);
	closedir(DATABASEDIR);

	foreach $dbmodule_file (@dbmodule_directory){

		# Remove the .pm suffix.

		$dbmodule_file =~ s/.pm$//;
		$dbmodule_list{$dbmodule_count}{Filename} = $dbmodule_file;
		$dbmodule_count++;

	}

	my %outputmodule_list;
	my @outputmodule_directory;
	my $outputmodule;
	my $outputmodule_file 		= "";
	my $outputmodule_count		= 0;
	my $outputmodule_config		= $main::kiriwrite_config{"system_outputmodule"};

	# Open and get the list of output modules (perl modules) by getting
	# only files which end in .pm.

	opendir(DATABASEDIR, "Modules/Output");
	@outputmodule_directory = grep /m*\.pm$/, readdir(DATABASEDIR);
	closedir(DATABASEDIR);

	foreach $outputmodule_file (@outputmodule_directory){

		# Remove the .pm suffix.

		$outputmodule_file =~ s/.pm$//;
		$outputmodule_list{$outputmodule_count}{Filename} = $outputmodule_file;
		$outputmodule_count++;

	}

	# Get the directory settings.

	my $directory_settings_database 	= $main::kiriwrite_config{"directory_data_db"};
	my $directory_settings_output	 	= $main::kiriwrite_config{"directory_data_output"};
	my $directory_settings_imagesuri 	= $main::kiriwrite_config{"directory_noncgi_images"};
	my $datetime_setting			= $main::kiriwrite_config{"system_datetime"};

	my $display_textareacols		= $main::kiriwrite_config{"display_textareacols"};
	my $display_textarearows		= $main::kiriwrite_config{"display_textarearows"};
	my $display_pagecount			= $main::kiriwrite_config{"display_pagecount"};
	my $display_templatecount		= $main::kiriwrite_config{"display_templatecount"};
	my $display_filtercount			= $main::kiriwrite_config{"display_filtercount"};

	my $database_server			= $main::kiriwrite_config{"database_server"};
	my $database_port			= $main::kiriwrite_config{"database_port"};
	my $database_protocol			= $main::kiriwrite_config{"database_protocol"};
	my $database_sqldatabase		= $main::kiriwrite_config{"database_sqldatabase"};
	my $database_username			= $main::kiriwrite_config{"database_username"};
	my $database_passwordhash		= $main::kiriwrite_config{"database_passwordhash"};
	my $database_password			= $main::kiriwrite_config{"database_password"};
	my $database_prefix			= $main::kiriwrite_config{"database_tableprefix"};

	# Print out a form for editing the settings.

	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{editsettings}, { Style => "pageheader" });
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addboldtext($main::kiriwrite_lang{setting}{warning});
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{warningmessage});
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();

	$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
	$main::kiriwrite_presmodule->startbox();
	$main::kiriwrite_presmodule->addhiddendata("mode", "settings");
	$main::kiriwrite_presmodule->addhiddendata("action", "edit");
	$main::kiriwrite_presmodule->addhiddendata("confirm", 1);

	$main::kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

	$main::kiriwrite_presmodule->startheader();
	$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{setting}, { Style => "tablecellheader" });
	$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{value}, { Style => "tablecellheader" });
	$main::kiriwrite_presmodule->endheader();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{directories});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{databasedirectory});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("databasedir", { Size => 32, MaxLength => 64, Value => $directory_settings_database });
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{outputdirectory});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("outputdir", { Size => 32, MaxLength => 64, Value => $directory_settings_output });
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{imagesuripath});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("imagesuripath", { Size => 32, MaxLength => 512, Value => $directory_settings_imagesuri });
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{display});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{textareacols});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("textareacols", { Size => 3, MaxLength => 3, Value => $display_textareacols });
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{textarearows});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("textarearows", { Size => 3, MaxLength => 3, Value => $display_textarearows });
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{pagecount});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("pagecount", { Size => 4, MaxLength => 4, Value => $display_pagecount });
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{filtercount});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("filtercount", { Size => 4, MaxLength => 4, Value => $display_filtercount });
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{templatecount});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("templatecount", { Size => 4, MaxLength => 4, Value => $display_templatecount });
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{date});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{dateformat});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("datetime", { Size => 32, MaxLength => 64, Value => $datetime_setting });
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->startbox("datalist");

	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{singleday});
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{doubleday});
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{singlemonth});
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{doublemonth});
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{singleyear});
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{doubleyear});
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{singlehour});
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{doublehour});
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{singleminute});
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{doubleminute});
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{singlesecond});
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{doublesecond});
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{othercharacters});
	$main::kiriwrite_presmodule->endbox();
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{language});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{systemlanguage});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");

	$main::kiriwrite_presmodule->addselectbox("language");

	# Process the list of available languages.

	foreach $language (keys %language_list){

		# Check if the language filename matches the filename in the configuration
		# file.

		if ($language_list{$language}{Filename} eq $language_config){

			$main::kiriwrite_presmodule->addoption($language_list{$language}{Name}, { Value => $language_list{$language}{Filename} , Selected => 1 });

		} else {

			$main::kiriwrite_presmodule->addoption($language_list{$language}{Name}, { Value => $language_list{$language}{Filename} });

		}

	}

	$main::kiriwrite_presmodule->endselectbox();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{modules});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecellheader");
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{presentationmodule});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");

	$main::kiriwrite_presmodule->addselectbox("presmodule");

	# Process the list of available presentation modules.

	foreach $presmodule (keys %presmodule_list){

		# Check if the presentation module fileanme matches the filename in the 
		# configuration file.

		if ($presmodule_list{$presmodule}{Filename} eq $presmodule_config){

			$main::kiriwrite_presmodule->addoption($presmodule_list{$presmodule}{Filename}, { Value => $presmodule_list{$presmodule}{Filename} , Selected => 1 });

		} else {

 			$main::kiriwrite_presmodule->addoption($presmodule_list{$presmodule}{Filename}, { Value => $presmodule_list{$presmodule}{Filename} });

		}

	}

	$main::kiriwrite_presmodule->endselectbox();

	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{outputmodule});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");

	# Process the list of available output modules.

	$main::kiriwrite_presmodule->addselectbox("outputmodule");

	foreach $outputmodule (keys %outputmodule_list){

		# Check if the output module fileanme matches the filename in the 
		# configuration file.

		if ($outputmodule_list{$outputmodule}{Filename} eq $outputmodule_config){

			$main::kiriwrite_presmodule->addoption($outputmodule_list{$outputmodule}{Filename}, { Value => $outputmodule_list{$outputmodule}{Filename} , Selected => 1 });

		} else {

 			$main::kiriwrite_presmodule->addoption($outputmodule_list{$outputmodule}{Filename}, { Value => $outputmodule_list{$outputmodule}{Filename} });

		}


	}

	$main::kiriwrite_presmodule->endselectbox();

	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{databasemodule});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");

	# Process the list of available database modules.

	$main::kiriwrite_presmodule->addselectbox("dbmodule");

	foreach $dbmodule (keys %dbmodule_list){

		# Check if the database module fileanme matches the filename in the 
		# configuration file.

		if ($dbmodule_list{$dbmodule}{Filename} eq $dbmodule_config){

			$main::kiriwrite_presmodule->addoption($dbmodule_list{$dbmodule}{Filename}, { Value => $dbmodule_list{$dbmodule}{Filename} , Selected => 1 });

		} else {

 			$main::kiriwrite_presmodule->addoption($dbmodule_list{$dbmodule}{Filename}, { Value => $dbmodule_list{$dbmodule}{Filename} });

		}


	}

	$main::kiriwrite_presmodule->endselectbox();

	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{databaseserver});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("database_server", { Size => 32, MaxLength => 128, Value => $database_server });
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{databaseport});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("database_port", { Size => 5, MaxLength => 5, Value => $database_port });
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{databaseprotocol});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");

	# Check if TCP is being used.

	$main::kiriwrite_presmodule->addselectbox("database_protocol");

	if ($database_protocol eq "tcp"){

		# The TCP protocol is selected so have the TCP option selected.

		$main::kiriwrite_presmodule->addoption("TCP", { Value => "tcp", Selected => 1});

	} else {

		# The TCP protocol is not selected.

		$main::kiriwrite_presmodule->addoption("TCP", { Value => "tcp"});

	} 

	# Check if UDP is being used.

	if ($database_protocol eq "udp"){

		# The UDP protocol is selected so have the UDP option selected.

		$main::kiriwrite_presmodule->addoption("UDP", { Value => "udp", Selected => 1});

	} else {

		# The UDP protocol is not selected.

		$main::kiriwrite_presmodule->addoption("UDP", { Value => "udp"});

	}

	$main::kiriwrite_presmodule->endselectbox();

	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{databasename});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("database_sqldatabase", { Size => 32, MaxLength => 32, Value => $database_sqldatabase });
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{databaseusername});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("database_username", { Size => 16, MaxLength => 16, Value => $database_username });
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{databasepassword});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("database_password", { Size => 16, MaxLength => 64, Password => 1 });
	$main::kiriwrite_presmodule->addtext(" ");
	$main::kiriwrite_presmodule->addcheckbox("database_password_keep", { OptionDescription => "Keep the current password", Checked => 1 });
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{setting}{tableprefix});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("database_tableprefix", { Size => 16, MaxLength => 16, Value => $database_prefix });
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->endtable();

	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{setting}{changesettingsbutton});
	$main::kiriwrite_presmodule->addtext(" | ");
	$main::kiriwrite_presmodule->addreset($main::kiriwrite_lang{common}{restorecurrent});
	$main::kiriwrite_presmodule->addtext(" | ");
	$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=settings", { Text => $main::kiriwrite_lang{setting}->{returnsettingslist} });
	$main::kiriwrite_presmodule->endbox();
	$main::kiriwrite_presmodule->endform();

	return $main::kiriwrite_presmodule->grab();

} 

sub kiriwrite_output_config{
#################################################################################
# kiriwrite_output_config: Outputs the configuration file.			#
#										#
# Usage:									#
#										#
# kiriwrite_output_config(settings);						#
#										#
# settings	Specifies the following settings in any order.			#
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
# OutputModule		Specifies the new output module to use for Kiriwrite.	#
# TextAreaCols		Specifies the width of the text area.			#
# TextAreaRows		Specifies the height of the text area.			#
# PageCount		Specifies the amount of pages to view.			#
# FilterCount		Specifies the amount of filters to view.		#
# TemplateCount		Specifies the amount of templates to view.		#
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

	my ($passedsettings)	= @_;

	# Get the data from the hash.

	my $settings_databasedir		= $passedsettings->{"DatabaseDirectory"};
	my $settings_outputdir			= $passedsettings->{"OutputDirectory"};
	my $settings_imagesuri			= $passedsettings->{"ImagesURIPath"};
	my $settings_datetime			= $passedsettings->{"DateTimeFormat"};
	my $settings_systemlanguage		= $passedsettings->{"SystemLanguage"};
	my $settings_presmodule			= $passedsettings->{"PresentationModule"};
	my $settings_outputmodule		= $passedsettings->{"OutputModule"};
	my $settings_dbmodule			= $passedsettings->{"DatabaseModule"};

	my $settings_textareacols		= $passedsettings->{"TextAreaCols"};
	my $settings_textarearows		= $passedsettings->{"TextAreaRows"};
	my $settings_pagecount			= $passedsettings->{"PageCount"};
	my $settings_filtercount		= $passedsettings->{"FilterCount"};
	my $settings_templatecount		= $passedsettings->{"TemplateCount"};

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
		$settings_imagesuri =~ s/\r//g;
		$settings_imagesuri =~ s/\n//g;

	}

	# Check if the database password value is undefined and if it is then
	# set it blank.

	if (!$settings_database_password){

		$settings_database_password = "";

	}

	# Create the Kiriwrite configuration file layout.

	my $configdata = "[config]\r\n";

	$configdata = $configdata . "directory_data_db = " . $settings_databasedir . "\r\n";
	$configdata = $configdata . "directory_data_output = "  . $settings_outputdir . "\r\n";
	$configdata = $configdata . "directory_noncgi_images = "  . $settings_imagesuri . "\r\n\r\n";

	$configdata = $configdata . "system_language = "  . $settings_systemlanguage . "\r\n";
	$configdata = $configdata . "system_presmodule = "  . $settings_presmodule . "\r\n";
	$configdata = $configdata . "system_dbmodule = "  . $settings_dbmodule . "\r\n";
	$configdata = $configdata . "system_outputmodule = "  . $settings_outputmodule . "\r\n";
	$configdata = $configdata . "system_datetime = "  . $settings_datetime . "\r\n\r\n";

	$configdata = $configdata . "display_textareacols = "  . $settings_textareacols . "\r\n";
	$configdata = $configdata . "display_textarearows = "  . $settings_textarearows . "\r\n";
	$configdata = $configdata . "display_pagecount = " . $settings_pagecount . "\r\n";
	$configdata = $configdata . "display_filtercount = " . $settings_filtercount . "\r\n";
	$configdata = $configdata . "display_templatecount = " . $settings_templatecount . "\r\n\r\n";

	$configdata = $configdata . "database_server = "  . $settings_database_server . "\r\n";
	$configdata = $configdata . "database_port = "  . $settings_database_port . "\r\n";
	$configdata = $configdata . "database_protocol = "  . $settings_database_protocol . "\r\n";
	$configdata = $configdata . "database_sqldatabase = "  . $settings_database_sqldatabase . "\r\n";
	$configdata = $configdata . "database_username = "  . $settings_database_username . "\r\n";
	$configdata = $configdata . "database_password = "  . $settings_database_password . "\r\n";
	$configdata = $configdata . "database_tableprefix = "  . $settings_database_tableprefix . "\r\n\r\n";

	# Open the Kiriwrite configuration file and write the new settings to the
	# configuration file.

	open(my $filehandle_config, "> ", "kiriwrite.cfg");
	print $filehandle_config $configdata;
	close($filehandle_config);

	return;

};

1;