#!/usr/bin/env python

#Modification summary:
#Checking for DFP or DFF: to suit both 180nm and 65nm. 'DFPQX wont work for 65nm since there are FFs with 'DFPQNX', 'DFPHQNX' etc: June 27 2014
#Modified DFFPOSX1 to DFPQX to suit the 65nm requirement: 25/4/2014
#Changed the column iteration number for header from range(5) to range(6), since the drain number is also added: Feb 11 2014

#This script reads in the <path>/<design_case>/results/weighted/gates_FF/low_slack/spice_results/spice_rtl_difference_summary.csv and count_flips_summary.csv in the same path, to classify the observed flips. Two files are written out:\n1. <path>/spice_results/strike_on_gates.csv and\n2.<path>/spice_results/strike_on_FF.csv.\n The classification data for the gates is written out to another pdf called  <path>/taxonomy_report.pdf 

#Assumption: We are assuming that the output FFs in all subdirectoies have "Qout" or "Q" or "output" in their names and that no other FFs have these strings in their names. If this condition is not met, the results will be incorrect!
#Nanditha Rao
#Example usage: python python_gate_strike_taxonomy.py  -p /home/external/iitb/nanditha/simulations/decoder_ip_opFF_rise -m decoder_op_ip

def gate_strike_taxonomy(path,module):

	import optparse
	import re,os
	import csv, re

	"""
	from optparse import OptionParser

	parser = OptionParser('This script reads in the <path>/<design_case>/results/weighted/gates_FF/low_slack/spice_results/spice_rtl_difference_summary.csv and count_flips_summary.csv in the same path, to classify the observed flips. Two files are written out:\n1. <path>/spice_results/strike_on_gates.csv and\n2.<path>/spice_results/strike_on_FF.csv.\n The classification data is written out to another pdf called  <path>/taxonomy_report_gates.pdf \nAuthor:Nanditha Rao(nanditha@ee.iitb.ac.in)\n')

	parser.add_option("-p", "--path", dest="path",help="Enter the ENTIRE path to the folder which contains /spice_results  ")
	parser.add_option("-m", "--mod", dest="module",help="Enter the name of the design module ")

	(options, args) = parser.parse_args()

	path=options.path
	module=options.module

	"""
	#Removing the existing combined results file in the results folder
	if os.path.isfile("%s/spice_results/spice_rtl_difference_2nd_edge_count_flips.csv" %(path)):
		print "****Removing the spice_rtl_difference_count_flips.csv in results folder****\n"
		os.remove("%s/spice_results/spice_rtl_difference_2nd_edge_count_flips.csv" %(path))
	else:
		print "No file to be deleted"


	if os.path.isfile("%s/spice_results/spice_rtl_difference_3rd_edge_count_flips.csv" %(path)):
		print "****Removing the spice_rtl_difference_count_flips.csv in results folder****\n"
		os.remove("%s/spice_results/spice_rtl_difference_3rd_edge_count_flips.csv" %(path))
	else:
		print "No file to be deleted"



	#Do the following only if the directory has results in it.. 
	if (os.path.isdir('%s/spice_results' %(path))):

		#Append the spice_rtl_diff summary with the flip count
		f = open('%s/spice_results/count_flips_2nd_edge_summary.csv' %(path), 'rb')
		fsum = open('%s/spice_results/spice_rtl_difference_2nd_edge_summary.csv' %(path), 'rb')
		fout = open('%s/spice_results/spice_rtl_difference_2nd_edge_count_flips.csv' %(path,), 'wb')


		reader = csv.reader(f)
		reader_summary = csv.reader(fsum)
		writer = csv.writer(fout)

		headers = reader_summary.next() #Read the headers from the summary file into this list called 'headers'
		print "\nsummary headers:",headers
		summary=[] #This will be a list of lists. Only this can be written into a csv using writerows() function
		headers.append("total_flip_count_2nd_edge")
		print "\nsummary headers:",headers

		#Append header
		summary.append(headers)
		print "\nsummary:",summary

		reader.next() #Skip the header in the count_flips_summary file

		"""
		count_file_row=reader.next()
		print "\nRow in count flip file is:", count_file_row
		flip_count=count_file_row[len(count_file_row) -1]
		print "\nFlip count is:",flip_count
		"""

		total_csv_rows=0
		########################## Write out the flip count and the spice summary into one file##########################
		#Read each row of the reader_summary file and then append the flip count from the count_flips_summary.csv to the destination file

		for row in reader_summary: #For every row in the summary file
			#print "\nRow in summary file is:", row
			total_csv_rows=total_csv_rows+1
			count_file_row=reader.next() #This is a list which captures the next row in count_flips_summary.csv
			#print "\nRow in count flip file is:", count_file_row

			flip_count=count_file_row[len(count_file_row) -1] #Find the last element of the row, which is the flip_count value
			#print "\nFlip count is:",flip_count
			row.append(flip_count) #Append it to the row
			#print "\nFinal Row to be appended is:", row
			summary.append(row) #rows in diff file
			#print "\n*****************************************\n",

		#This csv writer will only take in a list of lists as input. Hence, summary has to be a list of lists
		writer.writerows(summary)

		f.close()
		fsum.close()
		fout.close()
		#####################################################################################################################

		########################## Write out separate files strike_on_gates and strike_on_FF##########################

		fin = open('%s/spice_results/spice_rtl_difference_2nd_edge_count_flips.csv' %(path), 'rb')
		fgate = open('%s/spice_results/strike_on_gates_2nd_edge.csv' %(path), 'wb')
		fDFF = open('%s/spice_results/strike_on_FF_2nd_edge.csv' %(path), 'wb')

		reader = csv.reader(fin)
		gate_file = csv.writer(fgate)
		FF_file = csv.writer(fDFF)

		header=reader.next()
		gate_list=[]
		FF_list=[]
		gate_list.append(header)
		FF_list.append(header)

		for row in reader:
		#The gate name is the 4th element in the row. Classify the gates based on whether it was a DFF or not
			if re.search("DFP|DFF",row[3]): 
				FF_list.append(row)
			else:
				gate_list.append(row)
			

		gate_file.writerows(gate_list)
		FF_file.writerows(FF_list)

		fin.close()
		fgate.close()
		fDFF.close()

		#####################Calculate the output FF flips and input FF flips separately########################
		#Calculate the indices of the output nodes
		fsum = open('%s/spice_results/spice_rtl_difference_2nd_edge_summary.csv' %(path), 'rb')
		reader_summary = csv.reader(fsum)

		headers = reader_summary.next() #Read the headers from the summary file into this list called 'headers'
		#qout_index=[]
		qout_2nd_edge_index=[]
		qout_fall_index=[]

		#Save the index in a row, which has output FFs. This is found by seeing if the header contains "Qout"
		for i in range(0,len(headers)): #python loops till len(headers)-1
			if re.search("(Q|out|Qout)", headers[i]): #Get the output nodes
				#print "\nHeader match!:",headers[i]
				#print "\nHeader index:",i
				#Separate out the outputs at the rise edge and the fall edge.
				#The 2nd_edge rise edge outputs are expected to have the term 'rise' in their name
				if re.search("rise", headers[i]): #In this case, all nodes will have the word 'rise'
				#print "\nHeader match!:",headers[i]
				#print "\nHeader index:",i
					qout_2nd_edge_index.append(i)
				else:
					qout_fall_index.append(i)



		print "\nTotal header length!:",len(headers)
		#Add only the contents of those cells which are indexed above into qout_index
		#This will add the contents of the cells belonging to Qout only. We can hence count the flips that happened
		#only at the output FFs.
		#Do this for each row of the gate file and the FF file

		fgate = open('%s/spice_results/strike_on_gates_2nd_edge.csv' %(path), 'rb')
		#fDFF = open('%s/spice_results/strike_on_FF_2nd_edge.csv' %(path), 'rb')
		gate_file = csv.reader(fgate)
		#FF_file = csv.reader(fDFF)
		#the header in both files
		gate_header=gate_file.next()
		#FF_header=FF_file.next()


		gate_header.append("outputFF_2nd_edge_flips")
		gate_header.append("inputFF_2nd_edge_flips")
		#gate_header.append("type_of_fault")
		#FF_header.append("outputFF_2nd_edge_flips")
		#FF_header.append("inputFF_2nd_edge_flips")
		#FF_header.append("type_of_fault")

		#output files
		fgate2 = open('%s/spice_results/strike_on_gates_count_2nd_edge.csv' %(path), 'wb')
		#fDFF2 = open('%s/spice_results/strike_on_FF_count_2nd_edge.csv' %(path), 'wb')
		gate_outfile = csv.writer(fgate2)
		#FF_outfile = csv.writer(fDFF2)

		#Lists to save rows of each file to be written to the output file
		gates_list=[]
		#FFs_list=[]

		#Write header to the output files
		gates_list.append(gate_header)
		#FFs_list.append(FF_header)
		#print "\nGate header:",gates_list
		#print "\nFF header:",FFs_list

		gate_csv_rows=0
		#Parse the gates file first for the 2nd rise edge
		for row in gate_file:
			gate_csv_rows=gate_csv_rows+1 #This is excluding the header, since we have already done diff_file.next() to count the header
			out_flip_count2=0

			for i in range(0,len(qout_2nd_edge_index)): 
				out_flip_count2= out_flip_count2+(int(row[qout_2nd_edge_index[i]])) #This is the output FF flip count

			#Calculate input flip count. This is total flip count (which is the last element in the row) minus output flip count
			in_flip_count2= int(row[len(row)-1])  - out_flip_count2
			row.append(out_flip_count2) #Add the output flip count to the row, first
			row.append(in_flip_count2) #Add the input flip count to the row
			gates_list.append(row)

		gate_outfile.writerows(gates_list)
		fgate.close()
		fgate2.close()
		fsum.close()
	##########################################Gates: 3rd edge summary#################################################

	#Append the spice_rtl_diff summary with the flip count
		f_3 = open('%s/spice_results/count_flips_3rd_edge_summary.csv' %(path), 'rb')
		fsum_3 = open('%s/spice_results/spice_rtl_difference_3rd_edge_summary.csv' %(path), 'rb')
		fout_3 = open('%s/spice_results/spice_rtl_difference_3rd_edge_count_flips.csv' %(path), 'wb')


		reader_3 = csv.reader(f_3)
		reader_summary_3 = csv.reader(fsum_3)
		writer_3 = csv.writer(fout_3)

		headers_3 = reader_summary_3.next() #Read the headers from the summary file into this list called 'headers'
		summary_3=[] #This will be a list of lists. Only this can be written into a csv using writerows() function
		headers_3.append("total_flip_count_3rd_edge")
		print "\nsummary headers:",headers_3

		#Append header
		summary_3.append(headers_3)
		print "\nsummary:",summary_3

		reader_3.next() #Skip the header in the count_flips_summary file

		"""
		count_file_row=reader.next()
		print "\nRow in count flip file is:", count_file_row
		flip_count=count_file_row[len(count_file_row) -1]
		print "\nFlip count is:",flip_count
		"""

		total_csv_rows_3=0
		########################## Write out the flip count and the spice summary into one file##########################
		#Read each row of the reader_summary file and then append the flip count from the count_flips_summary.csv to the destination file

		for row_3 in reader_summary_3: #For every row in the summary file
			#print "\nRow in summary file is:", row
			total_csv_rows_3=total_csv_rows_3 + 1
			count_file_row_3=reader_3.next() #This is a list which captures the next row in count_flips_summary.csv
			#print "\nRow in count flip file is:", count_file_row_3

			flip_count_3=count_file_row_3[len(count_file_row_3) -1] #Find the last element of the row, which is the flip_count value
			#print "\nFlip count is:",flip_count
			row_3.append(flip_count_3) #Append it to the row
			#print "\nFinal Row to be appended is:", row
			summary_3.append(row_3) #rows in diff file
			#print "\n*****************************************\n",

		#This csv writer will only take in a list of lists as input. Hence, summary has to be a list of lists
		writer_3.writerows(summary_3)

		f_3.close()
		fsum_3.close()
		fout_3.close()
		#####################################################################################################################

		########################## Write out separate files strike_on_gates and strike_on_FF##########################

		fin_3 = open('%s/spice_results/spice_rtl_difference_3rd_edge_count_flips.csv' %(path), 'rb')
		fgate_3 = open('%s/spice_results/strike_on_gates_3rd_edge.csv' %(path), 'wb')
		fDFF_3 = open('%s/spice_results/strike_on_FF_3rd_edge.csv' %(path), 'wb')

		reader_3 = csv.reader(fin_3)
		gate_file_3 = csv.writer(fgate_3)
		FF_file_3 = csv.writer(fDFF_3)

		header_3=reader_3.next()
		gate_list_3=[]
		FF_list_3=[]
		gate_list_3.append(header_3)
		FF_list_3.append(header_3)

		for row_3 in reader_3:
		#The gate name is the 4th element in the row. Classify the gates based on whether it was a DFF or not
			if re.search("DFP|DFF",row_3[3]): 
				FF_list_3.append(row_3)
			else:
				gate_list_3.append(row_3)

		gate_file_3.writerows(gate_list_3)
		FF_file_3.writerows(FF_list_3)

		fin_3.close()
		fgate_3.close()
		fDFF_3.close()

		#####################Calculate the output FF flips and input FF flips separately########################
		#Calculate the indices of the output nodes
		fsum3 = open('%s/spice_results/spice_rtl_difference_3rd_edge_summary.csv' %(path), 'rb')
		reader_summary3 = csv.reader(fsum3)

		headers3 = reader_summary3.next() #Read the headers from the summary file into this list called 'headers'
		#qout_index=[]
		qout_3rd_edge_index=[]


		#Save the index in a row, which has output FFs. This is found by seeing if the header contains "Qout"
		for i3 in range(0,len(headers3)): #python loops till len(headers3)-1
			if re.search("(Q|out|Qout)", headers[i3]): #Get the output nodes
				qout_3rd_edge_index.append(i3)
				#print "\nHeader match!:",headers[i]
				#print "\nHeader index:",i
				#Separate out the outputs at the rise edge and the fall edge.
				#The 2nd_edge rise edge outputs are expected to have the term 'rise' in their name

		print "\nTotal header length!:",len(headers3)
		#Add only the contents of those cells which are indexed above into qout_index
		#This will add the contents of the cells belonging to Qout only. We can hence count the flips that happened
		#only at the output FFs.
		#Do this for each row of the gate file and the FF file

		fgate_3 = open('%s/spice_results/strike_on_gates_3rd_edge.csv' %(path), 'rb')
		#fDFF_3 = open('%s/spice_results/strike_on_FF_3rd_edge.csv' %(path), 'rb')
		gate_file_3 = csv.reader(fgate_3)
		#FF_file_3 = csv.reader(fDFF_3)
		#the header in both files
		gate_header_3=gate_file_3.next()
		#FF_header_3=FF_file_3.next()

	
		gate_header_3.append("outputFF_3rd_edge_flips")
		gate_header_3.append("inputFF_3rd_edge_flips")
		#gate_header_3.append("type_of_fault")
		#FF_header_3.append("outputFF_3rd_edge_flips")
		#FF_header_3.append("inputFF_3rd_edge_flips")
		#FF_header_3.append("type_of_fault")

		#output files
		fgate3_out = open('%s/spice_results/strike_on_gates_count_3rd_edge.csv' %(path), 'wb')
		#fDFF3_out = open('%s/spice_results/strike_on_FF_count_3rd_edge.csv' %(path), 'wb')
		gate_outfile3 = csv.writer(fgate3_out)
		#FF_outfile3 = csv.writer(fDFF3_out)

		#Lists to save rows of each file to be written to the output file
		gates_list_out3=[]
		#FFs_list_out3=[]

		#Write header to the output files
		gates_list_out3.append(gate_header_3)
		#FFs_list_out3.append(FF_header_3)
		#print "\nGate header:",gates_list
		#print "\nFF header:",FFs_list

		gate_csv_rows3=0
		#Parse the gates file first for the 3rd rise edge
		for row33 in gate_file_3:
			gate_csv_rows3=gate_csv_rows3+1 #This is excluding the header, since we have already done gate_file_3.next() to count the header
			out_flip_count3=0

			for i in range(0,len(qout_3rd_edge_index)): 
				out_flip_count3= out_flip_count3+(int(row33[qout_3rd_edge_index[i]])) #This is the output FF flip count

			#Calculate input flip count. This is total flip count (which is the last element in the row) minus output flip count
			in_flip_count3= int(row33[len(row33)-1])  - out_flip_count3
			row33.append(out_flip_count3) #Add the output flip count to the row
			row33.append(in_flip_count3) #Add the input flip count to the row
			gates_list_out3.append(row33)


		gate_outfile3.writerows(gates_list_out3)
		fgate_3.close()
		fgate3_out.close()
		fsum3.close()
		fDFF_3.close()
	###########################################################################################################################

	#Now, write out the 2nd edge and 3rd flip summary for gates into one file.. and identify the type of fault

		fgate2 = open('%s/spice_results/strike_on_gates_count_2nd_edge.csv' %(path), 'rb')
		gate_read2 = csv.reader(fgate2)

		fgate3 = open('%s/spice_results/strike_on_gates_count_3rd_edge.csv' %(path), 'rb')
		gate_read3 = csv.reader(fgate3)

		fgate_final = open('%s/spice_results/strike_on_gates_taxonomy.csv' %(path), 'wb')
		gate_final_csv = csv.writer(fgate_final)


		#Lists to save rows of each file to be written to the output file
		gates_list_final=[]

		#Write out headers
		headers2=gate_read2.next() 
		#print "\nheaders2:",headers2
		#gates_list_final.append(headers2)
		headers3=gate_read3.next() 
		#print "\nheaders3:",headers3
	#Append header - start from 6- since we are omitting first 6 columns which have deck_num,clk,glitch,gate and subcktlinenum info,drain
		for aa in range(6,len(headers3)):  
			headers2.append(headers3[aa])
		#print "\nheaders2+3:",headers2
		headers2.append("type of fault")
		#print "\nheaders2+3+fault:",headers2
		gates_list_final.append(headers2)
		#print "\ngates_list:",gates_list_final

		#This list will contain a single entry
		inputFF_2nd_rise=[]
		outputFF_2nd_rise=[]
		#Now, to match the headers corresponding to 2nd and 3rd rise:

		#Save the index in a row, which has the 2nd rise output flip count. This is found by seeing if the header contains a specific phrase
		#This list will contain a single entry
		for i in range(0,len(headers2)): #python loops till len(headers2)-1
			if re.search("inputFF_2nd_edge_flips", headers2[i]): #Get the output nodes
				inputFF_2nd_rise.append(i)
		print "Index containing \"inputFF_2nd_edge_flips\" is:", inputFF_2nd_rise[0]

		for i in range(0,len(headers2)): #python loops till len(headers2)-1
			if re.search("outputFF_2nd_edge_flips", headers2[i]): #Get the output nodes
				outputFF_2nd_rise.append(i)
		print "Index containing \"outputFF_2nd_edge_flips\" is:", outputFF_2nd_rise[0]

		#Save the index in a row, which has the 3rd rise output flip count. This is found by seeing if the header contains a specific phrase
		#This list will contain a single entry
		inputFF_3rd_rise=[]
		outputFF_3rd_rise=[]
		##Repeat the same for the 3rd edge
		for i in range(0,len(headers3)): #python loops till len(headers3)-1
			if re.search("inputFF_3rd_edge_flips", headers3[i]): #Get the output nodes
				inputFF_3rd_rise.append(i)
		print "Index containing \"inputFF_3rd_edge_flips\" is:", inputFF_3rd_rise[0]

		for i in range(0,len(headers3)): #python loops till len(headers3)-1
			if re.search("outputFF_3rd_edge_flips", headers3[i]): #Get the output nodes
				outputFF_3rd_rise.append(i)
		print "Index containing \"outputFF_3rd_edge_flips\" is:", outputFF_3rd_rise[0]

		#Now append rows in both the 2nd and 3rd edge gate rows into one file..
		gate_glitch_captured=0
		gate_glitch_captured_multiple=0
		gate_no_effect=0
		gate_strange_FF=0
		gate_strange_FN=0
		gate_cascaded_multiple=0

		for row in gate_read2:
	
			temp_row=[]
			for aa in range(0,len(row)):
				temp_row.append(row[aa])  #Append the 2nd rise edge rows
			#a.append(temp_row)
			#print "current row in rise edge 2 is", row
			#print "\ntemp_row:",temp_row
			row3=gate_read3.next()

			#The 1st 6 values are already appended. They contain,clk num, deck num,gate name etc
		#Append header - start from 6- since we are omitting first 6 columns which have deck_num,clk,glitch,gate and subcktlinenum info,drain
			for aa in range(6,len(row3)):  
				temp_row.append(row3[aa])  #Append the 3rd rise edge rows
			#print "current row in rise edge 3 is", row3
			#print "\ntemp_row:",temp_row
			#a.append(temp_row)
		#Now, append the type of fault to the same row..
			#2nd rise edge data is available in gate_read2 (row), 3rd rise edge data is available in gate_read3 (row3)
			#print "int(row[inputFF_2nd_rise[0]])" ,int(row[inputFF_2nd_rise[0]])
			#print "int(row3[outputFF_3rd_rise[0]])",int(row3[outputFF_3rd_rise[0]])
		
			#Whichever flip-flop flips at the 2nd edge 
			FF_at_2nd_rise= int(row[inputFF_2nd_rise[0]]) + int(row[outputFF_2nd_rise[0]])
			#Whichever flip-flop flips at the 3rd edge 
			FF_at_3rd_rise= int(row3[inputFF_3rd_rise[0]]) + int(row3[outputFF_3rd_rise[0]])

			if (FF_at_2nd_rise==0 and FF_at_3rd_rise==0):
				print "case 1"
				temp_row.append("No effect")
				gate_no_effect=gate_no_effect+1
			elif (FF_at_2nd_rise==0 and FF_at_3rd_rise>=1):
				#row.append("Glitched and captured at FF(s)")
				print "case 2"
				gate_glitch_captured=gate_glitch_captured+1
				if (FF_at_3rd_rise>1): #Calculating multiple flips
					temp_row.append("Glitched and captured at multiple FFs")
					gate_glitch_captured_multiple=gate_glitch_captured_multiple+1

				elif(FF_at_3rd_rise==1):
					temp_row.append("Glitched and captured at a single FF")
		
			#If a strike happens on a gate, an input FF cannot flip!!
			elif (FF_at_2nd_rise>=1 and FF_at_3rd_rise==0):
				print "case 3"
				temp_row.append("FN- Strange?!")
				gate_strange_FN=gate_strange_FN+1

			elif (FF_at_2nd_rise>=1 and FF_at_3rd_rise>=1):
				print "case 4"
				temp_row.append("FF- Strange?!")
				gate_strange_FF=gate_strange_FF+1

				if (FF_at_3rd_rise>1): #Calculating multiple flips
					temp_row.append("Cascaded, flipped at multiple FFs")
					gate_cascaded_multiple=gate_cascaded_multiple+1

				elif(FF_at_3rd_rise==1):
					temp_row.append("Cascaded, flipped at a single FF")

			#print "temp_row final:", temp_row

			gates_list_final.append(temp_row) #Append this to the list.. At the end of for loop, it would be a list of lists
			#print "gates_list:", gates_list_final
		gate_final_csv.writerows(gates_list_final)


		gate_atleast_1_flip= (gate_csv_rows - gate_no_effect)
		gate_multiple_flips= gate_cascaded_multiple + gate_glitch_captured_multiple

		print"\n*************************************************************\n"
		print"\nTotal number of particle strikes is:",total_csv_rows

		print"\nNumber of gate strikes is:",gate_csv_rows
		print"\nNumber of no effect due to gate strike is:",gate_no_effect
		print"\nNumber of atleast one flip cases: ",gate_atleast_1_flip
		print"\nNumber of captured flips due to gate strike is:",gate_glitch_captured
		print"\nNumber of Multiple captured flips amongst the captured flips:",gate_glitch_captured_multiple
		prob_gate_strike=(float(gate_csv_rows)/float(total_csv_rows))

		if gate_csv_rows>0:
			prob_gate_no_effect=(float(gate_no_effect)/float(gate_csv_rows))
			prob_gate_glitch_captured=(float(gate_glitch_captured)/float(gate_csv_rows))
			prob_gate_FN=(float(gate_strange_FN)/float(gate_csv_rows))
			prob_gate_FF=(float(gate_strange_FF)/float(gate_csv_rows))
			prob_gate_atleast_1flip= float(gate_atleast_1_flip)/float(gate_csv_rows)

		else:
			prob_gate_no_effect=0.0
			prob_gate_glitch_captured=0.0
			prob_gate_FN=0.0
			prob_gate_FF=0.0
			prob_gate_atleast_1flip=0.0


		if (gate_atleast_1_flip >1) :
			prob_gate_multiple_conditional= float(gate_multiple_flips)/float(gate_atleast_1_flip)
		else:
			prob_gate_multiple_conditional=0.0

		#To avoid divide by zero error:	
		if gate_glitch_captured >0: #Calculating conditional probability
			prob_gate_glitch_captured_multiple=(float(gate_glitch_captured_multiple)/float(gate_glitch_captured))
		else:
			prob_gate_glitch_captured_multiple=0.0

		if gate_strange_FF >0: #Calculating conditional probability
			prob_gate_cascaded_multiple=(float(gate_cascaded_multiple)/float(gate_strange_FF))
		else:
			prob_gate_cascaded_multiple=0.0

		print"\n*************************************************************"
		print"\nProbability of a gate strike amongst total cases is:",prob_gate_strike

		print"\n*************************************************************"
		print"\nProbability of atleast one flip is:",prob_gate_atleast_1flip
		print"Probability of multiple flips (conditional) is:",prob_gate_multiple_conditional
		print"\n************************Taxonomy*************************************"

		print"\nProbability of no effect due to gate strike is:",prob_gate_no_effect

		print"Probability of captured flips due to gate strike (glitch) is:",prob_gate_glitch_captured

		print "Output written: %s/spice_results/taxonomy_summary_gates_%s.csv" %(path,module)

		print"\n*************************************************************\n"
		fgate2.close()
		fgate3.close()
		fgate_final.close()


		#Final output (taxonomy) written into a taxonomy_summary_<design>.csv file inside the respective results folders
		fout = open('%s/spice_results/taxonomy_summary_gates_%s.csv' %(path,module), 'wb')
		fout.write ("\n*****************************%s results**********************************\n" %module)

		fout.write ("\nNumber of gate strikes is: %d" %gate_csv_rows)
		fout.write ("\nNumber of atleast one flip cases: %d" %gate_atleast_1_flip)
		fout.write ("\nNumber of Multiple flips: %d" %gate_glitch_captured_multiple)	
		fout.write ("\nProbability of a gate strike amongst total cases is: %f" %prob_gate_strike)
		fout.write ("\nProbability of atleast one flip is: %f"  %prob_gate_atleast_1flip)
		fout.write ("\nConditional probability of multiple captured flips given atleast one flip, due to gate strike: %f" %prob_gate_multiple_conditional)
		fout.write ("\n**********************************Taxonomy***************************************\n")
		fout.write ("\nNumber of NN(no effect due to gate strike) is: %d" %gate_no_effect)
		fout.write ("\nNumber of NF(glitch propagation and capture) due to gate strike is: %d" %gate_glitch_captured)
		fout.write ("\nNumber of Multiple captured flips amongst the captured flips: %d" %gate_glitch_captured_multiple)
		fout.write ("\nProbability of NN(no effect due to gate strike) is: %f" %prob_gate_no_effect)
		fout.write ("\nProbability of NF(propagated and captured flips due to gate strike (glitch)) is: %f" %prob_gate_glitch_captured)
		fout.write ("\nP(multiple|NF): Conditional Probability of multiple captured flips given NF : %f" %prob_gate_glitch_captured_multiple)
		fout.write ("\nProbability of FN(flip in 2nd cycle, no flip in 3rd cycle), due to gate strike is: %f" %prob_gate_FN)
		fout.write ("\nProbability of FF(flip in 2nd cycle and flip in 3rd cycle), due to gate strike is: %f" %prob_gate_FF)
		fout.write ("\nP(multiple|FF): Conditional Probability of multiple captured flips given FF : %f" %prob_gate_cascaded_multiple)
		fout.close()

		###########################Write out the results into a table in a pdf############################

		from reportlab.lib import colors
		from reportlab.lib.pagesizes import letter
		from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
		from reportlab.lib.styles import getSampleStyleSheet
		from reportlab.lib.units import inch
		styles = getSampleStyleSheet()

		#Create one pdf result for each design and place it in the <path>
		doc1 = SimpleDocTemplate("%s/spice_results/taxonomy_report_gates_%s.pdf" %(path,module), pagesize=letter)

		# container for the 'Flowable' objects
		elements = [] #Keep appending whatever you want to add to the pdf, here to the elements

		style = styles["Normal"]
		styleH = styles["Heading2"]
		p = Paragraph('''Multiple-bit error/fault classification''', styleH)
		elements.append(p)
		p = Paragraph('''Design: %s''' %module, style)
		elements.append(p)
		p = Paragraph(''' Taxonomy for strike on gates''', style)
		elements.append(p)
		elements.append(Spacer(1,0.2*inch))



		#Table for gates
		data_gate= [['Parameter', 'Probability'],
		       ['Gate strike', prob_gate_strike],
			#['Atleast one flip',prob_gate_atleast_1flip],
			#['Conditional prob of multiple flips',prob_gate_multiple_conditional],
		       ['NN (No impact)', prob_gate_no_effect],
		       ['NF(Glitch- Propagated and captured)', prob_gate_glitch_captured],
		       ['P(multiple flips at output | NF)', prob_gate_glitch_captured_multiple],
			['FN (flip in 2nd cycle, no flip in 3rd cycle)', prob_gate_FN],
			 ['FF (cascaded flip)', prob_gate_FF],
			['P(multiple flips at output | FF)', prob_gate_cascaded_multiple],
			 ['P(multiple flips NFm or FFm | atleast one flip)', prob_gate_multiple_conditional]]

		t=Table(data_gate)
		t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.white),
				       ('TEXTCOLOR',(0,0),(1,0),colors.blue),  #(columns,rows) or (0,0,(-1,-4)
					('INNERGRID', (0,0), (-1,-1), 0.25, colors.black), 
					 ('BOX', (0,0), (-1,-1), 0.5, colors.black)  #(-1,-1) indicates the (last column, last row)
		       ]))
		elements.append(t)

		elements.append(Spacer(1,0.3*inch))


		print "Elements in table is: ",elements
		print "\n**Completed executing the gate_strike_taxonomy script***\n"
		print "%s/spice_results/taxonomy_report_gates_%s.pdf has the results." %(path,module)
		doc1.build(elements)

		return (gate_glitch_captured_multiple,gate_glitch_captured)


