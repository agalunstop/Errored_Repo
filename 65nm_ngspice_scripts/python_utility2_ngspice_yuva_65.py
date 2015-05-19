
#!/usr/bin/env python


#Added option to pass operating voltage for comparison in the compare scripts -- sonal
#Created a time0 spice_rtl_difference file will check the initial condition that is obtained vs expected- so that we can check if there is some error - July 2014
#Modified the GNU_Parallel_hspice file to check if any deck is simulated using 'pseudo-transient method' - July 9th 2014
#Creating multiple RTL.csv and RTL_2ndedge.csv files- as many as there are number of outer loops: June 15 2014
#Backup directories renamed to 'backup_spice_decks_3rd_edge' and 'backup_spice_decks_2nd_edge': feb 12 2014.
#Calling the python_FF_strike_taxonomy.py and python_gate_strike_taxonomy.py scripts explicitly, since calling it through a function did not run on the yuva cluster: Feb 11 2014
#Calling the python_taxonomy_gate_FF.py script to tabulate the gate and FF taxonomy and combine the resultant 2 pdf files: Feb 11 2014
#Backup directories etc created for the 2nd rise edge measurement backup. Other scripts which are being used to measure the 2nd rise edge data are being run from this script: Feb 7 2014
#This version of the script has the facility of selecting the gate based on the area of the gate. This version of the script uses another script python_weighted_gateselection.py to pick the random gate based on its area: Nov 17 2013
#Glitch insertion window is within the 2.5 cycles, and not the 6.5 cycles that is required for the case with intermediate FFs

#Example usage: python /home/external/iitb/nanditha/simulations/65nm/scripts_run/python_utility2_ngspice_yuva_65.py -m c1908_clk_ipFF -p /home/external/iitb/nanditha/simulations/65nm/c1908 -d c1908 -t 65 -n 4 --group 4 --clk 350 --scripts_path /home/external/iitb/nanditha/simulations/65nm/scripts_run/

import optparse
import re,os
import glob,shutil,csv
import random
import subprocess, time
import random,sys
from  python_weighted_gateselection_65 import weight_selection
from  python_drain_selection_65 import drain_selection
from  python_gate_strike_taxonomy_65 import gate_strike_taxonomy

from optparse import OptionParser

parser = OptionParser("This script reads in the template spice file and the inputs to the script are listed as arguments below, which are all necessary arguments.\nAfter a previous script has copied the current working directory to a remote cluster, this script invokes several scripts inturn:\n1.perl_calculate_gates_clk.pl\n2.perl_calculate_drain.pl\n3.deckgen_remote_seed.pl\n4.python_GNUparallel_ngspice_remote.py\n5.python_compare_remote_seed.py\n6.python_count_flips_remote_seed.py\n\nThe tasks of these scripts will be described in the help section of the respective scripts. The current script needs pnr/reports/5.postRouteOpt_mult/mult_postRoute.slk as an input. The current script will calculate the number of gates in the design(spice) file, pick a random gate, calculate the number of distinct drains for this gate and pick a drain to introduce glitch it. It then invokes deckgen.pl to modify the template spice file to introduce the glitched version of the gate in the spice file. The deckgen creates multiple spice files which will contain different input conditions since they are generated at different clk cycles.\nThe python_GNUparallel_ngspice_remote.py will then distribute these spice files across the different machines in the cluster and simulate these decks using ngspice. The results are csv files which contain output node values after spice simulation.\nThe results are then concatenated into one file and compared against the expected reference outputs that were obtained by the RTL simulation. If the results match, then it means that there was no bit-flip, so a 0 is reported, else a 1 is reported for a bit-flip. The number of flips in a single simulation is counted. Finally, if there are multiple flips given atleast one flip, it is reported as a percentage.\nAuthor:Nanditha Rao(nanditha@ee.iitb.ac.in)\n")

