#Example: perl perl_glitchLibGen_65.pl -p /home/users/nanditha/Documents/utility/65nm/b03 -i CORE65GPSVT_selected_lib_vg.sp

#!/usr/bin/perl


#Modifications:
#The condition of distinct drains is removed: (($dlist=~m/$drain/) is deleted : Oct 20 2014
#Modified the script to inject +ve current for PMOS and -ve current for NMOS. Also, PMOS current magnitude will be 1/3rd as that of NMOS: Aug 12 2014
#Writing glitch_CORE65GPSVT_selected_lib_vgRC.sp instead of glitch_CORE65GPSVT_selected_lib_vg.sp - Jul 9 2014
#Absolute paths introduced everywhere in the script, so that they can be run from one directory and no need of duplicating the scripts in all directories: June 25 2014
#Introduced comments on the line that contains ---.. else, error occurs in hspice: June 2014
#Modified M to M* in   if($sub_ckt[$i]=~m/^M*\d* /) to match all transistors in the new 65nm lib file: Mar 18 2014
#searching between subckt and ends modified to 'SUBCKT' and 'ENDS' to suit the 65nm lib requirements : Mar 18 2014

use Getopt::Long;
use Cwd;
#####################################################################
#
# Author        : Shahbaz Sarik
# Date          : 7th February 2013
# Purpose       : To create a glitch introduced library of a given
#                 spice library 
#                 
# Copyright	: IIT BOMBAY
####################################################################

#  Routine to print Error message
sub printErrMessage {

 print "GlitchLibGen ERROR: BAD SYNTAX\n";
 print "TRY '$0 -h' or '$0 --help'  for help\n";
}
#  Routine to print man page
sub printManPage {
  print STDERR <<END; 
    
GlitchLibGen(1)                                                                                  

NAME

GlitchLibGen − Utility to create a glitch induced version of a spice library.

SYNOPSIS

GlitchLibGen [input library file]  

DESCRIPTION

GlitchLibGen utility takes a spice library CORE65GPSVT_selected_lib_vg.sp (sp file containing standard cells in 65nm), say, <std_cell>.sp as input and creates a glitched induced library where each subciruit has different version, each version has glitch induced to one of its distinct drain excluding Vdd and gnd. The output of this file is glitch_CORE65GPSVT_selected_lib_vg.sp in the design folder.

OPTIONS

 
Input library file

-i |--input = <input library>.sp- which contains std cells (subckts) in spice format

This file should be the spice library whose glitched version is to be created.


Examples:

perl GlitchLibGen.pl -i osu018_stdcells_correct_original.sp

SEE ALSO

SPICE.

AUTHOR
Shahbaz sarik (shahbaz\@ee.iitb.ac.in) and modified by Nanditha Rao (nanditha@ee.iitb.ac.in)

This utility has been written for the “ Impact of soft error on circuit” experiment carried out under the guidence of Prof. Madhav. P. Desai (madhav\@ee.iitb.ac.in) at IITBombay.

COPYRIGHT
GPL IIT-Bombay
GlitchLibGen January 3rd February 2013  
    
    
END
}

#  Get the command line arguments
#  check for missing/extra arguments and show usage

GetOptions( #"o|output=s"=>\$glib,
            "i|input=s"=>\$library,
            "p|path=s"=>\$path,
            "h|help"=>\$help
          );
      
if ($help) {
  printManPage();
  exit(0);
}
$glib="glitch_".$library;
print "Glib is $glib\n\n";
if ($#ARGV >= 0 || $glib eq "" || $library eq ""|| $path eq "" ) {
  print STDERR "-E- Found missing/excess arguments\n";
  printErrMessage();
  exit(1);
}
#Getting job start time
chomp($date=`date`);
#$log=$0."_run_".$date.".log";
print "\t\t**********    Job started   at $date    **********\n";

#opening the required files
my $pwd = cwd();
print "CWD is $pwd\n\n";

print "Path is $path/$library";
open(NET,"$path/$library")||die("unable to open file : $!");
open(out,">$path/$glib");
open(drain_out,">$path/drain_areas.txt");
#open(logf,">$log");
print  out "*"x10;
print  out " Glitched induced version of LIBRARY : $library ";
print  out "*"x10;
print  out "\n\n\n";

#intializing the variables
@sub_ckt="";
$drain_num=0; 
$drain="";
$sub_ckt_num=0;
$index=0;
$sub_ckt_name="";
$info="\n\n**** SUBCIRCUIT\t\t|VERSION COUNT\n**-----------------------------------------\n";

