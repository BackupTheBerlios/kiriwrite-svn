#################################################################################
# Kiriwrite Database Module - SQLite Database Module (SQLite.pm)		#
# Database module for mainipulating SQLite databases in the database directory. #
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

package Kiriwrite::Database::SQLite;

# Enable strict and use warnings.

use strict;
use warnings;

# Load the following Perl modules.

use DBI qw(:sql_types);

# Set the following values.

our $VERSION 	= "0.1.0";
my ($options, %options);
my $database_handle;
my $statement_handle;
my $error = "";
my $errorext = "";
my $database_filename;
my $second_database_filename;
my $second_database_handle;
my $second_statement_handle;
my $templatedb_loaded = 0;
my $templatedb_exists = 1;
my $template_statement_handle;
my $template_database_handle;
my $filterdb_loaded = 0;
my $filterdb_exists = 1;
my $filterdb_statement_handle;
my $filterdb_database_handle;


#################################################################################
# Generic Subroutines.								#
#################################################################################

sub new{
#################################################################################
# new: Create an instance of Kiriwrite::Database::SQLite			#
# 										#
# Usage:									#
#										#
# $dbmodule = Kiriwrite::Database::SQLite->new();				#
#################################################################################
	
	# Get the perl module name.

	my $class = shift;
	my $self = {};

	return bless($self, $class);

}

sub loadsettings{
#################################################################################
# loadsettings: Loads settings into the SQLite database module			#
#										#
# Usage:									#
#										#
# $dbmodule->loadsettings(Directory, options);					#
#										#
# options	Specifies the following options (in any order).			#
#										#
# Directory	Specifies the directory to use for getting databases.		#
# DateTime	Specifies the date and time format to use.			#
# Server	Specifies the server to use.					#
# Database	Specifies the database to use.					#
# Username	Specifies the username to use.					#
# Password	Specifies the password to use.					#
# HashType	Specifies the password hash type to use.			#
# Port		Specifies the server port to use.				#
# Protocol	Specifies the protocol to use.					#
# TablePrefix	Specifies the table prefix to use.				#
#################################################################################

	# Get the data passed to the subroutine.

	my $class = shift;
	my ($passedoptions)	= @_;

	# Add the directory setting to the list of options (as it's the only
	# one needed for this database module).

	%options = (
		"Directory" 	=> $passedoptions->{"Directory"},
		"DateTime"	=> $passedoptions->{"DateTime"},
	);

}

sub convert{
#################################################################################
# convert: Converts data into SQL formatted data.				#
#										#
# Usage:									#
#										#
# $dbmodule->convert(data);							#
#										#
# data		Specifies the data to convert.					#
#################################################################################

	# Get the data passed to the subroutine.

	my $class	= shift;
	my $data	= shift;

	if (!$data){
		$data = "";
	}

	$data =~ s/'/''/g;
	$data =~ s/\b//g;

	return $data;

}

sub dateconvert{
#################################################################################
# dateconvert: Converts a SQL date into a proper date.				#
#										#
# Usage:									#
#										#
# $dbmodule->dateconvert(date);							#
#										#
# date		Specifies the date to convert.					#
#################################################################################

	# Get the date passed to the subroutine.

	my $class 	= shift;
	my $data	= shift;

	# Convert the date given into the proper date.

	# Create the following varialbes to be used later.

	my $date;
	my $time;
	my $day;
	my $day_full;
	my $month;
	my $month_check;
	my $month_full;
	my $year;
	my $year_short;
	my $hour;
	my $hour_full;
	my $minute;
	my $minute_full;
	my $second;
	my $second_full;
	my $seek = 0;
	my $timelength;
	my $datelength;
	my $daylength;
	my $secondlength;
	my $startchar = 0;
	my $char;
	my $length;
	my $count = 0;

	# Split the date and time.

	$length = length($data);

	if ($length > 0){

		do {

			# Get the character and check if it is a space.

			$char = substr($data, $seek, 1);

			if ($char eq ' '){

				# The character is a space, so get the date and time.

				$date 		= substr($data, 0, $seek);
				$timelength	= $length - $seek - 1;
				$time 		= substr($data, $seek + 1, $timelength);

			}

			$seek++;

		} until ($seek eq $length);

		# Get the year, month and date.

		$length = length($date);
		$seek = 0;

		do {

			# Get the character and check if it is a dash.

			$char = substr($date, $seek, 1);

			if ($char eq '-'){

				# The character is a dash, so get the year, month or day.

				$datelength = $seek - $startchar;

				if ($count eq 0){

					# Get the year from the date.

					$year		= substr($date, 0, $datelength) + 1900;
					$startchar	= $seek;
					$count = 1;

					# Get the last two characters to get the short year
					# version.

					$year_short	= substr($year, 2, 2);

				} elsif ($count eq 1){

					# Get the month and day from the date.

					$month 	= substr($date, $startchar + 1, $datelength - 1) + 1;

					# Check if the month is less then 10, if it is
					# add a zero to the value.

					if ($month < 10){

						$month_full = '0' . $month;

					} else {

						$month_full = $month;

					}

					$startchar	= $seek;
					$count = 2;

					$daylength	= $length - $seek + 1;
					$day		= substr($date, $startchar + 1, $daylength);

					# Check if the day is less than 10, if it is
					# add a zero to the value.

					if ($day < 10){

						$day_full 	= '0' . $day;

					} else {

						$day_full	= $day;

					}

				}

			}

			$seek++;

		} until ($seek eq $length);

		# Get the length of the time value and reset certain
		# values to 0.

		$length = length($time);
		$seek = 0;
		$count = 0;
		$startchar = 0;

		do {

			# Get the character and check if it is a colon.

			$char = substr($time, $seek, 1);

			if ($char eq ':'){

				# The character is a colon, so get the hour, minute and day.

				$timelength = $seek - $startchar;

				if ($count eq 0){

					# Get the hour from the time.

					$hour = substr($time, 0, $timelength);
					$count = 1;
					$startchar = $seek;

					# If the hour is less than ten then add a
					# zero.

					if ($hour < 10){

						$hour_full = '0' . $hour;

					} else {

						$hour_full = $hour;

					}

				} elsif ($count eq 1){

					# Get the minute and second from the time.

					$minute = substr($time, $startchar + 1, $timelength - 1);
					$count = 2;
						
					# If the minute is less than ten then add a
					# zero.

					if ($minute < 10){

						$minute_full = '0' . $minute;

					} else {

						$minute_full = $minute;

					}

					$startchar = $seek;

					$secondlength = $length - $seek + 1;
					$second = substr($time, $startchar + 1, $secondlength);
					
					# If the second is less than ten then add a
					# zero.

					if ($second < 10){

						$second_full = '0' . $second;

					} else {

						$second_full = $second;

					}

				}

			}

			$seek++;

		} until ($seek eq $length);

		# Get the setting for displaying the date and time.

		$data = $options{"DateTime"};

		# Process the setting for displaying the date and time
		# using regular expressions

		$data =~ s/DD/$day_full/g;
		$data =~ s/D/$day/g;
		$data =~ s/MM/$month_full/g;
		$data =~ s/M/$month/g;
		$data =~ s/YY/$year/g;
		$data =~ s/Y/$year_short/g;

		$data =~ s/hh/$hour_full/g;
		$data =~ s/h/$hour/g;
		$data =~ s/mm/$minute_full/g;
		$data =~ s/m/$minute/g;
		$data =~ s/ss/$second_full/g;
		$data =~ s/s/$second/g;

	}

	return $data;

}

sub geterror{
#################################################################################
# geterror: Gets the error message (or extended error message).			#
#										#
# Usage:									#
#										#
# $dbmodule->geterror(extended);						#
#										#
# Extended	Specifies if the extended error should be retrieved.		#
#################################################################################

	# Get the data passed to the subroutine.

	my $class	= shift;
	my $extended	= shift;

	if (!$extended){
		$extended = 0;
	}

	if (!$errorext){
		$errorext = "";
	}

	if (!$error){
		$error = "";
	}

	# Check to see if extended information should be returned.

	if ($extended eq 1){

		# Extended information should be returned.

		return $errorext;

	} else {

		# Basic information should be returned.

		return $error;

	}

}

sub dbpermissions{
#################################################################################
# dbpermissions: Check if the permissions for the database are valid.		#
#										#
# Usage:									#
#										#
# $database->dbpermissions(dbname, read, write);				#
#										#
# dbname	Specifies the database name to check.				#
# read		Check to see if the database can be read.			#
# write		Check to see if the database can be written.			#
#################################################################################

	# Get the database name, read setting and write setting.

	my ($class, $dbname, $readper, $writeper)	= @_;

	# Check if the database can be read.

	if ($readper){

		if (-r $options{"Directory"} . '/' . $dbname . ".db.sqlite"){

			# The database can be read.

		} else {

			# The database cannot be read, so return a value
			# of 1.

			return 1;

		}

	}

	# Check if the database can be written.

	if ($writeper){

		if (-w $options{"Directory"} . '/' . $dbname . ".db.sqlite"){

			# The database can be read.

		} else {

			# The database cannot be read, so return a value
			# of 1.

			return 1;

		}

	}

	# No errors have occured while checking so return a value
	# of 0.

	return 0;

}

