#!/usr/bin/env python
#Read in a RTL file, do synthesis and placement, route
#Example usage: python python1_read_RTL_syn_pnr_65.py -f /home/users/nanditha/Documents/utility/65nm/LFSR/lfsr.vhd -m lfsr -c 400

#Absolute paths introduced everywhere in the script, so that they can be run from one directory and no need of duplicating the scripts in all directories: June 25 2014
#Introduced -define_name_rules and -change_names for the created rules, to create case-insenstive net names.. i.e., to avoid same net names such as 'N1' and 'n1' in spice- which creates shorts. June 23 2014
#Eliminating clock gating: June 2014
#65nm lib files added: Apr 2014
#freq added to synthesis part: Nov 19 2013

import optparse
import re,os
import fileinput
import subprocess, time
from optparse import OptionParser

parser = OptionParser('This script reads in a vhdl or verilog file (RTL) and its test bench. It invokes rtl2gds utility to do synthesis and placement and route. The requirements of rtl2gds are the following tools: Design Compiler, SoC Encounter and Modelsim. The inputs to the script are listed as arguments below, which are all necessary arguments.\n The outputs of this script are same as the outputs of the rtl2gds utility. It creates varioous folders:man1, pnr, rtl, simulation, synthesis and template in the current working directory.\nThe files of interest to us are the following:\n1. pnr/op_data/$module_final.v - PNR verilog netlist\n2. pnr/op_data/$module_final.dspf - spice netlist \n3. pnr/reports/$module_summary.rpt - Cell area report - which will be used for optimisation later on.\nAuthor:Nanditha Rao(nanditha@ee.iitb.ac.in)\n')

parser.add_option("-f","--rtl", help='Enter the RTL (verilog or vhdl) file path- THE ENTIRE PATH',dest='filepath')
parser.add_option("-m","--mod", help='Enter the entity name(vhdl) or module name (verilog) to be synthesised',dest='module_name')
parser.add_option("-c","--clk", help='Enter the clk frequency in MHz, for eg., if 900MHz, enter 900',dest='clkfreq')
parser.add_option("-p", "--path", dest="path",help="Enter the ENTIRE path to your design folder (your working dir)- /home/user1/simulations/<design_folder_name>")
#This is the most important line which will parse the cmd line arguments
(options, args) = parser.parse_args()

filepath=options.filepath
clkfreq=options.clkfreq
module=options.module_name
path=options.path

#Invoke rtl2gds and create directories in CURRENT WORKING DIRECTORY ONLY
os.chdir("%s" %path)
os.system("rtl2gds -genScr=%s" %(path))

#Run synthesis
os.system('rtl2gds -rtl=%s -rtl_top=%s -syn -frequency=%s' %(filepath,options.module_name,clkfreq))	

#These 3 commands also work
#os.system("rtl2gds -rtl={0} -rtl_top={1} -syn".format(options.filepath, options.module_name))
#os.system("rtl2gds -rtl={options.filepath} -rtl_top={options.module_name} -syn".format(args=args))
#subprocess.call(['rtl2gds', '-rtl=' + options.filepath, '-rtl_top=' + options.module_name, '-syn'])
fcr = open('%s/synthesis/scripts/compile_dc.tcl' %(path), 'r') ## This is the tcl file for synthesis
data=fcr.readlines()
#print data
fcr.close()

fcw = open('%s/synthesis/scripts/compile_dc_backup.tcl' %(path), 'w') ## This is the tcl file for synthesis- backup
fcw.writelines(data)
fcw.close()

os.remove('%s/synthesis/scripts/compile_dc.tcl' %(path))

fin = open('%s/synthesis/scripts/compile_dc_backup.tcl' %(path), 'r') 
fnew = open('%s/synthesis/scripts/compile_dc.tcl' %(path), 'w') ## This is the new tcl file for synthesis


#Replace a current line
#with open('input') as fin, open('output','w') as fout:
for line in fin:
	if line == 'set_clock_gating_style  \\n':
		fnew.write('#set_clock_gating_style  \\n')
	elif line == 'insert_clock_gating > ../logs/insert_clock_gating.log\n':
		fnew.write('#insert_clock_gating > ../logs/insert_clock_gating.log\n')
	elif line == 'propagate_constraints -gate_clock\n':
		fnew.write('#propagate_constraints -gate_clock\n')
	elif line == 'identify_clock_gating\n':
		fnew.write('#identify_clock_gating\n')
	elif line == 'report_clock_gating -verbose > ../reports/clk_gate_verbose.rpt\n':
		fnew.write('#report_clock_gating -verbose > ../reports/clk_gate_verbose.rpt\n')
	elif line == 'change_names -rules verilog -hierarchy\n':
		fnew.write('define_name_rules rules_name -check_internal_net_name -case_insensitive\n')
		fnew.write('change_names -rules verilog -hierarchy\n')
		fnew.write('change_names -rules rules_name -hierarchy\n')
	else:
		fnew.write(line)

