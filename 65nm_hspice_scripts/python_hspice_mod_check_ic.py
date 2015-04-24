#!/usr/bin/env python


#Added time=0 measurements for checking if the initial conditions are being set correctly= Jul 10 2014
#Deleting the *.txt files in spice_decks folder : Jul 9 2014
#Commented out lines that create hspice*.sp glitch file-- not needed. July 9 2014
#Writing hspice_glitch_CORE65GPSVT_selected_lib_vg.sp: June 18 2014

#Example usage: python python_hspice_mod_check_ic.py -p /home/users/nanditha/Documents/utility/65nm/FF_optimisation/c432 -n 1 -d c432 -o 1 -c /home/users/nanditha/Documents/utility/65nm/scripts_run


import optparse
import re,os,glob,csv
import fileinput
import subprocess, time
from optparse import OptionParser
import sys

parser = OptionParser('This script converts the ngspice file into a hspice simulatable file. This script inturn calls python_GNUparallel_hspice_local_mc_65.py script to simulate the decks in parallel using GNU Parallel. Added time=0 measurements for checking if the initial conditions are being set correctly. \nAuthor:Nanditha Rao(nanditha@ee.iitb.ac.in)\n')

parser.add_option("-p","--path", help='Enter the RTL (verilog or vhdl) file path- THE ENTIRE PATH',dest='filepath')
parser.add_option("-n", "--num", type="int", dest="num_spice",help="Enter the number of spice decks to be simulated at a time")
parser.add_option("-d", "--dir", dest="folder",help="Enter the name of the design folder that is copied to remote machine")
parser.add_option("-o", "--dir_num", dest="dir_num",help="the number of the spice_decks_%d directory. Enter 1 if it is spice_Decks_1, Enter 2 if its spice_decks_2 etc")
parser.add_option("-c", "--cwd", dest="scripts_dir",help="path_of_script")

#This is the most important line which will parse the cmd line arguments
(options, args) = parser.parse_args()

path=options.filepath
num=int(options.num_spice)
folder=options.folder
dir_num=int(options.dir_num)
scripts_dir=options.scripts_dir

#Write hspice glitch file.. that does not have duplicate gnd and vdd nodes
#fin = open('%s/glitch_CORE65GPSVT_selected_lib_vg.sp' %(path), 'r') 
#fnew= open('%s/hspice_glitch_CORE65GPSVT_selected_lib_vg.sp' %(path), 'w') 

fin = open('%s/glitch_CORE65GPSVT_selected_lib_vg.sp' %(path), 'r') 
fnew= open('%s/hspice_glitch_CORE65GPSVT_selected_lib_vg.sp' %(path), 'w') 
for line in fin:
	if "gnd gnd vdd vdd" in line:
		line = line.replace("gnd gnd vdd vdd","gnd gnds vdd vdds")
		fnew.write(line)
	else:
		fnew.write(line)

fnew.close()
fin.close()
		
	
if os.path.exists('%s' %path):
	os.chdir('%s/spice_decks_%d' %(path,dir_num))
	for f in glob.glob("hspice_deck_*.sp"):
		os.remove(f)
		
	for f in glob.glob("*.st0"):
		os.remove(f)
		
	for f in glob.glob("*.txt"):
		os.remove(f)
	
	for f in glob.glob("*.csv"):
		os.remove(f)
	
	for f in glob.glob(".nfs*"):
		os.remove(f)

	for f in glob.glob("*.ic0"):
		os.remove(f)
	
	for f in glob.glob("*.bat"):
		os.remove(f)
		
file_names=os.listdir('%s/spice_decks_%d' %(path,dir_num))
num_of_files = len(file_names)
deck_num=[]

for j in range(0,num_of_files):
	text = file_names[j]
	m = re.search('deck_(.+?).sp', text)
	if m:
		deck_num.append(m.group(1))

print "Deck numbers", deck_num
	
		
print "Num of files= %d" %num_of_files
print "File names", file_names