sub dbexists{
#################################################################################
# dbexists: Check if the database exists.					#
#										#
# Usage:									#
#										#
# $dbmodule->dbexists(dbname);							#
#										#
# dbname	Specifies the database name to check.				#
#################################################################################

	# Get the value that was passed to the subroutine.

	my $class	= shift;
	my ($filename)  = @_;

	# Check if the filename exists, if it does, return a value of 1, else
	# return a value of 0, meaning that the file was not found.

	if (-e $options{"Directory"} . '/' . $filename . ".db.sqlite"){

		# Specified file does exist so return a value of 0.

		return 0;

	} else {

		# Specified file does not exist so return a value of 1.

		return 1;

	}

}

#################################################################################
# Database Subroutines.								#
#################################################################################

sub getdblist{
#################################################################################
# getdblist: Gets the list of available databases.				#
#										#
# Usage:									#
# 										#
# $dbmodule->getdblist();							#
#################################################################################

	# Get the list of databases.

	my @data_directory;
	my @data_directory_final;
	my $database;
	my $database_filename_length;
	my $database_filename_friendly;

	# Check if the database directory has valid permission settings.

	if (-e $options{"Directory"}){

		# The database directory does exist. So check if
                # the permission settings are valid.

		if (-r $options{"Directory"}){

			# The permission settings for reading the directory
			# are valid.

		} else {

			# The permission settings for reading the directory
			# are invalid so return an error value.

			$error = "DataDirInvalidPermissions";
			return;

		}

	} else {

		# The database directory does not exist, so return an
		# error value.

		$error = "DataDirMissing";
		return;

	}

	opendir(DATADIR, $options{"Directory"});
	@data_directory = grep /m*\.db.sqlite$/, readdir(DATADIR);
	closedir(DATADIR);

	# Process the list of databases.

	foreach $database (@data_directory){

		$database =~ s/.db.sqlite$//og;
		$database_filename_friendly = $database;

		#$database_filename_length = length($database);
		#$database_filename_friendly = substr($database, 0, $database_filename_length - 10);
		push(@data_directory_final, $database_filename_friendly);

	}

	# Return the list of databases.

	return @data_directory_final;

}

sub getdatabaseinfo{
#################################################################################
# getdatabaseinfo: Get information about the database.				#
#										#
# Usage:									#
#										#
# $dbmodule->getdatabaseinfo();							#
#################################################################################

	# Get the database information.

	my $class = shift;
	my ($databaseinfo, %databaseinfo);
	my ($sqldata, @sqldata);

	$error = "";
	$errorext = "";

	$statement_handle = $database_handle->prepare('SELECT name, description, notes, categories, kiriwrite_version_major, kiriwrite_version_minor, kiriwrite_version_revision FROM kiriwrite_database_info LIMIT 1') or (
		$error = "DatabaseError", $errorext = $database_handle->errstr, return
	);
	$statement_handle->execute();

	@sqldata = $statement_handle->fetchrow_array();

	# Process the database information into a hash.

	%databaseinfo = (
		"DatabaseName"	=> $sqldata[0],
		"Description"	=> $sqldata[1],
		"Notes"		=> $sqldata[2],
		"Categories"	=> $sqldata[3],
		"Major"		=> $sqldata[4],
		"Minor"		=> $sqldata[5],
		"Revision"	=> $sqldata[6]
	);

	$statement_handle->finish();
	undef $statement_handle;

	return %databaseinfo;

}

sub getseconddatabaseinfo{
#################################################################################
# getseconddatabaseinfo: Get information about the database that pages will be	#
# moved or copied to.								#
#										#
# Usage:									#
#										#
# $dbmodule->getseconddatabaseinfo();						#
#################################################################################

	# Get the database information.

	my $class = shift;
	my ($databaseinfo, %databaseinfo);
	my ($sqldata, @sqldata);

	$error = "";
	$errorext = "";

	$second_statement_handle = $second_database_handle->prepare('SELECT name, description, notes, categories, kiriwrite_version_major, kiriwrite_version_minor, kiriwrite_version_revision FROM kiriwrite_database_info LIMIT 1') or (
		$error = "DatabaseError", $errorext = $second_database_handle->errstr, return
	);
	$second_statement_handle->execute();

	@sqldata = $second_statement_handle->fetchrow_array();

	# Process the database information into a hash.

	%databaseinfo = (
		"DatabaseName"	=> $sqldata[0],
		"Description"	=> $sqldata[1],
		"Notes"		=> $sqldata[2],
		"Categories"	=> $sqldata[3],
		"Major"		=> $sqldata[4],
		"Minor"		=> $sqldata[5],
		"Revision"	=> $sqldata[6]
	);

	$second_statement_handle->finish();
	undef $second_statement_handle;

	return %databaseinfo;

}

sub adddatabase{
#################################################################################
# adddatabase: Adds a Kiriwrite database.					#
#										#
# Usage:									#
#										#
# $dbmodule->adddatabase(options);						#
#										#
# options	Specifies the following options in any order.			#
#										#
# DatabaseFilename	Specifies the database file/shortname to use.		#
# DatabaseName		Specifies the database name to use.			#
# DatabaseDescription	Specifies the database description to use.		#
# DatabaseNotes		Specifies the database notes to use.			#
# DatabaseCategories	Specifies the database categories to use.		#
# VersionMajor		Specifies the major version.				#
# VersionMinor		Specifies the minor version.				#
# VersionRevision	Specifies the revision version.				#
#################################################################################

	# Get the database that was passed to the subroutine.

	$error	= "";
	$errorext = "";

	my $class	= shift;
	my ($passedoptions) = @_;

	my $dbfilename		= $passedoptions->{"DatabaseFilename"};
	my $dbname		= $passedoptions->{"DatabaseName"};
	my $dbdescription	= $passedoptions->{"DatabaseDescription"};
	my $dbnotes		= $passedoptions->{"DatabaseNotes"};
	my $dbcategories	= $passedoptions->{"DatabaseCategories"};
	my $dbmajorver		= $passedoptions->{"VersionMajor"};
	my $dbminorver		= $passedoptions->{"VersionMinor"};
	my $dbrevisionver	= $passedoptions->{"VersionRevision"};

	# Check if the database with the filename given already exists.

	my $database_exists	= $class->dbexists($dbfilename);

	if ($database_exists eq 0){

		# The database filename exists so set the error value.

		$error = "DatabaseExists";
		return;

	}

	# Create the database structure.

	$database_handle	= DBI->connect("dbi:SQLite:dbname=" . $options{"Directory"} . '/' . $dbfilename . ".db.sqlite");
	$database_handle->{unicode} = 1;
	$statement_handle		= $database_handle->prepare('CREATE TABLE kiriwrite_database_info(
			name varchar(256) primary key, 
			description varchar(512), 
			notes text, 
			categories varchar(512), 
			kiriwrite_version_major int(4), 
			kiriwrite_version_minor int(4), 
			kiriwrite_version_revision int(4)
	)') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	$statement_handle 	= $database_handle->prepare('CREATE TABLE kiriwrite_database_pages(
			filename varchar(256) primary key, 
			pagename varchar(512), 
			pagedescription varchar(512), 
			pagesection varchar(256),
			pagetemplate varchar(64),
			pagedata text,
			pagesettings int(1),
			lastmodified datetime
	)') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	# Convert the values into SQL query formatted values and add an entry
	# to the kiriwrite_database_info table.

	$statement_handle = $database_handle->prepare('INSERT INTO kiriwrite_database_info (name, description, notes, categories, kiriwrite_version_major, kiriwrite_version_minor, kiriwrite_version_revision) VALUES(
		\'' . $class->convert($dbname) . '\',
		\'' . $class->convert($dbdescription) . '\',
		\'' . $class->convert($dbnotes) . '\',
		\'' . $class->convert($dbcategories) . '\',
		\'' . $class->convert($dbmajorver) . '\',
		\'' . $class->convert($dbminorver) . '\',
		\'' . $class->convert($dbrevisionver) . '\'
	)') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

}

