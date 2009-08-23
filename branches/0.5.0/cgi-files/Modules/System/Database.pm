package Modules::System::Database;

use Modules::System::Common;
use strict;
use warnings;
use Exporter;

our @ISA = qw(Exporter);
our @EXPORT = qw(kiriwrite_database_list kiriwrite_database_add kiriwrite_database_edit kiriwrite_database_delete);

sub kiriwrite_database_list{
#################################################################################
# kiriwrite_database_list: Lists the databases available.			#
#										#
# Usage:									#
# 										#
# kiriwrite_database_list();							#
#################################################################################

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

	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databaselist}, { Style => "pageheader" });
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->starttable("", { CellPadding => "5", CellSpacing => "0" });
	$main::kiriwrite_presmodule->startheader();
	$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{database}{databasename}, { Style => "tablecellheader" });
	$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{database}{databasedescription}, { Style => "tablecellheader" });
	$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{database}{databaseoptions}, { Style => "tablecellheader" });
	$main::kiriwrite_presmodule->endheader();

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

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell($table_style_name);

		if (!$database_name){
			$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang->{blank}->{noname});
		} else {
			$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=page&action=view&database=" . $database_filename_friendly, { Text => $database_name });
		}

		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell($table_style_name);

		if (!$database_description){
			$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{blank}{nodescription});
		} else {
			$main::kiriwrite_presmodule->addtext($database_description);
		}

		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell($table_style_name);
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{'script_filename'} . "?mode=db&action=edit&database=" . $database_filename_friendly, { Text => $main::kiriwrite_lang{options}{edit} });
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{'script_filename'} . "?mode=compile&action=compile&type=single&database=" . $database_filename_friendly, { Text => $main::kiriwrite_lang{options}{compile} });
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{'script_filename'} . "?mode=db&action=delete&database=" . $database_filename_friendly, { Text => $main::kiriwrite_lang{options}{delete} });
		$main::kiriwrite_presmodule->endrow();

		$database_count++;
		$nodescription = 0;
		$noname = 0;

	}

	$main::kiriwrite_presmodule->endtable();

	# Disconnect from the database server.

	$main::kiriwrite_dbmodule->disconnect();

	# Check if there are no valid databases are if there is no
	# valid databases then write a message saying that no
	# valid databases are available.

	if ($database_count eq 0){

		$main::kiriwrite_presmodule->clear();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databaselist}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startbox("errorbox");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{nodatabasesavailable});
		$main::kiriwrite_presmodule->endbox();

	}

	# Check if any databases with problems have appeared and if they
	# have, print out a message saying which databases have problems.

	if (@permissions_list){

		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databaseinvalidpermissions}, { Style => "smallpageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databaseinvalidpermissionstext});
		$main::kiriwrite_presmodule->addlinebreak();

		foreach $data_file (@permissions_list){
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addtext($data_file);
		}

		$main::kiriwrite_presmodule->addlinebreak();

	}

	if (@error_list){

		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databaseerrors}, { Style => "smallpageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databaseerrorstext});
		$main::kiriwrite_presmodule->addlinebreak();

		foreach $data_file (@error_list){
			$main::kiriwrite_presmodule->addlinebreak();
			$main::kiriwrite_presmodule->addtext($data_file);
		}

		$main::kiriwrite_presmodule->addlinebreak();

	}

	return $main::kiriwrite_presmodule->grab();	# Return to the main part of the script with the processed information.

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

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		my $database_name_final = $database_name;

		# Create the database.

		$main::kiriwrite_dbmodule->adddatabase({ DatabaseFilename => $database_filename, DatabaseName => $database_name, DatabaseDescription => $database_description, DatabaseNotes => $database_notes, DatabaseCategories => $database_categories, VersionMajor => $main::kiriwrite_version{"major"}, VersionMinor => $main::kiriwrite_version{"minor"}, VersionRevision => $main::kiriwrite_version{"revision"} });

		# Check if any errors have occured.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseExists"){

			# A database with the filename given already exists, so
			# return an error.

			kiriwrite_error("fileexists");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error with
			# the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{adddatabase}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{database}{databaseadded} , $database_name_final));
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=db", { Text => $main::kiriwrite_lang{database}{databaselistreturnlink} });

		return $main::kiriwrite_presmodule->grab();

	}

	# There is confirm value is not 1, so write a form for creating a database to
	# store pages in.

	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{adddatabase}, { Style => "pageheader" });
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
	$main::kiriwrite_presmodule->startbox();	
	$main::kiriwrite_presmodule->addhiddendata("mode", "db");
	$main::kiriwrite_presmodule->addhiddendata("action", "new");
	$main::kiriwrite_presmodule->addhiddendata("confirm", "1");
	$main::kiriwrite_presmodule->endbox();
	$main::kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });

	$main::kiriwrite_presmodule->startheader();
	$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{setting}, { Style => "tablecellheader"});
	$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{value}, { Style => "tablecellheader"});
	$main::kiriwrite_presmodule->endheader();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databasename});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("databasename", { Size => 64, MaxLength => 256 });
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databasedescription});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("databasedescription", { Size => 64, MaxLength => 512 });
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databasecategories});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("databasecategories", { Size => 64, MaxLength => 512 });
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databasenotes});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addtextbox("databasenotes", { Columns => $main::kiriwrite_config{"display_textareacols"}, Rows => $main::kiriwrite_config{"display_textarearows"}, WordWrap => 0 });
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->startrow();
	$main::kiriwrite_presmodule->addcell("tablecell1");
	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databasefilename});
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->addcell("tablecell2");
	$main::kiriwrite_presmodule->addinputbox("databasefilename", { Size => 32, MaxLength => 32 });
	$main::kiriwrite_presmodule->startlist();
	$main::kiriwrite_presmodule->additem($main::kiriwrite_lang{database}{adddatabaseautogenerate});
	$main::kiriwrite_presmodule->additem($main::kiriwrite_lang{database}{adddatabasenoextensions});
	$main::kiriwrite_presmodule->additem($main::kiriwrite_lang{database}{adddatabasecharacterlength});
	$main::kiriwrite_presmodule->additem($main::kiriwrite_lang{database}{adddatabasecharacters});
	$main::kiriwrite_presmodule->endlist();
	$main::kiriwrite_presmodule->endcell();
	$main::kiriwrite_presmodule->endrow();

	$main::kiriwrite_presmodule->endtable();
	$main::kiriwrite_presmodule->startbox();
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{database}{adddatabasebutton});
	$main::kiriwrite_presmodule->addtext("|");
	$main::kiriwrite_presmodule->addreset($main::kiriwrite_lang{database}{clearvaluesbutton});
	$main::kiriwrite_presmodule->addtext("| ");
	$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=db", { Text => $main::kiriwrite_lang{database}{databaselistreturnlink} });
	$main::kiriwrite_presmodule->endbox();
	$main::kiriwrite_presmodule->endform();

	# Exit the subroutine taking the data in the pagadata variable with it.

	return $main::kiriwrite_presmodule->grab();

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

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Get the database.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database_shortname });

		# Check if any errors had occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# FIX THIS!! >O

		$main::kiriwrite_dbmodule->editdatabase({ DatabaseNewFilename => $database_newfilename, DatabaseName => $database_newname , DatabaseDescription => $database_newdescription , DatabaseNotes => $database_notes, DatabaseCategories => $database_categories });

		# Check if any errors had occured while using the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "DataDirInvalidPermissions"){

			# The database directory has invalid permissions set, so
			# return an error.

			kiriwrite_error("datadirectoryinvalidpermissions");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "DatabaseExists"){

			# A database already exists with the new filename, so
			# return an error.

			kiriwrite_error("databasealreadyexists");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error with
			# the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Disconnect from the server.

		$main::kiriwrite_dbmodule->disconnect();

		# Write out a message saying that the database has been updated.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{editeddatabase}, { Style => "pageheader" } );
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{database}{databaseupdated}, $database_newname));
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=db", { Text => $main::kiriwrite_lang{database}{databaselistreturnlink} });

		return $main::kiriwrite_presmodule->grab();

	} else {

		my (%database_info);

		# Check if the database filename given is valid and return an error
		# if it isn't.

		# Connect to the database server.

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Select the database.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database_shortname });

		# Check if any errors had occured while setting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist, so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet"){

			# The database has invalid permissions set, so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Get the database information.

		%database_info = $main::kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors had occured while getting the database
		# information.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error and
			# also the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Get the values needed from the kiriwrite_database_info table.

		my $database_oldname 		= $database_info{"DatabaseName"};
		my $database_olddescription	= $database_info{"Description"};
		my $database_notes		= $database_info{"Notes"};
		my $database_categories		= $database_info{"Categories"};

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		# Print out the form for editing a database's settings.

		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{database}{editdatabase}, $database_oldname), { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addhiddendata("mode", "db");
		$main::kiriwrite_presmodule->addhiddendata("action", "edit");
		$main::kiriwrite_presmodule->addhiddendata("database", $database_shortname);
		$main::kiriwrite_presmodule->addhiddendata("confirm", "1");
		$main::kiriwrite_presmodule->endbox();

		$main::kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });
		$main::kiriwrite_presmodule->startheader();
		$main::kiriwrite_presmodule->addheader("Setting", { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->addheader("Value", { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->endheader();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databasename});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("databasename", { Size => 64, MaxLength => 256, Value => $database_oldname } );
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databasedescription});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("databasedescription", { Size => 64, MaxLength => 512, Value => $database_olddescription } );
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databasecategories});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("databasecategories", { Size => 64, MaxLength => 512, Value => $database_categories } );
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databasenotes});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addtextbox("databasenotes", { Columns => $main::kiriwrite_config{"display_textareacols"}, Rows => $main::kiriwrite_config{"display_textarearows"}, Value => $database_notes } );
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{databasefilename});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("databasefilename", { Size => 32, MaxLength => 32, Value => $database_shortname } );
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->endtable();

		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{database}{editdatabasebutton});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addreset($main::kiriwrite_lang{common}{restorecurrent});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=db", { Text => $main::kiriwrite_lang{database}{databaselistreturnlink} });
		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->endform();

		return $main::kiriwrite_presmodule->grab();

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

	$main::kiriwrite_dbmodule->connect();

	# Check if any errors occured while connecting to the database server.

	if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

		# A database connection error has occured so return
		# an error.

		kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

	}

	# Check if the database filename given is valid and return an error
	# if it isn't.

	kiriwrite_variablecheck($database_filename, "filename", "", 0);

	# Check if the request to delete a database has been confirmed. If it has, 
	# then delete the database itself.

	if ($database_confirm eq 1){
		# There is a value in the confirm variable of the HTTP query.

		# Select the database to delete and get the database name.

		$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database_filename });

		# Check if any error occured while selecting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet") {

			# The database has invalid permissions set so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		my %database_info	= $main::kiriwrite_dbmodule->getdatabaseinfo();

		# Check if any errors have occured while getting the database
		# name.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

			# A database error has occured so return an error with
			# the extended error information.

			kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		my $database_name = $database_info{"DatabaseName"};

		# Delete the selected database.

		$main::kiriwrite_dbmodule->deletedatabase({ DatabaseName => $database_filename });

		# Check if any error occured while deleting the database.

		if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

			# The database does not exist so return an error.

			kiriwrite_error("databasemissingfile");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet") {

			# The database has invalid permissions set so return
			# an error.

			kiriwrite_error("databaseinvalidpermissions");

		}

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		# Write a message saying that the database has been deleted.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{deleteddatabase}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{database}{deleteddatabasemessage}, $database_name));
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=db", { Text => $main::kiriwrite_lang{database}{databaselistreturnlink} }); 

		return $main::kiriwrite_presmodule->grab();

	}

	# The action has not been confirmed, so write out a form asking the 
	# user to confirm.

	# Get the database name.

	$main::kiriwrite_dbmodule->selectdb({ DatabaseName => $database_filename });

	# Check if any error occured while selecting the database.

	if ($main::kiriwrite_dbmodule->geterror eq "DoesNotExist"){

		# The database does not exist so return an error.

		kiriwrite_error("databasemissingfile");

	} elsif ($main::kiriwrite_dbmodule->geterror eq "InvalidPermissionsSet") {

		# The database has invalid permissions set so return
		# an error.

		kiriwrite_error("databaseinvalidpermissions");


	}

	# Check if any errors have occured.

	my %database_info	= $main::kiriwrite_dbmodule->getdatabaseinfo();

	if ($main::kiriwrite_dbmodule->geterror eq "DatabaseError"){

		# A database error has occured so return an error with
		# the extended error information.

		kiriwrite_error("databaseerror", $main::kiriwrite_dbmodule->geterror(1));

	}

	my $database_name = $database_info{"DatabaseName"};

	# Disconnect from the database server.

	$main::kiriwrite_dbmodule->disconnect();

	# Write out the form to ask the user to confirm the deletion of the 
	# selected database.

	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{database}{deletedatabase}, { Style => "pageheader" });
	$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
	$main::kiriwrite_presmodule->startbox();
	$main::kiriwrite_presmodule->addhiddendata("mode", "db");
	$main::kiriwrite_presmodule->addhiddendata("action", "delete");
	$main::kiriwrite_presmodule->addhiddendata("database", $database_filename);
	$main::kiriwrite_presmodule->addhiddendata("confirm", "1");
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{database}{deletedatabasemessage}, $database_name));
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{database}{deletedatabasebutton});
	$main::kiriwrite_presmodule->addtext(" | ");
	$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=db", { Text => $main::kiriwrite_lang{database}{deletedatabasereturn} });
	$main::kiriwrite_presmodule->endbox();
	$main::kiriwrite_presmodule->endform();

	return $main::kiriwrite_presmodule->grab();

}

1;