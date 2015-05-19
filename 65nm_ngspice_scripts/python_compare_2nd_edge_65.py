#!/usr/bin/env python

#added -v option to pass operating voltage from jobscript
#Commented out copying glitch_reports.csv. Introduced an option of backing up hspice_deck*.sp or deck*.sp: June 23 2014
#Modified RTL_2ndedge.csv to RTL_2ndedge<loop_var>.csv.. RTL_1.csv, RTL_2.csv: June 15 2014
#Changed the #column iteration number from range(5) to range(6), since the drain number is also added: Feb 11 2014
#Compare results of spice and RTL, creates difference files and validation files for each run. Compare the 2nd rising edge in Verilog with the 2nd falling edge in spice: Feb 7 2014

#Example usage: python python_compare_2nd_edge.py -m decoder_op_ip -f /home/external/iitb/nanditha/simulations/decoder_ip_opFF_rise -n 10 -t 65 -l 1

import optparse
import re,os
import csv, re
import random,shutil

#import python_compare_remote

from optparse import OptionParser


#def main(): #Defining a main function
parser = OptionParser('This script reads in the <path>/spice_results/final_results_spice_outputs_%d.csv (spice output Flip-flop values at 2nd rising edge) and <path>/<module>_reference_out/RTL_2nd_edge.csv (RTL reference output values) to compare the spice simulation (with glitch) output with the original RTL simulation (no glitch) output. Two files are written out:\n1. <path>/spice_results/spice_rtl_difference_2ndedge_%d.csv and\n2.<path>/spice_results/spice_rtl_diff_testing_2ndedge_%d.csv.\n Both contain essentially same data but the _testing file has both spice and RTL outputs so that the result in the other file can be verified by us.\nIt then counts the number of flips- single/double etc., each time this script is executed (for a group of simulations) and then backs up few decks randomly for each case- no_flip case, single,double flip and triple flip case. These decks are saved in backup_spice_decks folder and a separate folder is created for each of the no flip, single, double flips etc.,\nAuthor:Nanditha Rao(nanditha@ee.iitb.ac.in)\n')

parser.add_option("-m", "--mod",dest='module', help='Enter the entity name(vhdl) or module name (verilog)')
parser.add_option("-v", "--volt",dest='volt', help='Enter the operating voltage')
parser.add_option("-f", "--folder", dest="path",help="Enter the ENTIRE path to your design folder(your working dir)- either on this machine or remote machine ")
parser.add_option("-n", "--num",dest='number', help='Enter the number of spice outputs to be compared to RTL outputs')
parser.add_option("-t", "--tech",dest='tech', help='Enter the technology node-for eg., For 180nm, enter 180')
parser.add_option("-l", "--outloop",dest='outloop', help='This is the number of times this script is executed in a loop. In case we are a lot of simulations, we can divide them into groups. For eg., if 10000 simulations need to be run, we can run only 1000 at a time. So we run this 10 times, and this becomes the outloop variable. This is passed from the top level script.')
#parser.add_option("-s", "--seed",dest='seed', help='Enter the random seed')

(options, args) = parser.parse_args()


module=options.module
volt=options.volt
path=options.path
num=options.number #num=num_at_a_time
tech=options.tech
outloop=options.outloop
#seed=int(options.seed)



if (tech == '180'):
	if (volt == ''):
		vdd_val=1.8
	else:
		vdd_val=volt
elif (tech == '130'):
	if (volt == ''):
		vdd_val=1.5
	else:
		vdd_val=volt
elif (tech == '90'):
	if (volt == ''):
		vdd_val=1.2
	else:
		vdd_val=volt
elif (tech == '65'):
	if (volt == ''):
		vdd_val=1.0
	else:
		vdd_val=volt
elif (tech == '45'):
	if (volt == ''):
		vdd_val=1.0
	else:
		vdd_val=volt
elif (tech == '32'):
	if (volt == ''):
		vdd_val=0.9
	else:
		vdd_val=volt
elif (tech == '22'):
	if (volt == ''):
		vdd_val=0.8
	else:
		vdd_val=volt

