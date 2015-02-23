
#Example: perl perl_spice_netlist_format_65.pl -v ../c432/c432_modelsim.v -s ../c432/pnr/op_data/c432_final_new.dspf -c 300 -t 65 -m c432 -p ../c432 -v 1.1

#Example: perl perl_spice_netlist_format_65.pl -v ../c432/c432_clk_ipFF_modelsim.v -s ../c432/pnr/op_data/c432_clk_ipFF_final_new.dspf -c 350 -t 65 -m c432_clk_ipFF -p ../c432 -v 0.9

#clk frequency in MHz

#Modifications:
# Added -v option to pass operating voltage from top level script 

#Automated the flip-flop type selection in meas statements and module instantiation of .ic statement (q_reg) for ISCAS and non-ISCAS benchmarks: Oct 15 2014 
#'Q' and 'QN' nodes in meas tran statements have been automated: Oct 15 2014
# .ic statements for all flip-flop types automated: Oct 14 2014
#Most flip-flops in the designs are : DFPQX4 and DFPQX9. Initialisation nodes for flip-flops other than DFPQX4 and DFPQX9 are being edited manually in the reference_spice right now since the internal initialisation nodes are different.
#.ic on net0148:F59 and net0148:F65 for DFPQX4 and DFPQX9 - Jul 10 2014
#Added time=0 measure and echo statements to test the initial conditions - Jul 9 2014
#Include glitch_CORE65GPSVT_selected_lib_vgRC.sp instead of glitch_CORE65GPSVT_selected_lib_vg.sp - includes R & C to solve the pseudo=tran method convergence issue- Jul 9 2014
#Absolute paths introduced everywhere in the script, so that they can be run from one directory and no need of duplicating the scripts in all directories: June 25 2014

#Initialisation nodes

# (net0139:F125)-M28 drain and M31 drain for HS65_GS_DFPQNX9,
# net0139:F163 (M28 drain) and net0139:F95 (M31 drain) for DFPHQNX9
# net0238:F149 (M24 source) for DFPHQX9. June 23 2014
#.ic on net0148:F59 (M25 source) and net0148:F65 (M29 drain) of the DFPQX4 and DFPQX9 to initialise correctly. This value should be the inverted value of what was supposed to be initialised originally.: April 2nd 2014

#rise and fall edge measurements limitedto 50ps duration. Else false values were being calculated: April 25 2014

#.ic square brackets being replaced by _ : feb 26 2014
#.ic statement being specified to all outputs of all FFs.. and are being initialised to the rising edge of the current clk cycle thats picked : Feb 21 2014
#.ic for all primary outputs being deleted. changed the PWL. It doesnt change value before 1st clk rising edge (reverting back to the original PWL statement): feb 21 2014

#Spice output value measurement was being done from 2nd clk cycle to 2nd clk cycle +(0.2*clk_period). This might be too long a duration to measure the value. Hence value is now being measured on (2nd rising edge + 150ps) and   (2nd falling edge + 150ps).  : Feb 17 2014

# Added meas and echo statements,added rise_edge parameters for measuring Flip Flop output at 2nd rising edge. Renamed ff_op_ to ff_op__fall. : Feb 7 2014

#Added param for change_time_rise. Modified PWL statement to initialise all FFs to previous cycle value to begin with and then change the input of the FF to the current cycle reference input in Verilog sim - Feb 7 2014

#This is for the no FF optimisation case/ extra _q_reg is added back. And simulation run for 2.5 cycles instead of 6.5 cycles. - Nov 19 2013

#Initialising output of all FFs to initial value-..commented out
#The meas statement is reverted back to original one.. where the extra _q_reg is not appended. It was appended for the c499 (without balance reg option) - oct 22
#If there are several modules, and dffs inside these, the code was printing out all DFFs. Modified this to search for DFF outputs only within the top  module - Oct 21 2013
#Modified PWL statements for the input nodes to simulate for. 6.5 clk cycles instead of 2.5 cycles. Increased sim_time, fall_from and fall_to times. Introduced new variables- for cycle (minus3, minus2 and minus1, current k cycle). Renamed end_PWL to k_plus1. 
#Code modified to write out .ic statements in spice file for inputs of all FFs .. later commented it out.. doesnt help - Oct 11 2013
#Code modified to write out internal subckt nodes (of all outputs of all FFs) in the echo and meas statements, so that we dont need to bring out those nodes as a subckt port  - Oct 8 2013


use Getopt::Long;
#####################################################################
#
# Author        : Shahbaz Sarik
# Date          : 7th March 2013
# Purpose       : To create a simulatable netlist from the rtl2gds output .dspf file
#                 
# Copyright	: IIT BOMBAY
####################################################################

