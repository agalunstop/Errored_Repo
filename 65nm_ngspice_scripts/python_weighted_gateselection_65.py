
#!/usr/bin/env python

#Example usage: python python_weighted_gateselection.py 

#This script picks the random gate on which the glitch needs to be injected, based on the gate area. The gate with the largest area has a higher probability of getting picked. It has a database/array of the STMicro 65nm gates and their areas. This database will need to be modified for other  technology nodes as per its library and gate area. The rest of the script can be reused. This script is called as a function-call from the main script. The random gate is returned from the function. For eg., if the spice file contains AND, OR and XOR gates in that order, and if OR gate has the highest area, the index of OR gate, that is 1, is returned (indexing starts from 0)
#Nanditha Rao

#Modifications:
#Gate array modified according to the decoder and c432 example of 65nm. Need to add more gates as and when larger examples are run and their areas are known: 25/4/2014

def weight_selection(path):
	
	import random,re

	gates=["HS65_GSS_XOR2X6","HS65_GS_AND2X4","HS65_GS_AOI22X6","HS65_GS_BFX284","HS65_GS_DFPQX4","HS65_GS_IVX9","HS65_GS_NAND2X7","HS65_GS_NOR2X6","HS65_GS_NOR3X4","HS65_GS_AO212X4","HS65_GS_AO311X9  ", "HS65_GS_AOI12X2", "HS65_GS_AOI212X4", "HS65_GS_AOI311X4", "HS65_GS_AOI32X5", "HS65_GS_AOI33X5", "HS65_GS_NAND2AX7","HS65_GS_NAND3AX6", "HS65_GS_NAND3X5", "HS65_GS_NAND4ABX3", "HS65_GS_NOR3AX2", "HS65_GS_NOR4ABX2","HS65_GS_NOR4ABX4", "HS65_GS_OA12X9", "HS65_GS_OAI212X5", "HS65_GS_OAI21X3", "HS65_GS_OAI33X3", "HS65_GS_OR2X9","HS65_GSS_XNOR2X6", "HS65_GSS_XOR3X2","HS65_GS_AND2X27", "HS65_GS_AND3X4","HS65_GS_AO12X4","HS65_GS_AO31X9","HS65_GS_AOI21X2","HS65_GS_AOI222X2", "HS65_GS_AOI32X3", "HS65_GS_CBI4I1X5","HS65_GS_DFPQX9","HS65_GS_FA1X4", "HS65_GS_IVX2","HS65_GS_LDLQX9","HS65_GS_MX41X4","HS65_GS_NAND2X2","HS65_GS_NAND3AX3","HS65_GS_NOR2AX3","HS65_GS_NOR2X2", "HS65_GS_NOR3X1", "HS65_GS_OA112X4","HS65_GS_OA12X4","HS65_GS_OA212X4","HS65_GS_OA32X4","HS65_GS_OAI12X2", "HS65_GS_OAI13X1", "HS65_GS_OR2X4","HS65_GS_PAOI2X1","HS65_GS_AO22X9","HS65_GSS_XNOR3X2","HS65_GS_AND3X9"," HS65_GS_OAI32X5","HS65_GS_AO112X9", "HS65_GS_AO12X9", "HS65_GS_CB4I1X9", "HS65_GS_CBI4I6X5", "HS65_GS_OAI211X5", "HS65_GS_OAI22X6", "HS65_GS_OAI31X5", "HS65_GS_NOR3AX4","HS65_GS_AND4X6", "HS65_GS_AO33X9", "HS65_GS_AOI13X5", "HS65_GS_NAND4X9", "HS65_GS_OAI311X5","HS65_GS_CB4I6X9", "HS65_GS_DFPQNX9", "HS65_GS_OAI12X5", "HS65_GS_OAI222X2","HS65_GS_AO32X4", "HS65_GS_AOI112X4","HS65_GSS_XOR2X3", "HS65_GS_AO222X4", "HS65_GS_AO22X4", "HS65_GS_AO312X4", "HS65_GS_AO31X4", "HS65_GS_AOI13X2", "HS65_GS_AOI212X2", "HS65_GS_AOI311X2", "HS65_GS_AOI312X2", "HS65_GS_CBI4I1X3", "HS65_GS_HA1X4", "HS65_GS_MUXI21X2", "HS65_GS_NAND2AX4", "HS65_GS_NAND3X2", "HS65_GS_NOR3X2", "HS65_GS_OA22X4", "HS65_GS_OAI311X2","HS65_GS_AO312X9", "HS65_GS_AOI312X4", "HS65_GS_BFX7", "HS65_GS_DFPHQNX9", "HS65_GS_DFPHQX9", "HS65_GS_MX41X7", "HS65_GS_OA112X9", "HS65_GS_OA31X9","HS65_GS_AOI12X6", "HS65_GS_NAND2X5","HS65_GS_MUX21X4","HS65_GS_AOI12X3", "HS65_GS_AOI22X1", "HS65_GS_AOI33X2", "HS65_GS_CBI4I6X2", "HS65_GS_OAI212X3", "HS65_GS_OAI22X1","HS65_GS_NAND4ABX6","HS65_GSS_XOR3X4","HS65_GS_BFX18"]