print "vdd value is ",vdd_val

#Removing the existing combined results file in the results folder
#if os.path.isfile("%s/spice_decks/results/count_flips.csv" %path):
#	print "****Removing the existing count_flips.csv in results folder****\n"
#	os.remove("%s/spice_decks/results/count_flips.csv" %path)



f = open('%s/spice_results/final_results_spice_outputs_rise_%d.csv' %(path,int(outloop)), 'rb')
frtl = open('%s/%s_reference_out/RTL_2nd_edge_%d.csv' %(path,module,int(outloop)), 'rb')
fout = open('%s/spice_results/spice_rtl_difference_2nd_edge_%d.csv' %(path,int(outloop)), 'wb')


reader = csv.reader(f)
reader_rtl = csv.reader(frtl)
writer = csv.writer(fout)


headers = reader.next() #Spice headers

#print "\nSpice Headers:%s", headers
del headers[-1]  #Deleting the process id at the end of the spice output csv file
#print "\nSpice Headers after removing the extra last header:", headers
#print "\nHeader len:\n", range(len(headers)) #[0, 1, 2, 3, 4, 5, 6, 7] 
#print "\nHeader len:\n", (len(headers)) #length

#print "\nSpice Headers[0]:\n", headers[0]



column = {}
for h in headers:
	column[h] = []
	#print "\nSpice Column inside for:\n", column

#print "\nSpice Column:\n", column
#print "\nColumn 1:\n",column['output_dec_7_']

for row in reader:
	for h, v in zip(headers, row):
		column[h].append(v)

#print "\n column[headers[0]]:\n", column[headers[0]]  #This means, column[output_dec_7_], where output_dec_7_ is the headers[0]
#print "\nSpice Column:\n", column

####################################################################################
headers_rtl = reader_rtl.next() #RTL headers

#print "\nRTL Headers:\n", headers_rtl
#print "\nRTL Headers[0]:\n", headers_rtl[0]

column_rtl = {}
for h2 in headers_rtl:
	column_rtl[h2] = []

#print "\nRTL Column:\n", column_rtl
#print "\nColumn 1:\n",column_rtl['output_dec_7_']

for row2 in reader_rtl:
	for h2, v2 in zip(headers_rtl, row2):
		column_rtl[h2].append(v2)

#print "\nColumn :\n", column_rtl[headers_rtl[0]]

####################################################################################
#k= range(2000) ##List in python

km=[]

#For non-matching headers
#Match the header in rtl file with that in every header in spice file
for r in range(len(headers_rtl)):
	no_match_flag=1	 ##Reset this every r loop only
	for s in range(len(headers)):
		if (no_match_flag==1): # If a header match is found, stop looping
			if (headers[s]!= headers_rtl[r]): ##That is, if the headers in spice file do not match with the
			#if (re.match(headers[s], headers_rtl[r]) == None): ##That is, if the headers in spice file do not match with the rtl headers
				no_match_flag=1 #No match
			else:
				no_match_flag=0 #Match


	if (no_match_flag==1):	 #If at the end of the looping over all headers, still there is no match, then #print out the header as it is		
		#print "\n\nNo Match!! \nHeader: %s \nspice column: %s \nRTL column: %s:\n" %(headers_rtl[r],column[headers[s]],column_rtl[headers_rtl[r]])
		k1=[]
		k1.append(headers_rtl[r]) #Append header
		rt= column_rtl[headers_rtl[r]] #Get the entire column in the RTL file

		for num_rows in range(0,int(num)): # 10 rows. This will be a user input
			k1.append(rt[num_rows])
			#print "\n rtl contents inside no match header is:", rt[num_rows]

		km.append(k1) # appended to an empty list
		#print "km is\n",km
	


