
#!/usr/bin/env python

#Original file is chosen to be the one which has R & C included. - July 9 2014
#Example usage: python python_choose_subckts_library.py -p /home/users/nanditha/Documents/utility/65nm/b12 -m b12
#Absolute paths introduced everywhere in the script, so that they can be run from one directory and no need of duplicating the scripts in all directories: June 25 2014

import optparse
import re,os
import time
from optparse import OptionParser

parser = OptionParser('This script collects the subckt instance names in the current design (from the pnr post layout dspf/spice file) and writes a library file with only those cells. This is done to reduce the lib file size .This reduces the simulation time in spice when it loads the file. Input is CORE65GPSVT_all_vdd_gnd_bulk_node.sp which needs to be supplied and the output is CORE65GPSVT_selected_lib_vg.sp which gets created in the design folder\nAuthor:Nanditha Rao(nanditha@ee.iitb.ac.in)\n')

parser.add_option("-p", "--path", dest="path",help="Enter the ENTIRE path to your design folder (your working dir)- /home/user1/simulations/<design_folder_name>")
parser.add_option("-m","--mod", help='Enter the entity name(vhdl) or module name (verilog) to be synthesised',dest='module_name')


#This is the most important line which will parse the cmd line arguments
(options, args) = parser.parse_args()

path=options.path
module=options.module_name


#f=open("../CORE65GPSVT_all_vdd_gnd_bulk_node_WL.sp" ,"r")
#f=open("../CORE65GPSVT_all_vdd_gnd_WL_noR.txt" ,"r")
#f=open("../CORE65GPSVT_all_vdd_gnd_WL_ad_noR.txt" ,"r")
f=open("../CORE65GPSVT_all_vdd_gnd_WL_ad.sp" ,"r")


os.chdir("%s" %path)
fnew=open("%s/CORE65GPSVT_selected_lib_vg.sp" %path ,"w")

lib_data=f.readlines()

fsp=open("%s/pnr/op_data/%s_final_new.dspf" %(path,module) ,"r")
data_dspf=fsp.readlines()

subckt1=[]
#Collect the subckt instance names in the current design

for i in range(0,len(data_dspf)):
	#Get each line
	current_line=data_dspf[i]
	#print "i=%d, current line=%s" %(i,current_line)
	if re.match("X",current_line):  #if it is a subckt instance
		#get the gate instance name	
		words=current_line.split()
		last_word=words[-1] #Save the last word	
		subckt1.append(last_word)		

		
print "Original Subckt list:",subckt1			
print "Length of original Subckt list:", len(subckt1)

###########################################################################

subckt=[]
#print "finding new subckt list"
for i in range(0,len(subckt1)):
	cur_elem=subckt1[i]
	#print "current elem:", cur_elem
	match=0
	for j in range(i+1,len(subckt1)):
		if (cur_elem==subckt1[j]):
			match=1
			#print "match=1, cur elem=%s, subckt1[%d]=%s ..exit while\n" %(cur_elem,j,subckt1[j])
	
	if match==0:
		subckt.append(cur_elem)
			

#Alternate option: subckt=set(subckt1)	
print "\n\nUnique Subckt list:",subckt			
print "Length of the unique subckt list:", len(subckt)
###########################################################################
#Parse the library file, match for "subckt" keyword and search for the desired instance name

fnew.writelines("\n***Library file consisting only the library cell instances in the %s/pnr/op_data/%s_final_new.dspf file\n\n" %(path,module))
fnew.writelines("***Library cell instances: \n")
fnew.writelines("***Total number of cell instances: %d\n" %(len(subckt)))
for g in range(0,len(subckt)):
	fnew.writelines("**%s\n" %(subckt[g]))
	
fnew.writelines("\n\n")
for i in range(0,len(lib_data)):
	current_line=lib_data[i]
	#print "current line:%s, i=%d" %(current_line,i)
	if re.match(".SUBCKT",current_line):
		#print "subckt line:", current_line
		#found=0
#		while(found==0): #Stop searching in the current line, once the subckt instance is found
		for ii in range(0,len(subckt)):
			#print "subckt element searching:",subckt[ii]
		#Take each element of the subckt list, i.e., each library cell.Find a match in the library file
			if (re.search(subckt[ii],current_line)):
				#Save the subckt definition to a new file
				#print "match found searching:",subckt[ii]
				#print "inside if ,current line: %s, i=%d" %(current_line,i)
				 #The for loop starts from the current line where the subckt instance was found in the previous step
				for a in range(i,len(lib_data)):
				#Continue till .ENDS is found	
					if (re.match(".ENDS",lib_data[a])):
						fnew.writelines(lib_data[a]) #Write out .ENDS and then stop
						fnew.writelines("\n\n")
						stop=1
						break
					else:
						fnew.writelines(lib_data[a]) #Write out current line
				
				#print "done writing data"
		
		