#capturing the subcircuits from the library
while(<NET>)
 {  
   if(/.SUBCKT/ .. /.ENDS/)
     {
     
       $sub_ckt[$index++]=$_;
       if($_=~m/.SUBCKT/)
         { print "\nInside if\n";
	   ($temp,$sub_ckt_name)=split(" ",$_);
	   print "temp is $temp \n";
   	   print "subckt name is $sub_ckt_name \n";  
   	   $nth= (split " ", $_)[3]; 
   	   print "nth is $nth \n";
	 }
     }
#creating the glitched version of a subcircuit and writing it to output file
   else
     {
       if($index!=0)
	 {
	   $index=0;
	   $sub_ckt_num++;
	   print out "\n******************************* ORIGINAL SUBCIRCUIT : $sub_ckt_name ******************************* \n\n";
   	  	print "orig subckt\n";
	   print out join("",@sub_ckt);
	   #print "printed join("",@sub_ckt);
	   $head=shift (@sub_ckt);
           $tail=pop (@sub_ckt);  
           print "head is $head, tail is $tail\n";
	  # print "Working on subcircuit : $sub_ckt_num :$sub_ckt_name \n";
#obtaining the distinct drain of the subcircuit
           foreach $i (0 .. $#sub_ckt)
	     {
	     #  print "inside for of the subckt\n";
	       $glitch_sub_ckt=join("",@sub_ckt);
	       print "subckt[i] is: $sub_ckt[$i]\n";
	       if($sub_ckt[$i]=~m/^M+/)  #If the line is starting with "M"
	         {
		  #  print "obtaining drains of the subckt\n";
		    ($temp,$drain)=split(' ',$sub_ckt[$i]);
		    
		  #  print "temp is $temp \n"; #this is the matched word- beginning with M
   		    print "drain is $drain \n";  #This is the split word- the drain- the 1st word
	   	   $pmos= (split " ", $sub_ckt[$i])[5]; 
  	   		print "5th word is pmos or nmos: $pmos \n";
 	   		
 	   		#Identify the drain area
	  	   	#if( $sub_ckt[$i] =~/(AD(\d))/)
	  	   	#($drain_area) = $sub_ckt[$i] =~ m/ AD=(.*)p /;
	  	   	#($temp,$drain_area) = $sub_ckt[$i] =~ m/ (ad=|AD=)(.*)p (AS|as)/;
	  	   	($temp,$drain_area) = $sub_ckt[$i] =~ / (ad=|AD=)(.*?)p /;
	  	   	
	  	   	
			#my($drain_area) = $sub_ckt[$i] =~ /(AD=(\d))/g;

	  	   	print "AD/ad drain area: $drain_area \n";
	             	             	
	             	
		     if(!(($drain=~m/gnd/)||($drain=~m/vdd/i))) #($dlist=~m/$drain/)||
		       {			                   
			$dlist.=" $drain";
		        $drain_num++;
		        print "drain number is $sub_ckt_name,$drain_num, AD is $drain_area\n";
		        print drain_out "$sub_ckt_name\_$drain_num $drain_area\n";
			if($head=~s/$sub_ckt_name\_\d+/$sub_ckt_name\_$drain_num/)
                         {
                         }
			else
                         {
			  $head=~s/$sub_ckt_name/$sub_ckt_name\_$drain_num/;                         
                         }			
			$tail=~s/$sub_ckt_name.*/$sub_ckt_name\_$drain_num/;
			chomp($drain);
			#introducing glitch into the selected drain depending on whether it is NMOS or PMOS
			if ($pmos =~ /NSVTGP/) #This is NMOS
			{ 
			#-ve current for the NMOS drain
			$i="**NMOS current injection\nIcharge $drain 0 EXP (0 current_magnitude rise_delay rise_time_constant fall_delay fall_time_constant )\n\n";
			print "We're talking about NMOS\n\n";
			}
			else
			{
			#+ve current for the PMOS drain with a current magnitude that is 1/3rd of that of NMOS
			$i="**PMOS current injection\n.param current_magnitude_by3='current_magnitude/3'\nIcharge 0 $drain EXP (0 current_magnitude_by3 rise_delay rise_time_constant fall_delay fall_time_constant )\n\n";
			print "We're talking about PMOS\n\n";
			}

                       # $i="Icharge 0 $drain EXP (0 current_magnitude rise_delay rise_time_constant fall_delay fall_time_constant)\n";
			$glitch_sub_ckt=$head.$i.$glitch_sub_ckt.$tail;
#writing the glitch introduced subcircuit to output file
			print out "\n****** $sub_ckt_name : Glitched version $drain_num : glitch at $drain ******\n";                      
			#print "new subckt\n";
			print out "\n$glitch_sub_ckt";
			$count++;
                       }  
		      $drain="";			               
		 }
	     }
#collecting the information about the subcircuits
	   $info=$info."**** $sub_ckt_name\t\t|\t$drain_num\n";
	   $head="";
           $tail="";
	   @sub_ckt="";
	   $sub_ckt_name="";
	   $drain_num=0;
           $dlist="";
	   $sub_ckt_name="";
	   print out "\n";			
	 }
      }
 } 
#writing the information to output and displaying the completion message
chomp($date=`date`);  
print "\t\t**********    Job completed at $date    **********\n";
print "\t\t\t*************** !! RUN SUCESSFULL !! ****************\n";
chomp($path = `pwd`);
print "*********Glitch introduced library '$glib' created at $path/$glib\n\n\nDONE\n\n";
print out "\t\t**************************************** LIBRARAY INFORMATION ****************************************\n";
print out " **** This Library contains $sub_ckt_num glitch free Subcircuits \n";
print out " **** This Library contains $count glitch affected Subcircuits \n";
print out " **** Following are the details of these Subcircuits\n";
print out $info;
print out "*"x60;
print out " END ";
print out "*"x60; 
close(NET);
close(out);