#For matching headers
for r in range(len(headers_rtl)):
	match_flag=0	 ##Reset this every r loop only
	for s in range(len(headers)):
		if (match_flag==0): # If a header match is not found, loop through the spice headers, else if match found stop looping
			#print "\n\nlooping !! \nHeader RTL: %s \nspice header: %s \n" %(headers_rtl[r],headers[s])
	
			if (headers_rtl[r] == headers[s]): ##That is, if the headers in spice file match with the rtl headers
		#if (re.match(headers_rtl[r], headers[s]) != None): ##re.match which for the pattern at the beginning of the string. So IN_N1 and IN_N13 will say it matches
		
				k= [] ##Empty the temporary List before starting to append a new column
				#print "\n\nMatch found!! \n spice Header: %s \n RTL header: %s\nspice column: %s \nRTL column: %s:\n" %(headers[s],headers_rtl[r],column[headers[s]],column_rtl[headers_rtl[r]])
				match_flag=1 #match has been found. stop looping for this string pattern.
				k.append('diff_rise_edge_'+headers_rtl[r]) #Append header

				sp= column[headers[s]] #Get the entire column in the spice file
				#Each item in the column is referenced as sp[0], sp[1] etc
				#print "\nspice is:\n",sp[0]

				rt= column_rtl[headers_rtl[r]] #Get the entire column in the RTL file
				#Each item in the column is referenced as rt[0], rt[1] etc as many are the number of rows
				#print "\nrtl is:\n",rt[0]
	
				for num_rows in range(0,int(num)): # 10 rows. This will be a user input: total num
						
					spice_val=sp[num_rows]
					if rt[num_rows] == '1': 
						rtl_val = vdd_val  #This will have to depend on the techn node
						#print "\nrt val in rt[num_rows] == 1: is", rtl_val
					else: 
						rtl_val = 0
						#print "\nrt val in else is", rtl_val
		
		
					ab=abs(float(spice_val) - float(rtl_val))
					#print "\ndiff is\n",ab
					#print "\nab is\n", ab
					if ab <= 0.2*float(vdd_val): #This will have to depend on the techn node
						k.append('0')
						#print "\nab in ab<0.5 is\n", ab
					else:
						#if ab > 1.2: #This will have to depend on the techn node
						k.append('1')
						#print "\nab in > 1.2 is\n", ab
		
					#print "\nk inside s\n", k
				#print "\nk is\n", k  #All the data in the column is collected in k
				km.append(k) # appended to an empty list
				#print "km is\n",km
	
				

#Since we have collected data column-wise, and python has no way of writing out column wise to a csv,
#We take a transpose of the list and print it out!!
#print "transpose:\n",zip(*km)
writer.writerows(zip(*km))

fout.close()

################################# Validation file ###################################################

fd = open('%s/spice_results/spice_rtl_difference_2nd_edge_%d.csv' %(path,int(outloop)), 'rb') #Open in read mode
fv = open('%s/spice_results/spice_rtl_diff_testing_2nd_edge_%d.csv' %(path,int(outloop)), 'wb')

diff_file = csv.reader(fd)
validator= csv.writer(fv)

a=[]
####################################################################################
headers_diff = diff_file.next() #Diff headers

#print "\nDiff Headers:\n", headers_diff
#print "\nDiff Headers[0]:\n", headers_diff[0]

a.append(headers_diff)
#print "a=\n",a

column_diff = {}
for hd in headers_diff:
	column_diff[hd] = []

#print "\nColumn diff:\n", column_diff

for row in diff_file:  
	for hd, v in zip(headers_diff, row):
		column_diff[hd].append(v)

#print "\nColumn 0:\n", column_diff[headers_diff[0]]

####################################################################################

test=[]

#For all columns in RTL file
for r in range(len(headers_rtl)):
	#print "\n\nHeader: %s  \nRTL column: %s:\n" %(headers_rtl[r],column_rtl[headers_rtl[r]])
	k1=[]
	k1.append('rtl_2nd_rise_'+headers_rtl[r]) #Append header
	rt= column_rtl[headers_rtl[r]] #Get the entire column in the RTL file

	for num_rows in range(0,int(num)): # 10 rows. This will be a user in
		k1.append(rt[num_rows])
		#print "\n rtl contents in test file is:", rt[num_rows]

	test.append(k1) # appended to an empty list
	#print "test array is\n",test


