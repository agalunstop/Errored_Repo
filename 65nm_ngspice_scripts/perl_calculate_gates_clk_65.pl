#Example: perl perl_calculate_gates_clk_65.pl -s reference_spice.sp  -r decoder_op_ip_reference_out/tool_reference_out.txt -m decoder_op_ip -f /home/nanditha/Documents/simulations/ngspice_sim/65nm/sim/decoder_65nm

#perl %s/perl_calculate_gates_clk.pl -s %s/reference_spice.sp  -r %s/%s_reference_out/tool_reference_out.txt -m %s -f %s

#Removed the option of reading the $lib file : not needed: Mar 19 2014

#!/usr/bin/perl
use Getopt::Long;
#####################################################################
#
# Author        : Shahbaz Sarik
# Date          : 7th February 2013
# Purpose       : To calculate the number of gates in the design and the number of clock cycles in the vhdl simulation
#                 
# Copyright	: IIT BOMBAY
####################################################################

#  Routine to print Error message
sub printErrMessage {

 print "calculate_gates_clk.pl ERROR: BAD SYNTAX\n";
 print "TRY '$0 -h' or '$0 --help'  for help\n";
}

#  Routine to print man page
sub printManPage {
  print STDERR <<END; 
    
calculate_gates_clk(1)                                                                                  

NAME

calculate_gates_clk − Utility to create a glitch induced version of a spice library.

SYNOPSIS

calculate_gates_clk [reference_spice_file,glitch_lib,tool_reference_output,module_name,entire_path to current working directory]

DESCRIPTION

calculate_gates_clk script reads in the template/reference spice netlist (reference_spice.sp) and reports out the number of subckts/gates in the spice file so that the main script can pick a random gate out of these. It also reads in the <module>_pnr_reference_out/tool_reference_out.txt file to count the number of simulatable clock cycles so that the main script can pick a random clk cycle to simulate. This script outputs a tmp_random.txt in the current working directory which contains the number of gates in the circuit and the number of clk cycles

OPTIONS

perl perl_calculate_gates_clk.pl
-s reference_spice.sp  - This is the template/reference spice file in current working directory- which is the output of NetLstFrmt.pl
-l glitch_<std_cell>.sp  - This is the output of GlitchLibGen.pl and contains the glitched versions of the std cell library subckts
-r <module>_reference_out/tool_reference_out.txt  - this contains the reference output and input values of flip-flops from RTL simulation
-m <module> - this is the top module name in pnr verilog netlist
-f <entire_path_to_current_working_dir>


Examples:

perl perl_calculate_gates_clk.pl -s reference_spice.sp -l glitch_osu018_stdcells_correct_original.sp -r decoder_behav_pnr_reference_out/tool_reference_out.txt -m decoder_behav_pnr -f /home/user1/simulations/decoder

SEE ALSO

SPICE.

AUTHOR
Shahbaz sarik (shahbaz\@ee.iitb.ac.in)

This utility has been written for the “ Impact of soft error on circuit” experiment carried out under the guidence of Prof. Madhav. P. Desai (madhav\@ee.iitb.ac.in) at IITBombay.

COPYRIGHT
GPL IIT-Bombay
calculate_gates_clk January 3rd February 2013  
    
    
END
}
#  Get the command line arguments
#  check for missing/extra arguments and show usage

GetOptions( "s|spice=s"=>\$spc,
	    "r|ref=s"=>\$ref,
	     "m|module=s"=>\$module,
	    "f|folder=s"=>\$folder,
	     "h|help"=>\$help,
            
          );
      
if ($help) {
  printManPage();
  exit(0);
}

if ($#ARGV >= 0 || $ref eq "" || $spc eq ""||  $module eq ""|| $folder eq "") {
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
       #print "Vdd for this technology is $vdd \n";
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
$num_of_gates=$#gates+1; #Dont do gates-1, since python will consider one gate less than the total number for doing rand()
#If there are total 28 gates, rand (28) will be 0 to 27
print "first subckt: $gates[0]\n";
print "last subckt: $gates[27]\n";
print RAN "$num_of_gates\n";


#selecting a random clock cycle from the total number of cycles (as in refrence file)
open(REF,"$ref")||die("unable to open file : $!");
$count =0;
while(<REF>)
 {  
   $count++;
 }
close(REF);
#Removing 3 lines for header "xxxx" and "\n"
$count-=3;
#Removing not simulatable 10 cycles
$count-=10;

#Number of clk cycles
print "\nNumber of gates is $num_of_gates\n";
print "number of simulatable clock cycles is $count \n";

#Pick a random clk cycle to simulate
print RAN "$count\n";



#$cycle=int(rand($count));
#print "selected clock cycle : $cycle\n";
#$count=0;
#storing the input output values from reference file for present clock cycle and next cycle

#print "header : $header \n";
#print " clock cycle : $cycle input/output condition is $current_cycle \n";
#print " next clock cycle input/output condition is $next_cycle \n";
#@cycle1=split(" ",$current_cycle);
#@cycle2=split(" ",$next_cycle);

#selecting a random glitch location (between 1.2 clock_period to 1.5 clock period)
#$clk_period=$sim_time/2.5;

#Pick a random glitch location in the clk cycle
#Number of clk cycles
#$glitch_location=1.2*$clk_period + rand(0.3*$clk_period);
#print "Random glitch point is at time $glitch_location \n"; 


#creating the spice deck
#`mkdir $folder/spice_decks_$outloop`;
#open(OPT,">$folder/spice_decks_$outloop/deck_$deck_num.sp")||die("unable to open file : $!");
#print "\t\t\t\t\t\t\t !! SPICE DECK DIRECTORY CREATED !!\n";
#writing into the new spice file
#$count=0;
#open(SPC,"$spc")||die("unable to open file : $!");

#Appending to the RTL reference output file, which contains outputs of those clk cycles that were picked by this script randomly
#open(IM,">>$folder/$module\_reference_out/RTL.csv");
#print IM "\n";
#print IM "$deck_num,$cycle,$glitch_location,";
#@temp=split (" ",$next_cycle);
#$start=$#temp-$num_opt+1;



