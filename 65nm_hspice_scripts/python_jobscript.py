#!/usr/bin/env python
import re,os,sys
import time
import optparse
import os.path
from optparse import OptionParser

if os.path.isfile('sanity.log'):
	os.system('rm sanity.log')

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("sanity.log", "a")
        self.log2 = open("result_sanity.log", "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def write2(self, message):
        self.terminal.write(message)
        self.log2.write(message)  

sys.stdout = Logger()

def run_sim(ckt,volt,freq,sim,curr):
	time.sleep(1)
#	if os.path.isfile('log_sim_%s_%s_%s' %(ckt,freq,volt)):
#		pass
#	else:	
	os.system('python python_utility2_hspice_2cycles_time0_65.py -m %s_clk_ipFF -p /home/users/guptasonal/Fault_Project/Simulation/sim_65nm/sim_%s -d sim_%s -t 65 -n %s --group 3 --clk %s --volt %s --curr %s --scripts_path /home/users/guptasonal/Fault_Project/Simulation/sim_65nm/scripts/65nm_hspice_scripts >/dev/null 2&>log_sim_%s_%s_%s' %(ckt,ckt,ckt,sim,freq,volt,curr,ckt,freq,volt))
#	os.system('echo Probability of atleast one flip is: 0.0000 > log_sim_%s_%s' %(freq,volt))
#	os.system('cp /home/users/guptasonal/Fault_Project/Simulation/sim_65nm/sim_decoder_1000_1/spice_results/taxonomy_summary_FFs_decoder_op_ip.csv /home/users/guptasonal/Fault_Project/Simulation/sim_65nm/sim_decoder_1000_1/sim_results/taxonomy_%s_%s_summary_FFs_decoder_op_ip.csv' %(freq,volt))
#	os.system('cp /home/users/guptasonal/Fault_Project/Simulation/sim_65nm/sim_decoder_1000_1/spice_results/taxonomy_summary_gates_decoder_op_ip.csv /home/users/guptasonal/Fault_Project/Simulation/sim_65nm/sim_decoder_1000_1/sim_results/taxonomy_%s_%s_summary_gates_decoder_op_ip.csv' %(freq,volt))

def check_log(log_sim):
	fail = 1
	no_of_prob = 0
	for line in open('%s' %(log_sim)):
		if "Probability of atleast one flip is" in line:
			output_file.write('%s'%(line))
			no_of_prob += 1
	   		prob_flip=float(line.split(': ')[1])
	#		print prob_flip
			if prob_flip == 0.0:
				fail = 0
			else:
				fail = 1
	if fail == 0:
		return 0
	else:
		if no_of_prob > 0:
			return 1
		else:
			return 2

######## Main program starts #########
circuits = ['c499','c880','c1355','c1908']
simulation = [9,90,900,3000]
op_cond_volt = 		[1,		0.9,		0.8,		0.7,		0.6,		0.5,		0.4,		0.3]
op_cond_freq_dict = {	'c499' : [1646,	869,		575,		194,		43,			3,			0.5,		0.032],
						'c880' : [1843,	904,		595,		131,		29,			4,			0.563,		0.053],
						'c1355': [1622,	807,		607,		186,		30,			4,			0.375,		0.03],
						'c1908': [2000,	900,		700,		200,		50,			5,			0.6,		0.06]}

parser = OptionParser("It takes arguments\n")

parser.add_option("-m", "--mod",dest='mode', help='mode can be either "sim" or "sanity"')

(options, args) = parser.parse_args()


mode=options.mode
output_file=sys.stdout
if mode == 'sanity':
	output_file.write('entered sanity\n')
	for ckt_n in range(0,3):
		ckt = circuits[ckt_n]
		op_cond_freq = op_cond_freq_dict[ckt]
		op_cond_min_freq = [0,	0,			0,			0,			0,			0,			0,			0]
		output_file.write('simulating for %s\n' %(ckt))
		for n in range(2,4):
			no_of_sim = simulation[n]
			for i in range(len(op_cond_volt)):
				freq = op_cond_freq[i]
				volt = op_cond_volt[i]
				curr = 0.0
				resolution = 1
				exit = 0
				inval_sim = 0
				while exit == 0:
					output_file.write('%s : Running %s simulations at voltage = %s, frequency = %s, current = %s\n' %(ckt,no_of_sim,volt,freq,curr))
					run_sim(ckt,volt,freq,no_of_sim,curr)
					output_file.write('Created log_sim_%s_%s_%s\n' %(ckt,freq,volt))
					log_sim = 'log_sim_%s_%s_%s' %(ckt,freq,volt)
					err_stat = check_log(log_sim)
					if err_stat == 0:				#passed
						output_file.write('%s passed\n' %(log_sim))
						op_cond_min_freq[i] = freq
						inval_sim = 0
					elif err_stat == 1:				#failed
						output_file.write('%s failed\n' %(log_sim))
						op_cond_freq[i] = freq
						inval_sim = 0
					else:
						output_file.write('%s invalid\n' %(log_sim))
						inval_sim += 1
						if inval_sim == 3:
							exit = 1
					if op_cond_freq[i] <= resolution:
						resolution = float(resolution)/10
						output_file.write('resolution changed to %s\n' %(resolution))
						op_cond_min_freq[i] = float(op_cond_min_freq[i])
						op_cond_freq[i] = float(op_cond_freq[i])
					if inval_sim == 0:
						if (op_cond_freq[i] - op_cond_min_freq[i]) > resolution:
							if no_of_sim < 100:
								if resolution >= 1:
									freq = int((op_cond_freq[i]+op_cond_min_freq[i])/2)
								else:
									freq = round((op_cond_freq[i]+op_cond_min_freq[i])/2, 3)
							else:
								freq = freq - resolution
						else:
							exit = 1
					if exit == 1:
						if i < (len(op_cond_volt)-1):
							if op_cond_freq[i+1] > op_cond_min_freq[i] and op_cond_min_freq[i] > 0:
								op_cond_freq[i+1] = op_cond_min_freq[i]
		for i in range(len(op_cond_volt)):
			output_file.write2('%s passed for Voltage = %s, Frequency = %s\n' %(ckt,op_cond_volt[i],op_cond_min_freq[i]))
		
		output_file.write2('\n')
		os.system('rm log_sim_%s_*'%(ckt))		
	
else:
	mode = 'sim'
	print "Simulating"
	curr = 0.4
	no_of_sim = 3000