#For all columns in spice file
for s in range(len(headers)):
	#print "\n\nHeader: %s \nspice column: %s\n" %(headers[s],column[headers[s]])
	k1=[]
	k1.append('spice_2nd_rise_'+headers[s]) #Append header
	sp= column[headers[s]] #Get the entire column in the RTL file

	for num_rows in range(0,int(num)): # 10 rows..
		k1.append(sp[num_rows])
		#print "\n rtl contents in test file is:", sp[num_rows]

	test.append(k1) # appended to an empty list
	#print "test array is\n",test

#print "diff file entering\n"


#For all columns in diff file
for s in range(len(headers_diff)):
	#pattern= re.compile('deck_num |clk |glitch')
	#if (pattern.match(headers_diff[s])): 
	#	print "Match found\n"
	if ((re.match(headers_diff[s], 'deck_num') == None) and (re.match(headers_diff[s], 'clk') == None) and (re.match(headers_diff[s], 'glitch') == None)and (re.match(headers_diff[s], 'gate') == None)and (re.match(headers_diff[s], 'subcktlinenum') == None)):
		#print "\n\nDiff Header: %s \nspice column: %s\n" %(headers_diff[s],column_diff[headers_diff[s]])
		k1=[]
		k1.append(headers_diff[s]) #Append header
		d= column_diff[headers_diff[s]] #Get the entire column in the RTL file

		for num_rows in range(0,int(num)): # 10 rows including header. This will be a user in
			k1.append(d[num_rows])
			#print "\n rtl contents in test file is:", d[num_rows]

		test.append(k1) # appended to an empty list
		#print "test array is\n",test

validator.writerows(zip(*test))

fv.close()
fd.close()

print "Ending compare\n"

	
	
#return per_multiple


"""
#Function call, returned value collected in x
if __name__ == "__main__":
    ret_multiple= main()
    print( ret_multiple )
"""

# Remember to uncomment this once debugging is done
if os.path.isfile('%s/spice_results/final_results_spice_outputs_rise_%d.csv' %(path,int(outloop))):
	print "****Removing the existing combined results file in results folder****\n"
	os.remove('%s/spice_results/final_results_spice_outputs_rise_%d.csv' %(path,int(outloop)))

	############################Comparison done#######################



###Count the number of flips so that the we can pick the files to be backed up. #########

###############Count the number of flips############
fd = open('%s/spice_results/spice_rtl_difference_2nd_edge_%d.csv' %(path,int(outloop)), 'rb') 
diff_file = csv.reader(fd)


diff_headers = diff_file.next() #diff headers

flip=[]
#k=[]
no_flip=[]
one_flip=[]
two_flips=[]
three_flips=[]
four_flips=[]
more_than4_flips=[]

num_col=len(diff_headers)
last_col=num_col+1


csv_rows=0


for row in diff_file: #For every row in the diff file. row is a list. 
	
	#csv_rows will give the row number
	csv_rows=csv_rows+1 #This is excluding the header, since we have already done diff_file.next() to count the header
	#k=[]
	count_num=0
	#print "\nRow in diff file is:", row
	#print "\nRow number is:", csv_rows
	deck_number= ((int(outloop)-1)*int(num)) + csv_rows
	#print "\nDeck number is:", deck_number

#column iteration - number of columns. Dont count first 6 columns- since they are deck_num, clk and glitch, gate and subcktlinenum,drain
	for i in (range(6,num_col)): #len is 11. so loop indexs stops at 10. So, if we want it to loop from 3 to 10, give range(3,11)		
		#k.append(row [i])
		count_num = count_num + int(row[i])
		
	
	if (count_num == 0):
		no_flip.append(deck_number)
	elif (count_num == 1):
		one_flip.append(deck_number)
	elif (count_num == 2):
		two_flips.append(deck_number)
	elif (count_num == 3):
		three_flips.append(deck_number)
	elif (count_num == 4):
		four_flips.append(deck_number)
	elif (count_num > 4):
		more_than4_flips.append(deck_number)

"""	
print "four flip decks=",four_flips
print "three flip decks=",three_flips
print "two flip decks=",two_flips
print "one flip decks=",one_flip
print "No flip decks=",no_flip	
"""

