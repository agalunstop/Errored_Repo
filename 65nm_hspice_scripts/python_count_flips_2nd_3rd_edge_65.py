#!/usr/bin/env python

#Compare results of spice and RTL

#Changed the column iteration number for header from range(5) to range(6), since the drain number is also added: Feb 11 2014
#This script will count flips on the 2nd rising edge: Feb 7 2014

#Example usage: python python_count_flips_2nd_3rd_rise_65.py -f /home/users/nanditha/Documents/utility/65nm/b12/ -n 2000 --group 1000 -s 2594275917096658334

import optparse
import re,os
import csv, re,shutil
import math


from optparse import OptionParser


parser = OptionParser('This script counts the number of flips in each simulation result. It first combines all the <path>/spice_results/spice_rtl_difference_*.csv files into one file <path>/spice_results/spice_rtl_difference_summary.csv for both 2nd and 3rd edges. This file is then read and the number of flips is counted. If there is a flip, a \'1\' is reported for that output, and a \'0\' is reported for a no-flip case. \n\nThis information is written out in a table format into a file at <path>/spice_results/count_flips_final_summary.csv, in which the each row stands for one simulation, and each column contains the names of the output nodes\n This script reports the cases in which there was single flip, multiple flips, double flip, triple and atleast one flip. It calculates the probability of multiple flips given atleast one flip. So this means that, if there is a single particle strike causing a single glitch, and if it happens to cause a single bit-flip (fault), what is the probability that in such cases, more than one fault is likely to occur. The statistics such as mean, variance, stddeviation and std error are calculated. The number of decks to be simulated are chosen such that the std error will be less than 0.1.\n The single random seed from which the random numbers are generated is saved in the count_flips_final_summary.csv file so that the results can be reproduced. Author:Nanditha Rao(nanditha@ee.iitb.ac.in)\n')

parser.add_option("-f", "--folder", dest="path",help="Enter the ENTIRE path to your design folder(your working dir)- either on this machine or remote machine ")
parser.add_option("-n", "--num",dest='num',  help='Enter the total number of spice decks that were simulated')
parser.add_option("--group",dest='group',  help='Enter the number of spice decks that were simulated at a time. For eg., if -n option is 10000, and say we want to run 100 at a time, then enter 100')
parser.add_option("-s", "--seed",dest='seed', help='Enter the random seed so that it is saved in the result file, for future reference')

(options, args) = parser.parse_args()

num=options.num
num_at_a_time=options.group
path=options.path
seed=options.seed

num_of_loops=(int(num)/int(num_at_a_time))

print "\n****Counting flips****\n"

##############################Combine all the spice_rtl_difference_*.csv files into one file#############################

fw = open('%s/spice_results/spice_rtl_difference_3rd_edge_summary.csv' %(path), 'w') #2nd falling edge
summary_writer = csv.writer(fw)
fd = open('%s/spice_results/spice_rtl_difference_3rd_edge_1.csv' %(path), 'r') #Open in read mode: To read the header
diff_file = csv.reader(fd) 

diff_headers = diff_file.next() #diff headers
summary=[]


#print "\ndiff headers:",diff_headers
#Append header
summary.append(diff_headers)
#print "\nsummary is", summary
#summary_writer.writerows(summary)

fd.close()

#Combine data from all csv files
#for the number of files that exist
for num in range(1,(num_of_loops+1)): 
	fr = open("%s/spice_results/spice_rtl_difference_3rd_edge_%d.csv" %(path,num), "r")
	diff_file = csv.reader(fr)
	diff_headers = diff_file.next() #diff headers - exclude this. it has already been written

	for row in diff_file: #For every row in the diff file
		#print "\nRow in diff file is:", row
		summary.append(row) #rows in diff file

	fr.close()

summary_writer.writerows(summary)

fw.close()


##############################Combine all the spice_rtl_difference_2nd_edge_*.csv files into one file#############################
fw2 = open('%s/spice_results/spice_rtl_difference_2nd_edge_summary.csv' %(path), 'w')
summary_writer = csv.writer(fw2)
fd2 = open('%s/spice_results/spice_rtl_difference_2nd_edge_1.csv' %(path), 'r') #Open in read mode: To read the header
diff_file = csv.reader(fd2) 

diff_headers = diff_file.next() #diff headers
summary=[]