parser.add_option("-m", "--mod",dest='module', help='Enter the entity name(vhdl) or module name (verilog)')
parser.add_option("-n", "--num",dest='num',  help='Enter the number of spice decks to be generated and simulated')
parser.add_option("-p", "--path", dest="path",help="Enter the ENTIRE path to your design folder (your working dir)- either this machine or remote machine.")
parser.add_option("-e", "--scripts_path", dest="scripts_path",help="Enter the ENTIRE path to your scripts folder.")
parser.add_option("-v", "--volt", dest="volt",help="Enter the operating voltage")
parser.add_option("-d", "--design", dest="design_folder",help="Enter the name of your design folder")
parser.add_option("-t", "--tech",dest='tech', help='Enter the technology node-for eg., For 180nm, enter 180')
parser.add_option("--group",dest='group',  help='Enter the number of spice decks to be simulated at a time. For eg., if -n option is 10000, and say we want to run 100 at a time, then enter 100')
parser.add_option("-c", "--clk",dest='clk', help='Enter the clk freq in MHz')
parser.add_option("-a", "--curr",dest='curr', help='Enter the peak current for glitch')


(options, args) = parser.parse_args()


module=options.module
volt=options.volt
num=options.num
path=options.path
design_folder=options.design_folder
tech=options.tech
num_at_a_time=options.group
clk=(options.clk)
curr=(options.curr)
scripts_path=options.scripts_path

start_loop=1

clk_period = (1.0/float(clk))*(0.000001)
half_clk_period = clk_period/2.0
change_time= half_clk_period/3.0
end_PWL= half_clk_period + change_time #in ns generally

#Whatever number of decks to be simulated- is assumed to be more than or equal to 1000.
#At a time, only 1000 are generated and run- to save disk space. After collecting results, they are deleted
num_of_loops=(int(num)/int(num_at_a_time))

print "path of the script being run: ",os.path.dirname(os.path.abspath(__file__))
print "current working dir: ",os.getcwd()
scripts_dir=os.getcwd()

os.system('python %s/python_subckts_in_weight_script.py -m %s -p %s --scripts %s' %(scripts_path,module,path,scripts_path))

if os.path.exists('%s/spice_results' %path):
	os.chdir('%s/spice_results' %path)
	for f in glob.glob("count*.csv"):
		os.remove(f)
		
if os.path.exists('%s/spice_results' %path):
	os.chdir('%s/spice_results' %path)
	for f in glob.glob("*.txt"):
		os.remove(f)
		
if os.path.exists('%s/spice_results' %path):
	os.chdir('%s/spice_results' %path)
	for f in glob.glob("spice_rtl_*.csv"):
		os.remove(f)

if os.path.exists('%s/spice_results' %path):
	os.chdir('%s/spice_results' %path)
	for f in glob.glob("tax*.csv"):
		os.remove(f)
		
if os.path.exists('%s/spice_results' %path):
	os.chdir('%s/spice_results' %path)
	for f in glob.glob("final_results_spice_outputs_*.csv"):
		os.remove(f)

if os.path.exists('%s/spice_results' %path):
	os.chdir('%s/spice_results' %path)
	for f in glob.glob("strike_*.csv"):
		os.remove(f)

if os.path.exists('%s/spice_results' %path):
	os.chdir('%s/spice_results' %path)
	for f in glob.glob("*.pdf"):
		os.remove(f)


os.chdir("%s" %scripts_dir)


#time.sleep(2)

#Clear Back up directory

backup_dir = '%s/backup_spice_decks_3rd_edge' %(path)


if os.path.exists(backup_dir):
	shutil.rmtree(backup_dir)

if not os.path.exists(backup_dir):
	os.mkdir(backup_dir)	


#Clear Back up directory for the rise edge case

backup_dir_rise = '%s/backup_spice_decks_2nd_edge' %(path)

if os.path.exists(backup_dir_rise):
	shutil.rmtree(backup_dir_rise)

if not os.path.exists(backup_dir_rise):
	os.mkdir(backup_dir_rise)	

#Clear Back up directory for the rise edge case

backup_dir_rise = '%s/backup_spice_decks_time0' %(path)

if os.path.exists(backup_dir_rise):
	shutil.rmtree(backup_dir_rise)

if not os.path.exists(backup_dir_rise):
	os.mkdir(backup_dir_rise)	