################################### Counting flips done ###################################################

##########################################Backup few random decks of the total spice files#########################################
loop=int(outloop)

len_morethan4=0
len4=0
len3=0
len2=0
len1=0
len0=0

#Backup all files		
##copytree requires that the destination directory not already exist
#shutil.copytree('%s/spice_decks' %path, '%s/backup_spice_decks/spice_%d' %(path,loop),symlinks=False, ignore=None)
#Save decks in which > 4 flips occured
if len(more_than4_flips) != 0 :
	
	len_morethan4=len(more_than4_flips)
	if not os.path.exists('%s/backup_spice_decks_2nd_edge/four_flip' %(path)):
		os.mkdir('%s/backup_spice_decks_2nd_edge/four_flip' %(path))
	for i in (range(0,len_morethan4)):
		if os.path.isfile('%s/spice_decks_%d/deck_%d.sp' %(path,loop,more_than4_flips[i])):
			shutil.copy('%s/spice_decks_%d/deck_%d.sp' %(path,loop,more_than4_flips[i]), '%s/backup_spice_decks_2nd_edge/four_flip' %(path))
			#shutil.copy('%s/spice_decks_%d/glitch_report_outputs_rise_%d.csv' %(path,loop,more_than4_flips[i]), '%s/backup_spice_decks_2nd_edge/four_flip' %(path))
		if os.path.isfile('%s/spice_decks_%d/hspice_deck_%d.sp' %(path,loop,more_than4_flips[i])):
			shutil.copy('%s/spice_decks_%d/hspice_deck_%d.sp' %(path,loop,more_than4_flips[i]), '%s/backup_spice_decks_2nd_edge/four_flip' %(path))


#Save decks in which 4 flips occured
if len(four_flips) != 0 :
	
	len4=len(four_flips)
	if not os.path.exists('%s/backup_spice_decks_2nd_edge/four_flip' %(path)):
		os.mkdir('%s/backup_spice_decks_2nd_edge/four_flip' %(path))
	for i in (range(0,len4)):
		if os.path.isfile('%s/spice_decks_%d/deck_%d.sp' %(path,loop,four_flips[i])):
			shutil.copy('%s/spice_decks_%d/deck_%d.sp' %(path,loop,four_flips[i]), '%s/backup_spice_decks_2nd_edge/four_flip' %(path))
			#shutil.copy('%s/spice_decks_%d/glitch_report_outputs_rise_%d.csv' %(path,loop,four_flips[i]), '%s/backup_spice_decks_2nd_edge/four_flip' %(path))
		if os.path.isfile('%s/spice_decks_%d/hspice_deck_%d.sp' %(path,loop,four_flips[i])):
			shutil.copy('%s/spice_decks_%d/hspice_deck_%d.sp' %(path,loop,four_flips[i]), '%s/backup_spice_decks_2nd_edge/four_flip' %(path))

#Save decks in which 3 flips occured
if len(three_flips) != 0 :
	
	len3=len(three_flips)
	if not os.path.exists('%s/backup_spice_decks_2nd_edge/three_flip' %(path)):
		os.mkdir('%s/backup_spice_decks_2nd_edge/three_flip' %(path))
	for i in (range(0,len3)):
		if os.path.isfile('%s/spice_decks_%d/deck_%d.sp' %(path,loop,three_flips[i])):
			shutil.copy('%s/spice_decks_%d/deck_%d.sp' %(path,loop,three_flips[i]), '%s/backup_spice_decks_2nd_edge/three_flip' %(path))
			#shutil.copy('%s/spice_decks_%d/glitch_report_outputs_rise_%d.csv' %(path,loop,three_flips[i]), '%s/backup_spice_decks_2nd_edge/three_flip' %(path))
		if os.path.isfile('%s/spice_decks_%d/hspice_deck_%d.sp' %(path,loop,three_flips[i])):
			shutil.copy('%s/spice_decks_%d/hspice_deck_%d.sp' %(path,loop,three_flips[i]), '%s/backup_spice_decks_2nd_edge/three_flip' %(path))

