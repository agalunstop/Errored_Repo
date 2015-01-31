#!/usr/bin/env python

#ASSUMPTION: This will always be excecuted on the 48core cluster user1@10.107.105.201 and the design folder will be copied always to /home/user1/simulations folder and executed

#Added time=0 measurements= Jul 9 2014
# Code modified to do post processing of the result files for the 2nd rising edge. Last section of the code is added : Feb 7 2014
#Multiple spice decks that were generated using deckgen in the remote machine, will be run using ngspice and GNU Parallel on the cluster. We can also ssh to other machines which have GNU Parallel and ngspice installed. ssh-keygen should have been done so that it would not ask for ssh password everytime we ssh to the machines.

#Example usage: python python_hspice_combine_csv_results.py -n 1000 -d LFSR -o 3 -p /home/user1/simulations/65nm/LFSR


import optparse
import re,os
import fileinput
import glob
import shutil
import time,csv

from optparse import OptionParser

parser = OptionParser('Once simulations are complete, the spice_decks folder contains glitch_report_outputs_%d.csv files which will all be combined into one output file in this script:<path>/spice_results/final_results_spice_outputs_%d.csv, where %d will be the outloop variable. 3 different summary files are created: 1. Containing flip-flop output values at 2nd rising edge - final_results_spice_output_rise.csv,\n 2. Containing flip-flop output values at 3rd rising edge- final_results_spice_output.csv.\n 3. Containing flip-flop output values at time=0 - final_results_spice_output_time0.csv- to check if the initial conditions are being set correctly.\n Author:Nanditha Rao(nanditha@ee.iitb.ac.in)\n')


parser.add_option("-n", "--num", type="int", dest="num_spice",help="Enter the number of spice decks to be simulated at a time")
#parser.add_option("-s", "--ssh", dest="ssh_txt",help="Enter the path to the text file which contains the IP addresses of the machines to which we can ssh to run ngspice using GNU Parallel. Eg is provided in sshmachines.txt")
parser.add_option("-p", "--path", dest="path",help="Enter the entire path to the design folder that is copied to remote machine")
parser.add_option("-d", "--dir", dest="folder",help="Enter the name of the design folder that is copied to remote machine")
parser.add_option("-o", "--outloop", dest="outloop",help="This is the number of times this script is executed in a loop. In case we have a lot of simulations, we can divide them into groups. For eg., if 10000 simulations need to be run, we can run only 1000 at a time. So we run this 10 times, and this becomes the outloop variable. This is passed from the top level script.")

(options, args) = parser.parse_args()

num_spice=int(options.num_spice)
#ssh_txt=options.ssh_txt
folder=options.folder
path=options.path
outloop=int(options.outloop)


#######################PRE-PROCESSING#######################

####################### NGSPICE SIMULATION RUN#######################
##seq 1 n - run n decks in current folder
# This is to execute GNU Parallel. +0 means utilise all cores in the processor.
#--sshloginfile file.txt uses the IP addresses of machines given the file.txt to ssh to them and run simulations. 
#THESE MACHINES SHOULD HAVE 'GNU Parallel' AND NGSPICE INSTALLED IN THEM. AND ALSO, SSH-KEY-GEN SHOULD BE DONE TO DO A PASSWORD-LESS LOGIN


start= ((outloop-1)*num_spice) + 1  # ((1-1)*10) +1 =1  , ((2-1)*10) +1 =11
end = (num_spice)*outloop  #(10*1) = 10, (10*2)=20


#os.system("seq %d %d| parallel --progress -j +0 --sshloginfile %s/sshmachines.txt 'cd %s/spice_decks_%s; pwd; hspice %s/spice_decks_%s/deck_{}.sp;pwd;' " % (start,end, path,path,outloop,path,outloop))

#time.sleep(2)

#print "****Resulting csv files are saved in the same folder in which the spice decks are****\n"

###################################################################################################################
#######################Now do the post processing of the result files for 3rd rise edge (2nd fall edge)#######################

