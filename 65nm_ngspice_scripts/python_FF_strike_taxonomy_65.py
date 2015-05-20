#!/usr/bin/env python

#Modification summary:
#Changed the cases and classification. At 2nd edge, any FF flip either input or output is considered as the same. Similarly for the 3rd edge. : feb 12 2014
#Changed the column iteration number for header from range(5) to range(6), since the drain number is also added: Feb 11 2014


#This script reads in the <path>/<design_case>/results/weighted/gates_FF/low_slack/spice_results/spice_rtl_difference_summary.csv and count_flips_summary.csv in the same path, to classify the observed flips. Two files are written out:\n1. <path>/spice_results/strike_on_gates.csv and\n2.<path>/spice_results/strike_on_FF.csv.\n The classification data for the gates is written out to another pdf called  <path>/taxonomy_report.pdf 

#Assumption: We are assuming that the output FFs in all subdirectoies have "Qout" or "Q" or "output" in their names and that no other FFs have these strings in their names. If this condition is not met, the results will be incorrect!
#Nanditha Rao

#Example usage: python python_FF_strike_taxonomy.py  -p /home/external/iitb/nanditha/simulations/decoder_ip_opFF_rise -m decoder_op_ip -g %d -c %d



import optparse
import re,os
import csv, re, time

from optparse import OptionParser


parser = OptionParser('This script reads in the <path>/<design_case>/results/weighted/gates_FF/low_slack/spice_results/spice_rtl_difference_summary.csv and count_flips_summary.csv in the same path, to classify the observed flips. Two files are written out:\n1. <path>/spice_results/strike_on_gates.csv and\n2.<path>/spice_results/strike_on_FF.csv.\n The classification data is written out to another pdf called  <path>/taxonomy_report_FFs.pdf \nAuthor:Nanditha Rao(nanditha@ee.iitb.ac.in)\n')

parser.add_option("-p", "--path", dest="path",help="Enter the ENTIRE path to the folder which contains /spice_results  ")
parser.add_option("-m", "--mod", dest="module",help="Enter the name of the design module ")
parser.add_option("-g", "--gl_multiple", dest="gate_multiple",help="Enter the number of multiple flips due to glitch (gate strike) ")
parser.add_option("-c", "--gl_capture", dest="gate_capture",help="Enter the number of glitch capture (gate strike) ")

(options, args) = parser.parse_args()

path=options.path
module=options.module
gate_multiple=int(options.gate_multiple)
gate_capture=int(options.gate_capture)


print "Executing FF strike taxonomy\n"
time.sleep(2)

#Do the following only if the directory has results in it.. 
if (os.path.isdir('%s/spice_results' %(path))):

	#Append the spice_rtl_diff summary with the flip count
	f = open('%s/spice_results/count_flips_2nd_edge_summary.csv' %(path), 'rb')
	reader = csv.reader(f)
	headers = reader.next() #Read the headers from the summary file into this list called 'headers'

	total_csv_rows=0
	########################## Count the total number of rows in csv file############################

	for row in reader: #For every row in the summary file
		#print "\nRow in summary file is:", row
		total_csv_rows=total_csv_rows+1
	
	f.close()

	#####################################################################################################################



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


	fDFF = open('%s/spice_results/strike_on_FF_2nd_edge.csv' %(path), 'rb')

	FF_file = csv.reader(fDFF)
	FF_header=FF_file.next()

	FF_header.append("outputFF_2nd_edge_flips")
	FF_header.append("inputFF_2nd_edge_flips")

	#output file
	fDFF2 = open('%s/spice_results/strike_on_FF_count_2nd_edge.csv' %(path), 'wb')
	FF_outfile = csv.writer(fDFF2)

	#Lists to save rows of each file to be written to the output file
	FFs_list=[]

	#Write header to the output files
	FFs_list.append(FF_header)
	#print "\nFF header:",FFs_list

	FF_csv_rows=0
	#Parse the FF file first for the 2nd rise edge
	for row in FF_file:
		FF_csv_rows=FF_csv_rows+1 #This is excluding the header, since we have already done diff_file.next() to count the header
		out_flip_count2=0

		for i in range(0,len(qout_2nd_edge_index)): 
			out_flip_count2= out_flip_count2+(int(row[qout_2nd_edge_index[i]])) #This is the output FF flip count

		#Calculate input flip count. This is total flip count (which is the last element in the row) minus output flip count
		in_flip_count2= int(row[len(row)-1])  - out_flip_count2
		row.append(out_flip_count2) #Add the output flip count to the row
		row.append(in_flip_count2) #Add the input flip count to the row
		FFs_list.append(row)

	FF_outfile.writerows(FFs_list)

	fsum.close()
	fDFF2.close()
