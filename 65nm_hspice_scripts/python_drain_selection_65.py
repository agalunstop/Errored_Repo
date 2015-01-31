
#!/usr/bin/env python

#Example usage: python python_drain_selection_65.py /home/users/nanditha/Documents/utility/65nm/decoder_65nm

#This script chooses a random drain from the picked random gate. The list of the drains and the corresponding subckts of their gates,and the drain areas area are available in <path>/drain_areas.txt written out by perl_glitchlibgen.pl. Based on this, a random drain is chosen such that the drain with the larger area has a higher probability of getting picked.  The earlier perl script perl_calculate_drain_65.pl is not needed if this is run.
#Nanditha Rao


def drain_selection(path,rand_gate_name_in):
	
	import random,re,time
	print "Random gate name is %s" %rand_gate_name_in
	fg = open("%s/drain_areas.txt" %path , "r")
	data = [line.strip() for line in fg] #Get the lines in the file
	length=len(data) #number of lines in the file
	#print data
	print "\n\n"
	drain_areas=[]

	for i in range(len(data)):
		print "data is %s" %data[i]
		rand_gate_name=rand_gate_name_in+"_" #rand_gate_name=rand_gate_name+"_" will introduce recursively many '_'
		#print "Gate name is",rand_gate_name
		#time.sleep(3)
		if re.match(rand_gate_name,data[i]):
			print "match found in line %s" %data[i]
			words=data[i].split() #Split the sentence into words
			print words[1] #drain area

			drain_areas.append(float(words[1]))
	print "drain_areas"
	print drain_areas
	#print "drain_area is %f" %drain_areas[0]

	sum=0.0
	for j in range(len(drain_areas)):
		sum=sum+drain_areas[j]
		
	print "Sum is %f" %sum

	normalize_area=[]

	#Normalize
	for j in range(len(drain_areas)):
		normalize_area.append(drain_areas[j]/sum)
	#print "Normalize_area"
	#print normalize_area

	norm_sum=0.0
	for j in range(len(drain_areas)):
		norm_sum=norm_sum+normalize_area[j]

	#print "Norm Sum is %f" %norm_sum

	#Cumulative sum
	cumulative_sum=0.0
	cumulative_list=[]
	for j in range(len(normalize_area)):
		cumulative_sum=cumulative_sum+normalize_area[j]
		cumulative_list.append(cumulative_sum)	
	print "Cumulative list:"
	print cumulative_list

	rand_num=random.random()
	print "Random number is %f" %rand_num

	#Picking the drain with the higher area. 
	#Check for the first term in the list
	if rand_num < cumulative_list[0]:
		random_drain=1 #1st drain i.e., 0 + 1 (index + 1)
	else:

		for i in range(1, len(cumulative_list)):
			if rand_num < cumulative_list[i]:
				random_drain=i+1
				break;

	print "Random number was: %f, drain number or index number was %d" %(rand_num,random_drain)
	
	return (random_drain)