#print "\ndiff headers:",diff_headers
#Append header
summary.append(diff_headers) #
#print "\nsummary is", summary
#summary_writer.writerows(summary)

fd2.close()

#Combine data from all csv files
#for the number of files that exist
for num in range(1,(num_of_loops+1)): 
	fr2 = open("%s/spice_results/spice_rtl_difference_2nd_edge_%d.csv" %(path,num), "r")
	diff_file = csv.reader(fr2)
	diff_headers = diff_file.next() #diff headers - exclude this. it has already been written

	for row in diff_file: #For every row in the diff file
		#print "\nRow in diff file is:", row
		summary.append(row) #rows in diff file

	fr2.close()

summary_writer.writerows(summary)

fw2.close()

##############################Combine all the spice_rtl_difference_time0*.csv files into one file#############################

fwe = open('%s/spice_results/spice_rtl_difference_time0_summary.csv' %(path), 'w') #2nd falling edge
summary_writer = csv.writer(fwe)
fde = open('%s/spice_results/spice_rtl_difference_time0_1.csv' %(path), 'r') #Open in read mode: To read the header
diff_file = csv.reader(fde) 

diff_headers = diff_file.next() #diff headers
summary=[]


#print "\ndiff headers:",diff_headers
#Append header
summary.append(diff_headers)
#print "\nsummary is", summary
#summary_writer.writerows(summary)

fde.close()

#Combine data from all csv files
#for the number of files that exist
for num in range(1,(num_of_loops+1)): 
	fre = open("%s/spice_results/spice_rtl_difference_time0_%d.csv" %(path,num), "r")
	diff_file = csv.reader(fre)
	diff_headers = diff_file.next() #diff headers - exclude this. it has already been written

	for row in diff_file: #For every row in the diff file
		#print "\nRow in diff file is:", row
		summary.append(row) #rows in diff file

	fre.close()

summary_writer.writerows(summary)

fwe.close()

################################# Count the number of flips in 2nd and 3rd edge ###################################################
#The final file which will have the count for multiple flips
fflip_2nd = open('%s/spice_results/count_flips_2nd_edge_summary.csv' %path, 'wb')
fflip_3rd = open('%s/spice_results/count_flips_3rd_edge_summary.csv' %path, 'wb')
fflip = open('%s/spice_results/count_flips_final_summary.csv' %path, 'wb')
fd = open('%s/spice_results/spice_rtl_difference_3rd_edge_summary.csv' %path, 'rb') #3rd edge Rise = 2nd edge fall
fd_rise = open('%s/spice_results/spice_rtl_difference_2nd_edge_summary.csv' %path, 'rb') #2nd edge: Rise

diff_file = csv.reader(fd)
diff_file_rise = csv.reader(fd_rise)
flip_writer2 = csv.writer(fflip_2nd)
flip_writer3 = csv.writer(fflip_3rd)
flip_writer = csv.writer(fflip)

diff_headers = diff_file.next() #diff headers
diff_headers_rise= diff_file_rise.next() #diff headers
#print "diff_headers[0]= ",diff_headers[0]

flip=[]
flip2=[]
flip3=[]
k=[]
k2=[]
k3=[]

#Append header - start from 6- since we are omitting first 6 columns which have deck_num,clk,glitch,gate and subcktlinenum info,drain
#This is for the final summary file
for i in range(6,len(diff_headers)):
	k.append(diff_headers[i])
	#print "\nk in headers:",k

for i in range(6,len(diff_headers_rise)):
	k.append(diff_headers_rise[i])

k.append('flip_count')
flip.append(k)
#print "flip header is\n:", flip

#Header for the 2nd edge file
for i in range(6,len(diff_headers_rise)):
	k2.append(diff_headers_rise[i])

k2.append('flip_count_2nd_edge')
flip2.append(k2)


#Header for the 3rd edge file
for i in range(6,len(diff_headers)):
	k3.append(diff_headers[i])

k3.append('flip_count_3rd_edge')
flip3.append(k3)

num_col=len(diff_headers)
num_col_rise=len(diff_headers_rise)
last_col=num_col+num_col_rise+1
#print "Column numbers total: %d, last col=%d" %(num_col,last_col)

csv_rows=0
num_of_zero_flips=0
num_of_single_flips=0
num_of_double_flips=0
num_of_triple_flips=0
num_of_four_flips=0
more_than4_flips=0