#  Routine to print Error message
sub printErrMessage {

 print "NetldtFrmt ERROR: BAD SYNTAX\n";
 print "TRY '$0 -h' or '$0 --help'  for help\n";
}
#  Routine to print man page
sub printManPage {
  print STDERR <<END; 
    
NetlstFrmt(1)                                                                                  

NAME

perl_spice_netlist_format_65 − This script modifies the spice netlist to add parameters to make it simulatable.

SYNOPSIS

NetlstFrmt [input library file]  

DESCRIPTION

perl_spice_netlist_format_65 utility takes a spice file (dspf) from./<module>.dspf (generated by QRC or Soc encounter) as input. It adds parameters like: .control, .param, .tran, Voltage sources, meas, echo statements etc, instantiates the subckt so that the original dspf spice netlist is simulatable.  The outputs are the following: 1.reference_spice.sp- Template spice file that has simulation parameters included.\n 2.<pnr_module_reference_out>/RTL.csv - to write out RTL headers later on. The deckgen utility will write out the input, output information of the chosen clock cycle into this file later on.\n3.<pnr_module_reference_out>/RTL_backup.csv - to write out backup of RTL headers which will be needed later when the original RTL.csv is cleared\n4.spice_results/headers.csv - that contain spice output headers that will be later used to combine all spice outputs into a single file.\n

OPTIONS

 
Inputs:
perl NetlstFrmt.pl 

-v <module>_modelsim.v - modified pnr verilog netlist
-s <module>_final.dspf - spice(dspf) output from rtlgds
-l glitch_<std_cell>l.sp - output of GlitchLibgen.pl which contains glitched versions of std cell library subckts for spice
 c 1000 - clk frequency in MHz. For eg., if the frequency is 1GHz, enter 1000
-t 180 - technology parameter, for eg., enter 180 for 180nm technology
-m decoder_behav_pnr - module name in the pnr verilog file



Examples:

perl NetlstFrmt.pl -v decoder_behav_pnr_modelsim.v -s pnr/op_data/decoder_behav_pnr_final.dspf -l glitch_osu018_stdcells_correct_original.sp -c 1000 -t 180 -m decoder_behav_pnr


SEE ALSO

SPICE.

AUTHOR
Shahbaz sarik (shahbaz\@ee.iitb.ac.in)

This utility has been written for the “ Impact of soft error on circuit” experiment carried out under the guidence of Prof. Madhav. P. Desai (madhav\@ee.iitb.ac.in) at IITBombay.

COPYRIGHT
GPL IIT-Bombay
NetlstFrmt January 3rd February 2013  
    
    
END
}

#  Get the command line arguments
#  check for missing/extra arguments and show usage

GetOptions( "v|verilog=s"=>\$vlog,
            "s|spice=s"=>\$spc,
            "o|volt=s"=>\$volt,
	    "c|clk=s"=>\$clk,
	    "t|tech=s"=>\$tech,
	    "m|module=s"=>\$module,
             "p|path=s"=>\$path,
             "h|help"=>\$help
          );
      
if ($help) {
  printManPage();
  exit(0);
}

if ($#ARGV >= 0 || $vlog eq "" || $spc eq ""|| $clk eq "" || $module eq "" || $path eq "" ) {
  print STDERR "-E- Found missing/excess arguments\n";
  printErrMessage();
  exit(1);
}

#Getting job start time
chomp($date=`date`);
print "\t*******    Job started   at $date    **********\n";

#Initializing the parameters
$sim="reference_spice.sp";
@sub_ckt="";
$dnum=1;
$vdd=1.8;
$idd=2.2;
$flag=0;
$flag_sub =0;

use File::Path qw(mkpath);
mkpath("$path/spice_results");


#opening the required files to read
open(SPC,"$spc")||die("unable to open file : $!");
open(VLOG,"$vlog")||die("unable to open file : $!");


#To write
open(SIM,">$path/$sim");
open(FF_TYPE,">$path/flipflop_names.txt")||die("unable to open file : $!");


#
#Definig the technology dependent parameters
$vdd=1.8;
$idd=2.2;
##### this part commented because vdd and idd are now inserted in the final deck using deckgen script. reference.spice doesn't 
##### have any operating voltage or injected current

#if($tech==180)
#  {
#    if($volt=="") {$vdd=1.8;}
#    else {$vdd=$volt;}
#    $idd=2.2;
#  }
#elsif($tech==130)
#  {
#    if($volt=="") {$vdd=1.5;}
#    else {$vdd=$volt;}
#    $idd=1.8;
#  }
#elsif($tech==90)
#  {
#    if($volt=="") {$vdd=1.2;}
#    else {$vdd=$volt;}
#    $idd=1.5;
#  }
#elsif($tech==65)
#  {
#    if($volt=="") {$vdd=1.26;}
#    else {$vdd=$volt;}
#    $idd=0;
#  }
#elsif($tech==45)
#  {
#    if($volt=="") {$vdd=1.0;}
#    else {$vdd=$volt;}
#    $idd=1.0;
#  }
#elsif($tech==32)
#  {
#    if($volt=="") {$vdd=0.9;}
#    else {$vdd=$volt;}
#    $idd=0.8;
#  }
#elsif($tech==22)
#  {
#    if($volt=="") {$vdd=0.8;}
#    else {$vdd=$volt;}
#    $idd=0.6;
#  }

$vdd = "##op_voltage##";
$idd = "##injected_curr##";
#including the library files
print SIM "****Template spice file***"."\n\n";
print SIM ".include  ../hspice_glitch_CORE65GPSVT_selected_lib_vg.sp"."\n";
print SIM '.include ../hspice_65nm_models/diodeiso_typ.txt'."\n";
print SIM '.include ../hspice_65nm_models/ptm_nmos_65_no_X.txt'."\n";
print SIM '.include ../hspice_65nm_models/ptm_pmos_65_no_X.txt'."\n";
print "\t******Giltched version of the library file and technology file included in the spice file\n";
$loop_var=0;

print SIM "**********Subckt begins*********"."\n\n";
@to_ff;
@ff_inp_replace;
@ff_op_replace;
$new_inp;
#parsing the verilog file
$flag_flop=0;
$flag1=0;
$count_line=0;
$aj=0;
$qreg=0;