#time.sleep (3)			
#Modify each file to be hspice compatible
fhspice=open('%s/spice_decks_%d/hspice.bat' %(path,dir_num),'w')
	
	
for i in range(0,num_of_files):
	print ("Opening %s/spice_decks_%d/%s" %(path,dir_num,file_names[i]))
	print ("Loop number %d",i)
	fin = open('%s/spice_decks_%d/%s' %(path,dir_num,file_names[i]), 'r') 
	fnew= open('%s/spice_decks_%d/hspice_deck_%s.sp' %(path,dir_num,deck_num[i]), 'w') 
	fhspice.write("hspice hspice_deck_%s.sp\n" %(deck_num[i]))
	
	
	print ("Creating %s/spice_decks_%d/hspice_deck_%s.sp\n" %(path,dir_num,deck_num[i]))	
	for line in fin:
		if line ==".include ../glitch_CORE65GPSVT_selected_lib_vg.sp\n":
			line=".include ../hspice_glitch_CORE65GPSVT_selected_lib_vg.sp\n"
			fnew.write(line)
			#print "line replaced"
			#print line
			#time.sleep(3)
			
		#if "gnd gnds vdd vdds" in line:
		#	line = line.replace("gnd gnds vdd vdds","gnd vdd")
		#	fnew.write(line)
		elif ".control" in line:
			line = line.replace(".control",".option measdgt=5 measform=3")
			fnew.write(line)
		
		elif "tran 20ps" in line:
			line = line.replace("tran 20ps",".tran 20ps")
			fnew.write(line)		
			
		elif "meas tran " in line:
			line = line.replace("meas tran ",".measure tran ")
			fnew.write(line)
			
		elif "quit" in line:
			line = line.replace("quit","")
			fnew.write(line)
			
		elif ".endc" in line:
			line = line.replace(".endc","")
			fnew.write(line)
			
		elif "option rshunt = 1e12" in line:
			line = line.replace("option rshunt = 1e12",".option rshunt = 1e12")
			fnew.write(line)
			
		elif "option itl4 = 100  reltol =0.005  trtol=8 pivtol=1e-11  abstol=1e-10" in line:
			line = line.replace("option itl4 = 100  reltol =0.005  trtol=8 pivtol=1e-11  abstol=1e-10",".option itl4 = 100  reltol =0.005  trtol=8 pivtol=1e-11  abstol=1e-10")
			
			fnew.write(line)		
	
		else:
			if not "echo" in line:
				fnew.write(line)
				

	fnew.close()
	fin.close()
	
fhspice.close()
print "Done creating hspice decks\n"
#time.sleep (3)	

#Run hspice simulations
#os.chdir("%s/spice_decks_%d/" %(path,dir_num))
#os.system("bash %s/spice_decks_%d/hspice.bat" %(path,dir_num)) 

os.system('python %s/python_GNUparallel_hspice_local_mc_65.py -n %d -d %s -o %d -p %s' %(scripts_dir,num,folder,dir_num,path))
print "Done running hspice\n"
#time.sleep (3)
os.chdir("../")
		
file_names=os.listdir('%s/spice_decks_%d' %(path,dir_num))
num_of_files = len(file_names)
deck_num=[]

print "path of the script being run: ",os.path.dirname(os.path.abspath(__file__))
print "current working dir: ",os.getcwd()
#time.sleep (3)

print "filenames: ",file_names

for j in range(0,num_of_files):
	text = file_names[j]
	m = re.search('hspice_deck_(.+?).sp', text)
	if m:
		deck_num.append(m.group(1))

#print "Deck numbers", deck_num
num_of_csv=len(deck_num)
#print "Len of Deck numbers", num_of_csv

#time.sleep (3)

#Rename the csv output files
for j in range(0,num_of_csv):
	if os.path.exists('%s/spice_decks_%d/hspice_deck_%s.mt0.csv' %(path,dir_num,deck_num[j])):
		print "Renaming %s/spice_decks_%d/hspice_deck_%s.mt0.csv" %(path,dir_num,deck_num[j])
		os.rename('%s/spice_decks_%d/hspice_deck_%s.mt0.csv' %(path,dir_num,deck_num[j]),'%s/spice_decks_%d/glitch_report_outputs_%s.csv' %(path,dir_num,deck_num[j]))