for row in diff_file: #For every row in the diff file. There will be as many rows in diff_file_rise as well
	csv_rows=csv_rows+1 #This is excluding the header, since we have already done diff_file.next() to count the header
	k=[]
	k2=[]
	k3=[]
	count_num_fall=0
	count_num_rise=0	
	count_num=0
	
	row_rise= diff_file_rise.next() #get the next row in the diff_file_rise
#column iteration - number of columns. Dont count first 6 columns- since they are deck_num, clk, glitch, gate and subcktlinenum,drain

	#First append all the diff elements of 3rd rise edge (2nd fall) in one row
	for i in (range(6,num_col)): #python will stop looping at (num_col - 1)

		#print "\nRow in diff file is:", row
		#print "Row is:", row[i]  #Each value which is a string
		
		k.append(row[i]) #append the next row in the diff_file to the final count file
		k3.append(row[i]) #append the same in the fall edge file (3rd rise edge)
		count_num_fall = count_num_fall + int(row[i])

	k3.append(str(count_num_fall)) #Append to the last column thats newly added
	flip3.append(k3)
	
	#Next append all the diff_rise (2nd edge rise) elements in the same row
	for j in (range(6,num_col_rise)): #python will stop looping at (num_col - 1)

		#print "\nRow in diff_rise file is:", row_rise
		#print "Row in diff_rise file is:", row_rise
		#print "Row_rise is:", row_rise[j]  #Each value which is a string
		k.append(row_rise[j]) #append the next row in the diff_file_rise	
		k2.append(row_rise[j]) #append the same in the rise edge file (2nd rise edge)	
		count_num_rise = count_num_rise + int(row_rise[j])
	
	count_num= count_num_fall + count_num_rise

	k2.append(str(count_num_rise)) #Append to the last column thats newly added
	flip2.append(k2)	

	k.append(str(count_num)) #Append to the last column thats newly added
	#print "\n k with count is:",k
	flip.append(k)	
	#print"\nflip is:",flip

		
#	print "\nAt the end of row ",csv_rows
	#print "k is:",k

	#row[last_col]= count_num
	#print "\nAt the end of the row, count is: ",count_num 
	if (count_num == 0):
		num_of_zero_flips=num_of_zero_flips+1
	elif (count_num == 1):
		num_of_single_flips=num_of_single_flips+1
	elif (count_num == 2):
		num_of_double_flips=num_of_double_flips+1
	elif (count_num == 3):
		num_of_triple_flips=num_of_triple_flips+1
	elif (count_num == 4):
		num_of_four_flips=num_of_four_flips+1
	elif (count_num > 4):
		more_than4_flips=more_than4_flips+1



print"\nNumber of csv rows is:",csv_rows
num_of_multiple_flips = (csv_rows-num_of_zero_flips-num_of_single_flips)
atleast_one_flip = num_of_single_flips + num_of_multiple_flips  #(csv_rows-num_of_zero_flips)

print "\nZero flips=%d\nSingle flips=%d\nMultiple flips=%d\nDouble flips=%d\nTriple flips=%d\nFour flips=%d\nGreater than four flips=%d\nAtleast one flip=%d\n" %(num_of_zero_flips,num_of_single_flips,num_of_multiple_flips, num_of_double_flips,num_of_triple_flips,num_of_four_flips,more_than4_flips,atleast_one_flip)


print('\nNumber of random spice decks simulated:%d\n' %csv_rows)

if (num_of_multiple_flips > 0):
	probability=(float(num_of_multiple_flips)/float(atleast_one_flip))
else:
	probability=0.0
print '\nProbability of multiple flips given atleast one flip is:%d/%d = %f\nthat is: %f percent\n' %(num_of_multiple_flips,atleast_one_flip,probability,probability*100)


flip_writer2.writerows(flip2)	
flip_writer3.writerows(flip3)
flip_writer.writerows(flip)

fflip.write("\nZero flips=%d\nSingle flips=%d\nMultiple flips=%d\nDouble flips=%d\nTriple flips=%d\nFour flips=%d\nGreater than four flips=%d\nAtleast one flip=%d\n" %(num_of_zero_flips,num_of_single_flips,(csv_rows-num_of_zero_flips-num_of_single_flips), num_of_double_flips,num_of_triple_flips,num_of_four_flips,more_than4_flips,atleast_one_flip))

