#!/usr/bin/env python

##Example usage:  python python_ssh_addr_yuva.py -p /home/sonalg/Documents/utility/trial

import optparse
import re,os
import string
from optparse import OptionParser

parser = OptionParser('file read, write\n')
parser.add_option("-p","--path", help='Enter the path of design file at the cluster',dest='path')


#This is the most important line which will parse the cmd line arguments
(options, args) = parser.parse_args()

path=options.path

#fo = open('/home/sonalg/Documents/utility/trial/nodefile', 'r') 
#lines = fo.read()

#Read lines into a list
#lines = [line.strip() for line in open('/home/sonalg/Documents/utility/trial/nodefile')]
lines = [line.strip() for line in open('%s/nodes.txt' %path)]
new=[]

for r in range(len(lines)):
	#print r
	if r==0: 
		newstring=''.join(["16/sonalg@",lines[0]])		
		new.append(newstring)
	else:
		if(lines[r] != lines[r-1]):
			newstring=''.join(["16/sonalg@",lines[r]])
			new.append(newstring)



fw = open('%s/sshmachines.txt' %(path), 'w') 

#Write the following commands to this file
for item in new:
	fw.write("%s\n" %item)

fw.close()