print "Deleting the existing spice decks before creating new ones!\n"
os.system('rm -rf %s/spice_decks_*' %path)



frand = open('%s/random_number_histogram.txt' %(path), 'w')

seed = random.randint(0, sys.maxint)
print "seed is: ", seed
frand.write("Seed:%d\n" %seed)

random.seed(seed) #Seeding the random number generator


clk_period = (1.0/float(clk))*(0.000001) #for the MHz

print "\nclk is ",clk
print "\nClk_period: ", clk_period
##This is to write out the processor nodes in a file, to be used by GNU Parallel later
'''
os.system('cat $PBS_NODEFILE > %s/nodes.txt' %path)
print "PBS NODEFILE contents....written to nodes.txt\n"
#time.sleep(3)

os.system('python %s/python_ssh_addr_yuva_65.py -p %s' %(scripts_path,path))
os.system('cat %s/sshmachines.txt' %path)
print "Check contents of sshmachines.txt file....\n"
#time.sleep(10)
######################################################################################################
'''
os.system("perl %s/perl_calculate_gates_clk_65.pl -s %s/reference_spice.sp  -r %s/%s_reference_out/tool_reference_out.txt -m %s -f %s" %(scripts_path,path,path,module,module,path))

time.sleep(2)
fg = open('%s/tmp_random.txt' %(path), 'r')
gate_clk_data = [line.strip() for line in fg]

#random gate will be picked after weighting it according to its area.
#This is done in another script python_weighted_gateselection.py

num_of_gates=int(gate_clk_data[0])
print "\nnum of gates is %d" %num_of_gates

num_of_clks=int(gate_clk_data[1])
print "\nnum of clocks is %d" %num_of_clks

fg.close()


if os.path.isfile("%s/%s_reference_out/RTL*.csv" %(path,module)):
	print "****Removing the existing RTL.csv file in folder %s_reference_out ****\n" %(module)
	os.remove("%s/%s_reference_out/RTL*.csv" %(path,module))

if os.path.isfile("%s/%s_reference_out/RTL_2nd_edge*.csv" %(path,module)):
	print "****Removing the existing RTL_2nd_edge.csv file in folder %s_reference_out ****\n" %(module)
	os.remove("%s/%s_reference_out/RTL_2nd_edge*.csv" %(path,module))
		
if os.path.isfile("%s/%s_reference_out/RTL_time0*.csv" %(path,module)):
	print "****Removing the existing RTL_time0.csv file in folder %s_reference_out ****\n" %(module)
	os.remove("%s/%s_reference_out/RTL_time0*.csv" %(path,module))

#Fresh simulation
for loop in range(start_loop, (num_of_loops+1)): 

	print "Now, creating multiple spice decks in spice_decks folder in current directory on the remote machine\n"
	
	