#"HS65_GS_AOI12X3", "HS65_GS_AOI22X1", "HS65_GS_AOI33X2", "HS65_GS_CBI4I6X2", "HS65_GS_OAI212X3", "HS65_GS_OAI22X1"
#,3, 3, 5, 3, 4, 3
	gate_areas=[4,3,4,30,8,2,2,2,3,5,5,3,4,4,4,5,3,4,3,4,3,4,4,4,4,3,5,3,4,7,5,4,3,4,2,5,4,4,8,9,2,7,8,2,4,3,2,3,4,4,5,5,2,4,3,4,4, 8,4,4,4, 3, 4, 3, 3, 3, 3,3,5, 5, 3, 5, 4,4, 8, 3, 5,4,3,4, 5, 4, 5, 4, 3, 4, 4, 5, 3, 5, 3, 3, 2, 2, 4, 4, 5, 5, 2, 10, 10, 7, 4, 4,3,2,4, 3, 3, 5, 3, 4, 3,4,10,3]
	areas=gate_areas[:]; #copy list
	#sorted_index= [i[0] for i in sorted(enumerate(gate_areas), key=lambda x:x[1])]


	#sorted array:
	gate_areas.sort() #Ascending sort
	one=gate_areas[0] #The minimum sized gate is the first in the list
	relative_weight=gate_areas[:] #initialise the output list

	#Get the weights of each gate in the database, relative to the smallest gate
	for i in range(0,len(areas)):
		relative_weight[i]=areas[i]/one

	subckts=[]
	instance=[]
	gate_weights=[]
	gateindex=[]
	final_gate_index=[]
	dff=0;

	fg = open("%s/reference_spice.sp" %path, "r")
	print "Opening %s/reference_spice.sp\n\n" %path
	data = [line.strip() for line in fg] #Get the lines in the spice file
	length=len(data) #number of lines in the reference spice file
	j=0
	stop=0;
	#Write out the subcircuit instances in a separate file
	for i in range(0,length):
		line=data[i]
		if stop == 0:	
		#If you come across ENDS, do not count any more X subckts because the top level subckt instance will also have X
			if line == ".ENDS": 
				stop=1;
	#If the line is not empty and if the first letter in the line begins with a "X", it is the subckt statement we are looking for
	#Also, if the next line contains a "+", it is part of the same subckt too..
			if line and line[0]=="X":  
				nextline= data[i+1]
				if nextline[0]=="+":
					a=line
					next=nextline.split(" ",1)[1] #Split till the first instance of "space". Remove the "+".
					subckts.append(a+next) #Append the next line containing "+"
				else:
					subckts.append(line)
	fg.close()
	fw=open("/%s/subcktfile.sp" %path, "w")
	fa=open("/%s/subcktinstances.sp" %path, "w") #gates
	for line in subckts:
		fw.write("%s\n" %line) #Write out subckt instances

	print "Number of subckts is:", len(subckts) #How many subckt instances are there?

	#Grab the last word i.e., the gate..
	#GATE NAMES OF EACH SUBCKT
	for i in range(0,len(subckts)): 
		instance.append(subckts[i].split()[-1]) #For each line, get the gate and append it to the "instance" list
		fa.write("%s\n" %subckts[i].split()[-1])
		cur_gate=subckts[i].split()[-1];
		if re.search("DF",cur_gate): #Look for Flip-flop anywhere in the string
			dff=dff+1; #Count the number of DFFPOS


	len_instance=len(instance) #the standard cells
	print "\nNumber of gate + DFF instances is:", len(instance)
	print "\nNumber of DFF instances is: %s" %dff
	print "\nPercentage of DFF instances is: %f" %(float(dff)/float(len(instance))*100.0)

	
	fw.close()
	fa.close()
	fa=open("/%s/subcktinstances.sp" %path, "a+")
	#Compare each of the instances in the subckt with that of the standard gates and assign the weigths
	for i in range(0,len(instance)):
		for j in range(0,len(gates)):
			if instance[i]==gates[j]:
				gate_weights.append(relative_weight[j]) #Store the relative weights of the gates
			
	fa.write("Gate weigths is %s\n" %gate_weights)

	fa.write("\n\n\n")

	#print " gate weights array:", gate_weights

	for j in range(0,len(gates)):
		gateindex.append(j)

	#Main gate index is: .. commented out
	#print "Gate index:%s" %gateindex

	fa.write( "Gate index:%s\n" %gateindex)
	fa.write("\n\n\n")	
	
