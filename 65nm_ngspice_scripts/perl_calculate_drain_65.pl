#Example: perl perl_calculate_drain.pl -s reference_spice.sp -l1 glitch_CORE65GPSVT_selected_lib.sp -r decoder_behav_pnr_reference_out/tool_reference_out.txt -m decoder_behav_pnr -f /home/user1/simulations/decoder -g 27

#Modified for 65nm: to search through 3 glitch library files: Mar 19 2014


#perl %s/perl_calculate_drain.pl -s %s/reference_spice.sp -l %s/glitch_osu018_stdcells_correct_original.sp -r %s/%s_reference_out/tool_reference_out.txt -m %s -f %s -g %s


#!/usr/bin/perl
use Getopt::Long;
#####################################################################
#
# Author        : Shahbaz Sarik
# Date          : 7th February 2013
# Purpose       : To calculate the number of drains for a particular random gate that was picked
#                 
# Copyright	: IIT BOMBAY
####################################################################

#  Routine to print Error message
sub printErrMessage {

 print "calculate_drain.pl ERROR: BAD SYNTAX\n";
 print "TRY '$0 -h' or '$0 --help'  for help\n";
}
#  Routine to print man page
sub printManPage {
  print STDERR <<END; 
    
calculate_drain(1)                                                                                  

NAME

calculate_drain − Utility to create a glitch induced version of a spice library.

SYNOPSIS

calculate_drain [reference_spice_file,glitch_lib,tool_reference_output,module_name,entire_path to current working directory,random gate number]

DESCRIPTION

calculate_drain script reads in the random gate number passed from the main script. It checks the reference_spice file and identifies the gate corresponding to this gate number. For eg., if there are 3 gate instances-AND,OR and XOR. If the number is 2, it identifies it as XOR (starting index being 0). It searches for XOR in the glitched spice library to pick the number of unique drains for this gate and writes this number back to the tmp_random.txt. This number is used by the main script to pick one random drain out of these drains.

OPTIONS


Inputs:

perl perl_calculate_drain.pl
-s reference_spice.sp  - This is the template/reference spice file in current working directory- which is the output of NetLstFrmt.pl
-l glitch_<std_cell>.sp  - This is the output of GlitchLibGen.pl and contains the glitched versions of the std cell library subckts
-r <module>_reference_out/tool_reference_out.txt  - this contains the reference output and input values of flip-flops from RTL simulation
-m <module> - this is the top module name in pnr verilog netlist
-f <entire_path_to_current_working_dir>
-g gate_num : This is the gate number that was randomly picked by the top level script. For eg., if the design had 28 gates, this number will be between 0 and 27 (both including)



Examples:

perl perl_calculate_drain.pl -s reference_spice.sp -l glitch_osu018_stdcells_correct_original.sp -r decoder_behav_pnr_reference_out/tool_reference_out.txt -m decoder_behav_pnr -f /home/user1/simulations/decoder -g 27

SEE ALSO

SPICE.

AUTHOR
Shahbaz sarik (shahbaz\@ee.iitb.ac.in)

This utility has been written for the “ Impact of soft error on circuit” experiment carried out under the guidence of Prof. Madhav. P. Desai (madhav\@ee.iitb.ac.in) at IITBombay.

COPYRIGHT
GPL IIT-Bombay
calculate_drain January 3rd February 2013  
    
    
END
}

#  Get the command line arguments
#  check for missing/extra arguments and show usage

GetOptions( "s|spice=s"=>\$spc,
	    "l1|lib1=s"=>\$lib1,
   	     "r|ref=s"=>\$ref,
	    "m|module=s"=>\$module,
	    "g|randgate=s"=>\$rand_gate,
	    "f|folder=s"=>\$folder,
	     "h|help"=>\$help,
            
          );
      
if ($help) {
  printManPage();
  exit(0);
}

if ($#ARGV >= 0 || $ref eq "" || $spc eq ""|| $lib1 eq "" ||  $module eq ""|| $folder eq "" || $rand_gate eq "") {
  print STDERR "-E- Found missing/excess arguments\n";
  printErrMessage();
  exit(1);
}
#Getting job start time
chomp($date=`date`);
print "\t\t**********    Job started   at $date    **********\n";

