#################################################################################
# Kiriwrite Database Module - MySQL 5.x Database Module (MySQL5.pm)		#
# Database module for mainipulating data in a MySQL 5.x database.		#
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

package Kiriwrite::Database::MySQL5;

# Enable strict and use warnings.

use strict;
use warnings;
use Encode qw(decode_utf8);

# Load the following Perl modules.

use DBI qw(:sql_types);

# Set the following values.

our $VERSION 	= "0.1.0";
my ($options, %options);
my $database_handle;
my $statement_handle;
my $error;
my $errorext;
my $database_filename;
my $second_database_filename;

#################################################################################
# Generic Subroutines.								#
#################################################################################

sub new{
#################################################################################
# new: Create an instance of Kiriwrite::Database::MySQL				#
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
		"Server"	=> $passedoptions->{"Server"},
		"Database"	=> $passedoptions->{"Database"},
		"Username"	=> $passedoptions->{"Username"},
		"Password"	=> $passedoptions->{"Password"},
		"Port"		=> $passedoptions->{"Port"},
		"Protocol"	=> $passedoptions->{"Protocol"},
		"TablePrefix"	=> $passedoptions->{"TablePrefix"}
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

					$day =~ s/^0//;

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
					$hour =~ s/^0//;
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
					$minute =~ s/^0//;
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
					$second =~ s/^0//;
					
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

	# This subroutine is not needed for this database module.

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

	$error = "";
	$errorext = "";

	# Get the value that was passed to the subroutine.

	my $class	= shift;
	my ($filename)  = @_;

	my @table_data;
	my $table_exists = 0;

	# Check if the table exists.

	$statement_handle = $database_handle->prepare('SHOW TABLES LIKE \'' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($filename) . '_database_info\'') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	while (@table_data = $statement_handle->fetchrow_array()){

		$table_exists = 1;

	}

	# Check if the table really does exist.

	if ($table_exists eq 1){

		# The table exists so return a value of 0.

		return 0;

	} else {

		# The table does not exist so return a value of 1.

		return 1;

	}

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

	$error = "";
	$errorext = "";

	# Connect to the server.

	$database_handle = DBI->connect("DBI:mysql:database=" . $options{"Database"} . ";host=" . $options{"Server"} . ";protocol=" . $options{"Protocol"} . "port=" . $options{"Port"}, $options{"Username"}, $options{"Password"}, { "mysql_enable_utf8" => 1 }) or ( $error = "DatabaseConnectionError", $errorext = DBI->errstr, return );
	$database_handle->do('SET CHARACTER SET utf8');
	$database_handle->do('SET NAMES utf8');

}