###################################################################################################
##This is the final gate index which is having the duplicated instances of each gate for the number of times as indicated by the weights
	for i in range(0,len(gate_weights)):
		for j in range(0,gate_weights[i]): #Repeat the gates as many times as is the gate index
		#If the gate weight is 2, gate index has to be repeated 2 times, if the weight is 5, repeat gate index 5 times etc.,
			final_gate_index.append(i)
		
	
	fa.write ("Final gate index:\n")	
	fa.write("%s\n" %final_gate_index)	
	#commented out
	#print("Final gate index%s\n" %final_gate_index) 

	#commented out
	#print "Length of the final gate array=%d" %len(final_gate_index)
	lengthgates=len(final_gate_index)
	#Finally, we will pick a random number between 1 and the final length of this array. Say, it picked 5, The deckgen script will then go and pick the 5th subckt in the spice file	
	
	rand_gateindex= int(random.randrange(lengthgates)) 
	print "Random gate index=%d" %rand_gateindex
	subckt_index=final_gate_index[rand_gateindex]
	print "Random gate original index=%d" %subckt_index
	original_gate=instance[subckt_index];
	print "Random gate=%s" %original_gate

	fa.write ("\nNumber of gate instances is:%d" %len(instance))
	fa.write ( "\nNumber of DFF instances is: %s" %dff)
	fa.write ("\nPercentage of DFF instances is: %f" %(float(dff)/float(len(instance))*100.0))

	return (subckt_index,original_gate)

"""
path="/home/nanditha/Documents/iitb/utility/c432_priority_opFF";
num=weight_selection(path);
print "Random subckt line=%d" %num


fa=open("/%s/subcktinstances.sp" %path, "r")
fb=open("/%s/subcktinstances1.sp" %path, "w")
read=fa.readlines()
filelen=len(read)
fb.writelines(read[filelen-3])
fb.writelines(read[filelen-2])
fb.writelines(read[filelen-1])
fa.close()
fb.close()
"""