#########################################repeat_deckgen copied starting from here#######################################
		
		
	#Now, we need the header in RTL.csv, so we create an RTL.csv and copy the headers from the RTL_backup.csv that we had saved from Netlstfrmt.pl
	fout = open('%s/%s_reference_out/RTL_%d.csv' %(path,module,loop), 'w')
	fin = open('%s/%s_reference_out/RTL_backup.csv' %(path,module), 'r')

	in_data=fin.read()
	fout.write(in_data)

	fout.close()
	fin.close()


	#Now, we need the header in RTL_2nd_edge.csv, so we create an RTL.csv and copy the headers from the RTL_backup.csv that we had saved from Netlstfrmt.pl
	fout = open('%s/%s_reference_out/RTL_2nd_edge_%d.csv' %(path,module,loop), 'w')
	fin = open('%s/%s_reference_out/RTL_backup.csv' %(path,module), 'r')

	in_data=fin.read()
	fout.write(in_data)

	fout.close()
	fin.close()
	
	#Now, we need the header in RTL_time0.csv, so we create an RTL.csv and copy the headers from the RTL_backup.csv that we had saved from Netlstfrmt.pl
	fout = open('%s/%s_reference_out/RTL_time0_%d.csv' %(path,module,loop), 'w')
	fin = open('%s/%s_reference_out/RTL_backup.csv' %(path,module), 'r')

	in_data=fin.read()
	fout.write(in_data)

	fout.close()
	fin.close()
	
	
	
	if not os.path.exists('%s/spice_decks_%s' %(path,loop)):
		os.mkdir('%s/spice_decks_%s' %(path,loop))

	
	start= ((loop-1)*int(num_at_a_time)) + 1  # ((1-1)*10) +1 =1  , ((2-1)*10) +1 =11
	end = (int(num_at_a_time))*loop  #(10*1) = 10, (10*2)=20

	print "***Inside repeat_deckgen. Executing deckgen to create decks and RTL.csv reference file\n***"
	for loop_var in range(start, end+1): 
		
		#rand_gate= int(random.randrange(num_of_gates))  #A random gate picked. not used, because the below function will return the random weighted gate
		#This is called through a function written in python_weighted_gateselection.py
		rand_gate, rand_gate_name =  weight_selection(path);
		print "Random subckt line=%d" %rand_gate
		print "Random gate is: ",rand_gate_name

		
		#Calculates number of drains
		os.system('perl %s/perl_calculate_drain_65.pl -s %s/reference_spice.sp -l1 %s/glitch_CORE65GPSVT_selected_lib_vg.sp -r %s/%s_reference_out/tool_reference_out.txt -m %s -f %s -g %d ' %(scripts_path,path,path,path,module,module,path,rand_gate))

		fg = open('%s/tmp_random.txt' %(path), 'r')
		drain_data = [line.strip() for line in fg]

		num_of_drains=int(drain_data[0])
		print "\nnum of drains is %d" %num_of_drains

		fg.close()
#If num of drains is 2, randrange(2) returns 0 or 1,where as we want drain number 1 or drain number 2. so, doing +1
		#rand_drain= int(random.randrange(num_of_drains))+1  #A random drain picked. 
		
		#Pick random drain as per its area:
		rand_drain =  drain_selection(path,rand_gate_name);
		print "In main script-Random drain: %d" %rand_drain
		#A random clk picked. dont pick the 1st 10 clock cycles. 1st 3 have dont care outputs at the FFs. ANd we are simulating 6 clk cycles, so, initialisation is 4 clk cycles. so, leave a guardband by ignoring the 1st 10 clk cycles
		rand_clk= int(random.randrange(10,num_of_clks))  
		#print "Random clock cycle is: ",rand_clk
		
#Arrival_time_part + initial_clk_part should add up to 1.5 clk periods
#The clk starts from low to high and then low, before the 2nd rising edge starts. The input is changed in the high period and the glitch is expected to arrrive later on, and before the next rising edge (when the latch will open)
		#In every iteration, a different random number needs to be picked. Hence, this is inside the for loop
			

#This formula is incorrect if we run the expt with large slack. 
		#If slack is large, the glitch window gets reduced

		#unif=random.uniform(0,arrival_clk_part*clk_period)
		#rand_glitch= (initial_clk_part*clk_period) +  unif  #A random glitch picked
		
				
		#glitch in the 2nd cycle
		unif=random.uniform(0,0.99*clk_period) 
		rand_glitch= (0.51*clk_period) +  unif 

		#unif = random.uniform(0,1.0*clk_period) 
		#rand_glitch= (0.5*clk_period) +  unif 
		
		#glitch in the 3rd cycle
		#unif=random.uniform(0,0.95*clk_period) 
		#rand_glitch= (1.55*clk_period) +  unif 

		print "\nglitch within clk cycle= ",unif
		print "\nRandom gate: %d\nRandom drain: %d\nRandom clock cycle:%d\nRandom glitch location:%e\n " %(rand_gate,rand_drain,rand_clk,rand_glitch)
		frand.write("%d, %d, %d,%e\n" %(rand_gate,rand_drain,rand_clk,rand_glitch))

		#deckgen.pl will need to be remotely executed through python_repeat_deckgen.py multiple number of times
		os.system('perl %s/perl_deckgen_65.pl -s %s/reference_spice.sp  -r %s/%s_reference_out/tool_reference_out.txt -n %d -m %s -f %s  -o %s -g %s -d %s -c %s -i %s -v %s --clk %s --curr %s' %(scripts_path,path,path,module,loop_var,module,path,loop,rand_gate,rand_drain,rand_clk,rand_glitch,volt,clk,curr))
		
