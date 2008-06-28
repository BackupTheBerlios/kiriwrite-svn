package Modules::System::Template;

use Modules::System::Common;
use strict;
use warnings;
use Exporter;

our @ISA = qw(Exporter);
our @EXPORT = qw(kiriwrite_template_list kiriwrite_template_add kiriwrite_template_edit kiriwrite_template_delete);

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

		$main::kiriwrite_dbmodule->connect();

		# Connect to the template database.

		$main::kiriwrite_dbmodule->connecttemplate(1);

		# Check if any errors had occured.

		if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so
			# return an error.

			kiriwrite_error("templatedatabaseinvalidpermissions");

		}

		$main::kiriwrite_dbmodule->addtemplate({ TemplateFilename => $templatefilename, TemplateName => $templatename, TemplateDescription => $templatedescription, TemplateLayout => $templatelayout });

		if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

			# A database error has occured so return an error along
			# with the extended error information.

			kiriwrite_error("templatedatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so return
			# an error.

			kiriwrite_error("templatedatabaseinvalidpermissions");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplatePageExists"){

			# The template page already exists so return an error.

			kiriwrite_error("templatefilenameexists");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseUncreateable"){

			# The template databases is uncreatable so return an error.

			kiriwrite_error("templatedatabasenotcreated");

		}

		$main::kiriwrite_dbmodule->disconnecttemplate();

		# Disconnect from the template server.

		$main::kiriwrite_dbmodule->disconnect();

		# Print out the confirmation message.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{template}{addedtemplate}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{template}{addedtemplatemessage}, $templatename));
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=template", { Text => $main::kiriwrite_lang{template}{returntemplatelist} });
		return $main::kiriwrite_presmodule->grab();

	} else {
		# No confirmation was made, so print out a form for adding a template.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{template}{addtemplate}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addhiddendata("mode", "template");
		$main::kiriwrite_presmodule->addhiddendata("action", "add");
		$main::kiriwrite_presmodule->addhiddendata("confirm", 1);
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->starttable("", { CellSpacing => 0, CellPadding => 5 });

		$main::kiriwrite_presmodule->startheader();
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{setting}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{value}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->endheader();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{template}{templatename});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("templatename", { Size => 64, MaxLength => 512 });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{template}{templatedescription});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("templatedescription", { Size => 64, MaxLength => 512 });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{template}{templatefilename});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("templatefilename", { Size => 32, MaxLength => 64 });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{template}{templatelayout});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addtextbox("templatelayout", { Columns => $main::kiriwrite_config{"display_textareacols"}, Rows => $main::kiriwrite_config{"display_textarearows"} });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startbox("datalist");
		$main::kiriwrite_presmodule->addboldtext($main::kiriwrite_lang{common}{tags});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{common}{pagecontent});
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
		$main::kiriwrite_presmodule->endtable();

		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{template}{addtemplatebutton});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addreset($main::kiriwrite_lang{common}{clearvalues});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=template" , { Text => $main::kiriwrite_lang{template}{returntemplatelist} });

		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->endform();

		return $main::kiriwrite_presmodule->grab();

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

	$main::kiriwrite_dbmodule->connect();

	# Check if any errors occured while connecting to the database server.

	if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

		# A database connection error has occured so return
		# an error.

		kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

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

		$main::kiriwrite_dbmodule->connecttemplate();

		# Check if any errors had occured.

		if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so
			# return an error.

			kiriwrite_error("templatedatabaseinvalidpermissions");

		}

		# Edit the template.

		$main::kiriwrite_dbmodule->edittemplate({ TemplateFilename => $templatefilename, NewTemplateFilename => $templatenewfilename, NewTemplateName => $templatenewname, NewTemplateDescription => $templatenewdescription, NewTemplateLayout => $templatelayout });

		# Check if any error occured while editing the template.

		if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

			# A database error has occured, so return an error.

			kiriwrite_error("templatedatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so return
			# an error.

			kiriwrite_error("templatedatabaseinvalidpermissions");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

			# The template does not exist, so process the next template.

			kiriwrite_error("templatedoesnotexist");

		}

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		# Disconnect from the template database.

		$main::kiriwrite_dbmodule->disconnecttemplate();

		# Append a link so that the user can return to the templates list.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{template}{editedtemplate}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{template}{editedtemplatemessage}, $templatenewname));
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=template", { Text => $main::kiriwrite_lang{template}{returntemplatelist} });

	} else {

		# Connect to the template database.

		$main::kiriwrite_dbmodule->connecttemplate();

		# Check if any errors had occured.

		if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so
			# return an error.

			kiriwrite_error("templatedatabaseinvalidpermissions");

		}

		# Get the template information.

		my %template_info = $main::kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $templatefilename });

		# Check if any error occured while getting the template information.

		if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

			# A database error has occured, so return an error.

			kiriwrite_error("templatedatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

			# The template does not exist, so return an error.

			kiriwrite_error("templatedoesnotexist");

		}

		# Disconnect from the template database.

		$main::kiriwrite_dbmodule->disconnecttemplate();

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

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{template}{edittemplate}, { Style => "pageheader" });
 		$main::kiriwrite_presmodule->addlinebreak();
 		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addhiddendata("mode", "template");
		$main::kiriwrite_presmodule->addhiddendata("action", "edit");
		$main::kiriwrite_presmodule->addhiddendata("confirm", 1);
		$main::kiriwrite_presmodule->addhiddendata("template", $template_filename);
		$main::kiriwrite_presmodule->starttable("", { CellSpacing => 0, CellPadding => 5});

		$main::kiriwrite_presmodule->startheader();
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{setting}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{value}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->endheader();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{template}{templatename});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("newname", { Size => 64, MaxLength => 512, Value => $template_name });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{template}{templatedescription});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("newdescription", { Size => 64, MaxLength => 512, Value => $template_description });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{template}{templatefilename});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addinputbox("newfilename", { Size => 32, MaxLength => 64, Value => $template_filename });
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->endrow();

		$main::kiriwrite_presmodule->startrow();
		$main::kiriwrite_presmodule->addcell("tablecell1");
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{template}{templatelayout});
		$main::kiriwrite_presmodule->endcell();
		$main::kiriwrite_presmodule->addcell("tablecell2");
		$main::kiriwrite_presmodule->addtextbox("newlayout", { Columns => $main::kiriwrite_config{"display_textareacols"}, Rows => $main::kiriwrite_config{"display_textarearows"}, Value => $template_layout});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startbox("datalist");
		$main::kiriwrite_presmodule->addboldtext($main::kiriwrite_lang{common}{tags});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{common}{pagecontent});
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

		$main::kiriwrite_presmodule->endtable();

		$main::kiriwrite_presmodule->addlinebreak();

		$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{template}{edittemplatebutton});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addreset($main::kiriwrite_lang{common}{restorecurrent});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=template", { Text => $main::kiriwrite_lang{template}{returntemplatelist} });

		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->endform();

	}

	# Disconnect from the database server.

	$main::kiriwrite_dbmodule->disconnect();

	return $main::kiriwrite_presmodule->grab();

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

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Check if the template database exists and the file permissions
		# are valid and return an error if they aren't.

		$main::kiriwrite_dbmodule->connecttemplate();

		if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseDoesNotExist"){

			# The template database does not exist so write a warning
			# message.

			kiriwrite_error("templatedatabasemissing");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so
			# return an error.

			kiriwrite_error("templatedatabaseinvalidpermissions");

		}

		my %template_info = $main::kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $template_filename });

		# Check if any error occured while getting the template information.

		if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

			# A database error has occured, so return an error.

			kiriwrite_error("templatedatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

			# The template does not exist, so return an error.

			kiriwrite_error("templatedoesnotexist");

		}

		# Delete the selected template.

		$main::kiriwrite_dbmodule->deletetemplate({ TemplateFilename => $template_filename });

		# Check if any error occured while deleting the template.

		if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

 			# A database error has occured, so return an error.

			kiriwrite_error("templatedatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

			# The template does not exist, so process the next template.

			kiriwrite_error("templatedoesnotexist");

		}

		$main::kiriwrite_dbmodule->disconnecttemplate();

		# Get the deleted database name.

		my $database_template_name = $template_info{"TemplateName"};

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{template}{deletedtemplate}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{template}{deletedtemplatemessage}, $database_template_name) );
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=template", { Text => $main::kiriwrite_lang{template}{returntemplatelist} });

		return $main::kiriwrite_presmodule->grab();

	} elsif ($template_confirm eq 0) {

		# The template confirm value is 0 (previously blank and then set to 0), so
		# write out a form asking the user to confirm the deletion of the template.

		# Connect to the database server.

		$main::kiriwrite_dbmodule->connect();

		# Check if any errors occured while connecting to the database server.

		if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

			# A database connection error has occured so return
			# an error.

			kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		# Connect to the template database.

		$main::kiriwrite_dbmodule->connecttemplate();

		if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseDoesNotExist"){

			# The template database does not exist so write a warning
			# message.

			kiriwrite_error("templatedatabasemissing");

		} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

			# The template database has invalid permissions set so
			# return an error.

			kiriwrite_error("templatedatabaseinvalidpermissions");

		}

		my %template_info = $main::kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $template_filename });

		if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

			# A database error has occured, so return an error.

			kiriwrite_error("templatedatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

			# The template does not exist, so return an error.

			kiriwrite_error("templatedoesnotexist");

		}

		my $template_data_filename	= $template_info{"TemplateFilename"};
		my $template_data_name		= $template_info{"TemplateName"};

		$main::kiriwrite_dbmodule->disconnecttemplate();

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();

		# Write out the confirmation form.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{template}{deletetemplate}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "POST");
		$main::kiriwrite_presmodule->startbox();
		$main::kiriwrite_presmodule->addhiddendata("mode", "template");
		$main::kiriwrite_presmodule->addhiddendata("template", $template_filename);
		$main::kiriwrite_presmodule->addhiddendata("action", "delete");
		$main::kiriwrite_presmodule->addhiddendata("confirm", 1);
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addtext(kiriwrite_language($main::kiriwrite_lang{template}{deletetemplatemessage}, $template_data_name, $template_data_filename));
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addsubmit($main::kiriwrite_lang{template}{deletetemplatebutton});
		$main::kiriwrite_presmodule->addtext(" | ");
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=template", { Text => $main::kiriwrite_lang{template}{deletetemplatereturntolist} });
		$main::kiriwrite_presmodule->endbox();
		$main::kiriwrite_presmodule->endform();

		return $main::kiriwrite_presmodule->grab();

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
# kiriwrite_template_list([browsenumber]);					#
#										#
# browsenumber	Specifies the page browse number to use.			#
#################################################################################

	# Define certain values for later.

	my $template_browsenumber	= shift;

	my %template_info;

	my @templates_list;

	my $template;
	my $template_filename 		= "";
	my $template_filename_list	= "";
	my $template_name		= "";
	my $template_description 	= "";
	my $template_data		= "";

	my $template_split	= $main::kiriwrite_config{"display_templatecount"};
	my $template_list	= 0;

	my $template_count = 0;

	my $template_style = 0;
	my $template_stylename = "";

	my $templatewarning = "";

	# Connect to the database server.

	$main::kiriwrite_dbmodule->connect();

	# Check if any errors occured while connecting to the database server.

	if ($main::kiriwrite_dbmodule->geterror eq "DatabaseConnectionError"){

		# A database connection error has occured so return
		# an error.

		kiriwrite_error("databaseconnectionerror", $main::kiriwrite_dbmodule->geterror(1));

	}

	# Connect to the template database.

	$main::kiriwrite_dbmodule->connecttemplate();

	# Check if any errors had occured.

	if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseDoesNotExist"){

		# The template database does not exist so write a warning
		# message.

		$templatewarning = $main::kiriwrite_lang{template}{templatedatabasedoesnotexist};

	} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseInvalidPermissionsSet"){

		# The template database has invalid permissions set so
		# return an error.

		kiriwrite_error("templatedatabaseinvalidpermissions");

	} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

		# A database error occured while getting the list of
		# templates so return an error with the extended
		# error information.

		kiriwrite_error("templatedatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

	}

	# Get the list of template databases.

	if (!$templatewarning){

		# Get the total count of filters in the filter database.

		my $template_total_count	= $main::kiriwrite_dbmodule->gettemplatecount;

		# Check if any errors occured while getting the count of filters.

		if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

			# A database error has occured with the filter database.

			kiriwrite_error("templatedatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

		}

		if (!$template_browsenumber || $template_browsenumber eq 0){

			$template_browsenumber = 1;

		}

		# Check if the template browse number is valid and if it isn't
		# then return an error.

		my $kiriwrite_browsenumber_length_check		= kiriwrite_variablecheck($template_browsenumber, "maxlength", 7, 1);
		my $kiriwrite_browsenumber_number_check		= kiriwrite_variablecheck($template_browsenumber, "numbers", 0, 1);

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

		if ($template_total_count ne 0){

			if ($template_total_count eq $template_split){

				$template_list = int(($template_total_count / $template_split));

			} else {

				$template_list = int(($template_total_count / $template_split) + 1);

			}

		}

		my $start_from = ($template_browsenumber - 1) * $template_split;

		@templates_list = $main::kiriwrite_dbmodule->gettemplatelist({ StartFrom => $start_from, Limit => $template_split });

	}

	# Check if any errors had occured.

	if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

		# A database error occured while getting the list
		# of templates so return an error with the 
		# extended error information.

		kiriwrite_error("templatedatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

	}

	my $template_list_count;

	# Check if any templates are in the database and if there isn't
	# then write a message saying that there are no templates in the
	# database.

	if (!@templates_list && $template_browsenumber > 1){

		# There were no values given for the page browse
		# number given so write a message saying that
		# there were no pages for the page browse number
		# given.

		$main::kiriwrite_presmodule->clear();
		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{template}{viewtemplates}, { Style => "pageheader" });
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->startbox("errorbox");
		$main::kiriwrite_presmodule->enterdata($main::kiriwrite_lang{template}{notemplatesinpagebrowse});
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=template", { Text => $main::kiriwrite_lang{template}{returntofirstpagebrowse} });
		$main::kiriwrite_presmodule->endbox();

		# Disconnect from the database server.

		$main::kiriwrite_dbmodule->disconnect();
		$main::kiriwrite_dbmodule->disconnecttemplate();

		return $main::kiriwrite_presmodule->grab();

	} elsif (!@templates_list && !$templatewarning){
		$templatewarning = $main::kiriwrite_lang{template}{notemplatesavailable};
	}

	# Process the templates into a template list.

	$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{template}{viewtemplates}, { Style => "pageheader" });
	$main::kiriwrite_presmodule->addlinebreak();
	$main::kiriwrite_presmodule->addlinebreak();

	if ($templatewarning){

		$main::kiriwrite_presmodule->startbox("errorbox");
		$main::kiriwrite_presmodule->addtext($templatewarning);
		$main::kiriwrite_presmodule->endbox();

	} else {

		if (!$template_browsenumber || $template_browsenumber eq 0){

			$template_browsenumber = 1;

		}

		# Check if the template browse number is valid and if it isn't
		# then return an error.

		my $kiriwrite_browsenumber_length_check		= kiriwrite_variablecheck($template_browsenumber, "maxlength", 7, 1);
		my $kiriwrite_browsenumber_number_check		= kiriwrite_variablecheck($template_browsenumber, "numbers", 0, 1);

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

		# Start a form for using the template browsing list with.

		$main::kiriwrite_presmodule->startform($main::kiriwrite_env{"script_filename"}, "GET");
		$main::kiriwrite_presmodule->addhiddendata("mode", "template");

		# Write out the template browsing list.

		$main::kiriwrite_presmodule->addtext($main::kiriwrite_lang{template}{showlistpage});
		$main::kiriwrite_presmodule->addselectbox("browsenumber");

		# Write out the list of available pages to browse.

		if (!$template_list_count){

			$template_list_count = 0;

		}

		while ($template_list_count ne $template_list){

			$template_list_count++;

			if ($template_list_count eq 1 && !$template_browsenumber){

				$main::kiriwrite_presmodule->addoption($template_list_count, { Value => $template_list_count, Selected => 1 });

			} else {

				if ($template_browsenumber eq $template_list_count){

					$main::kiriwrite_presmodule->addoption($template_list_count, { Value => $template_list_count, Selected => 1 });

				} else {

					$main::kiriwrite_presmodule->addoption($template_list_count, { Value => $template_list_count });

				}

			}

		}

		$main::kiriwrite_presmodule->endselectbox();
		$main::kiriwrite_presmodule->addbutton("action", { Value => "view", Description => $main::kiriwrite_lang{template}{show} });		

		if ($template_list ne $template_browsenumber){

			$main::kiriwrite_presmodule->addtext(" | ");
			$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=template&action=view&browsenumber=" . ($template_browsenumber + 1), { Text => $main::kiriwrite_lang{template}{nextpage} });

		}

		# Check if the filter browse number is not blank and
		# not set as 0 and hide the Previous page link if
		# it is.

		if ($template_browsenumber > 1){

			$main::kiriwrite_presmodule->addtext(" | ");
			$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=template&action=view&browsenumber=" . ($template_browsenumber - 1), { Text => $main::kiriwrite_lang{template}{previouspage} });

		}

		$main::kiriwrite_presmodule->addlinebreak();
		$main::kiriwrite_presmodule->addlinebreak();

		$main::kiriwrite_presmodule->starttable("", { CellPadding => 5, CellSpacing => 0 });
		$main::kiriwrite_presmodule->startheader();
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{template}{templatefilename}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{template}{templatename}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{template}{templatedescription}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->addheader($main::kiriwrite_lang{common}{options}, { Style => "tablecellheader" });
		$main::kiriwrite_presmodule->endheader();

		foreach $template (@templates_list){

			# Get the template data.

			%template_info = $main::kiriwrite_dbmodule->gettemplateinfo({ TemplateFilename => $template, Reduced => 1 });

			# Check if any errors occured while trying to get the template
			# data.

			if ($main::kiriwrite_dbmodule->geterror eq "TemplateDatabaseError"){

				# A database error has occured, so return an error.

				kiriwrite_error("templatedatabaseerror", $main::kiriwrite_dbmodule->geterror(1));

			} elsif ($main::kiriwrite_dbmodule->geterror eq "TemplateDoesNotExist"){

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

			$main::kiriwrite_presmodule->startrow();
			$main::kiriwrite_presmodule->addcell($template_stylename);
			$main::kiriwrite_presmodule->addtext($template_info{"TemplateFilename"});
			$main::kiriwrite_presmodule->endcell();
			$main::kiriwrite_presmodule->addcell($template_stylename);

			# Check if the template name is blank and if it is
			# write a message to say there's no name for the
			# template.

			if (!$template_info{"TemplateName"}){
				$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{blank}{noname});
			} else {
				$main::kiriwrite_presmodule->addtext($template_info{"TemplateName"});
			}

			$main::kiriwrite_presmodule->endcell();
			$main::kiriwrite_presmodule->addcell($template_stylename);

			# Check if the template description is blank and if
			# it is then write a message to say there's no
			# description for the template.

			if (!$template_info{"TemplateDescription"}){
				$main::kiriwrite_presmodule->additalictext($main::kiriwrite_lang{blank}{nodescription});
			} else {
				$main::kiriwrite_presmodule->addtext($template_info{"TemplateDescription"});
			}

			$main::kiriwrite_presmodule->endcell();
			$main::kiriwrite_presmodule->addcell($template_stylename);
			$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=template&action=edit&template=" . $template_info{"TemplateFilename"}, { Text => $main::kiriwrite_lang{options}{edit} });
			$main::kiriwrite_presmodule->addlink($main::kiriwrite_env{"script_filename"} . "?mode=template&action=delete&template=" . $template_info{"TemplateFilename"}, { Text => $main::kiriwrite_lang{options}{delete} });
			$main::kiriwrite_presmodule->endcell();
			$main::kiriwrite_presmodule->endrow();

		}

		$main::kiriwrite_presmodule->endtable();
		$main::kiriwrite_presmodule->endform();

	}

	# Disconnect from the database server.

	$main::kiriwrite_dbmodule->disconnect();

	$main::kiriwrite_dbmodule->disconnecttemplate();
	return $main::kiriwrite_presmodule->grab();


}

1;