sub disconnect{
#################################################################################
# connect: Disconnect from the server.						#
#										#
# Usage:									#
#										#
# $dbmodule->disconnect();							#
#################################################################################
	
	# Disconnect from the server.

	if ($statement_handle){

		$statement_handle->finish();

	}

	if ($database_handle){

		$database_handle->disconnect();

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

	$error = "";
	$errorext = "";

	# Get the list of databases.

	$statement_handle = $database_handle->prepare("SHOW TABLES") or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	my @final_table_list;	
	my @database_table_list;
	my @table_name;
	my $table;

	while (@table_name = $statement_handle->fetchrow_array()){

		push(@database_table_list, decode_utf8($table_name[0]));

	}

	my $table_prefix = $options{"TablePrefix"};

	# Find all the database information tables with the correct table prefix.

	@database_table_list = grep /^$table_prefix/ , @database_table_list;
	@database_table_list = grep /m*database_info$/ , @database_table_list;

	foreach $table (@database_table_list){

		# Process each table name removing the table prefix name and
		# the _database_info part.

		$table =~ s/^$table_prefix(_)//g;
		$table =~ s/_database_info$//g;

		push (@final_table_list, $table);

	}

	# Return the final list of databases.

	return @final_table_list;

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

	my $dbname = $passedoptions->{"DatabaseName"};

	my $database_exists = $class->dbexists($dbname);

	if ($database_exists eq 1){

		# The database does not exist so return an error value
		# saying that the database does not exist.

		$error = "DoesNotExist";

		return;

	}

	$database_filename = $dbname;

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

	$error = "";
	$errorext = "";

	my $class = shift;
	my ($databaseinfo, %databaseinfo);
	my ($sqldata, @sqldata);

	$statement_handle = $database_handle->prepare('SELECT name, description, notes, categories, kiriwrite_version_major, kiriwrite_version_minor, kiriwrite_version_revision FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_info LIMIT 1') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	@sqldata = $statement_handle->fetchrow_array();

	# Process the database information into a hash.

	%databaseinfo = (

		"DatabaseName"	=> decode_utf8($sqldata[0]),
		"Description"	=> decode_utf8($sqldata[1]),
		"Notes"		=> decode_utf8($sqldata[2]),
		"Categories"	=> decode_utf8($sqldata[3]),
		"Major"		=> decode_utf8($sqldata[4]),
		"Minor"		=> decode_utf8($sqldata[5]),
		"Revision"	=> decode_utf8($sqldata[6])
	);

	$statement_handle->finish();

	return %databaseinfo;

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

	# Set the second database filename.

	$second_database_filename = $dbname;

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

	$statement_handle = $database_handle->prepare('SELECT name, description, notes, categories, kiriwrite_version_major, kiriwrite_version_minor, kiriwrite_version_revision FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($second_database_filename) . '_database_info LIMIT 1') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	@sqldata = $statement_handle->fetchrow_array();

	# Process the database information into a hash.

	%databaseinfo = (
		"DatabaseName"	=> decode_utf8($sqldata[0]),
		"Description"	=> decode_utf8($sqldata[1]),
		"Notes"		=> decode_utf8($sqldata[2]),
		"Categories"	=> decode_utf8($sqldata[3]),
		"Major"		=> decode_utf8($sqldata[4]),
		"Minor"		=> decode_utf8($sqldata[5]),
		"Revision"	=> decode_utf8($sqldata[6])
	);

	$statement_handle->finish();

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

	# Create the database structure (info and page tables);

	$statement_handle	= $database_handle->prepare('CREATE TABLE ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($dbfilename) . '_database_info (
			name varchar(256) primary key,
			description varchar(512), 
			notes mediumtext,
			categories varchar(512), 
			kiriwrite_version_major int(4), 
			kiriwrite_version_minor int(4), 
			kiriwrite_version_revision int(4)
	) DEFAULT CHARSET=utf8') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	$statement_handle 	= $database_handle->prepare('CREATE TABLE ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($dbfilename) . '_database_pages (
			filename varchar(256) primary key, 
			pagename varchar(512), 
			pagedescription varchar(512), 
			pagesection varchar(256),
			pagetemplate varchar(64),
			pagedata mediumtext,
			pagesettings int(1),
			lastmodified datetime
	) DEFAULT CHARSET=utf8') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	# Convert the values into SQL query formatted values and add an entry
	# to the kiriwrite_database_info table.

	$statement_handle = $database_handle->prepare('INSERT INTO ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($dbfilename) . '_database_info (name, description, notes, categories, kiriwrite_version_major, kiriwrite_version_minor, kiriwrite_version_revision) VALUES(
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

		# Check if a table with the filename already exists before using the
		# new filename.

		my $database_newexists		= $class->dbexists($dbnewfilename);

		if ($database_newexists eq 0){

			# The database filename exists so set the error value.

			$error = "DatabaseExists";
			return;

 		}

		# Rename the tables.

		$statement_handle = $database_handle->prepare('RENAME TABLE ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_info TO ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($dbnewfilename) . '_database_info, ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_pages TO ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($dbnewfilename) . '_database_pages');
		$statement_handle->execute();

	}

	# Get the current database information.

	$statement_handle = $database_handle->prepare('SELECT name FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($dbnewfilename) . '_database_info LIMIT 1') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	my @database_oldinfo	= $statement_handle->fetchrow_array();

	my $dboldname		= decode_utf8($database_oldinfo[0]);

	# Update the database information.

	$statement_handle = $database_handle->prepare('UPDATE ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($dbnewfilename) . '_database_info SET name = \'' . $class->convert($dbname) . '\',
	description = \'' . $class->convert($dbdescription) . '\',
	notes = \'' . $class->convert($dbnotes) . '\',
	categories = \'' . $class->convert($dbcategories) . '\'') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

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

	my @table_data;
	my $table_exists;

	# Check if the database with the filename given already exists.

	my $database_exists	= $class->dbexists($databasename);

	if ($database_exists eq 1){

		# The database does not exist so set the error value.

		$error = "DoesNotExist";
		return;

	}



	# Delete the database tables.

	$statement_handle = $database_handle->prepare('DROP TABLE ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($databasename) . '_database_info')  or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	# Check if the _database_pages table exists and delete it if it exists.

	$statement_handle = $database_handle->prepare('SHOW TABLES LIKE \'' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($databasename) . '_database_pages\'')  or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	while (@table_data = $statement_handle->fetchrow_array()){

		$table_exists = 1;

	}

	# Check if the _database_pages table really does exist.

	if ($table_exists eq 1){

		# the _database_pages table really does exist so delete it.

		$statement_handle = $database_handle->prepare('DROP TABLE ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($databasename) . '_database_pages')  or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
		$statement_handle->execute();

	}

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
	my $templatedb_exists = 0;
	my @templatedb_check;

	# Check if the template database exists.

	$statement_handle = $database_handle->prepare('SHOW TABLES LIKE \'' . $class->convert($options{"TablePrefix"}) . '_templates\'') or ( $error = "TemplateDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	while (@templatedb_check = $statement_handle->fetchrow_array()){

		$templatedb_exists = 1;

	}

	if (!$templatedb_exists){

		if (!$ignoremissing){

			$error = "TemplateDatabaseDoesNotExist";
			return;

		}

	}

}

sub disconnecttemplate{
#################################################################################
# disconnecttemplate: Disconnect from the template database.			#
#										#
# Usage:									#
#										#
# $dbmodule->disconnecttemplate();						#
#################################################################################

	# This subroutine is not used.

}

sub gettemplatelist{
#################################################################################
# gettemplatelist: Gets the list of templates.					#
#										#
# Usage:									#
#										#
# $dbmodule->gettemplatelist(options);						#
#										#
# options	Specifies the following options as a hash (in any order).	#
# 										#
# StartFrom	Specifies where the list of templates will start from.		#
# Limit		Specifies how many templates should be retrieved.		#
#################################################################################

	$error = "";
	$errorext = "";

	my $class		= shift;
	my ($passedoptions)	= @_;

	my $start_from		= $passedoptions->{"StartFrom"};
	my $limit		= $passedoptions->{"Limit"};

	if (defined($start_from)){

		if (!$limit){
			
			$limit = 0;

		}

		$statement_handle = $database_handle->prepare('SELECT filename FROM ' . $class->convert($options{"TablePrefix"}) . '_templates ORDER BY filename ASC LIMIT ' . $start_from . ',' .  $limit ) or ( $error = "TemplateDatabaseError", $errorext = $database_handle->errstr, return );
		$statement_handle->execute();		

	} else {

		$statement_handle = $database_handle->prepare('SELECT filename FROM ' . $class->convert($options{"TablePrefix"}) . '_templates ORDER BY filename ASC') or ( $error = "TemplateDatabaseError", $errorext = $database_handle->errstr, return );
		$statement_handle->execute();

	}

	my @database_template;
	my @templates_list;
	my $template_filename;

	while (@database_template = $statement_handle->fetchrow_array()){

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
# Reduced		Specifies if the reduced version of the template	#
#			information should be retrieved.			#
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
	my $reduced	= $passedoptions->{"Reduced"};

	if ($reduced && $reduced eq 1){

		$statement_handle = $database_handle->prepare('SELECT filename, templatename, templatedescription, datemodified FROM ' . $class->convert($options{"TablePrefix"}) . '_templates WHERE filename = \'' . $class->convert($filename) . '\'') or ( $error = "TemplateDatabaseError", $errorext = $database_handle->errstr, return );
		$statement_handle->execute();

	} else {

		$statement_handle = $database_handle->prepare('SELECT filename, templatename, templatedescription, templatelayout, datemodified FROM ' . $class->convert($options{"TablePrefix"}) . '_templates WHERE filename = \'' . $class->convert($filename) . '\'') or ( $error = "TemplateDatabaseError", $errorext = $database_handle->errstr, return );
		$statement_handle->execute();

	}

	while (@template_data = $statement_handle->fetchrow_array()){

		# Get certain values from the array.

		$template_filename 	= decode_utf8($template_data[0]);
		$template_name 		= decode_utf8($template_data[1]);
		$template_description 	= decode_utf8($template_data[2]);
		$template_layout	= decode_utf8($template_data[3]);
		$template_datemodified 	= decode_utf8($template_data[4]);

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

sub gettemplatecount{
#################################################################################
# gettemplatecount: Gets the count of templates in the template database.	#
#										#
# Usage:									#
#										#
# $dbmodule->gettemplatecount();						#
#################################################################################

 	$error = "";
 	$errorext = "";
 
 	my $class	= shift;
 
 	$statement_handle	= $database_handle->prepare('SELECT COUNT(*) FROM ' . $class->convert($options{"TablePrefix"}) . '_templates') or ( $error = "FilterDatabaseError", $errorext = $database_handle->errstr, return);
 	$statement_handle->execute();
 
 	my $count = $statement_handle->fetchrow_array();
 
 	return $count;

}

sub addtemplate{
#################################################################################
# addtemplate: Adds a template to the template database.			#
#										#
# Usage:									#
#										#
# $dbmodule->addtemplate(options);						#
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
	my @templatedb_check;
	my $templatedb_exists;
	my $blankfile = 0;

	my $template_filename		= $passedoptions->{"TemplateFilename"};
	my $template_name		= $passedoptions->{"TemplateName"};
	my $template_description	= $passedoptions->{"TemplateDescription"};
	my $template_layout		= $passedoptions->{"TemplateLayout"};

	# Check if the template database exists.

	$statement_handle = $database_handle->prepare('SHOW TABLES LIKE \'' . $class->convert($options{"TablePrefix"}) . '_templates\'') or ( $error = "TemplateDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	while (@templatedb_check = $statement_handle->fetchrow_array()){

		$templatedb_exists = 1;

	}

	# Check if the template database table exists and if it doesn't
	# then create the template database table.

	if (!$templatedb_exists){

		$statement_handle = $database_handle->prepare('CREATE TABLE ' . $class->convert($options{"TablePrefix"}) . '_templates (
			filename varchar(256) primary key,
			templatename varchar(512),
			templatedescription varchar(512),
			templatelayout mediumtext,
			datemodified datetime
		) DEFAULT CHARSET=utf8') or ( $error = "TemplateDatabaseError", $errorext = $database_handle->errstr, return );
		$statement_handle->execute();

	}

	# Check if the template already exists before adding.

	if (!$templatedb_exists){

		$statement_handle = $database_handle->prepare('SELECT filename FROM ' . $class->convert($options{"TablePrefix"}) . '_templates WHERE filename = \'' . $class->convert($template_filename) . '\' LIMIT 1') or ($blankfile = 1);

		if ($blankfile eq 0){

			$statement_handle->execute();

			while (@page_exists = $statement_handle->fetchrow_array()){

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

 	$statement_handle = $database_handle->prepare('INSERT INTO ' . $class->convert($options{"TablePrefix"}) . '_templates (filename, templatename, templatedescription, templatelayout, datemodified) VALUES(
  			\'' . $class->convert($template_filename) . '\',
  			\'' . $class->convert($template_name) . '\',
  			\'' . $class->convert($template_description) . '\',
  			\'' . $class->convert($template_layout) . '\',
  			\'' . $class->convert($template_date) . '\'
 	)') or ( $error = "TemplateDatabaseError", $errorext = $database_handle->errstr, return );
 	$statement_handle->execute();

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

	# Check if the template exists.

	$statement_handle = $database_handle->prepare('SELECT filename FROM ' . $class->convert($options{"TablePrefix"}) . '_templates WHERE filename = \'' . $class->convert($template_filename) . '\' LIMIT 1') or ( $error = "TemplateDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	while (@template_info = $statement_handle->fetchrow_array()){

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

	$statement_handle = $database_handle->prepare('UPDATE ' . $class->convert($options{"TablePrefix"}) . '_templates SET
		filename = \'' . $class->convert($new_template_filename) . '\',
		templatename = \'' . $class->convert($new_template_name) . '\',
		templatedescription = \'' . $class->convert($new_template_description) . '\',
		templatelayout = \'' . $class->convert($new_template_layout) . '\',
		datemodified = \'' . $class->convert($templatenewdate) . '\'
		WHERE filename = \'' . $class->convert($template_filename) . '\'
	') or ( $error = "TemplateDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

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

	$statement_handle = $database_handle->prepare('SELECT filename FROM ' . $class->convert($options{"TablePrefix"}) . '_templates WHERE filename = \'' . $class->convert($template_filename) . '\' LIMIT 1') or ( $error = "TemplateDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	while (@pagedata = $statement_handle->fetchrow_array()){

		$template_count++;

	}

	if ($template_count eq 0){

		# No pages were returned so return an error value.

		$error = "TemplateDoesNotExist";
		return;

	}

	# Delete the template from the template database.

	$statement_handle = $database_handle->prepare('DELETE FROM ' . $class->convert($options{"TablePrefix"}) . '_templates WHERE filename = \'' . $class->convert($template_filename) . '\'') or ( $error = "TemplateDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

}

#################################################################################
# Page subroutines.								#
#################################################################################

sub getpagecount{
#################################################################################
# getpagecount: Get the count of pages that are in the database.		#
#										#
# Usage:									#
#										#
# $dbmodule->getpagecount();							#
#################################################################################

	$error = "";
	$errorext = "";

	my $class	= shift;

	$statement_handle	= $database_handle->prepare('SELECT COUNT(*) FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_pages') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return);
	$statement_handle->execute();

	my $count = $statement_handle->fetchrow_array();

	return $count;

}

sub getpagelist{
#################################################################################
# getpagelist: Gets the list of pages from the database.			#
#										#
# Usage:									#
#										#
# $dbmodule->getpagelist(options);						#
#										#
# options	Specifies the following options as a hash (in any order).	#
#										#
# StartFrom	Start from the specified page in the database.			#
# Limit		Get the amount of pages given.					#
#################################################################################

	$error = "";
	$errorext = "";

	my $class	= shift;
	my ($passedoptions)	= shift;

	my $start_from	= $passedoptions->{"StartFrom"};
	my $limit	= $passedoptions->{"Limit"};
	
	if (defined($start_from)){

		if (!$limit){
			
			$limit = 0;

		}

		$statement_handle	= $database_handle->prepare('SELECT filename FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_pages LIMIT ' . $start_from . ',' . $limit) or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
		$statement_handle->execute();

	} else {

		$statement_handle	= $database_handle->prepare('SELECT filename FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_pages') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
		$statement_handle->execute();

	}

	my @database_pagefilenames;
	my @database_pagefilenames_final;

	# Process the collected pages.

	while (@database_pagefilenames = $statement_handle->fetchrow_array){

		# Add each page to the list of pages in the database.

		push(@database_pagefilenames_final, decode_utf8($database_pagefilenames[0]));

	}

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

	if ($page_reduced eq 1){

		$statement_handle	= $database_handle->prepare('SELECT filename, pagename, pagedescription, lastmodified FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
		$statement_handle->execute();

		# Check if the page exists in the database.

		while (@data_page = $statement_handle->fetchrow_array()){

			# Get the values from the array.

			$pagefilename 		= decode_utf8($data_page[0]);
			$pagename		= decode_utf8($data_page[1]);
			$pagedescription	= decode_utf8($data_page[2]);
			$pagelastmodified	= decode_utf8($data_page[3]);

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

		$statement_handle	= $database_handle->prepare('SELECT filename, pagename, pagedescription, pagesection, pagetemplate, pagedata, pagesettings, lastmodified FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
		$statement_handle->execute();

		# Check if the page exists in the database.

		while (@data_page = $statement_handle->fetchrow_array()){

			# Get the values from the array.

			$pagefilename 		= decode_utf8($data_page[0]);
			$pagename		= decode_utf8($data_page[1]);
			$pagedescription	= decode_utf8($data_page[2]);
			$pagesection		= decode_utf8($data_page[3]);
			$pagetemplate		= decode_utf8($data_page[4]);
			$pagedata		= decode_utf8($data_page[5]);
			$pagesettings		= decode_utf8($data_page[6]);
			$pagelastmodified	= decode_utf8($data_page[7]);

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

	$statement_handle = $database_handle->prepare('SELECT filename FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
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

	$statement_handle = $database_handle->prepare('INSERT INTO ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_pages (filename, pagename, pagedescription, pagesection, pagetemplate, pagedata, pagesettings, lastmodified) VALUES (
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

	$statement_handle = $database_handle->prepare('SELECT filename FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
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

	$statement_handle = $database_handle->prepare('DELETE FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\'') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
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

	$statement_handle = $database_handle->prepare('SELECT filename FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
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

		$statement_handle = $database_handle->prepare('SELECT filename FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_pages WHERE filename = \'' . $class->convert($page_newfilename) . '\' LIMIT 1') or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
		$statement_handle->execute();

		# Check if a page really is using the new filename.

		while (@page_info = $statement_handle->fetchrow_array()){

			# The page information is found.

			$page_found = 1;

		}

		if ($page_found eq 1){

			$error = "PageAlreadyExists";
			return;

		}

	}

	# Get the current date.

 	my ($created_second, $created_minute, $created_hour, $created_day, $created_month, $created_year, $created_weekday, $created_yearday, $created_dst) = localtime;
 	my $page_date = $created_year . '-' . $created_month . '-' . $created_day . ' ' . $created_hour . ':' . $created_minute . ':' . $created_second;

	# Edit the selected page.

	$statement_handle = $database_handle->prepare('UPDATE ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_pages SET filename = \'' . $class->convert($page_newfilename) . '\', pagename = \'' . $class->convert($page_newname) . '\', pagedescription = \'' . $class->convert($page_newdescription) . '\', pagesection = \'' . $class->convert($page_newsection) . '\', pagetemplate = \'' . $class->convert($page_newtemplate) . '\', pagedata = \'' . $class->convert($page_newcontent) . '\', pagedata = \'' . $class->convert($page_newcontent) . '\', pagesettings = \'' . $class->convert($page_newsettings) . '\', lastmodified = \'' . $page_date . '\' WHERE filename = \'' . $class->convert($page_filename) . '\'')  or ( $error = "DatabaseError", $errorext = $database_handle->errstr, return );
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

	$statement_handle = $database_handle->prepare('SELECT filename, pagename, pagedescription, pagesection, pagetemplate, pagedata, pagesettings, lastmodified FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "OldDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	# Check if the page really does exist.

	while (@page_info = $statement_handle->fetchrow_array()){

		# Get the values from the array.

		$pagefilename 		= decode_utf8($page_info[0]);
		$pagename		= decode_utf8($page_info[1]);
		$pagedescription	= decode_utf8($page_info[2]);
		$pagesection		= decode_utf8($page_info[3]);
		$pagetemplate		= decode_utf8($page_info[4]);
		$pagedata		= decode_utf8($page_info[5]);
		$pagesettings		= decode_utf8($page_info[6]);
		$pagelastmodified	= decode_utf8($page_info[7]);

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

	$statement_handle = $database_handle->prepare('SELECT filename FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($second_database_filename) . '_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "NewDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	while (@page_info = $statement_handle->fetchrow_array()){

		$page_found = 1;

	}

	# Check if the page really does exist.

	if ($page_found){

		$error = "PageAlreadyExists";
		return;

	}

	# Add the page to the new database.

	$statement_handle = $database_handle->prepare('INSERT INTO ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($second_database_filename) . '_database_pages (filename, pagename, pagedescription, pagesection, pagetemplate, pagedata, pagesettings, lastmodified) VALUES (
		\'' . $class->convert($database_page{"PageFilename"}) . '\',
		\'' . $class->convert($database_page{"PageName"}) . '\',
		\'' . $class->convert($database_page{"PageDescription"}) . '\',
		\'' . $class->convert($database_page{"PageSection"}) . '\',
		\'' . $class->convert($database_page{"PageTemplate"}) . '\',
		\'' . $class->convert($database_page{"PageContent"}) . '\',
		\'' . $class->convert($database_page{"PageSettings"}) . '\',
		\'' . $class->convert($database_page{"PageLastModified"}) . '\'
	)') or ( $error = "NewDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	# Delete the page from the old database.

	$statement_handle = $database_handle->prepare('DELETE FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_pages WHERE filename = \'' . $class->convert($database_page{"PageFilename"}) . '\'') or ( $error = "OldDatabaseError", $errorext = $database_handle->errstr, return );
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

	$statement_handle = $database_handle->prepare('SELECT filename, pagename, pagedescription, pagesection, pagetemplate, pagedata, pagesettings, lastmodified FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($database_filename) . '_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "OldDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	# Check if the page really does exist.

	while (@page_info = $statement_handle->fetchrow_array()){

		# Get the values from the array.

		$pagefilename 		= decode_utf8($page_info[0]);
		$pagename		= decode_utf8($page_info[1]);
		$pagedescription	= decode_utf8($page_info[2]);
		$pagesection		= decode_utf8($page_info[3]);
		$pagetemplate		= decode_utf8($page_info[4]);
		$pagedata		= decode_utf8($page_info[5]);
		$pagesettings		= decode_utf8($page_info[6]);
		$pagelastmodified	= decode_utf8($page_info[7]);

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

	$statement_handle = $database_handle->prepare('SELECT filename FROM ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($second_database_filename) . '_database_pages WHERE filename = \'' . $class->convert($page_filename) . '\' LIMIT 1') or ( $error = "NewDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	while (@page_info = $statement_handle->fetchrow_array()){

		$page_found = 1;

	}
	
	# Check if the page really does exist.

	if ($page_found){

		$error = "PageAlreadyExists";
		return;

	}

	# Add the page to the new database.

	$statement_handle = $database_handle->prepare('INSERT INTO ' . $class->convert($options{"TablePrefix"}) . '_' . $class->convert($second_database_filename) . '_database_pages (filename, pagename, pagedescription, pagesection, pagetemplate, pagedata, pagesettings, lastmodified) VALUES (
		\'' . $class->convert($database_page{"PageFilename"}) . '\',
		\'' . $class->convert($database_page{"PageName"}) . '\',
		\'' . $class->convert($database_page{"PageDescription"}) . '\',
		\'' . $class->convert($database_page{"PageSection"}) . '\',
		\'' . $class->convert($database_page{"PageTemplate"}) . '\',
		\'' . $class->convert($database_page{"PageContent"}) . '\',
		\'' . $class->convert($database_page{"PageSettings"}) . '\',
		\'' . $class->convert($database_page{"PageLastModified"}) . '\'
	)') or ( $error = "NewDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

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
	my @filterdb_check;
	my $filterdb_exists = 0;

	# Check if the template database exists.

	$statement_handle = $database_handle->prepare('SHOW TABLES LIKE \'' . $class->convert($options{"TablePrefix"}) . '_filters\'') or ( $error = "FilterDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	while (@filterdb_check = $statement_handle->fetchrow_array()){

		$filterdb_exists = 1;

	}

	if (!$filterdb_exists){

		if (!$ignoremissing){

			$error = "FilterDatabaseDoesNotExist";
			return;

		}

	}

}

sub disconnectfilter{
#################################################################################
# disconnectfilter: Disconnect from the filter database.			#
#										#
# Usage:									#
#										#
# $dbmodule->disconnectfilter();						#
#################################################################################

	# This subroutine is not used.

}

sub getfilterlist{
#################################################################################
# getfilterlist: Gets the list of filters in the filter database.		#
#										#
# Usage:									#
#										#
# $dbmodule->getfilterlist(options);						#
#										#
# options	Specifies the following options as a hash (in any order).	#
#										#
# StartFrom	Specifies where the list of filters should start from.		#
# Limit		Specifies the amount of the filters to get.			#
#################################################################################

	$error = "";
	$errorext = "";

	my $class = shift;
	my ($passedoptions)	= shift;

	my @filter_list;
	my @filter_data;

	my $start_from	= $passedoptions->{"StartFrom"};
	my $limit	= $passedoptions->{"Limit"};

	if (defined($start_from)){

		if (!$limit){
			
			$limit = 0;

		}

  		$statement_handle	= $database_handle->prepare('SELECT id, priority FROM ' . $class->convert($options{"TablePrefix"}) . '_filters ORDER BY priority ASC LIMIT ' . $start_from . ',' . $limit) or ( $error = "FilterDatabaseError", $errorext = $database_handle->errstr, return );
 		$statement_handle->execute();

	} else {
 
  		$statement_handle	= $database_handle->prepare('SELECT id, priority FROM ' . $class->convert($options{"TablePrefix"}) . '_filters ORDER BY priority ASC') or ( $error = "FilterDatabaseError", $errorext = $database_handle->errstr, return );
  		$statement_handle->execute();

	}

	while (@filter_data = $statement_handle->fetchrow_array()){

		# Add the filter to the list of available filters.

		push(@filter_list, decode_utf8($filter_data[0]));

	}

	return @filter_list;

}

sub getfiltercount{
#################################################################################
# getfiltercount: Gets the count of filters in the filters database.		#
#										#
# Usage:									#
#										#
# $dbmodule->getfiltercount();							#
#################################################################################

	$error = "";
	$errorext = "";

	my $class	= shift;

	$statement_handle	= $database_handle->prepare('SELECT COUNT(*) FROM ' . $class->convert($options{"TablePrefix"}) . '_filters') or ( $error = "FilterDatabaseError", $errorext = $database_handle->errstr, return);
	$statement_handle->execute();

	my $count = $statement_handle->fetchrow_array();

	return $count;

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
# Reduced	Specifies to get the reduced version of the filter information.	#
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
	my $reduced		= $passedoptions->{"Reduced"};

	if ($reduced && $reduced eq 1){

		$statement_handle = $database_handle->prepare('SELECT id, priority, findsetting, replacesetting, enabled FROM ' . $class->convert($options{"TablePrefix"}) . '_filters where id = \'' . $class->convert($filter_id) . '\'') or ( $error = "FilterDatabaseError", $errorext = $database_handle->errstr, return );
		$statement_handle->execute();

	} else {

		$statement_handle = $database_handle->prepare('SELECT id, priority, findsetting, replacesetting, enabled, notes FROM ' . $class->convert($options{"TablePrefix"}) . '_filters where id = \'' . $class->convert($filter_id) . '\'') or ( $error = "FilterDatabaseError", $errorext = $database_handle->errstr, return );
		$statement_handle->execute();

	}

	# Get the filter information.

	while (@filter_data = $statement_handle->fetchrow_array()){

		$filter_info{"FilterID"}	= decode_utf8($filter_data[0]);
		$filter_info{"FilterPriority"}	= decode_utf8($filter_data[1]);
		$filter_info{"FilterFind"}	= decode_utf8($filter_data[2]);
		$filter_info{"FilterReplace"}	= decode_utf8($filter_data[3]);
		$filter_info{"FilterEnabled"}	= decode_utf8($filter_data[4]);
		$filter_info{"FilterNotes"}	= decode_utf8($filter_data[5]);

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
# Enabled	Specifies if the filter should be enabled.			#
# Notes		Specifies the notes to use.					#
#################################################################################

	$error = "";
	$errorext = "";

	# Get the values passed to the subroutine.

	my $class = shift;
	my ($passedoptions) = @_;

	# Define some variables for later.

	my @database_filters;
	my @filterdb_check;
	my @filterid_list;
	my @filterid_check;
	my $nofiltertable = 0;
	my $filter_found = 0;
	my $filter_count = 0;
	my $filterdb_exists = 0;
	my $filter_id;
	my $new_id;

	# Get the values from the hash.

	my $filter_find		= $passedoptions->{"FindFilter"};
	my $filter_replace	= $passedoptions->{"ReplaceFilter"};
	my $filter_priority	= $passedoptions->{"Priority"};
	my $filter_enabled	= $passedoptions->{"Enabled"};
	my $filter_notes	= $passedoptions->{"Notes"};

	# Check if the template database exists.

	$statement_handle = $database_handle->prepare('SHOW TABLES LIKE \'' . $class->convert($options{"TablePrefix"}) . '_filters\'') or ( $error = "FilterDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	while (@filterdb_check = $statement_handle->fetchrow_array()){

		$filterdb_exists = 1;

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

	if (!$filter_enabled){

		$filter_enabled = "";

	}

	# Check if there is really no filter table.

	if (!$filterdb_exists){

		# Create the filter database table.

		$statement_handle = $database_handle->prepare('CREATE TABLE ' . $class->convert($options{"TablePrefix"}) . '_filters (
		        id int(7) primary key,
        		priority int(5),
        		findsetting varchar(1024),
        		replacesetting varchar(1024),
        		notes text
		) DEFAULT CHARSET=utf8') or ( $error = "FilterDatabaseError", $errorext = $database_handle->errstr, return );
		$statement_handle->execute();

	}

	# Find the lowest filter identification number available.

	$statement_handle = $database_handle->prepare('SELECT id FROM ' . $class->convert($options{"TablePrefix"}) . '_filters ORDER BY id ASC') or ( $error = "FilterDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	while (@database_filters = $statement_handle->fetchrow_array()){

		$filter_id	= decode_utf8($database_filters[0]);

		# Add the filter identification to the list of filter IDs.

		push(@filterid_list, $filter_id);

	}

	$filter_id = "";

	# Process each filter looking for a blank available filter.

	foreach $filter_id (@filterid_list){

		# Check the next filter ID to see if it's blank.

		$new_id = $filter_id + 1;

		$statement_handle = $database_handle->prepare('SELECT id FROM ' . $class->convert($options{"TablePrefix"}) . '_filters WHERE id = \'' . $class->convert($new_id) . '\'') or ( $error = "FilterDatabaseError", $errorext = $database_handle->errstr, return );
		$statement_handle->execute();

		# Get the filter identification number.

		while (@filterid_check = $statement_handle->fetchrow_array()){

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

	$statement_handle = $database_handle->prepare('INSERT INTO ' . $class->convert($options{"TablePrefix"}) . '_filters (id, priority, findsetting, replacesetting, notes) VALUES (
		\'' . $class->convert($new_id) . '\',
		\'' . $class->convert($filter_priority) . '\',
		\'' . $class->convert($filter_find) . '\',
		\'' . $class->convert($filter_replace) .'\',
		\'' . $class->convert($filter_notes) . '\'
	)') or ( $error = "FilterDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

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
# NewEnabled		Specifies if the filter is enabled.			#
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
	my $filter_enabled	= $passedoptions->{"NewEnabled"};
	my $filter_newnotes	= $passedoptions->{"NewFilterNotes"};

	# Check if the filter exists before editing it.

	$statement_handle = $database_handle->prepare('SELECT id FROM ' . $class->convert($options{"TablePrefix"}) . '_filters where id = \'' . $class->convert($filter_id) . '\'') or ( $error = "FilterDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	# Check if the filter exists.

	while (@filter_data = $statement_handle->fetchrow_array()){

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

	$statement_handle = $database_handle->prepare('UPDATE ' . $class->convert($options{"TablePrefix"}) . '_filters SET
		findsetting = \'' . $class->convert($filter_newfind) . '\',
		replacesetting = \'' . $class->convert($filter_newreplace) . '\',
		priority = \'' . $class->convert($filter_newpriority) . '\',
		enabled = \'' . $class->convert($filter_enabled) . '\',
		notes = \'' . $class->convert($filter_newnotes) . '\'
	WHERE id = \'' . $class->convert($filter_id) . '\'') or ( $error = "FilterDatabaseError", $errorext = $database_handle->errstr, return );	
	$statement_handle->execute();

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

	$statement_handle = $database_handle->prepare('SELECT id FROM ' . $class->convert($options{"TablePrefix"}) . '_filters where id = \'' . $class->convert($filter_id) . '\'') or ( $error = "FilterDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

	while (@filter_data = $statement_handle->fetchrow_array()){

		$filter_exists = 1;

	}

	# Check to see if the filter really does exist.

	if (!$filter_exists){

		$error = "FilterDoesNotExist";
		return;

	}

	# Delete the filter from the filter database.

	$statement_handle = $database_handle->prepare('DELETE FROM ' . $class->convert($options{"TablePrefix"}) . '_filters where id = \'' . $class->convert($filter_id) . '\'') or ( $error = "FilterDatabaseError", $errorext = $database_handle->errstr, return );
	$statement_handle->execute();

}

1;