##################Script repeat_deckgen copied ends here####################################
	
		
	#The following script will run GNU Parallel and hspice 
	#os.system ('python python_hspice_mod_check_ic.py -p %s -n %s -d %s -o %d -c %s' %(path,num_at_a_time,design_folder,loop,scripts_dir))
	
	#os.system('python python_hspice_combine_csv_results.py -n %s -d %s -o %d -p %s' %(num_at_a_time,design_folder,loop,path))
	
	print "Running GNU Parallel and ngspice on the created decks\n"
	os.system('python %s/python_GNUparallel_ngspice_yuva_65.py -n %s -d %s -o %s -p %s' %(scripts_path,num_at_a_time,design_folder,loop,path))
	
	seed_new= int(random.randrange(100000)*random.random())  #Used by compare script to backup random decks
	#seed_new=seed*loop
	print "New seed every outer loop is ", seed_new

	#python_results_compare.py will then need to be remotely executed
	#Might need to execute these last 3 in a loop till the results are acceptable
	

	print "Comparing the RTL and spice outputs at the 2nd falling edge (3rd rising edge)\n"
	os.system('python %s/python_compare_3rd_edge_65.py -m %s -f %s -n %s -t %s -l %d -v %s' %(scripts_path,module,path,num_at_a_time,tech,loop,volt))
	print "Comparing the RTL and spice outputs at the 2nd rising edge \n"
	os.system('python %s/python_compare_2nd_edge_65.py -m %s -f %s -n %s -t %s -l %d -v %s' %(scripts_path,module,path,num_at_a_time,tech,loop,volt))
	
	print "Comparing the RTL and spice outputs at the time=0 \n"
	os.system('python %s/python_compare_time0_65.py -m %s -f %s -n %s -t %s -l %d -v %s' %(scripts_path,module,path,num_at_a_time,tech,loop,volt))

	
#For testing out new glitch files (afterdeleting process if at each echo statement). comment this out in the final run, else it will copy ALL spice files and consume lot of disk space
	
#########################################################
#Comment this out to see the decks and the result files it generates. 	

	spice_dir = '%s/spice_decks_%s' %(path,loop)

	
	if os.path.exists(spice_dir):
		shutil.rmtree(spice_dir)


########################################End of loop########################################################

print "Combining all rtl diff files\n"
#seed="1644931266534706027"
os.system('python  %s/python_count_flips_2nd_3rd_edge_65.py -f %s  -n %s  --group %s -s %s' %(scripts_path,path,num,num_at_a_time,seed))  #To save the seed to results file


#Add the details of number of DFFs
fa=open('%s/subcktinstances.sp' %path, 'r')
fb=open('%s/spice_results/count_flips_final_summary.csv' %path, 'a+')
read=fa.readlines()
filelen=len(read)
fb.writelines(read[filelen-3])
fb.writelines(read[filelen-2])
fb.writelines(read[filelen-1])
fa.close()
fb.close()

#Doing the gate taxonomy and strike taxonomy functions through this script.
print "\nDoing the taxonomy for gates\n"

"""
os.system('python  %s/python_gate_strike_taxonomy_65.py  -p %s -m %s' %(scripts_path,path,module)) 
"""
#Always run the gates first and then the FFs. FF script needs some outputs which are written out from the gates script.
gate_glitch_captured_multiple, gate_glitch_captured =  gate_strike_taxonomy(path,module);

print "\nDoing the taxonomy for FFs\n"
os.system('python  %s/python_FF_strike_taxonomy_65.py  -p %s -m %s --gl_multiple %d --gl_capture %d' %(scripts_path,path,module,gate_glitch_captured_multiple,gate_glitch_captured)) 

'''
print "\nCombining the pdf reports\n"
os.system('python %s/python_combine_pdfs_yuva_65.py -p %s/spice_results -m %s' %(scripts_path,path,module))
'''