print('\nSeed generated was:%d\n' %(int(seed)))
fflip.write('\nSeed passed into the main script was:%d\n' %(int(seed)))

fflip.write('\nProbability of multiple flips given atleast one flip is:%d/%d = %f\nthat is: %f percent\n' %(num_of_multiple_flips,atleast_one_flip,probability,probability*100))

fflip.write('\nNumber of random spice decks simulated:%d\n' %csv_rows)

#Calculating statistics: mean, standard deviation, standard error and confidence intervals 
#Do this only if there is atleast one multiple flip. Else, there is no point in calculating it.
#And also, it will result in division by zero- for std_error_by_mean calculation

if (num_of_multiple_flips > 0):
	mean= (float(num_of_multiple_flips)/float(atleast_one_flip))

	variance_1st_term = (((1.0-mean)**2) * num_of_multiple_flips)  # number**2 indicates square of the number 
	variance_2nd_term = (((0.0-mean)**2) * (atleast_one_flip - num_of_multiple_flips))
	print "\nvariance 1st term ", variance_1st_term
	print "\nvariance 2nd term ", variance_2nd_term
	#N is made (N-1) when random sampling is involved. Hence we use (atleast_one_flip - 1)
	if (atleast_one_flip >1):
		variance = (variance_1st_term + variance_2nd_term) /(atleast_one_flip - 1) #no need to make atleast_one_flip as float

	else:
		variance = (variance_1st_term + variance_2nd_term) /(atleast_one_flip) 
		#fflip.write('\nVariance cannot be calculated since there is only one case of atleast one flip')
		#fflip.write('\nHence the statistics for design at path %s: cannot be printed \n' %path )	

	print "\nvariance ", variance

	standard_deviation = math.sqrt(variance) #this returns a float
	print "\nstandard_deviation ", standard_deviation
	standard_error = standard_deviation/(math.sqrt(atleast_one_flip)) #float again
	print "\nstandard_error ", standard_error
	std_error_by_mean = standard_error/mean
	print "\nstd_error_by_mean ", std_error_by_mean
	#95% confidence intervals

	lower_limit = mean - (standard_error*1.96)
	upper_limit = mean + (standard_error*1.96)

	print "\nconfidence intervals: upper limit: %f, lower limit: %f\n " %(lower_limit,upper_limit)

	print('\n***STATISTICS FOR MULTIPLE BUT FLIPS, GIVEN THAT ATLEAST ONE FAULT (FLIP) HAS OCCURED***\n' )
	print('Mean of multiple flips given atleast one flip is: %f\n' %(mean))
	print('Variance is: %f\n' %variance)
	print('Standard deviation is: %f\n' %standard_deviation)
	print('Standard error is (sigma/sqrt(N)): %f\n' %standard_error)
	print('Standard error divided by mean is (sigma/sqrt(N)/mean): %f\n' %std_error_by_mean)
	print('95 percent Confidence interval is: %f to %f \n' %(upper_limit,lower_limit))
	print('95 percent Confidence interval in percent is: %f percent to %f percent \n' %(lower_limit*100,upper_limit*100))

	fflip.write('\n***STATISTICS*** for design at path %s:\n' %path )
	fflip.write('Mean of multiple flips given atleast one flip is: %f\n' %(mean))
	fflip.write('Variance is: %f\n' %variance)
	fflip.write('Standard deviation is: %f\n' %standard_deviation)
	fflip.write('Standard error is (sigma/sqrt(N)): %f\n' %standard_error)
	fflip.write('Standard error divided by mean is (sigma/sqrt(N)/mean): %f\n' %std_error_by_mean)
	fflip.write('95 percent Confidence interval is: %f to %f \n' %(lower_limit,upper_limit))
	fflip.write('95 percent Confidence interval in percent is: %f percent to %f percent \n' %(lower_limit*100,upper_limit*100))

	

fflip.close()
fflip_2nd.close()
fflip_3rd.close()

"""
#Add the details of number of DFFs
fa=open('/%s/subcktinstances.sp' %path, 'r')
fb=open('/%s/spice_results/count_flips_summary.csv' %path, 'a+')
read=fa.readlines()
filelen=len(read)
fb.writelines(read[filelen-3])
fb.writelines(read[filelen-2])
fb.writelines(read[filelen-1])
fa.close()
fb.close()

"""