#time.sleep (3)
#Modify the output csv files.. remove the headers etc..
for i in range(0,num_of_csv):
	print "opening file %s/glitch_report_outputs_%s.csv to modify, remove headers"  %(path,deck_num[i])
	f=open("%s/spice_decks_%d/glitch_report_outputs_%s.csv"  %(path,dir_num,deck_num[i]),'r')
	lines=f.readlines()
	f.close()
	f=open("%s/spice_decks_%d/glitch_report_outputs_new1_%s.csv"  %(path,dir_num,deck_num[i]),'w')
	f.writelines(lines[4]) #Write values, ignoring the first few lines
	f.close()


	fr = open("%s/spice_decks_%d/glitch_report_outputs_new1_%s.csv" %(path,dir_num,deck_num[i]),"r")
	fout = open("%s/spice_decks_%d/glitch_report_outputs_new2_%s.csv" %(path,dir_num,deck_num[i]),"w")
	reader=csv.reader(fr)
	writer = csv.writer(fout)
	k=[]
	
	for row in reader:
		#print row 
		del row[-1] #last element  alter#
		del row[-1] #last but one element temp
		#print "new row:\n" , row
		k.append(row)
		#print "k is", k

	writer.writerows(k)  #write csv
	print "Written csv file without last 2 columns"
	fr.close()
	fout.close()
	
	print "To Write csv files three separate ones- rise, fall and time=0"
	f = open('%s/spice_decks_%d/glitch_report_outputs_new2_%s.csv' %(path,dir_num,deck_num[i]), 'rb')
	fout = open('%s/spice_decks_%d/glitch_report_outputs_new_%s.csv' %(path,dir_num,deck_num[i]), 'wb')
	fout2 = open('%s/spice_decks_%d/glitch_report_outputs_rise_new_%s.csv' %(path,dir_num,deck_num[i]), 'wb')
	fout0 = open('%s/spice_decks_%d/glitch_report_outputs_time0_%s.csv' %(path,dir_num,deck_num[i]), 'wb')

	reader = csv.reader(f)
	writer=  csv.writer(fout)
	writer2= csv.writer(fout2)
	writer0= csv.writer(fout0)
	#for row in reader:
		#print row
		
	row_len=len(row)
	half=row_len/3 #Divide by 3 since there are 3 different sets of values- fall, rise, and time=0
	#print "half is", half
	a=[]
	b=[]
	c=[]
	first_half=[]
	second_half=[]
	third_half=[]
	for h in range(0,half):
		#print "appending first half:",row[h]
		a.append(row[h])
		#print "list:",a
		b.append(row[h+half])
		#print "list2:",b
		c.append(row[h+half+half])
	print "***********\n"
	first_half.append(a)
	#print "list:",first_half
	second_half.append(b)	
	#print "list2:",second_half
	third_half.append(c)	
	writer.writerows(first_half)  #write csv
	writer2.writerows(second_half)  #write csv
	writer0.writerows(third_half)  #write csv
	
	f.close()
	fout.close()
	fout2.close()		
	fout0.close()


if os.path.exists('%s' %path):
	os.chdir('%s/spice_decks_%d' %(path,dir_num))
	for f in glob.glob("glitch_report_outputs_new1_*.csv"):
		os.remove(f)
	for f in glob.glob("glitch_report_outputs_new2_*.csv"):
		os.remove(f)	
		
#Alternate way of coding inline .. need not be used now..
"""
	for line in fileinput.input('%s/spice_decks_%d/%s' %(path,dir_num,file_names[i]), inplace=1):
		if "glitch_CORE65GPSVT_selected_lib_vg.sp" in line:
			line = line.replace("glitch_CORE65GPSVT_selected_lib_vg.sp","hspice_glitch_CORE65GPSVT_selected_lib_vg.sp")
		if "gnd gnds vdd vdds" in line:
			line = line.replace("gnd gnds vdd vdds","gnd vdd")
		if ".control" in line:
			line = line.replace(".control",".option list measdgt=5 measform=3")
		if "tran 20ps" in line:
			line = line.replace("tran 20ps",".tran 20ps")
		if "meas tran " in line:
			line = line.replace("meas tran ",".measure tran ")
		if "quit\n\n.endc" in line:
			line = line.replace("quit\n\n.endc\n","\n")
		
			sys.stdout.write(line)
	
	else:
		if not "echo" in line:
			sys.stdout.write(line) 
	
"""