fnew.close()
fin.close()

fnew = open('%s/synthesis/scripts/compile_dc.tcl' %(path), 'r') 
newdata=fnew.readlines()
#print (newdata)

f1 = open('%s/synthesis/scripts/compile_dc_backup.tcl' %(path), 'w') 
#f1.writelines("This was the script compiled by the Design Compiler\n It gets overwritten in the pnr stepp. Hence saving a backup here\n\n")
f1.writelines(newdata)

f1.close()
fnew.close()

print "Done creating a new synthesis compile script \"synthesis/scripts/compile_dc.tcl\" \n"
print "There are no duplicate node or net names in the design \n"
print "Eliminating clock gating\n"

time.sleep(5)

##################################################################################################
fcr = open('%s/synthesis/scripts/technology.tcl' %(path), 'r') ## This is the tcl file for synthesis
data=fcr.readlines()
#print data
fcr.close()

fcw = open('%s/synthesis/scripts/technology_backup.tcl' %(path), 'w') ## This is the tcl tech file for synthesis- backup
fcw.writelines(data)
fcw.close()

os.remove('%s/synthesis/scripts/technology.tcl'%(path))

fin = open('%s/synthesis/scripts/technology_backup.tcl' %(path), 'r') 
fnew = open('%s/synthesis/scripts/technology.tcl' %(path), 'w') ## This is the new tcl file for synthesis


fnew.writelines('set TLIB /home/projects1/ST_Models/cmos065_534/CORE65GPSVT_5.1/SYNOPSYS/PR/CORE65GPSVT/LM/CORE65GPSVT_nom_1.00V_25C.db\n')

fnew.writelines('set LIBPATH /home/projects1/ST_Models/cmos065_534/CORE65GPSVT_5.1/SYNOPSYS/\n')

for i in range(4,(len(data))):
	fnew.writelines(data[i])
	
fnew.close()
fin.close()

fnew = open('%s/synthesis/scripts/technology.tcl' %(path), 'r') 
newdata=fnew.readlines()
#print (newdata)

f1 = open('%s/synthesis/scripts/technology_backup.tcl' %(path), 'w') 
#f1.writelines("This was the script compiled by the Design Compiler\n It gets overwritten in the pnr stepp. Hence saving a backup here\n\n")
f1.writelines(newdata)

f1.close()
fnew.close()

print "Done creating a new technology script for synthesis \"synthesis/scripts/technology.tcl\" \n"


if os.path.exists('%s/synthesis/run/' %(path)):
	os.chdir('%s/synthesis/run/' %(path))
	os.system('bash %s/synthesis/run/run_dc.bash' %path)

os.chdir('../../')
print "...Pause...Done synthesis with 65nm tech files.. Starting pnr"
time.sleep(5)

#########################Done synthesis#########################################
#Run place and route

os.system('rtl2gds -rtl=%s -rtl_top=%s -pnr -frequency=%s' %(filepath,options.module_name,clkfreq))	
#print "\n ****Completed synthesis and place and route****\n"


#Editing the scripts for 65nm
fcr = open('%s/pnr/conf/encounter.conf' %(path), 'r') ## This is the pnr conf script
data=fcr.readlines()
#print data
fcr.close()

fcw = open('%s/pnr/conf/encounter_backup.conf' %(path), 'w') ## This is the pnr conf script- backup
fcw.writelines(data)
fcw.close()

os.remove('%s/pnr/conf/encounter.conf' %(path))

fin = open('%s/pnr/conf/encounter_backup.conf' %(path), 'r') 
fnew = open('%s/pnr/conf/encounter.conf' %(path), 'w') ## This is the new pnr conf script


#with open('input') as fin, open('output','w') as fout:
for line in fin:
	if line == 'set TLF /cad/digital/rtl2gds/rtl2gds_install/LIB/lib/tsmc018/lib/osu018_stdcells.tlf\n':
		fnew.write('set TLF /home/projects1/ST_Models/cmos065_534/CORE65GPSVT_5.1/libs/CORE65GPSVT_nom_1.00V_25C.lib\n')
	elif line == 'set LEF /cad/digital/rtl2gds/rtl2gds_install/LIB/lib/tsmc018/lib/osu018_stdcells.lef\n':
		fnew.write('set LEF /home/projects1/ST_Models/cmos065_534/EncounterTechnoKit_cmos065_7m4x0y2z_AP@5.3.1/TECH/cmos065_7m4x0y2z_AP_Worst.lef \n')
	elif line == 'set rda_Input(ui_leffile) "${LEF}"\n':
		fnew.write('set rda_Input(ui_leffile) "${LEF} /home/projects1/ST_Models/cmos065_534/CORE65GPSVT_5.1/CADENCE/LEF/CORE65GPSVT_soc.lef" \n')
	else:
		fnew.write(line)
			
fnew.close()
fin.close()

fnew = open('%s/pnr/conf/encounter.conf' %(path), 'r') 
newdata=fnew.readlines()
#print (newdata)