##########################################Gates: 3rd edge summary#################################################


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

	fDFF_3 = open('%s/spice_results/strike_on_FF_3rd_edge.csv' %(path), 'rb')
	FF_file_3 = csv.reader(fDFF_3)
	FF_header_3=FF_file_3.next()


	FF_header_3.append("outputFF_3rd_edge_flips")
	FF_header_3.append("inputFF_3rd_edge_flips")
	#FF_header_3.append("type_of_fault")

	#output file
	fDFF3_out = open('%s/spice_results/strike_on_FF_count_3rd_edge.csv' %(path), 'wb')
	FF_outfile_3 = csv.writer(fDFF3_out)

	#Lists to save rows of each file to be written to the output file
	FFs_list_out3=[]

	#Write header to the output files
	FFs_list_out3.append(FF_header_3)
	#print "\nGate header:",gates_list
	#print "\nFF header:",FFs_list
	FF_csv_rows3=0

	#Parse the FF file first for the 3rd rise edge
	for row33 in FF_file_3:
		FF_csv_rows3 = FF_csv_rows3+1 #This is excluding the header, since we have already done gate_file_3.next() to count the header
		out_flip_count3=0

		for i in range(0,len(qout_3rd_edge_index)): 
			out_flip_count3= out_flip_count3+(int(row33[qout_3rd_edge_index[i]])) #This is the output FF flip count

		#Calculate input flip count. This is total flip count (which is the last element in the row) minus output flip count
		in_flip_count3= int(row33[len(row33)-1])  - out_flip_count3
		row33.append(out_flip_count3) #Add the output flip count to the row
		row33.append(in_flip_count3) #Add the input flip count to the row
		FFs_list_out3.append(row33)


	FF_outfile_3.writerows(FFs_list_out3)
	fsum3.close()
	fDFF_3.close()
	fDFF3_out.close()
###########################################################################################################################