sub editdatabase{
#################################################################################
# editdatabase: Edits a Kiriwrite Database.					#
#										#
# Usage:									#
#										#
# $dbmodule->editdatabase(options);						#
#										#
# options		Specifies the following options in any order.		#
#										#
# NewDatabaseFilename	Specifies the new database filename to use.		#
# DatabaseName		Specifies the new database name.			#
# DatabaseDescription	Specifies the new database description.			#
# DatabaseNotes		Specifies the new database notes.			#
# DatabaseCategories	Specifies the new database categories.			#
#################################################################################

	$error 		= "";
	$errorext 	= "";

	my $class	= shift;
	my ($passedoptions) = @_;

	my $dbnewfilename	= $passedoptions->{"DatabaseNewFilename"};
	my $dbname		= $passedoptions->{"DatabaseName"};
	my $dbdescription	= $passedoptions->{"DatabaseDescription"};
	my $dbnotes		= $passedoptions->{"DatabaseNotes"};
	my $dbcategories	= $passedoptions->{"DatabaseCategories"};

	# Check if a new database filename has been specified and if a
	# new database filename has been specified then change the
	# database filename.

	if ($database_filename ne $dbnewfilename){

		# A new database filename has been given so check if the output
		# directory has write access.

		if (-r $options{"Directory"}){
			
			# The directory is readable.

		} else {

			# The directory is not readable so set the error value.

			$error = "DataDirInvalidPermissions";

			return;

		}

		if (-w $options{"Directory"}){

			# The directory is writeable.

		} else {

			# The directory is not writeable so set the error value.

			$error = "DataDirInvalidPermissions";

			return;

		}

		# Check if a database filename already exists before using the
		# new filename.

		my $database_newexists		= $class->dbexists($dbnewfilename);

		if ($database_newexists eq 0){

			# The database filename exists so set the error value.

			$error = "DatabaseExists";
			return;

		}

		# Check if the database can be renamed (has write access).

		my $database_permissions	= $class->dbpermissions($database_filename, 1, 1);

		if ($database_permissions eq 1){

			# The database filename exists so set the error value.

			$error = "InvalidPermissionsSet";
			return;

		}

		# "Disconnect" from the database.

		$database_handle->disconnect();

		# Rename the database.

		($database_filename)	= $database_filename =~ /^([a-zA-Z0-9.]+)$/;
		($dbnewfilename)	= $dbnewfilename =~ /^([a-zA-Z0-9.]+)$/;

		rename($options{"Directory"} . '/' . $database_filename . '.db.sqlite', $options{"Directory"} . '/' . $dbnewfilename . '.db.sqlite');

		# Reload the database from the new filename.

		$database_handle = DBI->connect("dbi:SQLite:dbname=" . $options{"Directory"} . '/' . $dbnewfilename . ".db.sqlite");
		$database_handle->{unicode} = 1;
		$database_filename = $dbnewfilename;

	}

	# Check if the database can be altered with the new data.

	my $database_permissions	= $class->dbpermissions($database_filename, 1, 1);

	if ($database_permissions eq 1){

		# The database filename exists so set the error value.

		$error = "InvalidPermissionsSet";
		return;

	}

	# Get the current database information.

	$statement_handle = $database_handle->prepare('SELECT name FROM kiriwrite_database_info LIMIT 1') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	my @database_oldinfo	= $statement_handle->fetchrow_array();

	my $dboldname		= $database_oldinfo[0];

	# Update the database information.

	$statement_handle = $database_handle->prepare('UPDATE kiriwrite_database_info SET name = \'' . $class->convert($dbname) . '\',
	description = \'' . $class->convert($dbdescription) . '\',
	notes = \'' . $class->convert($dbnotes) . '\',
	categories = \'' . $class->convert($dbcategories) . '\'') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	undef $statement_handle;
	return;

}

sub deletedatabase{
#################################################################################
# deletedatabase: Deletes a Kiriwrite database.					#
#										#
# Usage:									#
#										#
# $dbmodule->deletedatabase(options);						#
#										#
# options	Specifies the following options in any order.			#
#										#
# DatabaseName	Specifies the Kiriwrite database to delete.			#
#################################################################################

	$error		= "";
	$errorext	= "";

	# Get the database filename.

	my $class		= shift;
	my ($passedoptions)	= shift;

	my $databasename	= $passedoptions->{"DatabaseName"};

	# Check if the database exists.

	my $database_exists		= $class->dbexists($databasename);

	if ($database_exists eq 1){

		# The database does not exist so set the error value.

		$error = "DoesNotExist";
		return;

	}

	# Check if the database permissions are valid.

	my $database_permissions	= $class->dbpermissions($databasename);

	if ($database_permissions eq 1){

		# The database permissions are invalid so set the error
		# value.

		$error = "InvalidPermissionsSet";
		return;

	}

	# Delete the database.

	($databasename)	= $databasename	=~ /^([a-zA-Z0-9.]+)$/;

	unlink($options{"Directory"} . '/' . $databasename . '.db.sqlite');

}

sub selectdb{
#################################################################################
# selectdb: Selects the Kiriwrite database.					#
#										#
# Usage:									#
#										#
# $dbmodule->connect(options);							#
#										#
# options	Specifies the following options in any order.			#
#										#
# DatabaseName	Specifies the Kiriwrite database to use.			#
#################################################################################

	# Get the database name.

	$error = "";
	$errorext = "";

	my $class = shift;
	my ($passedoptions) = @_;
	my (%database, $database);

	my $dbname = $passedoptions->{"DatabaseName"};

	# Check if the database exists.

	my $database_exists = $class->dbexists($dbname);

	if ($database_exists eq 1){

		# The database does not exist so return an error value
		# saying that the database does not exist.

		$error = "DoesNotExist";

		return;

	}

	# Check if the database has valid permissions set.

	my $database_permissions = $class->dbpermissions($dbname, 1, 0);

	if ($database_permissions eq 1){

		# The database has invalid permissions set so return
		# an error value saying that the database has invalid
		# permissions set.

		$error = "InvalidPermissionsSet";
		
		return;

	}

	# Connect to the database.

	$database_handle = DBI->connect("dbi:SQLite:dbname=" . $options{"Directory"} . '/' . $dbname . ".db.sqlite");
	$database_handle->{unicode} = 1;
	$database_filename = $dbname;

}

sub selectseconddb{
#################################################################################
# selectseconddb: Selects a second Kiriwrite database for moving and copying 	#
# pages to.									#
#										#
# Usage:									#
#										#
# $dbmodule->selectseconddb(options);						#
#										#
# options	Specifies the following options in any order.			#
#										#
# DatabaseName	Specifies the Kiriwrite database to use.			#
#################################################################################

	# Get the database name.

	$error = "";
	$errorext = "";

	my $class = shift;
	my ($passedoptions) = @_;
	my (%database, $database);

	my $dbname = $passedoptions->{"DatabaseName"};

	# Check if the database exists.

	my $database_exists = $class->dbexists($dbname);

	if ($database_exists eq 1){

		# The database does not exist so return an error value
		# saying that the database does not exist.

		$error = "DoesNotExist";

		return;

	}

	# Check if the database has valid permissions set.

	my $database_permissions = $class->dbpermissions($dbname, 1, 0);

	if ($database_permissions eq 1){

		# The database has invalid permissions set so return
		# an error value saying that the database has invalid
		# permissions set.

		$error = "InvalidPermissionsSet";
		
		return;

	}

	# Connect to the database.

	$second_database_handle = DBI->connect("dbi:SQLite:dbname=" . $options{"Directory"} . '/' . $dbname . ".db.sqlite");
	$second_database_handle->{unicode} = 1;
	$second_database_filename = $dbname;	

}

#################################################################################
# Page subroutines.								#
#################################################################################

sub getpagelist{
#################################################################################
# getpagelist: Gets the list of pages from the database.			#
#										#
# Usage:									#
#										#
# $dbmodule->getpagelist();							#
#################################################################################

	$error = "";
	$errorext = "";

	my $class	= shift;
	
	$statement_handle	= $database_handle->prepare('SELECT filename FROM kiriwrite_database_pages') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	my @database_pagefilenames;
	my @database_pagefilenames_final;

	# Process the collected pages.

	while (@database_pagefilenames = $statement_handle->fetchrow_array){

		# Add each page to the list of pages in the database.

		push(@database_pagefilenames_final, $database_pagefilenames[0]);

	}

	undef $statement_handle;
	return @database_pagefilenames_final;

}

