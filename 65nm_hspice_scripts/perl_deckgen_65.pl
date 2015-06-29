#Example: perl perl_deckgen_65.pl -s /home/external/iitb/nanditha/simulations/65nm/b03/reference_spice.sp  -r /home/external/iitb/nanditha/simulations/65nm/b03/b03_reference_out/tool_reference_out.txt -n 1 -m b03 -f /home/external/iitb/nanditha/simulations/65nm/b03/ -g 4 -d 26 -c 22411 -i 3.35392154768e-09 -o 1 

#Modifications:
#time=0 RTL value selection - Jul 10 2014
#Using loop number to create multiple RTL files: June 15 2014
#$vdd=1 is added. Else incorrect results were being obtained: April 2014
#Removed the option of reading the $lib file : not needed, .ic for ref_minus1 added: Mar 19 2014
#.ic substitution included as part of the code. This code existed but wasnt being used. Modified reference_minus1 to reference_1.: Feb 21 2014
#THe previous change was incorrect. Reverting it back to "$start=$#temp-$num_opt+1;". A comman is needed after printing the "$random_drain," info to the RTL.csv files. Hence the drain info that it was writing was incorrect earlier. : Feb 12 2014

#Since I added 'drain' info also, I had to modify "$start=$#temp-$num_opt+1;" to :$start=$#temp-$num_opt;" inorder to print out all the RTL reference output values to the RTL.csv and RTL_2ndedge.csv : Feb 11 2014
#Appended the $random_drain to the RTL*.csv. This is needed to generate decks by just looking at the taxonomy.csv: Feb 11 2014
#Introduced 'next_2_cycle', which will capture the value of the rising edge of the next to next clk cycle. This is in sync with the change in modperl2_outwrtr_new.pl which was modified to write out all outputs at the rising edge instead of -ve edge: Feb 6 2014
#Code changed to include .ic ref values to all outputs of all FFs- Oct 20 2013
#Code changed to include .ic ref values for all inputs of all FFs in the spice file- didnt help - Oct 11 2013


#!/usr/bin/perl
use Getopt::Long;
#####################################################################
#
# Author        : Shahbaz Sarik
# Date          : 7th February 2013
# Purpose       : To create spice decks from a reference spice file 
#                 
# Copyright	: IIT BOMBAY
####################################################################

#  Routine to print Error message
sub printErrMessage {

 print "deckgen_remote_seed ERROR: BAD SYNTAX\n";
 print "TRY '$0 -h' or '$0 --help'  for help\n";
}
#  Routine to print man page
sub printManPage {
  print STDERR <<END; 
    
deckgen_remote_seed(1)                                                                                  

NAME

deckgen − Utility to create a simulatable spice deck from the template reference_spice.sp


SYNOPSIS

deckgen [input library file]  

DESCRIPTION

deckgen.pl script will get the 4 random numbers as input: random clk, random glitch instant, random gate and the random drain. It will modify the template reference_spice file to introduce the glitched version of the gate in the spice file.  It will go to the corresponding clk cycle in the decoder_op_ip_reference_out/tool_reference_out.txt and grab the input values at that clk edge and will insert these values into the PWL of the reference_spice.sp file. Similarly the random glitch instant is introduced as a parameter to create, say, spice_deck_1/deck_1.sp.  Again, for the next set of random numbers, the same is repeated, till the max number of decks specified, is generated. For each of the random clk cycles picked, this script will also write out the corresponding expected RTL output values of the next 2 clock cycles, into the decoder_op_ip_reference_out/RTL_2nd_edge.csv  and RTL.csv (3rd edge) files, which will be used as a reference value, during comparison of spice vs verilog simulation. The output of each of the spice deck simulations will be a glitch_report.csv file that contains the output signal values of the flip-flop outputs. 

Inorder to occupy less drive space, different groups of spice decks are created in the main script.
For eg., if I need to generate 10000 decks, it is not created in one folder, instead it is divided into groups of say 1000 decks each. The number of spice decks and the group is both taken as an input from the user. Folder spice_deck_1 is created first. 1000 simulations are completed, results of these are stored in spice_results and this directory spice_deck_1 is deleted. Next spice_deck_2 is created and so on till spice_deck_10. This is done in a loop in the main script which calls this deckgen script.

OPTIONS

 
Input library file

-|--input = <input library>

This file should be the spice library whose glitched version is to be created.


NOTE:

Provide full path for files
The glitched libray created in the current directory and named as glitch_library_name

USAGE

Typical usage of the utility after installation is explained below.


Examples:

deckgen_remote_seed -i|--input <library name> 
deckgen_remote_seed -i /home/user/Desktop/osu_lib.sp 

SEE ALSO

SPICE.

AUTHOR
Shahbaz sarik (shahbaz\@ee.iitb.ac.in)

This utility has been written for the “ Impact of soft error on circuit” experiment carried out under the guidence of Prof. Madhav. P. Desai (madhav\@ee.iitb.ac.in) at IITBombay.

COPYRIGHT
GPL IIT-Bombay
deckgen_remote_seed January 3rd February 2013  
    
    
END
}