#Now, write out the 2nd edge and 3rd flip summary for gates into one file.. and identify the type of fault

	f2_read = open('%s/spice_results/strike_on_FF_count_2nd_edge.csv' %(path), 'rb')
	FF_read_2 = csv.reader(f2_read)

	f3_read = open('%s/spice_results/strike_on_FF_count_3rd_edge.csv' %(path), 'rb')
	FF_read_3 = csv.reader(f3_read)

	fDFF_final = open('%s/spice_results/strike_on_FF_taxonomy.csv' %(path), 'wb')
	DFF_final_csv = csv.writer(fDFF_final)


	#Lists to save rows of each file to be written to the output file
	DFF_list=[]

	#Write out headers
	headers2=FF_read_2.next() 
	headers3=FF_read_3.next() 
	#Append header - start from 6- since we are omitting first 6 columns which have deck_num,clk,glitch,gate and subcktlinenum info,drain
	for aa in range(6,len(headers3)):  
		headers2.append(headers3[aa])

	headers2.append("type of fault")

	DFF_list.append(headers2)


	#This list will contain a single entry
	inputFF_2nd_rise=[]
	outputFF_2nd_rise=[]
	#Now, to match the headers corresponding to 2nd and 3rd rise:

	#Save the index in a row, which has the 2nd rise output flip count. This is found by seeing if the header contains "Qout"
	#This list will contain a single entry
	for i in range(0,len(headers2)): #python loops till len(headers2)-1
		if re.search("inputFF_2nd_edge_flips", headers2[i]): #Get the output nodes
			inputFF_2nd_rise.append(i)
	print "Index containing \"inputFF_2nd_edge_flips\" is:", inputFF_2nd_rise[0]

	for i in range(0,len(headers2)): #python loops till len(headers2)-1
		if re.search("outputFF_2nd_edge_flips", headers2[i]): #Get the output nodes
			outputFF_2nd_rise.append(i)
	print "Index containing \"outputFF_2nd_edge_flips\" is:", outputFF_2nd_rise[0]

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

	FF_glitch_captured=0
	FF_glitch_captured_multiple=0
	FF_flip_masked=0
	FF_cascaded_flip=0
	FF_cascaded_flip_multiple=0
	FF_no_effect=0
	FF_output_glitch=0
	F0_first_flip=0
	for row in FF_read_2:
	
		temp_row=[]
		for aa in range(0,len(row)):
			temp_row.append(row[aa])  #Append the 2nd rise edge rows
	
		#print "current row in rise edge 2 is", row
		#print "\ntemp_row:",temp_row
		row3=FF_read_3.next()

		#The 1st 6 values are already appended. They contain,clk num, deck num,gate name etc
		for aa in range(6,len(row3)):  
			temp_row.append(row3[aa])  #Append the 3rd rise edge rows
		#print "current row in rise edge 3 is", row3
		#print "\ntemp_row:",temp_row
			
		#print "FF_at_2nd_rise" ,FF_at_2nd_rise
		#print "FF_at_3rd_rise",FF_at_3rd_rise

	#2nd rise edge data is available in FF_read_2 (row), 3rd rise edge data is available in FF_read_3 (row3)	
	#Now, append the type of fault to the same row..


		FF_at_2nd_rise= int(row[inputFF_2nd_rise[0]]) + int(row[outputFF_2nd_rise[0]])
		FF_at_3rd_rise= int(row3[inputFF_3rd_rise[0]]) + int(row3[outputFF_3rd_rise[0]])
		if (FF_at_2nd_rise==0 and FF_at_3rd_rise==0):
			#print "case 1"
			temp_row.append("No effect- NN")
			FF_no_effect=FF_no_effect+1
		elif (FF_at_2nd_rise==0 and FF_at_3rd_rise >=1):
			#print "case 2"
			FF_glitch_captured=FF_glitch_captured+1

			if (FF_at_3rd_rise>1): #Calculating multiple flips
				temp_row.append("Glitched and captured at multiple FFs- NF")
				FF_glitch_captured_multiple=FF_glitch_captured_multiple+1
			elif (FF_at_3rd_rise==1):
				temp_row.append("Glitched and captured at a FF")
			

		elif (FF_at_2nd_rise>=1 and FF_at_3rd_rise==0):
			#print "case 3"
			temp_row.append("Flipped and masked- FN")
			FF_flip_masked=FF_flip_masked+1
			F0_first_flip=F0_first_flip+1

		elif (FF_at_2nd_rise>=1 and FF_at_3rd_rise>=1):
			#temp_row.append("Cascaded flip")
			#print "case 4"
			FF_cascaded_flip=FF_cascaded_flip+1
			F0_first_flip=F0_first_flip+1

			if (FF_at_3rd_rise>1):
				temp_row.append("Cascaded flip: Multiple at output- FF")
				FF_cascaded_flip_multiple=FF_cascaded_flip_multiple+1

			elif (FF_at_3rd_rise==1):
				temp_row.append("Cascaded flip: Single flip at output")

		"""
		elif (int(row[outputFF_2nd_rise[0]])>=1):
			#temp_row.append("Cascaded flip")
			print "case 5"
	
			if (int(row[outputFF_2nd_rise[0]])>1):
				temp_row.append("Not possible to affect more than 1 o/p FF output by a direct strike")
			
			#Not classifying this as a separate type of fault. This o/p FF can be an i/p to another FF. So, this is classified as a glitch that got masked
			elif (int(row[outputFF_2nd_rise[0]])==1):
				temp_row.append("FF output flipped by a direct strike. Glitch: Masked")
				FF_flip_masked=FF_flip_masked+1

		elif (int(row[inputFF_3rd_rise[0]])>=1):
			#temp_row.append("Cascaded flip")
			print "case 6"
	
			if (int(row3[inputFF_3rd_rise[0]])>1):
				temp_row.append("Not possible to affect more than 1 i/p FF output by a direct strike")
			
			#Not classifying this as a separate type of fault. This o/p FF can be an i/p to another FF. So, this is classified as a glitch that got masked
			elif (int(row[inputFF_3rd_rise[0]])==1):
				temp_row.append("I/p FF flipped by a direct strike. Captured at 3rd edge")
				FF_glitch_captured=FF_glitch_captured+1
		"""