f1 = open('%s/pnr/conf/encounter_backup.conf' %(path), 'w') 
f1.writelines(newdata)

f1.close()
fnew.close()

print "Done creating a new pnr conf script \"%s/pnr/conf/encounter.conf\" \n" %(path)
time.sleep(5)


#####################  Editing pnr.tcl  #############################
import fileinput
import sys


for line in fileinput.input('%s/pnr/scripts/pnr.tcl' %(path), inplace=1):
	if "metal5" in line:
		line = line.replace("metal5","M5")
	if "metal6" in line:
		line = line.replace("metal6","M6")
	if "    addFiller -cell FILL -prefix FILL\n" in line:
		line = line.replace("    addFiller -cell FILL -prefix FILL\n","    ##addFiller -cell FILL -prefix FILL\n")
	if "    addFiller -cell FILL -prefix FILL -fillBoundary\n" in line:
		line = line.replace("    addFiller -cell FILL -prefix FILL -fillBoundary\n","    ##addFiller -cell FILL -prefix FILL -fillBoundary\n")
		
		sys.stdout.write(line)
	
	else:
		sys.stdout.write(line)  

#####################################################################
if os.path.exists('%s/pnr/run/' %(path)):
	os.chdir('%s/pnr/run/' %(path))
	os.system('bash %s/pnr/run/run_pnr.bash' %path)

os.chdir('../../')
print "...Pause...Done pnr with 65nm.."
time.sleep(5)

#########Finding slack###########

print "\n***The worst case slack information for this frequency of operation (%s MHz) is given below:***\n" %clkfreq
print "***Make sure that the slack is positive enough, so that it is guaranteed that the spice simulation will operate at this frequency\n"

fo = open('%s/pnr/reports/5.postRouteOpt_%s/%s_postRoute.slk' %(path,module,module), 'r') 
#Has slack information
lines = fo.readlines()
print "Slack information:\n%s %s\n" %(lines[0],lines[1])
print "...Pause..."
time.sleep(5)

with open("%s/pnr/reports/5.postRouteOpt_%s/%s_postRoute.slk" %(path,module,module),"r") as f:
	words=map(str.split, f)

line1=words[1] #2nd line after header
slack_read=line1[2]
print "\nSlack is: %s" %slack_read
"""
slack_string=slack_read.replace("*/","")
slack_time=float(slack_string)
print "\nSlack is: %f ns" %slack_time
print "...Pause..."
time.sleep(5)
if slack_time < 0 :
	print "WARNING: Slack is negative. Your design WILL NOT function at the frequency %s\n" %clkfreq
	time.sleep(30)
else:
	print "Slack is positive. Your design WILL function at the frequency %s MHz\n" %clkfreq
	time.sleep(5)


if '1\'b1' in open('%s/pnr/op_data/%s_final.v' %(path,module).read():
	print "\n*******************WARNING******************\n"
	print "\n1'b1 is present in the verilog file and the corresponding nets should be manually tie it to vdd in the spice file\n"
	time.sleep(15)
else:
	print "\n1'b1 is NOT present in the verilog file and there is no need to manually tie it to vdd in the spice file\n"
	time.sleep(5)

if '1\'b0' in open('%s/pnr/op_data/%s_final.v' %(path,module).read():
	print "\n*******************WARNING******************\n"
	print "\n1'b0 is present in the verilog file and the corresponding nets should be manually tie it to gnd in the spice file\n"
	time.sleep(15)
else:
	print "\n1'b0 is NOT present in the verilog file and there is no need to manually tie it to gnd in the spice file\n"
	time.sleep(5)
"""

"""
slack_string=slack_read.replace("*/","")
slack_time=float(slack_string)
print "\nSlack is: %f ns" %slack_time
print "...Pause..."
time.sleep(5)

if slack_time < 0 :
	print "WARNING: Slack is negative. Your design WILL NOT function at the frequency %s\n" %clkfreq
	time.sleep(30)
else:
	print "Slack is positive. Your design WILL function at the frequency %s MHz\n" %clkfreq
	time.sleep(5)
"""

if '1\'b1' in open('%s/pnr/op_data/%s_final.v' %(path,module)).read():
	print "\n*******************WARNING******************\n"
	print "\n1'b1 is present in the verilog file and the corresponding nets should be manually tie it to vdd in the spice file\n"
	time.sleep(15)
else:
	print "\n1'b1 is NOT present in the verilog file and there is no need to manually tie it to vdd in the spice file\n"
	time.sleep(5)

if '1\'b0' in open('%s/pnr/op_data/%s_final.v' %(path,module)).read():
	print "\n*******************WARNING******************\n"
	print "\n1'b0 is present in the verilog file and the corresponding nets should be manually tie it to gnd in the spice file\n"
	time.sleep(15)
else:
	print "\n1'b0 is NOT present in the verilog file and there is no need to manually tie it to gnd in the spice file\n"
	time.sleep(5)