sub getpageinfo{
#################################################################################
# getpageinfo: Gets the page information from the filename passed.		#
#										#
# Usage:									#
#										#
# $dbmodule->getpageinfo(options);						#
#										#
# options	Specifies the following options in any order.			#
#										#
# PageFilename	Specifies the page filename to get the page information from.	#
# Reduced	Specifies if the reduced version of the page information should #
#		be retrieved.							#
#################################################################################

	$error = "";
	$errorext = "";

	my $class		= shift;
	my ($passedoptions)	= shift;
	my (%database_page, $database_page);
	my ($pagefilename, $pagename, $pagedescription, $pagesection, $pagetemplate, $pagedata, $pagesettings, $pagelastmodified);

	my @data_page;
	my $page_found = 0;

	# Get the page from the database.

	my $page_filename	= $passedoptions->{"PageFilename"};
	my $page_reduced	= $passedoptions->{"Reduced"};

	if (!$page_reduced){

		$page_reduced = 0;

	}

	if ($page_reduced eq 1){

		$statement_handle	= $database_handle->prepare('SELECT filename, pagename, pagedescription, lastmodified FROM kiriwrite_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );

		$statement_handle->execute();

		# Check if the page exists in the database.

		while (@data_page = $statement_handle->fetchrow_array()){
	
			# Get the values from the array.
	
			$pagefilename 		= $data_page[0];
			$pagename		= $data_page[1];
			$pagedescription	= $data_page[2];
			$pagelastmodified	= $data_page[3];
	
			# Put the values into the page hash.
	
			%database_page = (
				"PageFilename" 		=> $pagefilename,
				"PageName"		=> $pagename,
				"PageDescription"	=> $pagedescription,
				"PageLastModified"	=> $class->dateconvert($pagelastmodified),
			);
	
			$page_found = 1;
	
		}


	} else {
		
		$statement_handle	= $database_handle->prepare('SELECT filename, pagename, pagedescription, pagesection, pagetemplate, pagedata, pagesettings, lastmodified FROM kiriwrite_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );

		$statement_handle->execute();

		# Check if the page exists in the database.

		while (@data_page = $statement_handle->fetchrow_array()){
	
			# Get the values from the array.
	
			$pagefilename 		= $data_page[0];
			$pagename		= $data_page[1];
			$pagedescription	= $data_page[2];
			$pagesection		= $data_page[3];
			$pagetemplate		= $data_page[4];
			$pagedata		= $data_page[5];
			$pagesettings		= $data_page[6];
			$pagelastmodified	= $data_page[7];
	
			# Put the values into the page hash.
	
			%database_page = (
				"PageFilename" 		=> $pagefilename,
				"PageName"		=> $pagename,
				"PageDescription"	=> $pagedescription,
				"PageSection"		=> $pagesection,
				"PageTemplate"		=> $pagetemplate,
				"PageContent"		=> $pagedata,
				"PageSettings"		=> $pagesettings,
				"PageLastModified"	=> $class->dateconvert($pagelastmodified),
			);
	
			$page_found = 1;
	
		}

	}
	
	# Check if the page did exist.

	if (!$page_found){

		$error = "PageDoesNotExist";
		return;

	}

	undef $statement_handle;
	return %database_page;

}

sub addpage{
#################################################################################
# addpage: Add a page to the selected database.					#
#										#
# Usage:									#
#										#
# $dbmodule->addpage(options);							#
#										#
# options	Specifies the following options in any order.			#
#										#
# PageFilename		Specifies the page filename to use.			#
# PageName		Specifies the page name to use.				#
# PageDescription	Specifies the page description to use.			#
# PageSection		Specifies the page section to use.			#
# PageTemplate		Specifies the page template to use.			#
# PageContent		Specifies the page content to use.			#
# PageSettings		Specifies the page settings to use.			#
#################################################################################

	# Get the data that was passed to the subroutine.

	$error = "";
	$errorext = "";

	my $class		= shift;
	my ($passedoptions)	= shift;

	my @database_page;
	my $page_count = 0;

	# Get the values passed to the hash.

	my $page_filename	= $passedoptions->{"PageFilename"};
	my $page_name		= $passedoptions->{"PageName"};
	my $page_description	= $passedoptions->{"PageDescription"};
	my $page_section	= $passedoptions->{"PageSection"};
	my $page_template	= $passedoptions->{"PageTemplate"};
	my $page_content	= $passedoptions->{"PageContent"};
	my $page_settings	= $passedoptions->{"PageSettings"};

	# Check to see if the filename given already exists
	# in the page database.

	$statement_handle = $database_handle->prepare('SELECT filename FROM kiriwrite_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	# Check if a page with the filename given really does
	# exist.

	while (@database_page = $statement_handle->fetchrow_array()){

		# A page does exist so increment the count to 1.

		$page_count++;
		
	}

	if ($page_count ne 0){

		# The page does exist so set the error value.

		$error = "PageExists";
		return;

	}

	# Check if certain values are undefined.

	if (!$page_name){

		$page_name = "";

	}

	if (!$page_description){

		$page_description = "";

	}

	if (!$page_section){

		$page_section = "";

	}

	if (!$page_content){

		$page_content = "";

	}

 	my ($created_second, $created_minute, $created_hour, $created_day, $created_month, $created_year, $created_weekday, $created_yearday, $created_dst) = localtime;
 	my $page_date = $created_year . '-' . $created_month . '-' . $created_day . ' ' . $created_hour . ':' . $created_minute . ':' . $created_second;

	# Add the page to the selected database.

	$statement_handle = $database_handle->prepare('INSERT INTO kiriwrite_database_pages (filename, pagename, pagedescription, pagesection, pagetemplate, pagedata, pagesettings, lastmodified) VALUES (
		\'' . $class->convert($page_filename) . '\',
		\'' . $class->convert($page_name) . '\',
		\'' . $class->convert($page_description) . '\',
		\'' . $class->convert($page_section) . '\',
		\'' . $class->convert($page_template) . '\',
		\'' . $class->convert($page_content) . '\',
		\'' . $class->convert($page_settings) . '\',
		\'' . $class->convert($page_date) . '\'
	)') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	undef $statement_handle;

}

sub deletepage{
#################################################################################
# deletepage: Delete a page from the selected database.				#
#										#
# Usage:									#
#										#
# $dbmodule->deletepage(options)						#
#										#
# options	Specifies the following options in any order.			#
#										#
# PageFilename	Specifies the page filename to delete.				#
#################################################################################

	$error = "";
	$errorext = "";

	# Get the data that was passed to the subroutine.

	my $class = shift;
	my ($passedoptions) = @_;
	my @page_info;
	my $page_found = 0;

	# Get the page filename.

	my $page_filename = $passedoptions->{"PageFilename"};

	# Check if the page exists before deleting it.

	$statement_handle = $database_handle->prepare('SELECT filename FROM kiriwrite_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	while (@page_info = $statement_handle->fetchrow_array()){

		$page_found = 1;

	}

	# Check if the page really does exist.

	if (!$page_found){

		$error = "PageDoesNotExist";
		return;

	}

	# Delete the page.

	$statement_handle = $database_handle->prepare('DELETE FROM kiriwrite_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\'') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

}

sub editpage{
#################################################################################
# editpage: Edit a page from the selected database.				#
#										#
# Usage:									#
#										#
# $dbmodule->editpage(options);							#
#										#
# options	Specifies the following options in any order.			#
#										#
# PageFilename		Specifies the filename to edit.				#
# PageNewFilename	Specifies the new filename to use.			#
# PageNewName		Specifies the new page name to use.			#
# PageNewDescription	Specifies the new page description to use.		#
# PageNewSection	Specifies the new page section to use.			#
# PageNewTemplate	Specifies the new page template to use.			#
# PageNewContent	Specifies the new page content to use.			#
# PageNewSettings	Specifies the new page settings to use.			#
#################################################################################

	$error = "";
	$errorext = "";

	# Get the values passed to the subroutine.

	my $class = shift;
	my ($passedoptions) = @_;
	my $page_found = 0;
	my @page_info;

	# Get the data that was passed to the subroutine.

	my $page_filename	= $passedoptions->{"PageFilename"};
	my $page_newfilename	= $passedoptions->{"PageNewFilename"};
	my $page_newname	= $passedoptions->{"PageNewName"};
	my $page_newdescription	= $passedoptions->{"PageNewDescription"};
	my $page_newsection	= $passedoptions->{"PageNewSection"};
	my $page_newtemplate	= $passedoptions->{"PageNewTemplate"};
	my $page_newcontent	= $passedoptions->{"PageNewContent"};
	my $page_newsettings	= $passedoptions->{"PageNewSettings"};

	# Check if the page with the filename given exists.

	$statement_handle = $database_handle->prepare('SELECT filename FROM kiriwrite_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	# Check if the page really does exist.

	while (@page_info = $statement_handle->fetchrow_array()){

		# The page information is found.

		$page_found = 1;

	}

	# Check if the page really does exist.

	if (!$page_found){

		$error = "PageDoesNotExist";
		return;

	}

	# Check if there is a page that already exists with the new
	# filename.

	$page_found = 0;

	if ($page_filename ne $page_newfilename){

		$statement_handle = $database_handle->prepare('SELECT filename FROM kiriwrite_database_pages WHERE filename = \'' . $class->convert($page_newfilename) . '\' LIMIT 1') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
		$statement_handle->execute();

		# Check if a page really is using the new filename.

		while (@page_info = $statement_handle->fetchrow_array()){

			# The page information is found.

			$page_found = 1;

		}

		if ($page_found eq 1){

			$error = "PageExists";
			return;

		}

	}

	# Get the current date.

 	my ($created_second, $created_minute, $created_hour, $created_day, $created_month, $created_year, $created_weekday, $created_yearday, $created_dst) = localtime;
 	my $page_date = $created_year . '-' . $created_month . '-' . $created_day . ' ' . $created_hour . ':' . $created_minute . ':' . $created_second;

	# Edit the selected page.

	$statement_handle = $database_handle->prepare('UPDATE kiriwrite_database_pages SET filename = \'' . $class->convert($page_newfilename) . '\', pagename = \'' . $class->convert($page_newname) . '\', pagedescription = \'' . $class->convert($page_newdescription) . '\', pagesection = \'' . $class->convert($page_newsection) . '\', pagetemplate = \'' . $class->convert($page_newtemplate) . '\', pagedata = \'' . $class->convert($page_newcontent) . '\', pagedata = \'' . $class->convert($page_newcontent) . '\', pagesettings = \'' . $class->convert($page_newsettings) . '\', lastmodified = \'' . $page_date . '\' WHERE filename = \'' . $class->convert($page_filename) . '\'')  or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

}

sub movepage{
#################################################################################
# movepage: Moves a page from the old database to the new database.		#
#										#
# Usage:									#
#										#
# $dbmodule->movepage(options);							#
#										#
# options	Specifies the following options in any order.			#
#										#
# PageFilename	Specifies the page with the filename to move.			#
#################################################################################

	$error = "";
	$errorext = "";

	# Get the values passed to the subroutine.

	my $class = shift;
	my ($passedoptions) = @_;

	my (%database_page, $database_page);
	my ($pagefilename, $pagename, $pagedescription, $pagesection, $pagetemplate, $pagedata, $pagesettings, $pagelastmodified);
	my @page_info;
	my $page_found = 0;

	# Get the data that was passed to the subroutine.

	my $page_filename = $passedoptions->{"PageFilename"};

	# Check if the page with the filename given exists.

	$statement_handle = $database_handle->prepare('SELECT filename, pagename, pagedescription, pagesection, pagetemplate, pagedata, pagesettings, lastmodified FROM kiriwrite_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "OldDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	# Check if the page really does exist.

	while (@page_info = $statement_handle->fetchrow_array()){

		# Get the values from the array.

		$pagefilename 		= $page_info[0];
		$pagename		= $page_info[1];
		$pagedescription	= $page_info[2];
		$pagesection		= $page_info[3];
		$pagetemplate		= $page_info[4];
		$pagedata		= $page_info[5];
		$pagesettings		= $page_info[6];
		$pagelastmodified	= $page_info[7];

		# Put the values into the page hash.

 		%database_page = (
 			"PageFilename" 		=> $pagefilename,
 			"PageName"		=> $pagename,
 			"PageDescription"	=> $pagedescription,
 			"PageSection"		=> $pagesection,
 			"PageTemplate"		=> $pagetemplate,
 			"PageContent"		=> $pagedata,
 			"PageSettings"		=> $pagesettings,
 			"PageLastModified"	=> $pagelastmodified,
 		);

		# The page information is found.

		$page_found = 1;

	}

	# Check if the page really does exist.

	if (!$page_found){

		$error = "PageDoesNotExist";
		return;

	}

	# Check if the page with the filename given already exists in
	# the database the page is being moved to.

	$page_found = 0;
 	@page_info = ();

	$second_statement_handle = $second_database_handle->prepare('SELECT filename FROM kiriwrite_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "NewDatabaseError", $errorext = $second_database_handle->errstr, return );
	$second_statement_handle->execute();

	while (@page_info = $second_statement_handle->fetchrow_array()){

		$page_found = 1;

	}
	
	# Check if the page really does exist.

	if ($page_found){

		$error = "PageAlreadyExists";
		return;

	}

	# Add the page to the new database.

	$second_statement_handle = $second_database_handle->prepare('INSERT INTO kiriwrite_database_pages (filename, pagename, pagedescription, pagesection, pagetemplate, pagedata, pagesettings, lastmodified) VALUES (
		\'' . $class->convert($database_page{"PageFilename"}) . '\',
		\'' . $class->convert($database_page{"PageName"}) . '\',
		\'' . $class->convert($database_page{"PageDescription"}) . '\',
		\'' . $class->convert($database_page{"PageSection"}) . '\',
		\'' . $class->convert($database_page{"PageTemplate"}) . '\',
		\'' . $class->convert($database_page{"PageContent"}) . '\',
		\'' . $class->convert($database_page{"PageSettings"}) . '\',
		\'' . $class->convert($database_page{"PageLastModified"}) . '\'
	)') or ( $error = "NewDatabaseError", $errorext = $second_database_handle->errstr, return );
	$second_statement_handle->execute();

	# Delete the page from the old database.

	$statement_handle = $database_handle->prepare('DELETE FROM kiriwrite_database_pages WHERE filename = \'' . $class->convert($database_page{"PageFilename"}) . '\'') or ( $error = "OldDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

}

sub copypage{
#################################################################################
# copypage: Copies a page from the old database to the new database.		#
#										#
# Usage:									#
#										#
# $dbmodule->copypage(options);							#
#										#
# options	Specifies the following options in any order.			#
#										#
# PageFilename	Specifies the page with the filename to copy.			#
#################################################################################

	$error = "";
	$errorext = "";

	# Get the values passed to the subroutine.

	my $class = shift;
	my ($passedoptions) = @_;

	my (%database_page, $database_page);
	my ($pagefilename, $pagename, $pagedescription, $pagesection, $pagetemplate, $pagedata, $pagesettings, $pagelastmodified);
	my @page_info;
	my $page_found = 0;

	# Get the data that was passed to the subroutine.

	my $page_filename = $passedoptions->{"PageFilename"};

	# Check if the page with the filename given exists.

	$statement_handle = $database_handle->prepare('SELECT filename, pagename, pagedescription, pagesection, pagetemplate, pagedata, pagesettings, lastmodified FROM kiriwrite_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "OldDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	# Check if the page really does exist.

	while (@page_info = $statement_handle->fetchrow_array()){

		# Get the values from the array.

		$pagefilename 		= $page_info[0];
		$pagename		= $page_info[1];
		$pagedescription	= $page_info[2];
		$pagesection		= $page_info[3];
		$pagetemplate		= $page_info[4];
		$pagedata		= $page_info[5];
		$pagesettings		= $page_info[6];
		$pagelastmodified	= $page_info[7];

		# Put the values into the page hash.

 		%database_page = (
 			"PageFilename" 		=> $pagefilename,
 			"PageName"		=> $pagename,
 			"PageDescription"	=> $pagedescription,
 			"PageSection"		=> $pagesection,
 			"PageTemplate"		=> $pagetemplate,
 			"PageContent"		=> $pagedata,
 			"PageSettings"		=> $pagesettings,
 			"PageLastModified"	=> $pagelastmodified,
 		);

		# The page information is found.

		$page_found = 1;

	}

	# Check if the page really does exist.

	if (!$page_found){

		$error = "PageDoesNotExist";
		return;

	}

	# Check if the page with the filename given already exists in
	# the database the page is being moved to.

	$page_found = 0;
 	@page_info = ();

	$second_statement_handle = $second_database_handle->prepare('SELECT filename FROM kiriwrite_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "NewDatabaseError", $errorext = $second_database_handle->errstr, return );
	$second_statement_handle->execute();

	while (@page_info = $second_statement_handle->fetchrow_array()){

		$page_found = 1;

	}
	
	# Check if the page really does exist.

	if ($page_found){

		$error = "PageAlreadyExists";
		return;

	}

	# Add the page to the new database.

	$second_statement_handle = $second_database_handle->prepare('INSERT INTO kiriwrite_database_pages (filename, pagename, pagedescription, pagesection, pagetemplate, pagedata, pagesettings, lastmodified) VALUES (
		\'' . $class->convert($database_page{"PageFilename"}) . '\',
		\'' . $class->convert($database_page{"PageName"}) . '\',
		\'' . $class->convert($database_page{"PageDescription"}) . '\',
		\'' . $class->convert($database_page{"PageSection"}) . '\',
		\'' . $class->convert($database_page{"PageTemplate"}) . '\',
		\'' . $class->convert($database_page{"PageContent"}) . '\',
		\'' . $class->convert($database_page{"PageSettings"}) . '\',
		\'' . $class->convert($database_page{"PageLastModified"}) . '\'
	)') or ( $error = "NewDatabaseError", $errorext = $second_database_handle->errstr, return );
	$second_statement_handle->execute();

}

#################################################################################
# Filter subroutines.								#
#################################################################################

sub connectfilter{
#################################################################################
# connectfilter: Connect to the filter database.				#
#										#
# Usage:									#
#										#
# $dbmodule->connectfilter(missingignore);					#
#										#
# missingignore	Ignore error about database being missing.			#
#################################################################################

	$error = "";
	$errorext = "";

	my $class = shift;
	my $ignoremissing = shift;

	# Check if the template database exists.

	my $filterdatabase_exists = main::kiriwrite_fileexists("filters.db.sqlite");
	
	if ($filterdatabase_exists eq 1){

		$filterdb_exists = 0;

		if (!$ignoremissing){

			$error = "FilterDatabaseDoesNotExist";
			return;

		}

	}

	# Check if the permission settings for the template database are valid.

	my $filterdb_permissions = main::kiriwrite_filepermissions("filters.db.sqlite", 1, 0);

	if ($filterdb_permissions eq 1){

		# The template database has invalid permissions set
		# so return an error value.

		if (!$ignoremissing){

			$error = "FilterDatabaseInvalidPermissionsSet";
			return;

		}

	}

	# Connect to the template database.

	$filterdb_database_handle = DBI->connect("dbi:SQLite:dbname=filters.db.sqlite");
	$filterdb_database_handle->{unicode} = 1;
	$filterdb_loaded = 1;

}

sub disconnectfilter{
#################################################################################
# disconnectfilter: Disconnect from the filter database.			#
#										#
# Usage:									#
#										#
# $dbmodule->disconnectfilter();						#
#################################################################################

	# Disconnect the template database.

	if ($filterdb_loaded eq 1){

		undef $filterdb_statement_handle;
		$filterdb_database_handle->disconnect();

	}

}

sub getfilterlist{
#################################################################################
# getfilterlist: Gets the list of filters in the filter database.		#
#										#
# Usage:									#
#										#
# $dbmodule->getfilterlist();							#
#################################################################################

	$error = "";
	$errorext = "";

	my @filter_list;
	my @filter_data;

	# Get the list of filters available.

	$filterdb_statement_handle	= $filterdb_database_handle->prepare('SELECT id FROM kiriwrite_filters ORDER BY priority ASC') or ( $error = "FilterDatabaseError", $errorext = $filterdb_database_handle->errstr, return );
	$filterdb_statement_handle->execute();

	while (@filter_data = $filterdb_statement_handle->fetchrow_array()){

		# Add the filter to the list of available filters.

		push(@filter_list, $filter_data[0]);

	}

	undef $filterdb_statement_handle;
	return @filter_list;

}

sub getfilterinfo{
#################################################################################
# getfilterinfo: Gets information about the filter.				#
#										#
# Usage:									#
#										#
# $dbmodule->getfilterinfo(options);						#
#										#
# options	Specifies the following options in any order.			#
#										#
# FilterID	Specifies the filter ID number to get information from.		#
#################################################################################

	$error = "";
	$errorext = "";

	# Get the values passed to the subroutine.

	my $class		= shift;
	my ($passedoptions) 	= @_;

	my %filter_info;
	my $filter_exists	= 0;
	my @filter_data;

	# Get the values that are in the hash.

	my $filter_id		= $passedoptions->{"FilterID"};

	$filterdb_statement_handle = $filterdb_database_handle->prepare('SELECT id, priority, findsetting, replacesetting, notes FROM kiriwrite_filters where id = \'' . $class->convert($filter_id) . '\'') or ( $error = "FilterDatabaseError", $errorext = $filterdb_database_handle->errstr, return );
	$filterdb_statement_handle->execute();

	# Get the filter information.

	while (@filter_data = $filterdb_statement_handle->fetchrow_array()){

		$filter_info{"FilterID"}	= $filter_data[0];
		$filter_info{"FilterPriority"}	= $filter_data[1];
		$filter_info{"FilterFind"}	= $filter_data[2];
		$filter_info{"FilterReplace"}	= $filter_data[3];
		$filter_info{"FilterNotes"}	= $filter_data[4];

		$filter_exists = 1;

	}

	# Check if the filter exists.

	if (!$filter_exists){

		# The filter does not exist so return
		# an error value.

		$error = "FilterDoesNotExist";
		return;

	}

	# Return the filter information.

	undef $filterdb_statement_handle;
	return %filter_info;

}

sub addfilter{
#################################################################################
# addfilter: Adds a filter to the filter database.				#
# 										#
# Usage:									#
#										#
# $dbmodule->addfilter(options);						#
#										#
# options	Specifies the following options in any order.			#
#										#
# FindFilter	Specifies the find filter to add.				#
# ReplaceFilter	Specifies the replace filter to add.				#
# Priority	Specifies the filter priority to use.				#
# Notes		Specifies the notes to use.					#
#################################################################################

	$error = "";
	$errorext = "";

	# Get the values passed to the subroutine.

	my $class = shift;
	my ($passedoptions) = @_;

	# Define some variables for later.

	my @database_filters;
	my @filterid_list;
	my @filterid_check;
	my $nofiltertable = 0;
	my $filter_found = 0;
	my $filter_count = 0;
	my $filter_id;
	my $new_id;

	# Get the values from the hash.

	my $filter_find		= $passedoptions->{"FindFilter"};
	my $filter_replace	= $passedoptions->{"ReplaceFilter"};
	my $filter_priority	= $passedoptions->{"Priority"};
	my $filter_notes	= $passedoptions->{"Notes"};

	# Check if the filter database permissions are valid.

	my $filterdb_exists = main::kiriwrite_fileexists("filters.db.sqlite", 1, 1);
	my $filterdb_permissions = main::kiriwrite_filepermissions("filters.db.sqlite", 1, 1);

	if ($filterdb_permissions eq 1){

		if ($filterdb_exists eq 0){
			$error = "FilterDatabaseInvalidPermissionsSet";
			return;
		}

	}

	# Check if certain values are undefined and if they
	# are then set them blank.

	if (!$filter_find){

		$filter_find = "";

	}

	if (!$filter_replace){

		$filter_replace = "";

	}

	if (!$filter_priority){

		$filter_priority = 1;

	}

	if (!$filter_notes){

		$filter_notes = "";

	}

	my $directory_permissions = main::kiriwrite_filepermissions(".", 1, 1, 0);

	if ($directory_permissions eq 1 && $filterdb_exists){

		# The template database cannot be created because of invalid directory
		# permissions so return an error value.

		$error = "FilterDatabaseFileUncreateable";
		return;	

	}

	# Check if the filter table exists.

	$filterdb_statement_handle = $filterdb_database_handle->prepare('SELECT id FROM kiriwrite_filters ORDER BY id ASC') or ( $nofiltertable = 1 );

	# Check if there is really no filter table.

	if ($nofiltertable){

		# Create the filter database table.

		$filterdb_statement_handle = $filterdb_database_handle->prepare('CREATE TABLE kiriwrite_filters (
		        id int(7) primary key,
        		priority int(5),
        		findsetting varchar(1024),
        		replacesetting varchar(1024),
        		notes text
		)') or ( $error = "FilterDatabaseError", $errorext = $filterdb_database_handle->errstr, return );
		$filterdb_statement_handle->execute();

	}

	# Find the lowest filter identification number available.

	$filterdb_statement_handle = $filterdb_database_handle->prepare('SELECT id FROM kiriwrite_filters ORDER BY id ASC') or ( $error = "FilterDatabaseError", $errorext = $filterdb_database_handle->errstr, return );
	$filterdb_statement_handle->execute();

	while (@database_filters = $filterdb_statement_handle->fetchrow_array()){

		$filter_id	= $database_filters[0];

		# Add the filter identification to the list of filter IDs.

		push(@filterid_list, $filter_id);

	}

	$filter_id = "";

	# Process each filter looking for a blank available filter.

	foreach $filter_id (@filterid_list){

		# Check the next filter ID to see if it's blank.

		$new_id = $filter_id + 1;

		$filterdb_statement_handle = $filterdb_database_handle->prepare('SELECT id FROM kiriwrite_filters WHERE id = \'' . $class->convert($new_id) . '\'') or ( $error = "FilterDatabaseError", $errorext = $filterdb_database_handle->errstr, return );
		$filterdb_statement_handle->execute();

		# Get the filter identification number.

		while (@filterid_check = $filterdb_statement_handle->fetchrow_array()){

			$filter_found = 1;

		}

		# Check if a filter was found.

		if (!$filter_found){

			# No filter was found using this ID so exit the loop.

			last;

		}

		# Increment the filter count and reset the filter found value.

		$filter_count++;
		$filter_found = 0;
		$new_id = 0;

	}

	# Check if there were any filters in the filter database.

	if (!$filter_count && !$new_id){

		# There were no filters in the filter database so set
		# the new filter identification value to 1.

		$new_id = 1;

	}

	# Add the filter to the filter database.

	$filterdb_statement_handle = $filterdb_database_handle->prepare('INSERT INTO kiriwrite_filters (id, priority, findsetting, replacesetting, notes) VALUES (
		\'' . $class->convert($new_id) . '\',
		\'' . $class->convert($filter_priority) . '\',
		\'' . $class->convert($filter_find) . '\',
		\'' . $class->convert($filter_replace) .'\',
		\'' . $class->convert($filter_notes) . '\'
	)') or ( $error = "FilterDatabaseError", $errorext = $filterdb_database_handle->errstr, return );
	$filterdb_statement_handle->execute();

}

sub editfilter{
#################################################################################
# editfilter: Edits a filter in the filter database.				#
#										#
# Usage:									#
#										#
# $dbmodule->editfilter(options);						#
#										#
# options	Specifies the following options in any order.			#
#										#
# FilterID		Specifies the filter to edit.				#
# NewFindFilter		Specifies the new find filter setting.			#
# NewReplaceFilter	Specifies the new replace filter setting.		#
# NewFilterPriority	Specifies the new filter priority setting.		#
# NewFilterNotes	Specifies the new notes for the filter.			#
#################################################################################

	$error = "";
	$errorext = "";

	# Get the values passed to the subroutine.

	my $class = shift;
	my ($passedoptions) = @_;

	my @filter_data;
	my $filter_exists = 1;
	my $blankfile = 0;

	# Get the values from the hash.

	my $filter_id		= $passedoptions->{"FilterID"};
	my $filter_newfind	= $passedoptions->{"NewFindFilter"};
	my $filter_newreplace	= $passedoptions->{"NewReplaceFilter"};
	my $filter_newpriority	= $passedoptions->{"NewFilterPriority"};
	my $filter_newnotes	= $passedoptions->{"NewFilterNotes"};

	# Check if the filter database permissions are valid.

	my $filterdb_exists = main::kiriwrite_fileexists("filters.db.sqlite", 1, 1);
	my $filterdb_permissions = main::kiriwrite_filepermissions("filters.db.sqlite", 1, 1);

	if ($filterdb_permissions eq 1){

		if ($filterdb_exists eq 0){
			$error = "FilterDatabaseInvalidPermissionsSet";
			return;
		}

	}

	# Check if the filter exists before editing it.

	$filterdb_statement_handle = $filterdb_database_handle->prepare('SELECT id FROM kiriwrite_filters where id = \'' . $class->convert($filter_id) . '\'') or ( $error = "FilterDatabaseError", $errorext = $filterdb_database_handle->errstr, return );
	$filterdb_statement_handle->execute();

	# Check if the filter exists.

	while (@filter_data = $filterdb_statement_handle->fetchrow_array()){

		$filter_exists = 1;

	}	

	# Check if the filter really does exist.

	if (!$filter_exists){

		# The filter does not exist so return
		# an error value.

		$error = "FilterDoesNotExist";
		return;

	}

	# Edit the selected filter.

	$filterdb_statement_handle = $filterdb_database_handle->prepare('UPDATE kiriwrite_filters SET
		findsetting = \'' . $class->convert($filter_newfind) . '\',
		replacesetting = \'' . $class->convert($filter_newreplace) . '\',
		priority = \'' . $class->convert($filter_newpriority) . '\',
		notes = \'' . $class->convert($filter_newnotes) . '\'
	WHERE id = \'' . $class->convert($filter_id) . '\'') or ( $error = "FilterDatabaseError", $errorext = $filterdb_database_handle->errstr, return );	
	$filterdb_statement_handle->execute();

	undef $filterdb_statement_handle;
	return;

}

sub deletefilter{
#################################################################################
# deletefilter: Deletes a filter from the filter database.			#
#										#
# Usage:									#
#										#
# $dbmodule->deletefilter(options);						#
#										#
# options	Specifies the following options in any order.			#
#										#
# FilterID	Specifies the filter to delete from the filter database.	#
#################################################################################

	$error = "";
	$errorext = "";

	# Get the values passed to the subroutine.

	my $class = shift;
	my ($passedoptions) = @_;

	my $filter_exists = 0;
	my @filter_data;

	# Get the values from the hash.

	my $filter_id		= $passedoptions->{"FilterID"};

	# Check if the filter exists before deleting.

	$filterdb_statement_handle = $filterdb_database_handle->prepare('SELECT id FROM kiriwrite_filters where id = \'' . $class->convert($filter_id) . '\'') or ( $error = "FilterDatabaseError", $errorext = $filterdb_database_handle->errstr, return );
	$filterdb_statement_handle->execute();

	while (@filter_data = $filterdb_statement_handle->fetchrow_array()){

		$filter_exists = 1;

	}

	# Check to see if the filter really does exist.

	if (!$filter_exists){

		$error = "FilterDoesNotExist";
		return;

	}

	# Delete the filter from the filter database.

	$filterdb_statement_handle = $filterdb_database_handle->prepare('DELETE FROM kiriwrite_filters where id = \'' . $class->convert($filter_id) . '\'') or ( $error = "FilterDatabaseError", $errorext = $filterdb_database_handle->errstr, return );
	$filterdb_statement_handle->execute();

	undef $filterdb_statement_handle;

}

#################################################################################
# Template subroutines.								#
#################################################################################

sub connecttemplate{
#################################################################################
# connecttemplate: Connect to the template database.				#
#										#
# Usage:									#
#										#
# $dbmodule->connecttemplate(missingignore);					#
#										#
# missingignore	Ignore errror about database being missing.			#
#################################################################################

	$error = "";
	$errorext = "";

	my $class = shift;
	my $ignoremissing = shift;

	# Check if the template database exists.

	my $templatedatabase_exists = main::kiriwrite_fileexists("templates.db.sqlite");
	
	if ($templatedatabase_exists eq 1){

		$templatedb_exists = 0;

		if (!$ignoremissing){

			$error = "TemplateDatabaseDoesNotExist";
			return;

		}

	}

	# Check if the permission settings for the template database are valid.

	my $templatedb_permissions = main::kiriwrite_filepermissions("templates.db.sqlite", 1, 0);

	if ($templatedb_permissions eq 1){

		# The template database has invalid permissions set
		# so return an error value.

		if (!$ignoremissing){

			$error = "TemplateDatabaseInvalidPermissionsSet";
			return;

		}

	}

	# Connect to the template database.

	$template_database_handle = DBI->connect("dbi:SQLite:dbname=templates.db.sqlite");
	$template_database_handle->{unicode} = 1;
	$templatedb_loaded = 1;

}

sub disconnecttemplate{
#################################################################################
# disconnecttemplate: Disconnect from the template database.			#
#										#
# Usage:									#
#										#
# $dbmodule->disconnecttemplate();						#
#################################################################################

	# Disconnect the template database.

	if ($templatedb_loaded eq 1){

		undef $template_statement_handle;
		$template_database_handle->disconnect();

	}

}

sub gettemplatelist{
#################################################################################
# gettemplatelist: Gets the list of templates.					#
#										#
# Usage:									#
#										#
# $dbmodule->gettemplatelist();							#
#################################################################################

	$error = "";
	$errorext = "";

	$template_statement_handle = $template_database_handle->prepare('SELECT filename FROM kiriwrite_templates ORDER BY filename ASC') or ( $error = "TemplateDatabaseError", $errorext = $template_database_handle->errstr, return );
	$template_statement_handle->execute();

	my @database_template;
	my @templates_list;
	my $template_filename;

	while (@database_template = $template_statement_handle->fetchrow_array()){

		# Get certain values from the array.

		$template_filename 	= $database_template[0];

		# Add the template to the list of templates.

		push(@templates_list, $template_filename);

	}

	return @templates_list;

}

sub gettemplateinfo{
#################################################################################
# gettemplateinfo: Get information on a template.				#
#										#
# Usage:									#
#										#
# $dbmodule->gettemplateinfo(options);						#
#										#
# options	Specifies the following options in any order.			#
#										#
# TemplateFilename	Specifies the template filename to use.			#
#################################################################################

	$error = "";
	$errorext = "";

	# Get the data passed to the subroutine.

	my $class = shift;
	my ($passedoptions) = @_;

	my %page_info;
	my @template_data;

	my $template_filename;
	my $template_name;
	my $template_description;
	my $template_datemodified;
	my $template_layout;

	my $template_found = 0;

	my $filename	= $passedoptions->{"TemplateFilename"};

	$template_statement_handle = $template_database_handle->prepare('SELECT filename, templatename, templatedescription, templatelayout, datemodified FROM kiriwrite_templates WHERE filename = \'' . $class->convert($filename) . '\'') or ( $error = "TemplateDatabaseError", $errorext = $template_database_handle->errstr, return );
	$template_statement_handle->execute();

	while (@template_data = $template_statement_handle->fetchrow_array()){

		# Get certain values from the array.

		$template_filename 	= $template_data[0];
		$template_name 		= $template_data[1];
		$template_description 	= $template_data[2];
		$template_layout	= $template_data[3];
		$template_datemodified 	= $template_data[4];

		# Process them into the hash.

		%page_info = (
			"TemplateFilename" => $template_filename,
			"TemplateName" => $template_name,
			"TemplateDescription" => $template_description,
			"TemplateLayout" => $template_layout,
			"TemplateLastModified" => $template_datemodified
		);

		$template_found = 1;

	}

	if ($template_found eq 0){

		# The template was not found in the template database so
		# write an error value.

		$error = "TemplateDoesNotExist";
		return;

	}

	return %page_info;

}

sub addtemplate{
#################################################################################
# addtemplate: Adds a template to the template database.			#
#										#
# Usage:									#
#										#
# $dbmodule->addtemplate();							#
#										#
# options	Specifies the following options in any order.			#
#										#
# TemplateFilename	Specifies the new template filename.			#
# TemplateName		Specifies the new template name.			#
# TemplateDescription	Specifies the new template description.			#
# TemplateLayout	Specifies the new template layout.			#
#################################################################################

	$error = "";
	$errorext = "";

	# Get the data passed to the subroutine.

	my $class = shift;
	my ($passedoptions) = @_;

	my @page_exists;
	my $notemplatetable;
	my $blankfile = 0;

	my $template_filename		= $passedoptions->{"TemplateFilename"};
	my $template_name		= $passedoptions->{"TemplateName"};
	my $template_description	= $passedoptions->{"TemplateDescription"};
	my $template_layout		= $passedoptions->{"TemplateLayout"};

	# Check if the template database permissions are valid.

	my $templatedb_exists = main::kiriwrite_fileexists("templates.db.sqlite", 1, 1);
	my $templatedb_permissions = main::kiriwrite_filepermissions("templates.db.sqlite", 1, 1);

	if ($templatedb_permissions eq 1){

		if ($templatedb_exists eq 0){
			$error = "TemplateDatabaseInvalidPermissionsSet";
			return;
		}

	}

	# Check if the template already exists before adding.

	if ($templatedb_exists eq 0){

		$template_statement_handle = $template_database_handle->prepare('SELECT filename FROM kiriwrite_templates WHERE filename = \'' . $class->convert($template_filename) . '\' LIMIT 1') or ($blankfile = 1);

		if ($blankfile eq 0){

			$template_statement_handle->execute();

			while (@page_exists = $template_statement_handle->fetchrow_array()){

				$error = "TemplatePageExists";
				return;

			}

		}

	}

 	# Get the current date.
 
 	my ($created_second, $created_minute, $created_hour, $created_day, $created_month, $created_year, $created_weekday, $created_yearday, $created_dst) = localtime;
 
 	my $template_date = $created_year . '-' . $created_month . '-' . $created_day . ' ' . $created_hour . ':' . $created_minute . ':' . $created_second;

	# Check if certain values are undefined and if they
	# are then set them blank.

	if (!$template_name){

		$template_name = "";

	}

	if (!$template_description){

		$template_description = "";

	}

	if (!$template_layout){

		$template_layout = "";

	}

	my $directory_permissions = main::kiriwrite_filepermissions(".", 1, 1, 0);

	if ($directory_permissions eq 1 && $templatedb_exists){

		# The template database cannot be created because of invalid directory
		# permissions so return an error value.

		$error = "TemplateDatabaseUncreateable";
		return;	

	}

	# Check to see if a template can be added.

	$template_statement_handle = $template_database_handle->prepare('INSERT INTO kiriwrite_templates (filename, templatename, templatedescription, templatelayout, datemodified) VALUES(
 				\'' . $class->convert($template_filename) . '\',
 				\'' . $class->convert($template_name) . '\',
 				\'' . $class->convert($template_description) . '\',
 				\'' . $class->convert($template_layout) . '\',
 				\'' . $class->convert($template_date) . '\'
	)') or ( $notemplatetable = 1 );

	if (!$notemplatetable){

		$template_statement_handle->execute();

	}

	# Check to see if there is no template table and attempt to create one.

	if ($notemplatetable){

		# Create a template table.

		my $directory_permissions = main::kiriwrite_filepermissions(".", 1, 1, 0);

		if ($directory_permissions eq 1){

			# The template database cannot be created because of invalid directory
			# permissions so return an error.

			$error = "TemplateDatabaseFileUncreateable";
			return;

		}

		$template_statement_handle = $template_database_handle->prepare('create table kiriwrite_templates(
			filename varchar(256) primary key,
			templatename varchar(512),
			templatedescription varchar(512),
			templatelayout text,
			datemodified datetime
		);') or ( $error = "TemplateDatabaseError", $errorext = $template_database_handle->errstr, return );
		$template_statement_handle->execute();

		$template_statement_handle = $template_database_handle->prepare('INSERT INTO kiriwrite_templates (filename, templatename, templatedescription, templatelayout, datemodified) VALUES(
 				\'' . $class->convert($template_filename) . '\',
 				\'' . $class->convert($template_name) . '\',
 				\'' . $class->convert($template_description) . '\',
 				\'' . $class->convert($template_layout) . '\',
 				\'' . $class->convert($template_date) . '\'
		)') or ( $error = "TemplateDatabaseError", $errorext = $template_database_handle->errstr, return );
		$template_statement_handle->execute();

	}

}

sub deletetemplate{
#################################################################################
# deletetemplate: Deletes a template from the template database.		#
#										#
# Usage:									#
#										#
# $dbmodule->deletetemplate(options);						#
#										#
# options	Specifies the following options in any order.			#
#										#
# TemplateFilename	Specifies the template filename to delete.		#
#################################################################################

	$error = "";
	$errorext = "";

	# Get the data passed to the subroutine.

	my $class = shift;
	my ($passedoptions) = @_;

	my @pagedata;
	my $template_filename = $passedoptions->{"TemplateFilename"};
	my $template_count = 0;

	# Check if the template exists.

	$template_statement_handle = $template_database_handle->prepare('SELECT filename FROM kiriwrite_templates WHERE filename = \'' . $class->convert($template_filename) . '\' LIMIT 1') or ( $error = "TemplateDatabaseError", $errorext = $template_database_handle->errstr, return );
	$template_statement_handle->execute();

	while (@pagedata = $template_statement_handle->fetchrow_array()){

		$template_count++;

	}

	if ($template_count eq 0){

		# No pages were returned so return an error value.

		$error = "TemplateDoesNotExist";
		return;

	}

	# Delete the template from the template database.

	$template_statement_handle = $template_database_handle->prepare('DELETE FROM kiriwrite_templates WHERE filename = \'' . $class->convert($template_filename) . '\'') or ( $error = "TemplateDatabaseError", $errorext = $template_database_handle->errstr, return );
	$template_statement_handle->execute();

}

sub edittemplate{
#################################################################################
# editttemplate: Edits a Kiriwrite template.					#
#										#
# Usage:									#
#										#
# $dbmodule->edittemplate(options);						#
#										#
# options	Specifies the following options in any order.			#
#										#
# TemplateFilename		Specifies the template filename to edit.	#
# NewTemplateFilename		Specifies the new template filename.		#
# NewTemplateName		Specifies the new template name.		#
# NewTemplateDescription	Specifies the new template description.		#
# NewTemplateLayout		Specifies the new template layout.		#
#################################################################################

	# Get the values passed.

	my $class = shift;
	my ($passedoptions) = @_;
	my $template_found = 0;
	my @template_info;

	# Process the values passed.

	my $template_filename		= $passedoptions->{"TemplateFilename"};
	my $new_template_filename	= $passedoptions->{"NewTemplateFilename"};
	my $new_template_name		= $passedoptions->{"NewTemplateName"};
	my $new_template_description	= $passedoptions->{"NewTemplateDescription"};
	my $new_template_layout		= $passedoptions->{"NewTemplateLayout"};

	# Check if the template database permissions are valid.

	my $templatedb_exists = main::kiriwrite_fileexists("templates.db.sqlite", 1, 1);
	my $templatedb_permissions = main::kiriwrite_filepermissions("templates.db.sqlite", 1, 1);

	if ($templatedb_permissions eq 1){

		if ($templatedb_exists eq 0){
			$error = "TemplateDatabaseInvalidPermissionsSet";
			return;
		}

	}

	# Check if the template exists.

	$template_statement_handle = $template_database_handle->prepare('SELECT filename FROM kiriwrite_templates WHERE filename = \'' . $class->convert($template_filename) . '\' LIMIT 1') or ( $error = "TemplateDatabaseError", $errorext = $template_database_handle->errstr, return );
	$template_statement_handle->execute();

	while (@template_info = $template_statement_handle->fetchrow_array()){

		$template_found = 1;

	}

	# Check to see if the template was found and set an error value if
	# it wasn't.

	if ($template_found eq 0){

		$error = "TemplateDoesNotExist";
		return;

	}

	# Get the date and time.

	my ($created_second, $created_minute, $created_hour, $created_day, $created_month, $created_year, $created_weekday, $created_yearday, $created_dst) = localtime;
	my $templatenewdate = $created_year . '-' . $created_month . '-' . $created_day . ' ' . $created_hour . ':' . $created_minute . ':' . $created_second;

	# Update the template information.

	$template_statement_handle = $template_database_handle->prepare('UPDATE kiriwrite_templates SET
		filename = \'' . $class->convert($new_template_filename) . '\',
		templatename = \'' . $class->convert($new_template_name) . '\',
		templatedescription = \'' . $class->convert($new_template_description) . '\',
		templatelayout = \'' . $class->convert($new_template_layout) . '\',
		datemodified = \'' . $class->convert($templatenewdate) . '\'
		WHERE filename = \'' . $class->convert($template_filename) . '\'
	') or ( $error = "TemplateDatabaseError", $errorext = $template_database_handle->errstr, return );
	$template_statement_handle->execute();

}

#################################################################################
# General subroutines.								#
#################################################################################

sub connect{
#################################################################################
# connect: Connect to the server.						#
#										#
# Usage:									#
#										#
# $dbmodule->connect();								#
#################################################################################

	# This function is not needed in this database module.

}

sub disconnect{
#################################################################################
# connect: Disconnect from the server.						#
#										#
# Usage:									#
#										#
# $dbmodule->disconnect();							#
#################################################################################

	# This function is not needed in this database module.

	undef $statement_handle;

}

1;