###########################################
		#print "temp_row final:", temp_row

		DFF_list.append(temp_row) #Append this to the list.. At the end of for loop, it would be a list of lists
		#print "gates_list:", DFF_list

	DFF_final_csv.writerows(DFF_list)
	FF_atleast_1_flip= (FF_csv_rows - FF_no_effect)
	FF_multiple_flips= FF_cascaded_flip_multiple + FF_glitch_captured_multiple
	print"\n*************************************************************\n"
	print"\nTotal number of particle strikes is:",total_csv_rows
	print"\nNumber of FF strikes is:",FF_csv_rows
	print"\nNumber of atleast one flip cases: ",FF_atleast_1_flip
	print"\nNumber of multiple flips given atleast 1 flip: ",FF_multiple_flips
	print"\nNumber of no effect due to strike on FF is:",FF_no_effect
	print"\nNumber of captured flips due to strike on FF is:",FF_glitch_captured
	print"\nNumber of multiple captured flips amongst the captured flips is:",FF_glitch_captured_multiple
	print"\nNumber of cascaded flips due to strike on FF is:",FF_cascaded_flip
	print"\nNumber of cascaded flips amongst the captured flips:",FF_cascaded_flip_multiple
	print"\nNumber of flips due to strike on FF that got masked at output is:",FF_flip_masked

	prob_FF_strike=(float(FF_csv_rows)/float(total_csv_rows))
	
	if FF_csv_rows>0:
		prob_FF_no_effect=(float(FF_no_effect)/float(FF_csv_rows))
		prob_FF_glitch_captured=(float(FF_glitch_captured)/float(FF_csv_rows))
		#prob_FF_output_glitch=(float(FF_output_glitch)/float(FF_csv_rows))
		prob_FF_atleast_1flip= float(FF_atleast_1_flip)/float(FF_csv_rows)
		prob_FF_flip_masked=(float(FF_flip_masked)/float(FF_csv_rows)) #FN
	else:
		prob_FF_no_effect=0.0
		prob_FF_glitch_captured=0.0
		prob_FF_atleast_1flip=0.0
		prob_FF_flip_masked=0.0	
		prob_gate_FF_NFm=0.0

	if (FF_atleast_1_flip >1):
		prob_FF_multiple_conditional= float(FF_multiple_flips)/float(FF_atleast_1_flip)
	else:
		prob_FF_multiple_conditional= 0.0

	print "Gate capture", gate_capture
	#To avoid divide by zero error:	
	if FF_glitch_captured >0: #Calculating conditional probability
		prob_FF_glitch_captured_multiple=(float(FF_glitch_captured_multiple)/float(FF_glitch_captured))
		if gate_capture >0:
			#af=float(FF_glitch_captured+gate_capture)
			#print "Gate capture in if %f" %af
			prob_gate_FF_NFm=(float(FF_glitch_captured_multiple+gate_multiple)/float(FF_glitch_captured+gate_capture))
		else:
			prob_gate_FF_NFm=0.0
	else:
		prob_FF_glitch_captured_multiple=0.0
		prob_gate_FF_NFm=0.0
	prob_FF_cascaded_flip=(float(FF_cascaded_flip)/float(FF_csv_rows))

	#To avoid divide by zero error:	
	if FF_cascaded_flip >0: #Calculating conditional probability
		prob_FF_cascaded_flip_multiple=(float(FF_cascaded_flip_multiple)/float(FF_cascaded_flip)) #Calculating conditional probability
	else:
		prob_FF_cascaded_flip_multiple=0.0

	
	if F0_first_flip>0:
		prob_FN_given_F0= (float(FF_flip_masked)/float(F0_first_flip))
	else:
		prob_FN_given_F0=0.0


	print"\n*************************************************************"
	print"Probability of a FF strike amongst total cases is:",prob_FF_strike
	print"\n*************************************************************"
	print"\nProbability of atleast one flip is:",prob_FF_atleast_1flip
	print "\nProbability of multiple flips given atleast one flip is:",prob_FF_multiple_conditional
	print"\n*************************Taxonomy************************************"
	print"Probability of no effect due to strike on FF is:",prob_FF_no_effect
	print"Probability of captured flips due to strike on FF (glitch) is:",prob_FF_glitch_captured
	print"Probability of cascaded flips due to strike on FF is:",prob_FF_cascaded_flip
	print"Probability of flips due to strike on FF that got masked at output is:",prob_FF_flip_masked
	#print"Probability of flips due to direct strike on output FF that got masked at output is:",prob_FF_output_glitch
	print"\n*************************************************************"
	print"Probability of multiple captured flips amongst the captured flips is:",prob_FF_glitch_captured_multiple
	print"Probability of multiple cascaded flips amongst the captured flips is:",prob_FF_cascaded_flip_multiple
	print"Probability of multiple flips NFm amongst the captured flips for both gate and flip-flop strike is:",prob_gate_FF_NFm

	print "Output written: %s/spice_results/taxonomy_summary_FFs_%s.csv" %(path,module)

	print"\n*************************************************************\n"

	fDFF.close()
	f2_read.close()
	f3_read.close()
	fDFF2.close()
	fDFF_final.close()


	#Final output (taxonomy) written into a taxonomy_summary_<design>.csv file inside the respective results folders
	fout = open('%s/spice_results/taxonomy_summary_FFs_%s.csv' %(path,module), 'wb')
	fout.write ("\n*****************************%s results**********************************\n" %module)
	fout.write ("\nNumber of FF strikes is: %d" %FF_csv_rows)
	fout.write ("\nNumber of atleast one flip cases: %d" %FF_atleast_1_flip)
	fout.write ("\nNumber of Multiple flips: %d" %FF_multiple_flips)	
	fout.write ("\n*************************************************************************\n")
	fout.write ("\nProbability of a FF strike amongst total cases is: %f" %prob_FF_strike)
	fout.write ("\nProbability of atleast one flip is: %f" %prob_FF_atleast_1flip)
	fout.write ("\n(P(F>=1)|P(F>0)): Conditional probability of multiple flips: NFm or FFm given atleast one flip in either of the cycles, due to strike on FF is: %f" %prob_FF_multiple_conditional)
	fout.write ("\nProbability of NN (no effect due to strike on FF) is: %f" %prob_FF_no_effect)
	fout.write ("\nProbability of NF (captured flips due to strike on FF (glitch)) is: %f" %prob_FF_glitch_captured)
	fout.write ("\nProbability of FF (cascaded flips due to strike on FF) is: %f" %prob_FF_cascaded_flip)
	fout.write ("\nProbability of FN (flips due to strike on FF that got masked at output) is: %f" %prob_FF_flip_masked)
	#fout.write ("\nProbability of flips due to direct strike on output FF that got masked at output is: %f" %prob_FF_output_glitch)
	fout.write ("\n************************MULTIPLE FLIPS*************************************\n")
	fout.write ("\nP(FN|first flip): Conditional probability of FN given the first flip occured, due to strike on FF is: %f" %prob_FN_given_F0)

	fout.write ("\nP(Multiple|NF): Conditional probability of multiple captured flips given atleast one flip, due to strike on FF is: %f" %prob_FF_glitch_captured_multiple)
	fout.write ("\nP(Multiple|FF): Conditional probability of multiple cascaded flips given atleast one flip, due to strike on FF is: %f" %prob_FF_cascaded_flip_multiple)
	fout.write ("\nP(NFm|NF for gate and flip-flop): %f" %prob_gate_FF_NFm)
	
	fout.close()

	
	###########################Write out the results into a table in a pdf############################
	"""
	from reportlab.lib import colors
	from reportlab.lib.pagesizes import letter
	from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
	from reportlab.lib.styles import getSampleStyleSheet
	from reportlab.lib.units import inch
	styles = getSampleStyleSheet()

	#Create one pdf result for each design and place it in the <path>
	doc1 = SimpleDocTemplate("%s/spice_results/taxonomy_report_FFs_%s.pdf" %(path,module), pagesize=letter)

	# container for the 'Flowable' objects
	elements = [] #Keep appending whatever you want to add to the pdf, here to the elements

	style = styles["Normal"]
	styleH = styles["Heading2"]
	p = Paragraph('''Multiple-bit error/fault classification''', styleH)
	elements.append(p)
	p = Paragraph('''Design: %s''' %module, style)
	elements.append(p)
	p = Paragraph(''' Taxonomy for strike on FFs''', style)
	elements.append(p)
	elements.append(Spacer(1,0.2*inch))


	#Table for FFs
	data_FF= [['Parameter', 'Probability'],
	       ['FF strike', prob_FF_strike],
		#['Atleast 1 flip',prob_FF_atleast_1flip],
		#['Conditional prob of multiple flips',prob_FF_multiple_conditional],
	       [' NN(No effect)', prob_FF_no_effect],
	       ['NF(Glitch- Propagated and captured)', prob_FF_glitch_captured],
		['P(multiple flips at output | NF)', prob_FF_glitch_captured_multiple],
		['FN(Flip- Masked)',prob_FF_flip_masked],
		['FF(Cascaded flips)', prob_FF_cascaded_flip],
		 ['P(multiple flips at output FFm | FF)', prob_FF_cascaded_flip_multiple],
		['FN|First flip (FN|F0)',prob_FN_given_F0],
		 ['P(multiple flips NFm or FFm | atleast one flip)', prob_FF_multiple_conditional],
		 ['P(NFm for gate and flip-flop | NF)', prob_gate_FF_NFm]]


		#['Glitch on output(direct strike)',prob_FF_output_glitch]]
	t1=Table(data_FF)
	t1.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.white),
			       ('TEXTCOLOR',(0,0),(1,0),colors.blue),  #(columns,rows) or (0,0,(-1,-4)
				('INNERGRID', (0,0), (-1,-1), 0.25, colors.black), 
				 ('BOX', (0,0), (-1,-1), 0.5, colors.black)  #(-1,-1) indicates the (last column, last row)
	       ]))
	elements.append(t1)
	doc1.build(elements)
	"""
	#print "Elements in table is: ",elements
	print "\n**Completed executing the gate_strike_taxonomy script***\n"
	print "%s/spice_results/taxonomy_report_FFs_%s.pdf has the results." %(path,module)
	