while(<VLOG>)
 {  
   
   if(($_=~m/^ *input/)||($_=~m/^ *output/)) #Extracting the input and output from the verilog code
     {
        chomp($_);
	chop($_);
	@temp=split(" ",$_);
	$type=shift(@temp);
	foreach $i(0..$#temp)
	   {
		if(!($temp[$i]=~m/.*[.*:.*].*/))
		  {
                     if(($type eq "input") || ($type eq "inout"))
			{
			  $inputs[$j++]=$temp[$i];
			}
		     elsif($type eq "output")   #Extracting output port names from pnr verilog file
			{
			  $outputs[$k++]=$temp[$i];
			}
		  }
	   }
	
     }

	#To check if q_reg is present in the verilog file. 
	#Depending on this, the measure statement will have different names
    if ($qreg==0)
    {
    	if(($_=~ m/q_reg/))
    	{
    		$qreg=1; #For ISCAS benchmarks
    	}
    }

 if($flag_flop==1)
    {
     # print $_;
      $flag_flop=0;
      chomp($new_inp=$_);
    #$new_inp_copy=$new_inp;
   # $new_inp_copy=~m/.Q\((.*)\)/;
  #   print $1."\n";
 #     push (@ff_op_replace,$1);

     
      $new_inp=~m/.D\((.*)\)/;
      #print $1."\n";
      push (@ff_inp_replace,$1);


     # print join("\n",@ff_inp_replace);
    }


  if(($_=~m/module $module \(/ .. /endmodule/)) #parsing the main module only
     {
	
	 if(($_=~m/DF/)||($_=~m/LATCH/)||($flag1==1)) #searching for flip flop and latches
	    {

		# ($junk,$ff_name)=split(" ",$_);
	       # push(@to_ff,$ff_name);
#		print $_;
		#print @to_ff;
		#print "\n";
	       # $flag_flop=1;

		if($flag1 == 0)
		   {
                     ($fftype1,$ffname1,$pin1)=split(" ",$_);#capturing the output pin of the flip flop
                     if ($fftype1 =~ m/dff_/)
                     {
                     $fftype1="HS65_GS_DFPQX4";
                     }
                     
                     
                     $ff_types[$aj++]=$fftype1;
		     print  FF_TYPE "$fftype1\n";
		     
		     $pin1=~m/\(.*\((.*)\)/;
		     $ffopin1[$i++]=$1;#this array has all output pins of all FFs
		     $flag1=1;
		  }
                else
		   {
                     $_=~m/.*\((.*)\)/; #capturing the input pin of the flip flop
		     #$ffipin[$j++]=$1; #captures input pins of all FFs
		     $flag1=0;
		   }
	    }
     }

if(($_=~m/module $module \(/ .. /endmodule/)) #parsing the main module only
     {

#This consists of ALL DFF outputs including the primary outputs
   if(($_=~m/DF/)||($_=~m/LATCH/)||($flag==1)) #searching for flip flop and latch outputs in pnr verilog file
     {
        ($junk,$ff_name)=split(" ",$_);
        push(@to_ff,$ff_name);
        $flag_flop=1;
        print "line is $_\n";
        print "\n";
     }
  
  }
 
} #End while

foreach $i(0 .. $#ff_types)
{
  print "$ff_types[$i]\n";

}
	



print "\n\t********** Input output of the RTL file extracted\n";

#Parsing the spice file
while(<SPC>)
 {  
   #skipping the .END line in the spice file
   if($_=~m/.END\b/)
     {
       next;
     }
   if(!($_=~m/ FILL$/)&&!($_=~m/^\*/))# removing the fills and comments
     {
	$new=$_;
	$new=~s/\[/_/g;
	$new=~s/\]/_/g;
	$new=~s/\//_/g;
	$new=~s/\//_/g;
	print SIM $new;
     }
        
    if(($_=~m/^x.*/i)&&(!($_=~m/ FILL$/)))
       {
        #print $_;
	chomp($gates[$i++]=$_);	
	$flag=1;
	$in=1;
      }
    if(($_=~m/^\+.*/i))
       {
         if($flag==1)
            {
	     chomp($tail=$_);
	     $tail=~s/\+//;
	     $gates[$i-1].=$tail;
	     
	    }
       }
   
  #raising a flab when the subcircuit line is reached
      if($_=~m/.SUBCKT/)
        {
          $flag_sub =1;
        }
  #Removing the flag when the statement after subcircuit doesnot starts with '+'
      if(($_!~m/.SUBCKT/)&&($flag_sub == 1)&&($_!~m/^\+/))
        {
          $flag_sub =0;
        }
  #print join("\n",@gates);
   if(/.SUBCKT/../Net Section/) #extracting the subcircuit
     {
        if(!(($_=~m/.SUBCKT/)||($_=~m/Net Section/))&&($_=~m/\+/)&&($flag_sub == 1))
         {
           $new=$_;
	   $new=~s/\[/_/g;
	   $new=~s/\]/_/g;
	   $new=~s/\//_/g;
	   $new=~s/\//_/g;
	   $sub_ckt[$i++]=$new;
	   $pin=$_;
           $pin=~s/\+ //;
	   @temp=split (" ",$pin);
           push @pins ,@temp;
         }
     
      }
   if($_=~m/.SUBCKT/) # Capturing the name of the subcircuit
     {
	$new=$_;
	$new=~s/\[/_/g;
	$new=~s/\]/_/g;
	$new=~s/\//_/g;
	$new=~s/\//_/g;	
	($temp,$s_name)=split(" ",$new);
     }
}

#instantiating the sub circuit

print SIM "\n\n******Simulation parameters*****"."\n\n";


#including the user defined clock information

#$clk_period = (1/$clk)*(0.000001);
#
##$sim_time=6.5*$clk_period;#defining simulation time
##$fall_from=(6*$clk_period); #defining fall time window
##$fall_to= 6.2*$clk_period;
#
#$sim_time=2.5*$clk_period;#defining simulation time
#$fall_from=(2*$clk_period); #defining fall time window
#$fall_to= ($fall_from + 50e-12);
#
#$rise_from_2nd=(1.5*$clk_period); #defining fall time window
#$rise_to_2nd= ($rise_from_2nd + 50e-12);

#$half_clk_period=$clk_period/2;
#$double_clk_period=2*$clk_period;
#$change_time=$half_clk_period/3;
#$k_plus1= $half_clk_period+$change_time;


#Declaring the param statements in sice file

print SIM "****Param definitions***"."\n";

print SIM ".param clk_period= '(1/##clk_period##)*(0.000001)' \n"; 
print SIM "+half_clk_period= '(clk_period/2)'\n";
print SIM "+double_clk_period= '(clk_period*2)'\n\n";


print SIM ".param fall_from_value=##fall_from##\n"; 
print SIM "+ fall_to_value=##fall_to##\n\n";

print SIM ".param init_delay = half_clk_period\n";
print SIM "+ rise_time= 50p\n";
print SIM "+ fall_time= 50p\n\n";

print SIM "**2.5 cycle simulation**\n";
print SIM ".param change_time='(half_clk_period/3)'\n";
print SIM ".param change_time_rise= '(change_time + 100ps)'\n";
print SIM ".param k_plus1= '(half_clk_period + change_time)'\n";
print SIM ".param k_plus1_rise = '(k_plus1 + 100ps)'\n";
#print SIM "+end_PWL_rise = \'(end_PWL + 100ps)\'\n\n";

#print SIM ".param k_minus_4='(half_clk_period/3)'\n";

#print SIM ".param k_minus_3='k_minus_4 + clk_period'\n";
#print SIM ".param k_minus_3rise='k_minus_3 + 100ps'\n";

#print SIM ".param k_minus_2='k_minus_3 + clk_period'\n";
#print SIM ".param k_minus_2rise='k_minus_2 + 100ps'\n";

#print SIM ".param k_minus_1='k_minus_2 + clk_period'\n";
#print SIM ".param k_minus_1rise='k_minus_1 + 100ps'\n";

#print SIM ".param k_cycle = 'k_minus_1 + clk_period'\n";
#print SIM ".param k_cycle_rise = 'k_cycle + 100ps'\n";

#print SIM ".param k_plus1= '(k_cycle + half_clk_period )'\n";

print SIM ".param current_magnitude = $idd";
print SIM "mA\n";
#Adding the glitch information
#Dont leave a space after the glitch_location_time and ns
print SIM "+rise_delay= ##glitch_location##s\n";
print SIM "+fall_delay= \'rise_delay+5p\'\n";
print SIM "+rise_time_constant = 1ps\n";
print SIM "+fall_time_constant=130ps\n\n";



#defining global pins
print SIM '.GLOBAL vdd gnd'."\n\n";
print SIM "Vvdd vdd 0 $vdd\n";
print SIM "Vgnd agnd 0 0\n";
print SIM "Rgnd agnd gnd 0\n";

#clock period
##print "Clock period".$clk_period."\n";
print SIM "VCk  clk   0  PULSE(0 $vdd init_delay rise_time fall_time half_clk_period clk_period)\n\n";

print SIM "\n\n******Instantiating the subckt*****"."\n\n";

chomp($sub_ckt[$#sub_ckt]);
$sub_ckt[$#sub_ckt].=" $sname";
print SIM "X$s_name\n";
print SIM join("",@sub_ckt);
print SIM $s_name;

print SIM "\n\n******Done instantiating the subckt*****"."\n";

print "\t*************Fills removed from the spice file\n";
print "\t*************Sub circuit instantiated in the spice file\n";

#classifying the pins as input and output pins

foreach $i (0..$#pins)
 {
   $flag=0;
   foreach $j (0..$#outputs)
     {
	$pin=$pins[$i];
	$pin=~s/\[.*\]//;
	if($pin eq $outputs[$j])
	   {
		$flag=1;
		push @opins ,$pins[$i];       
		last;
           } 
     }   
        if($flag==0)
	   {
		push @ipins ,$pins[$i];
	   }
    
 } 

#print "\nthe following are the input pins\n";
#print join("\n",@ipins);
#print "\nthe following are the output pins\n";
#print join("\n",@opins);
$measure_at_rising_edge="";
foreach $g(0 .. $#gates)
  {
   if(($gates[$g]=~m/DF/)||($gates[$g]=~m/LATCH/))
   {
     $gates[$g]=~m/:Q (.*:D) /;
	push @dffipin, $1;
  
   }
  }
 
#Initializing the inputs 

foreach $i(0 .. $#ipins)
 {
   $new=$ipins[$i];
   $new=~s/\[/_/g;
   $new=~s/\]/_/g;
   $new=~s/\//_/g;
   #print $new;

   if($new ne "clk")
   {
#Old PWL statement
##     print SIM "\n\nV$i $new 0 PWL( 0 ##$new\_reference_1## k_plus1 ##$new\_reference_1## k_plus1_rise ##$new\_reference_2## $sim_time ##$new\_reference_2##)\n";

#Simulating 6.5 cycles

    # print SIM "\n\nV$i $new 0 PWL( 0 ##$new\_reference_minus4##  k_minus_3 ##$new\_reference_minus4## k_minus_3rise ##$new\_reference_minus3## k_minus_2 ##$new\_reference_minus3## k_minus_2rise ##$new\_reference_minus2## k_minus_1 ##$new\_reference_minus2## k_minus_1rise ##$new\_reference_minus1## k_cycle ##$new\_reference_minus1## k_cycle_rise ##$new\_reference_1## k_plus1 ##$new\_reference_1## k_plus1_rise ##$new\_reference_2## $sim_time ##$new\_reference_2##)\n";

#Simulating 2.5 cycles
#This will initialise the outputs of all FFs to 0 to begin with and then change the input of the FF to the current cycle reference input in Verilog sim
# print SIM "\n\nV$i $new 0 PWL( 0 ##$new\_reference_minus1##  change_time ##$new\_reference_minus1## change_time_rise  ##$new\_reference_1## k_plus1 ##$new\_reference_1## k_plus1_rise ##$new\_reference_2## $sim_time ##$new\_reference_2##)\n";

# print SIM "\n\nV$i $new 0 PWL( 0  ##$new\_reference_1## k_plus1 ##$new\_reference_1## k_plus1_rise ##$new\_reference_2## $sim_time ##$new\_reference_2##)\n";
 print SIM "\n\nV$i $new 0 PWL( 0  ##$new\_reference_1## k_plus1 ##$new\_reference_1## k_plus1_rise ##$new\_reference_2## ##sim_time## ##$new\_reference_2##)\n";
 
   }
}

 
#foreach $i(0 .. $#dffipin)
# {
#   $new=$dffipin[$i];
#   $new=~s/\[/_/g;
#   $new=~s/\]/_/g;
#   $new=~s/\//_/g;
#   if($new ne "clk")
#   {
#      print SIM "**.ic v($new)= ##$new\_reference_1##\n";
#   }
#}

print SIM "\n**Initialising input of all FFs- commented this out. Doesnt help.PWL\n";
#foreach $i(0 .. $#to_ff)
# {
#if($i ne "clk")
#   {
#      print SIM "***.ic v(X$module.$to_ff[$i]:D)= ##$ff_inp_replace[$i]\_reference_minus4##\n";
#   }

   #$measure_at_falling_edge.="meas tran ff_op_$i MAX v(X$module.$to_ff[$i]:Q) from=$fall_from"."s"." to=$fall_to"."s\n";
 #}

print SIM "\n**Initialising output of all FFs- trying..\n";
print SIM "\n**This is the initial value on the Qbar signal inside the DFF. \n";


foreach $i(0 .. $#to_ff)
 {
  $new=$ffopin1[$i];
   $new=~s/\[/_/g;
   $new=~s/\]/_/g;
   $new=~s/\//_/g;
   
  
   
  #Initialisation nodes
   if($i ne "clk")
   {
     # print SIM ".ic v(X$module.$to_ff[$i]:Q)= ##$new\_reference_1##\n";  
      #print SIM ".ic v(X$module.$to_ff[$i]\_q\_reg:Q)= ##$new\_reference_1##\n";
 	
 	$ff_obtained=$ff_types[$i];
 
	if ($ff_obtained =~ m/(HS65_GS_DFPQX4|HS65_GS_DFPQX9)/)
	{
		if ($qreg==1)
		{ #For ISCAS benchmarks
		print "1. Obtained DFF name is $ff_obtained\n";
		print SIM ".ic v(X$module.X$to_ff[$i]\_q\_reg.net0148:F59)= ##$new\_reference_1_neg##\n";
		print SIM ".ic v(X$module.X$to_ff[$i]\_q\_reg.net0148:F65)= ##$new\_reference_1_neg##\n\n";
		}
		else
		{ #For ITC benchmarks
		print "1. Obtained DFF name is $ff_obtained\n";
		print SIM ".ic v(X$module.X$to_ff[$i].net0148:F59)= ##$new\_reference_1_neg##\n";
		print SIM ".ic v(X$module.X$to_ff[$i].net0148:F65)= ##$new\_reference_1_neg##\n\n";
		}
	}
	
	elsif ($ff_obtained =~ m/HS65_GS_DFPQNX9/)
	{
		
		if ($qreg==1)
		{
		print "2. Obtained DFF name is $ff_obtained\n";
		print SIM ".ic v(X$module.X$to_ff[$i]\_q\_reg.net0139:F125)= ##$new\_reference_1_neg##\n\n";
		}
		else
		{
		print "2. Obtained DFF name is $ff_obtained\n";
		print SIM ".ic v(X$module.X$to_ff[$i].net0139:F125)= ##$new\_reference_1_neg##\n\n";
		}
	
	}
	
	elsif ($ff_obtained =~ m/HS65_GS_DFPHQNX9/)
	{
	
		if ($qreg==1)
		{
		print "3. Obtained DFF name is $ff_obtained\n";
		print SIM ".ic v(X$module.X$to_ff[$i]\_q\_reg.net0139:F163)= ##$new\_reference_1_neg##\n";
		print SIM ".ic v(X$module.X$to_ff[$i]\_q\_reg.net0139:F95)= ##$new\_reference_1_neg##\n\n";
		}
		else
		{
		print "3. Obtained DFF name is $ff_obtained\n";
		print SIM ".ic v(X$module.X$to_ff[$i].net0139:F163)= ##$new\_reference_1_neg##\n";
		print SIM ".ic v(X$module.X$to_ff[$i].net0139:F95)= ##$new\_reference_1_neg##\n\n";
		}
		
	}
	
	elsif ($ff_obtained =~ m/HS65_GS_DFPHQX9/)
	{
		if ($qreg==1)
		{
		print "4. Obtained DFF name is $ff_obtained\n";
		print SIM ".ic v(X$module.X$to_ff[$i]\_q\_reg.net0238:F149)= ##$new\_reference_1_neg##\n\n";
		}
		else
		{
		print "4. Obtained DFF name is $ff_obtained\n";
		print SIM ".ic v(X$module.X$to_ff[$i].net0238:F149)= ##$new\_reference_1_neg##\n\n";
		}
		
	}
 
   }

   #$measure_at_falling_edge.="meas tran ff_op_$i MAX v(X$module.$to_ff[$i]:Q) from=$fall_from"."s"." to=$fall_to"."s\n";
 }

##Initialise primary outputs
 print SIM "\n**Initialising primary outputs to 0..commented out right now\n\n";
foreach $i(0 .. $#opins)
 {
   $new1=$opins[$i];
   $new1=~s/\[/_/g;
   $new1=~s/\]/_/g;
   $new1=~s/\//_/g;
   if($new1 ne "clk")
   {
      #print SIM ".ic v($new1)= ##$new1\_reference_1##\n";
      #commented the following out..
	#print SIM "*.ic v($new1)= 0\n";t
	
   }
}



$measure_at_time0="";
$measure_at_falling_edge="";
$measure_at_rising_edge="";
#to_ff consists of primary outputs also. So, the following part is not needed. This part contains only output ports.
#foreach $i(0 .. $#opins)
# {
#   $measure_at_falling_edge.="meas tran $opins[$i]_voltage MAX v($opins[$i]) from=$fall_from"."s"." to=$fall_to"."s\n";
# }


print "printing..\n";
print "length=$#to_ff\n";
foreach $i(0 .. $#to_ff)
 {


print "$to_ff[$i]\n" ;
print "v(X$module.$to_ff[$i]:Q)\n";
}

#Measure statements
foreach $i(0 .. $#to_ff)
 {

	$ff_obtained=$ff_types[$i];
 
	if ($ff_obtained =~ m/(HS65_GS_DFPQX4|HS65_GS_DFPQX9)/)
	{
		print "1. Obtained DFF name is $ff_obtained\n";
	
	####################  Fall edge  ##########################
	
		if ($qreg==1) #For ISCAS- benchmarks for eg.
		{
		$measure_at_falling_edge.="meas tran ff_op_fall_$i MAX v(X$module.$to_ff[$i]\_q\_reg:Q) from=##fall_from##"."s"." to=##fall_to##"."s\n";
		}
		else
		{ 
		#This will need to be enabled for non-ISCAS benchmark circuits for eg
 		$measure_at_falling_edge.="meas tran ff_op_fall_$i MAX v(X$module.$to_ff[$i]:Q) from=##fall_from##"."s"." to=##fall_to##"."s\n";
 		}
	####################  Rise edge  ########################## 
 		if ($qreg==1) #For ISCAS- benchmarks for eg.
		{
		 $measure_at_rising_edge.="meas tran ff_op_rise_$i MAX v(X$module.$to_ff[$i]\_q\_reg:Q) from=##rise_from_2nd##"."s"." to=##rise_to_2nd##"."s\n";
		}
		 else
		 {
		 #This will need to be enabled for non-ISCAS benchmark circuits for eg
		 $measure_at_rising_edge.="meas tran ff_op_rise_$i MAX v(X$module.$to_ff[$i]:Q) from=##rise_from_2nd##"."s"." to=##rise_to_2nd##"."s\n";
	 	}
 
	 ####################  Time 0  ########################## 
 		if ($qreg==1) #For ISCAS- benchmarks for eg.
		{
		$measure_at_time0.="meas tran ff_op_time0_$i MAX v(X$module.$to_ff[$i]\_q\_reg:Q) from=0.01e-9"."s"." to=0.05e-9"."s\n"
		}
		 else
		{
		#This will need to be enabled for non-ISCAS benchmark circuits for eg
		 $measure_at_time0.="meas tran ff_op_time0_$i MAX v(X$module.$to_ff[$i]:Q) from=0.01e-9"."s"." to=0.05e-9"."s\n";
		 }
	 
	}
	
	elsif ($ff_obtained =~ m/HS65_GS_DFPQNX9/)
	{
		print "2. Obtained DFF name is $ff_obtained\n";
	####################  Fall edge  ##########################
		if ($qreg==1) #For ISCAS- benchmarks for eg.
		{
		$measure_at_falling_edge.="meas tran ff_op_fall_$i MAX v(X$module.$to_ff[$i]\_q\_reg:QN) from=##fall_from##"."s"." to=##fall_to##"."s\n";
		}
		else
		{ 
		#This will need to be enabled for non-ISCAS benchmark circuits for eg
	 	$measure_at_falling_edge.="meas tran ff_op_fall_$i MAX v(X$module.$to_ff[$i]:QN) from=##fall_from##"."s"." to=##fall_to##"."s\n";
	 	}
 	####################  Rise edge  ########################## 
		if ($qreg==1) #For ISCAS- benchmarks for eg.
		{
		 $measure_at_rising_edge.="meas tran ff_op_rise_$i MAX v(X$module.$to_ff[$i]\_q\_reg:QN) from=##rise_from_2nd##"."s"." to=##rise_to_2nd##"."s\n";
		}
		else
		{ 
		#This will need to be enabled for non-ISCAS benchmark circuits for eg
		 $measure_at_rising_edge.="meas tran ff_op_rise_$i MAX v(X$module.$to_ff[$i]:QN) from=##rise_from_2nd##"."s"." to=##rise_to_2nd##"."s\n";
		} 
	 ####################  Time 0  ########################## 
	 	if ($qreg==1) #For ISCAS- benchmarks for eg.
		{
		$measure_at_time0.="meas tran ff_op_time0_$i MAX v(X$module.$to_ff[$i]\_q\_reg:QN) from=0.01e-9"."s"." to=0.05e-9"."s\n"
		}
		else
		{
		#This will need to be enabled for non-ISCAS benchmark circuits for eg
		 $measure_at_time0.="meas tran ff_op_time0_$i MAX v(X$module.$to_ff[$i]:QN) from=0.01e-9"."s"." to=0.05e-9"."s\n";
		}
	 
	}
	
	elsif ($ff_obtained =~ m/HS65_GS_DFPHQNX9/)
	{
		print "3. Obtained DFF name is $ff_obtained\n";
	####################  Fall edge  ##########################
		if ($qreg==1) #For ISCAS- benchmarks for eg.
		{
		 $measure_at_falling_edge.="meas tran ff_op_fall_$i MAX v(X$module.$to_ff[$i]\_q\_reg:QN) from=##fall_from##"."s"." to=##fall_to##"."s\n";
		 }
		else
		{
		 #This will need to be enabled for non-ISCAS benchmark circuits for eg
		 $measure_at_falling_edge.="meas tran ff_op_fall_$i MAX v(X$module.$to_ff[$i]:QN) from=##fall_from##"."s"." to=##fall_to##"."s\n";
		 }
 	
 	####################  Rise edge  ########################## 
	 	if ($qreg==1) #For ISCAS- benchmarks for eg.
		{
		$measure_at_rising_edge.="meas tran ff_op_rise_$i MAX v(X$module.$to_ff[$i]\_q\_reg:QN) from=##rise_from_2nd##"."s"." to=##rise_to_2nd##"."s\n";
		}

		else
		{
		#This will need to be enabled for non-ISCAS benchmark circuits
		 $measure_at_rising_edge.="meas tran ff_op_rise_$i MAX v(X$module.$to_ff[$i]:QN) from=##rise_from_2nd##"."s"." to=##rise_to_2nd##"."s\n";
		 }
	 
	 ####################  Time 0  ########################## 
	 	if ($qreg==1) #For ISCAS- benchmarks for eg.
		{
		$measure_at_time0.="meas tran ff_op_time0_$i MAX v(X$module.$to_ff[$i]\_q\_reg:QN) from=0.01e-9"."s"." to=0.05e-9"."s\n"
		}
		else
		{
		#This will need to be enabled for non-ISCAS benchmark circuits
		 $measure_at_time0.="meas tran ff_op_time0_$i MAX v(X$module.$to_ff[$i]:QN) from=0.01e-9"."s"." to=0.05e-9"."s\n";
		 }
	 
	 }
	
	elsif ($ff_obtained =~ m/HS65_GS_DFPHQX9/)
	{
		print "4. Obtained DFF name is $ff_obtained\n";
	####################  Fall edge  ##########################
		if ($qreg==1) #For ISCAS- benchmarks for eg.
		{
		$measure_at_falling_edge.="meas tran ff_op_fall_$i MAX v(X$module.$to_ff[$i]\_q\_reg:Q) from=##fall_from##"."s"." to=##fall_to##"."s\n";
		}
		
		else
		{
		 #This will need to be enabled for non-ISCAS benchmark circuits
	 	$measure_at_falling_edge.="meas tran ff_op_fall_$i MAX v(X$module.$to_ff[$i]:Q) from=##fall_from##"."s"." to=##fall_to##"."s\n";
 		}
 	####################  Rise edge  ########################## 
	 	if ($qreg==1) #For ISCAS- benchmarks for eg.
		{
		$measure_at_rising_edge.="meas tran ff_op_rise_$i MAX v(X$module.$to_ff[$i]\_q\_reg:Q) from=##rise_from_2nd##"."s"." to=##rise_to_2nd##"."s\n";
		}
		else
		{
		 #This will need to be enabled for non-ISCAS benchmark circuits
		 $measure_at_rising_edge.="meas tran ff_op_rise_$i MAX v(X$module.$to_ff[$i]:Q) from=##rise_from_2nd##"."s"." to=##rise_to_2nd##"."s\n";
	 	}
	 
	  ####################  Time 0  ########################## 
 		if ($qreg==1) #For ISCAS- benchmarks for eg.
		{
		$measure_at_time0.="meas tran ff_op_time0_$i MAX v(X$module.$to_ff[$i]\_q\_reg:Q) from=0.01e-9"."s"." to=0.05e-9"."s\n"
		}
		else
		{
		 #This will need to be enabled for non-ISCAS benchmark circuits
		 $measure_at_time0.="meas tran ff_op_time0_$i MAX v(X$module.$to_ff[$i]:Q) from=0.01e-9"."s"." to=0.05e-9"."s\n";
 		}
	 
	}
	
 
 }


 
#Adding the control part
print SIM "\n\n.control\n";
print SIM "option rshunt = 1e12\noption itl4 = 100  reltol =0.005  trtol=8 pivtol=1e-11  abstol=1e-10 \n**option CONVERGE=-1\n";
print SIM "tran 20ps ##sim_time##"."s\n\n";
print SIM "**Uncomment the following and run this spice file, if you need a waveform\n";
print SIM "**write waveform_file.raw v(clk) v(input_dec_2_) v(input_dec_1_) v(input_dec_0_)  v(output_dec_3_) v(output_dec_1_) \n*+v.xdecoder_behav_pnr.xu11.vcharge#branch \n\n";

print SIM "\n\n**************************** Measuring Flip Flop output at 2nd falling edge *************************************************\n";
$measure_at_falling_edge=~s/\[/_/g;
$measure_at_falling_edge=~s/\]/_/g;
$measure_at_falling_edge=~s/\//_/g;
print SIM $measure_at_falling_edge;

print SIM "\n\n**************************** Measuring Flip Flop output at 2nd rising edge *************************************************\n";
$measure_at_rising_edge=~s/\[/_/g;
$measure_at_rising_edge=~s/\]/_/g;
$measure_at_rising_edge=~s/\//_/g;
print SIM $measure_at_rising_edge;

print SIM "\n\n**************************** Measuring Flip Flop output t=0 *************************************************\n";
$measure_at_time0=~s/\[/_/g;
$measure_at_time0=~s/\]/_/g;
$measure_at_time0=~s/\//_/g;
print SIM $measure_at_time0;

#print SIM "echo deck_##deck_num## , ";
#print SIM "echo ";
##Still printing the echo statement

#to_ff consists of primary outputs also. So, the following part is not needed.This part contains only output ports.

# foreach $i(0 .. $#opins)
#{
#  $new=$opins[$i];
#  $new=~s/\[/_/g;
#  $new=~s/\]/_/g;
#  $new=~s/\//_/g; 
#
# if ($i == 0) 
#       {
#       print SIM 'echo "$&'.$new."_voltage\" , ";
#       print SIM '> glitch_report_outputs_'."##deck_num##.csv".'  $$New file'."\n"
#       } 
#       else 
#       {
#       print SIM 'echo "$&'.$new."_voltage\" , ";
#       print SIM '>> glitch_report_outputs_'."##deck_num##.csv".'  $$Appending to the file'."\n"
#       }
#
# } 

#Print out the measured spice outputs at the 2nd falling edge to glitch_report_outputs_*.csv
#to_ff consists of all FF output pins and primary outputs also.
print SIM "\n\n***************** saving the outputs at the 2nd falling edge ****************\n";

foreach $i(0 .. $#to_ff)
 {
 $new="ff_op_fall_".$i;

 if ($i == 0) 
  {
   print SIM 'echo "$&'.$new."\" , ";
   print SIM '> glitch_report_outputs_'."##deck_num##.csv".'  $$New file'."\n"
   } 
  else  
  {
   
   print SIM 'echo "$&'.$new."\" , ";
   print SIM '>> glitch_report_outputs_'."##deck_num##.csv".'  $$Appending to the file'."\n"
  }
 }
 
 #Print out the measured spice outputs at the 2nd rising edge to glitch_report_outputs_rise_*.csv
#to_ff consists of all FF output pins and primary outputs also.
print SIM "\n\n***************** saving the outputs at the 2nd rising edge ****************\n";

foreach $i(0 .. $#to_ff)
 {
 $new="ff_op_rise_".$i;

 if ($i == 0) 
  {
   print SIM 'echo "$&'.$new."\" , ";
   print SIM '> glitch_report_outputs_rise_'."##deck_num##.csv".'  $$New file'."\n"
   } 
  else  
  {
   
   print SIM 'echo "$&'.$new."\" , ";
   print SIM '>> glitch_report_outputs_rise_'."##deck_num##.csv".'  $$Appending to the file'."\n"
  }
 }
 

print SIM "\n\n***************** saving the outputs at time=0 ****************\n";

foreach $i(0 .. $#to_ff)
 {
 $new="ff_op_time0_".$i;

 if ($i == 0) 
  {
   print SIM 'echo "$&'.$new."\" , ";
   print SIM '> glitch_report_outputs_time0_'."##deck_num##.csv".'  $$New file'."\n"
   } 
  else  
  {
   
   print SIM 'echo "$&'.$new."\" , ";
   print SIM '>> glitch_report_outputs_time0_'."##deck_num##.csv".'  $$Appending to the file'."\n"
  }
 }
 
 
print SIM "\nquit\n\n";
print SIM ".endc\n\n\n";
print SIM ".end\n";





$num=@to_ff;
print SIM "\n** NUMBER OF OUTPUT PINS = $num";


print "\t********control statement written in the spice file\n";
#closing the files
close(SPC);
close(out);
chomp($sim1=`pwd`);
$sim1=$sim1."/$sim\n";
print "\n SPICE FILE written named ".$sim."\n";