#Combine all the csv results files and place the resulting file in the results folder
#Creating results folder is done way back in the modperl2_outwrtr_new.pl script. The spice headers are also written out in that script.

fh = open("%s/spice_results/headers.csv" %(path),"r")
header=fh.read()

fw1 = open("%s/spice_results/final_results_spice_outputs_%d.csv" %(path,outloop),"w")
#Write the header first and then write the csv outputs of the rest of the files
fw1.write(header)

start= ((outloop-1)*num_spice) + 1  # ((1-1)*10) +1 =1  , ((2-1)*10) +1 =11
end = (num_spice)*outloop  #(10*1) = 10, (10*2)=20


#Individual echo statements will lead to a process id at the end of each file. Deleteting them and getting transpose of all glitch_*.csv files
#Loop over all existing csv files

#######Combine the results of all csv files into one file final_results_spice_outputs_ ####

for num in range(start,(end+1)):  #Always for loop takes max len + 1
	fr = open("%s/spice_decks_%s/glitch_report_outputs_new_%d.csv" %(path,outloop,num), "r")
	data=fr.read()
	fw1.write(data)
	fr.close()

fw1.close()
fh.close()
print "****Combined all fall csv files into a single file in the results folder along with the header****\n"


###################################################################################################################
###################################################################################################################
#######################Now do the post processing of the result files for the 2nd rise edge #######################

#Combine all the csv results files and place the resulting file in the results folder
#Creating results folder is done way back in the modperl2_outwrtr_new.pl script. The spice headers are also written out in that script.

fh = open("%s/spice_results/headers.csv" %(path),"r")
header=fh.read()


fw1_rise = open("%s/spice_results/final_results_spice_outputs_rise_%d.csv" %(path,outloop),"w")
#Write the header first and then write the csv outputs of the rest of the files
fw1_rise.write(header)


start= ((outloop-1)*num_spice) + 1  # ((1-1)*10) +1 =1  , ((2-1)*10) +1 =11
end = (num_spice)*outloop  #(10*1) = 10, (10*2)=20


#Individual echo statements will lead to a process id at the end of each file. Deleteting them and getting transpose of all glitch_*.csv files
#Loop over all existing csv files
######Combine the results of all csv files into one file final_results_spice_outputs_rise_ #####

for num in range(start,(end+1)):  #Always for loop takes max len + 1
	fr = open("%s/spice_decks_%s/glitch_report_outputs_rise_new_%d.csv" %(path,outloop,num), "r")
	data=fr.read()
	fw1_rise.write(data)
	fr.close()

fw1_rise.close()
fh.close()
print "****Combined all rise csv files into a single file in the results folder along with the header****\n"



###################################################################################################################
#######################Now do the post processing of the result files for time=0 #######################

#Combine all the csv results files and place the resulting file in the results folder
#Creating results folder is done way back in the modperl2_outwrtr_new.pl script. The spice headers are also written out in that script.

fh = open("%s/spice_results/headers.csv" %(path),"r")
header=fh.read()


fw1_0 = open("%s/spice_results/final_results_spice_outputs_time0_%d.csv" %(path,outloop),"w")
#Write the header first and then write the csv outputs of the rest of the files
fw1_0.write(header)


start= ((outloop-1)*num_spice) + 1  # ((1-1)*10) +1 =1  , ((2-1)*10) +1 =11
end = (num_spice)*outloop  #(10*1) = 10, (10*2)=20


#Individual echo statements will lead to a process id at the end of each file. Deleteting them and getting transpose of all glitch_*.csv files
#Loop over all existing csv files
######Combine the results of all csv files into one file final_results_spice_outputs_rise_ #####

for num in range(start,(end+1)):  #Always for loop takes max len + 1
	fr = open("%s/spice_decks_%s/glitch_report_outputs_time0_%d.csv" %(path,outloop,num), "r")
	data=fr.read()
	fw1_0.write(data)
	fr.close()

fw1_0.close()
fh.close()
print "****Combined all time=0 csv files into a single file in the results folder along with the header****\n"



