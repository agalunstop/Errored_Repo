#This script just combines 2 pdfs

#Example usage: python python_combine_pdfs.py -p /home/external/iitb/nanditha/simulations/decoder_ip_opFF_rise/spice_results -m decoder_op_ip

#Path to pypdf on param yuva is added, uisng import sys and sys.append: Feb 12 2014
import optparse,os

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from optparse import OptionParser

#The below lines related to 'sys' are to find the pyPdf module on the Param yuva cluster. 
#Ideally, if we run it on our systems, the below line should be  "from pyPdf import PdfFileWriter, PdfFileReader"

#import sys
#sys.path.append('/opt/app/Pypdf-1.13/lib/python2.6/site-packages/pyPdf')
from pyPdf import PdfFileWriter, PdfFileReader

parser = OptionParser('This script just combines 2 pdfs of gates taxonomy and flip-flop taxonomy. The final pdf containing the 2 results is generated in spice_results/taxonomy_report_all_<design>.pdf\nAuthor:Nanditha Rao(nanditha@ee.iitb.ac.in)\n')

parser.add_option("-p", "--path", dest="path",help="Enter the ENTIRE path to the folder which contains the 2 pdfs to be merged ")
parser.add_option("-m", "--mod", dest="module",help="Enter the module name ")

(options, args) = parser.parse_args()

path=options.path
design=options.module

#Combine the 2 reports
doc = SimpleDocTemplate("%s/taxonomy_report_all_%s.pdf" %(path,design), pagesize=letter)

#####################Merge the gate and FF pdfs into one final pdf##################


output = PdfFileWriter()

if (os.path.isdir('%s' %path)):
	#print "Inside if"		
	input1 = PdfFileReader(file("%s/taxonomy_report_gates_%s.pdf" %(path,design), "rb"))
	# print how many pages input1 has:
	print "\n%s/taxonomy_report_gates_%s.pdf has %s pages." % (path,design,input1.getNumPages())
	# add page 1 from input1 to output document, unchanged. Each pdf has only one page
	output.addPage(input1.getPage(0))

	input2 = PdfFileReader(file("%s/taxonomy_report_FFs_%s.pdf" %(path,design), "rb"))
	# print how many pages input1 has:
	print "\n%s/taxonomy_report_FFs_%s.pdf has %s pages." % (path,design,input1.getNumPages())
	# add page 1 from input1 to output document, unchanged. Each pdf has only one page
	output.addPage(input2.getPage(0))

# finally, write "output" to document-output.pdf
outputStream = file("%s/taxonomy_report_all_%s.pdf" %(path,design), "wb")
output.write(outputStream)
outputStream.close()

print "\nWritten final results file with taxonomy of all designs combined\n"
print "\nLocation of the file: %s/taxonomy_report_all_%s.pdf\n\n" %(path,design)