#Save decks in which 2 flips occured
if len(two_flips) != 0 :
			
	len2=len(two_flips)
	if not os.path.exists('%s/backup_spice_decks_2nd_edge/two_flip' %(path)):
		os.mkdir('%s/backup_spice_decks_2nd_edge/two_flip' %(path))
	for i in (range(0,len2)):
		if os.path.isfile('%s/spice_decks_%d/deck_%d.sp' %(path,loop,two_flips[i])):
			shutil.copy('%s/spice_decks_%d/deck_%d.sp' %(path,loop,two_flips[i]), '%s/backup_spice_decks_2nd_edge/two_flip' %(path))
			#shutil.copy('%s/spice_decks_%d/glitch_report_outputs_rise_%d.csv' %(path,loop,two_flips[i]), '%s/backup_spice_decks_2nd_edge/two_flip' %(path))
		if os.path.isfile('%s/spice_decks_%d/hspice_deck_%d.sp' %(path,loop,two_flips[i])):
			shutil.copy('%s/spice_decks_%d/hspice_deck_%d.sp' %(path,loop,two_flips[i]), '%s/backup_spice_decks_2nd_edge/two_flip' %(path))


save_1=1 #Save one single flip deck 
save_0=1 #Save one no flip deck

#Save decks in which 1 flip occured
if len(one_flip) != 0:
			
	len1=len(one_flip)
	if not os.path.exists('%s/backup_spice_decks_2nd_edge/one_flip' %(path)):
		os.mkdir('%s/backup_spice_decks_2nd_edge/one_flip' %(path))
	
	#for i in (range(0,save_1)):
	#random.seed(seed)
	random_deck= random.randrange(len1) #Pick a random array index in the length of the array
	if os.path.isfile('%s/spice_decks_%d/deck_%d.sp' %(path,loop,one_flip[random_deck])):
		shutil.copy('%s/spice_decks_%d/deck_%d.sp' %(path,loop,one_flip[random_deck]), '%s/backup_spice_decks_2nd_edge/one_flip' %(path))
		#shutil.copy('%s/spice_decks_%d/glitch_report_outputs_rise_%d.csv' %(path,loop,one_flip[random_deck]), '%s/backup_spice_decks_2nd_edge/one_flip' %(path))
		#print "one flip deck saved=",one_flip[random_deck]
	if os.path.isfile('%s/spice_decks_%d/hspice_deck_%d.sp' %(path,loop,one_flip[random_deck])):
		shutil.copy('%s/spice_decks_%d/hspice_deck_%d.sp' %(path,loop,one_flip[random_deck]), '%s/backup_spice_decks_2nd_edge/one_flip' %(path))
		
		
#Save decks in which no flip occured
if len(no_flip) != 0:
		
	len0=len(no_flip)
	if not os.path.exists('%s/backup_spice_decks_2nd_edge/no_flip' %(path)):
		os.mkdir('%s/backup_spice_decks_2nd_edge/no_flip' %(path))
	
	#for i in (range(0,save_0)):
	#random.seed(seed)
	random_deck= random.randrange(len0) #Pick a random array index in the length of the array
	if os.path.isfile('%s/spice_decks_%d/deck_%d.sp' %(path,loop,no_flip[random_deck])):
		shutil.copy('%s/spice_decks_%d/deck_%d.sp' %(path,loop,no_flip[random_deck]), '%s/backup_spice_decks_2nd_edge/no_flip' %(path))
		#shutil.copy('%s/spice_decks_%d/glitch_report_outputs_rise_%d.csv' %(path,loop,no_flip[random_deck]), '%s/backup_spice_decks_2nd_edge/no_flip' %(path))
		#print "Zero flip deck saved=",no_flip[random_deck]
	if os.path.isfile('%s/spice_decks_%d/hspice_deck_%d.sp' %(path,loop,no_flip[random_deck])):
		shutil.copy('%s/spice_decks_%d/hspice_deck_%d.sp' %(path,loop,no_flip[random_deck]), '%s/backup_spice_decks_2nd_edge/no_flip' %(path))


##################################### Backing up done ###########################################

