
#!/usr/bin/env python
#Read in a RTL file, do synthesis and placement, route
#Example usage: python python_subckts_in_weight_script.py -m c880_clk_ipFF -p /home/users/nanditha/Documents/utility/65nm/c880/ --scripts <path>

#freq added to synthesis part: Nov 19 2013

import optparse
import re,os
import time
from optparse import OptionParser

parser = OptionParser('A list of gates/flip-flops and their areas, is maintained in a database in another script. This current script will scan through the gates/flip-flops that are in the design, which have not been added in the database and warn the user. If the gate is not present, the user will need to add it to the database manually in python_weighted_gateselection_65.py \nAuthor:Nanditha Rao(nanditha@ee.iitb.ac.in)\n')

parser.add_option("-p","--path", help='Enter the path',dest='path')
parser.add_option("-m","--mod", help='Enter the entity name(vhdl) or module name (verilog) to be synthesised',dest='module_name')
parser.add_option("-e", "--scripts", dest="scripts",help="Enter the ENTIRE path to your scripts folder.")

#This is the most important line which will parse the cmd line arguments
(options, args) = parser.parse_args()

path=options.path
module=options.module_name
scripts_path=options.scripts

##############Find out the number of subckts in the current circuit############
f=open("%s/pnr/reports/%s_summary.rpt" %(path,module),"r")
fnew=open("%s/%s_weights_subckts.txt" %(path,module),"w")

lines=f.readlines()

flag=0
subckt_list=[]
num_of_instances=[]
total_area=[]
#Identify the lines in between "Cell Type" and #Pads
for i in range(0,len(lines)):
	#Get each line
	current_line=lines[i]
	
	if re.search("# Pads",current_line):
		flag=0
	if flag==1:
		#print "Current line:",current_line
		words=current_line.split()
		print "Words:",words
		print "subckt name:",words[0]
		subckt_list.append(words[0])
		num_of_instances.append(words[1])
		total_area.append(words[2])
		
	if re.search("Cell Type",current_line):
		flag=1
	
length=len(subckt_list)
print "Subckts names:",subckt_list
print "Length of subckts:",len(subckt_list)
fnew.writelines(subckt_list)

f.close()
fnew.close()


##############Find out the number of subckts in the weights script############
flag=0
f=open("%s/python_weighted_gateselection_65.py" %scripts_path,"r")
lines=f.readlines()


for i in range(0,len(lines)):
	#Get each line
	current_line=lines[i]				
	if re.search("gates=\[",current_line):
		flag=1
	else:
	 	flag=0
	if flag==1:
		subckt_line=current_line
		print "Subckt line:",subckt_line
		words=subckt_line.split(',')
		print words



weights=[]
print "***\n"
for j in range(0,len(words)):
	if re.search("\tgates=\[\"",words[j]):
		words[j] = re.sub("\tgates=\[", "", words[j])
	elif re.search("]\n",words[j]):
		words[j] = re.sub("]\n", "", words[j])
	if re.search("\"",words[j]):
		words[j] = re.sub("\"", "", words[j])
		#print "apostrophe replaced:", words[j]
	if re.search(" ",words[j]):
		words[j] = re.sub(" ", "", words[j])
	if re.search("  ",words[j]):
		words[j] = re.sub("  ", "", words[j])

	weights.append(words[j])	

print "Weights list" ,weights
print "Weights[0]" ,weights[0]		

len_weights=len(weights)
print "Length of weights",len_weights

print "Subckts names:",subckt_list
print "Subckts names[0]:",subckt_list[0]
print "Length of subckts:",len(subckt_list)
f.close()

##############Find out the subckts that are to be added to the weights script############
to_add=[]
num=[]
area=[]
ind_area=[]
int_area=[]
found=0
for k in range(0,len(subckt_list)):

	subckt_list[k]
	for j in range(0,len(weights)):
		if re.match(subckt_list[k],weights[j]):  
			#print "%s found to match with %s" %(s,weights[j])
			found=1
			break
		else:
			#print "%s not found to match with %s" %(s,weights[j])
			found=0	
		
	
	if found==0:
		to_add.append(subckt_list[k])
		num.append(num_of_instances[k])
		area.append(total_area[k])
		n=round((float(total_area[k])/float(num_of_instances[k])),2)
		ind_area.append(n)
		int_area.append(int(n))	
		#print "Subckt to be added:",subckt_list[k]

print "********************WARNING***********************\n"
print "*******Add these subckts to the weights selection script :*******\n",to_add


print "Length of the subckts to be added: ",len(to_add)
print "Instances of each:\n",num
print "Total area of the subckts to be added:\n",area
print "Individual area of the subckts to be added:\n",ind_area
print "Individual integer areas of the subckts to be added:\n",int_area
time.sleep(1)		