#Initializing the parameters
$sim="sim_".$spc;
@sub_ckt="";
$i=0;
$j=0;
$flag=0;
$in=0;
@gates="";
$done=0;
$cycle=0;
$current_cycle=0;
$next_cycle=0;
$sim_time=0;
$active=1;
$glitch_location=0;
$prnt=0;
$num_opt;
#opening the required files
open(SPC,"$spc")||die("unable to open file : $!");
while(<SPC>)
 {  
    $count++;
    if($_=~m/\.ENDS/i)
     {
      $active=0;
	$gate_end_point=$count;
     }
        
    if(($_=~m/^x.*/i)&&($active==1))
       {
        #print $_;
	chomp($gates[$i++]=$_);	
	$flag=1;
	$in=1;
      }
    if(($in==1 && $done == 0)&&($active==1))
      {
        $gate_start_point=$count-1;
        $done=1;
      }
    if((($_=~m/^\+.*/i))&&($active==1))
       {
         if($flag==1)
            {
	     chomp($tail=$_);
	     $tail=~s/\+//;
	     $gates[$i-1].=$tail;
	     
	    }
       }
    if($_=~m/tran 10ps (.*)s/i)
       {
        $sim_time=$1; #print "simulation time = $1\n";
       }
    if($_=~m/Vvdd vdd 0 (.*)/i)
       {
        chomp($vdd=$1);
       #s print "Vdd for this technology is $vdd \n";
       }
    if($_=~m/NUMBER OF OUTPUT PINS = (.*)/)
       {
         chomp($num_opt=$1)
       } 

 }
close(SPC);
#print "subcircuit starts from line number $gate_start_point and ends at line number $gate_end_point \n";
#print join("\n",@gates);
#print "total number of gates = $#gates \n";
#print "\nThis is deck number $deck_num\n";
#Pick a random gate in the design


open(RAN,">$folder/tmp_random.txt");
#Number of gates
#$num_of_gates=$#gates-1;

#print  "total num of gates: $num_of_gates\n";
print  "random gate: $rand_gate\n";

#$j=int(rand($#gates-1));
$j=int($rand_gate);
#$j+=1;
@temp=split(" ",$gates[$j]);
$random_gate=$temp[$#temp];
print "Random gate picked = $random_gate \n";
print "the random gate selected is gate number $j \n";

$found=0;
#selcting a random glitched gate
open(LIB1,"$lib1")||die("unable to open file : $!");

#Search for the gate in the first glitch file
while(<LIB1>)
 {  
   if($_=~m/^\*\*\*\* $random_gate/)
     {
       $_=~m/(\d+)$/;
	$drain=$1;
	last;
	$found=1;
     }
}



if ($found==0)
{
#Search in lib2
  while(<LIB2>)
   {  
     if($_=~m/^\*\*\*\* $random_gate/)
     {
       $_=~m/(\d+)$/;
	$drain=$1;
	last;
	$found=1;
     }
  }
  
  if ($found==0)
  {
#Search in lib3 if still not found
    while(<LIB3>)
     {  
     if($_=~m/^\*\*\*\* $random_gate/)
     {
       $_=~m/(\d+)$/;
	$drain=$1;
	last;
	$found=1;
     }
  }
 }
  
}





#Pick a random drain in the random gate in the design
#Number of drains info is in $drain
#$num_of_drains=$drain-1;
$num_of_drains=$drain; #Dont do drains-1 as python will generate one number less than the max randrange number anyway
print RAN "$num_of_drains\n";
#$random_drain=int(rand($num_of_drains));
#$random_drain+=1;
#print "$drain ----- $random_drain\n";
#print "$gates[$j]-------------$random_gate\n";
#$gates[$j]=~s/$random_gate/$random_gate\_$random_drain/;
#print join("\n",@gates);


print "num of drains is: $num_of_drains\n";