#  Get the command line arguments
#  check for missing/extra arguments and show usage

# $spc -- reference_spice.sp
GetOptions( "s|spice=s"=>\$spc,
	    "r|ref=s"=>\$ref,
	    "v|volt=s"=>\$voltage,
	    "z|clk=s"=>\$clk,
	    "a|curr=s"=>\$current,
	    "n|num=s"=>\$deck_num,
	    "m|module=s"=>\$module,
	    "f|folder=s"=>\$folder,
	     "o|outloop=s"=>\$outloop,
	     "g|gate=s"=>\$rand_gate,
	     "d|drain=s"=>\$rand_drain,
	     "c|rclk=s"=>\$rand_clk,
	     "i|glitch=s"=>\$rand_glitch,
            "h|help"=>\$help,
            
          );
      
if ($help) {
  printManPage();
  exit(0);
}

if ($#ARGV >= 0 || $ref eq "" || $spc eq ""|| $deck_num eq "" || $module eq ""|| $folder eq "" || $outloop eq "" || $rand_gate eq "" || $rand_drain eq "" || $rand_clk eq "" || $rand_glitch eq "") {
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
$current_cycle="";
$next_cycle="";
$next_2_cycle="";
$minus1_cycle="";
$minus2_cycle="";
$minus3_cycle="";
$minus4_cycle="";
$minus5_cycle="";

#$sim_time=0;
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
#    if($_=~m/tran 10ps (.*)s/i)
#       {
#        $sim_time=$1; #print "simulation time = $1\n";
#       }
#    if($_=~m/Vvdd vdd 0 (.*)/i)
#       {
#        chomp($vdd=$1);
#       # print "Vdd for this technology is $vdd \n";
#       }
    if($_=~m/NUMBER OF OUTPUT PINS = (.*)/)
       {
         chomp($num_opt=$1)
       } 

 }
close(SPC);
#print "subcircuit starts from line number $gate_start_point and ends at line number $gate_end_point \n";
#print join("\n",@gates);
#print "total number of gates = $#gates \n";
print "\nThis is deck number $deck_num\n";
#Pick a random gate in the design
#srand($seed);
#$j=int(rand($#gates-1));

$j=int($rand_gate);
#$j+=1;
@temp=split(" ",$gates[$j]);
$random_gate=$temp[$#temp];
print "Random gate picked = $random_gate \n";
#print "the random gate selected is gate number $j \n";


#selcting arandom glitched gate
#open(LIB,"$lib")||die("unable to open file : $!");
#while(<LIB>)
# {  
#   if($_=~m/^\*\*\*\* $random_gate/)
#     {
#       $_=~m/(\d+)$/;
#	$drain=$1;
#	last;
#     }
#}
#Pick a random drain in the random gate in the design
#srand($seed);
#$random_drain=int(rand($drain-1));

$random_drain=int($rand_drain);
#$random_drain+=1;
print "Random drain  ----- $random_drain\n";
print "$gates[$j]-------------$random_gate\n";
$gates[$j]=~s/$random_gate/$random_gate\_$random_drain/;
#print join("\n",@gates);


#selecting a random clock cycle from the total number of cycles (as in refrence file)

#Not being used here. count calculated in perl_calculate_gates.pl
#open(REF,"$ref")||die("unable to open file : $!");
#count =0;
#while(<REF>)
# {  
#   $count++;
# }
#close(REF);
#This count value denotes the number of actual simulatable cycles for error analysys.

#$count-=10;
#print "\nnumber of simulatable clock cycles is $count \n";

#Pick a random clk cycle to simulate
#srand($seed);
$cycle=int($rand_clk);
#print "selected clock cycle : $cycle\n";
$count=0;
#storing the input output values from reference output file for present clock cycle and next cycle
#This file handle should be actually REF instead of SPC.
open(SPC,"$ref")||die("unable to open file : $!");
while(<SPC>)
 {  
     
    $count++;
    if($count==1)
       {
         chomp($header=$_);
       }
    else
       {
 	 $minus5_cycle =  $minus4_cycle;
 	 $minus4_cycle =  $minus3_cycle;
         $minus3_cycle =  $minus2_cycle;
         $minus2_cycle =  $minus1_cycle;
         $minus1_cycle =  $current_cycle;
         $current_cycle=$next_cycle;
         $next_cycle=$next_2_cycle;
         chomp($next_2_cycle=$_);
       }
       
    if($count==($cycle+3))
       {
          #print "last line = $count\n";print "\nDONE\n";
	  last;
       }
 }
#print "header : $header \n";
#print " clock cycle : $cycle input/output condition is $current_cycle \n";
#print " next clock cycle input/output condition is $next_cycle \n";
@cycle1=split(" ",$current_cycle);
@cycle2=split(" ",$next_cycle);

@cycle_minus1=split(" ",$minus1_cycle);
@cycle_minus2=split(" ",$minus2_cycle);
@cycle_minus3=split(" ",$minus3_cycle);
@cycle_minus4=split(" ",$minus4_cycle);
@cycle_minus5=split(" ",$minus5_cycle);

#selecting a random glitch location (between 1.2 clock_period to 1.5 clock period)
#$clk_period=$sim_time/2.5;
##default values of $voltage and $injected_curr

if ($voltage=="") {$voltage=1.0};
if ($current=="") {$current=0};
if ($clk=="") {$clk=1000};
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

#Pick a random glitch location in the clk cycle
#srand($seed);
#$glitch_location=1.2*$clk_period + rand(0.3*$clk_period);
$glitch_location=$rand_glitch;
print "Random glitch point is at time $glitch_location \n"; 

##calculating clk parameters
$clk_period = (1/$clk)*(0.000001);

$sim_time=3*$clk_period;#defining simulation time
$time_resolution=($sim_time/40);
$fall_from=(2.5*$clk_period); #defining fall time window
$fall_to= ($fall_from + 50e-12);

$rise_from_2nd=(1.5*$clk_period); #defining fall time window
$rise_to_2nd= ($rise_from_2nd + 50e-12);

$vdd = $voltage;
#creating the spice deck
#`mkdir $folder/spice_decks_$outloop`;
print "$folder/spice_decks_$outloop/deck_$deck_num.sp\n";
open(OPT,">$folder/spice_decks_$outloop/deck_$deck_num.sp")||die("unable to open file : $!");
print "\t\t\ !! SPICE DECK DIRECTORY CREATED !!\n";
#writing into the new spice file
$count=0;
open(SPC,"$spc")||die("unable to open file : $!");
while(<SPC>)
 {
    
  if($_=~m/\.ENDS/i)
     { 
      print OPT "\n$_";
     }  
 if($prnt==0)
     {
      print OPT "**clk_$cycle\_glitch_$glitch_location\_random_gate_$random_gate\_random_drain_$random_drain\_deck_number_$deck_num\n";
      $prnt=1;
     }
    $count++;
    $new=$_;
#Substituting the random glitch location
     if($new=~m/##glitch_location##/)
        {
         $new='+rise_delay= '.$glitch_location."s\n";

        }
#Substituting the deck number
     if($new=~m/##deck_num##/)
        {
          $new=~s/##deck_num##/$deck_num/;
        }
#Substituting the operating voltage
		if($new=~m/##op_voltage##/)
		{
			$new=~s/##op_voltage##/$voltage/;
		}
#Substituting the injected current
		if($new=~m/##injected_curr##/)
		{
			$new=~s/##injected_curr##/$current/;
		}
#Substituting the clk_period
		if($new=~m/##clk_period##/)
		{
			$new=~s/##clk_period##/$clk/;
		}
#Substituting the sim_time
		if($new=~m/##sim_time##/)
		{
			$new=~s/##sim_time##/$sim_time/g;
		}
#Substituting the time_resolution
		if($new=~m/##time_resolution##/)
		{
			$new=~s/##time_resolution##/$time_resolution/g;
		}
#Substituting the fall_from
		if($new=~m/##fall_from##/)
		{
			$new=~s/##fall_from##/$fall_from/g;
		}
#Substituting the fall_to
		if($new=~m/##fall_to##/)
		{
			$new=~s/##fall_to##/$fall_to/g;
		}
#Substituting the rise_from_2nd
		if($new=~m/##rise_from_2nd##/)
		{
			$new=~s/##rise_from_2nd##/$rise_from_2nd/g;
		}
#Substituting the rise_to_2nd
		if($new=~m/##rise_to_2nd##/)
		{
			$new=~s/##rise_to_2nd##/$rise_to_2nd/g;
		}

#Substituting the reference values
     if(($new=~m/PWL\(/))# ||($new=~m/\.ic/)
        {
	   ($temp1,$pinname)=split(" ",$new);
           #print $pinname."\n";
           @temp=split(" ",$header);
           foreach $index( 0 .. $#temp)
              {
                if($pinname eq $temp[$index])
                   {
                      #print "match found $pinname === $temp[$index]\n";
			#This is for the PWL statements in the spice file
		      $ref1=$cycle1[$index]*$vdd;
		      $ref2=$cycle2[$index]*$vdd;
		      $ref_minus1=$cycle_minus1[$index]*$vdd;
		      $ref_minus2=$cycle_minus2[$index]*$vdd;
		      $ref_minus3=$cycle_minus3[$index]*$vdd;
		      $ref_minus4=$cycle_minus4[$index]*$vdd;

#                      $new=$_;
                      $new=~s/##$pinname\_reference_1##/$ref1/g;
		      $new=~s/##$pinname\_reference_2##/$ref2/g;
		      $new=~s/##$pinname\_reference_minus1##/$ref_minus1/g;
		      $new=~s/##$pinname\_reference_minus2##/$ref_minus2/g;
		      $new=~s/##$pinname\_reference_minus3##/$ref_minus3/g;
		      $new=~s/##$pinname\_reference_minus4##/$ref_minus4/g;

                   }
              }
           
        }
     
 

#This part of the code is used
if(($new=~m/\.ic/))
        {
	   ($junk1,$temp1,$pinname)=split(" ",$new);
           chomp($pinname);
           $pinname=~s/_reference_1.*//;
           $pinname=~s/\#\#//;
          # print "pin name $pinname\n";
          # print $pinname."\n";
           @temp=split(" ",$header);
           foreach $index( 0 .. $#temp)
              {
  	    #  print "pinname:$pinname, temp $temp[$index] \n";
                if($pinname eq $temp[$index])
                   {	#print "Match: pinname:$pinname, temp $temp[$index] \n";
                      $ref_1=$cycle1[$index]*$vdd;
     			$ref_1_neg= $vdd- ($cycle1[$index]*$vdd); #Inverted value

#                      $new=$_;
                      $new=~s/##$pinname\_reference_1##/$ref_1/g;
                       $new=~s/##$pinname\_reference_1_neg##/$ref_1_neg/g;

		     
                   }
              }
           
        }
######################




     if(($count<=$gate_start_point)||($count>$gate_end_point))
        {
           print OPT $new;
        }
     if($count==$gate_start_point+1)
        {
          print OPT join("\n",@gates);
        }

 }
 
 
 
 #Appending to the RTL_2nd_edge reference output file, which contains outputs of those clk cycles, that were picked by this script randomly , at the 2nd rising edge of the clk
#This will be used for the spice vs verilog simulation comparison
open(IM,">>$folder/$module\_reference_out/RTL_2nd_edge_$outloop.csv");
print IM "\n";
print "Random drain..RTL_2nd_edge_$outloop.csv  ----- $random_drain\n";
#A comma is needed at the end of the last entry
print IM "$deck_num,$cycle,$glitch_location,$random_gate,$rand_gate,$random_drain,";
@temp=split (" ",$next_cycle);
$start=$#temp-$num_opt+1;
#$start=$#temp-$num_opt;
foreach $index( $start .. $#temp)
  {
     
       if ($index == $#temp) 
	{
	print IM "$temp[$index]";
	} 
	else 
	{
	print IM "$temp[$index],";
	}

  }



#Appending to the RTL reference output file, which contains outputs of those clk cycles, that were picked by this script randomly, at the 3rd rising edge of the clk
#This will be used for the spice vs verilog simulation comparison
open(IM,">>$folder/$module\_reference_out/RTL_$outloop.csv");
print IM "\n";
print "Random drain..RTL_$outloop.csv  ----- $random_drain\n";
#A comma is needed at the end of the last entry
print IM "$deck_num,$cycle,$glitch_location,$random_gate,$rand_gate,$random_drain,";
@temp=split (" ",$next_2_cycle);
$start=$#temp-$num_opt+1;
#$start=$#temp-$num_opt;
foreach $index( $start .. $#temp)
  {
     
       if ($index == $#temp) 
	{
	print IM "$temp[$index]";
	} 
	else 
	{
	print IM "$temp[$index],";
	}

  }




#Appending to the RTL_time0 reference output file, which contains outputs of those clk cycles, that were picked by this script randomly , at time=0
#This will be used for the spice vs verilog simulation comparison
open(IM0,">>$folder/$module\_reference_out/RTL_time0_$outloop.csv");
print IM0 "\n";
print "Random drain..RTL_time0_$outloop.csv  ----- $random_drain\n";
#A comma is needed at the end of the last entry
print IM0 "$deck_num,$cycle,$glitch_location,$random_gate,$rand_gate,$random_drain,";
@temp=split (" ",$current_cycle);
$start=$#temp-$num_opt+1;
#$start=$#temp-$num_opt;
foreach $index( $start .. $#temp)
  {
     
       if ($index == $#temp) 
	{
	print IM0 "$temp[$index]";
	} 
	else 
	{
	print IM0 "$temp[$index],";
	}

  }




