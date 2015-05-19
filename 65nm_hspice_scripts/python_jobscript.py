#!/usr/bin/env python
#Author : Sonal Gupta
#Readability is what I strive for

import re
import os
import sys
import time
import optparse
import os.path
from optparse import OptionParser
import csv

class log_file_manager(object):
	"""Provides methods to write to a log file along
	with printing on stdout"""
	def __init__(self,log_file1="sanity.log",log_file2="result_sanity.log"):
		self.terminal = sys.stdout
		self.log_file1 = log_file1
		self.log_file2 = log_file2

	def open_logs(self,write_mode="a"):
		self.log1 = open(self.log_file1, write_mode)
		self.log2 = open(self.log_file2, write_mode)

	def write_to_log1(self, message):
		self.terminal.write(message)
		self.terminal.write("\n")
		self.log1.write(message)  
		self.log1.write("\n")  
	
	def write_to_log2(self, message):
		self.terminal.write(message)
		self.terminal.write("\n")
		self.log2.write(message)  
		self.log2.write("\n")  
	
	def close_logs(self):
		self.log1.close()
		self.log2.close()
	
	def clean_logs(self):
		if os.path.exists(self.log_file1):
			os.remove(self.log_file1)
		if os.path.exists(self.log_file2):
			os.remove(self.log_file2)
#------------------------------------------------------

def run_sim(circuit_name,op_volt,op_freq,no_of_sim,group,using_logger,inj_curr,just_checking_log_flag=0,simulator='ngspice'):
	time.sleep(1)
	if simulator == 'ngspice':
		script = 'python_utility2_ngspice_yuva_65.py'
		scripts_path = '/home/users/guptasonal/Fault_Project/Simulation/sim_65nm/scripts/65nm_ngspice_scripts'
	else:
		script = 'python_utility2_hspice_2cycles_time0_65.py'
		scripts_path = '/home/users/guptasonal/Fault_Project/Simulation/sim_65nm/scripts/65nm_hspice_scripts'

	if (just_checking_log_flag == 1):
		if os.path.isfile('log_sim_%s_%s_%s' %(circuit_name,op_freq,op_volt)):
			pass
		else:
			prob = 0.0
			if op_volt == 1.0:
				if op_freq >= 1000:
					prob = 1.0
			elif op_volt == 0.9:
				if op_freq >= 100:
					prob = 1.0
			elif op_volt == 0.8:
				if op_freq >= 10:
					prob = 1.0
			elif op_volt == 0.7:
				if op_freq >= 1:
					prob = 1.0
			elif op_volt == 0.6:
				if op_freq >= 0.1:
					prob = 1.0

			using_logger.write_to_log1('%s : Creating log for %s simulations at voltage = %s, frequency = %s, current = %s'\
				%(circuit_name,no_of_sim,op_volt,op_freq,inj_curr))
			os.system('echo "Probability of atleast one flip is: %s" > log_sim_%s_%s_%s' %(prob,circuit_name,op_freq,op_volt))
			os.system('echo "Probability of atleast one flip is: %s" >> log_sim_%s_%s_%s' %(prob,circuit_name,op_freq,op_volt))
	else:	
		if (circuit_name.startswith('c')):
			"""circuit to be simulated is ISCAS circuit"""
			using_logger.write_to_log1('%s : Running %s simulations at voltage = %s, frequency = %s, current = %s'\
				%(circuit_name,no_of_sim,op_volt,op_freq,inj_curr))
			os.system('python %s -m %s_clk_ipFF -p /home/users/guptasonal/Fault_Project/Simulation/sim_65nm/sim_%s -d sim_%s -t 65 -n %s --group %s --clk %s --volt %s --curr %s --scripts_path %s >/dev/null 2&>log_sim_%s_%s_%s_%s' %(script,circuit_name,circuit_name,circuit_name,no_of_sim,group,op_freq,op_volt,inj_curr,scripts_path,circuit_name,op_freq,op_volt,inj_curr))
		else:	
			"""circuit to be simulated is decoder"""
			using_logger.write_to_log1('%s : Running %s simulations at voltage = %s, frequency = %s, current = %s'\
				%(circuit_name,no_of_sim,op_volt,op_freq,inj_curr))
			os.system('python %s -m %s_op_ip -p /home/users/guptasonal/Fault_Project/Simulation/sim_65nm/sim_%s -d sim_%s -t 65 -n %s --group %s --clk %s --volt %s --curr %s --scripts_path %s >/dev/null 2&>log_sim_%s_%s_%s_%s' %(script,circuit_name,circuit_name,circuit_name,no_of_sim,group,op_freq,op_volt,inj_curr,scripts_path,circuit_name,op_freq,op_volt,inj_curr))

def check_log(simulation_log,using_logger,delete_log=0):
	"""Finds whether the probability of flip is 0 in the log"""
	fail = 1
	prob_sentences_found = 0
	if os.path.isfile(simulation_log):
		for line in open('%s' %(simulation_log)):
			if "Probability of atleast one flip is" in line:
				using_logger.write_to_log1('%s'%(line))
				prob_sentences_found += 1
		   		prob_flip=float(line.split(': ')[1])
				#print prob_flip
				if prob_flip == 0.0:
					fail = 0
				#	print "passed"
				else:
					fail = 1
				#	print "failed"
					break
		if delete_log == 1:
			os.system('rm -f %s'%(simulation_log))

		if fail == 0 and prob_sentences_found > 0:
			return ("%s passed"%(simulation_log))
		elif prob_sentences_found == 0:
			return ("%s log improper"%(simulation_log))
		else:
			return ("%s failed, %s probability statements found"%(simulation_log,prob_sentences_found))
	else:
		return ("%s not found"%(simulation_log))

class circuit(object):
	def __init__(self,name,op_voltages,max_op_freq):
		circuit.name = name
		circuit.op_voltages = op_voltages
		circuit.max_op_freq = max_op_freq
		circuit.op_frequencies = {}

def set_resolution(freq,resolution):
	while freq <= resolution:
		resolution = round(resolution/10,6)
	return resolution
	
def sanity_check(no_of_sim_arr,group,circuit,resolution,using_logger,inj_curr=0.0):
	op_freq = circuit.max_op_freq
	for op_volt in circuit.op_voltages:
		for no_of_sim in no_of_sim_arr:
			quit = 0
			while quit == 0:
				run_sim(circuit.name,op_volt,op_freq,no_of_sim,group,using_logger,inj_curr,just_checking_log_flag=0)	
				log_stat = check_log('log_sim_%s_%s_%s'%(circuit.name,op_freq,op_volt),using_logger)
				using_logger.write_to_log1(log_stat)
				if log_stat.endswith("passed"):
					using_logger.write_to_log1("Detected passed")
					quit = 1
				elif log_stat.endswith("improper"):
					using_logger.write_to_log1("Detected wrong log.. Re-running")
				else:
					using_logger.write_to_log1("Detected failed")
					resolution = set_resolution(op_freq,resolution)
					using_logger.write_to_log1("Resolution = %s"%(resolution))
					op_freq = op_freq - resolution
					op_freq = round(op_freq,6)
					using_logger.write_to_log1("New freq = %s"%(op_freq))
		using_logger.write_to_log2("%s passed for volt = %s freq = %s"%(circuit.name,op_volt,op_freq))
		circuit.op_frequencies[op_volt] = op_freq	
					
def simulate(no_of_sim,group,circuit,using_logger,inj_curr=0.0):
	curr_factor = 1
	for op_volt in circuit.op_voltages:
		inj_curr = op_volt*curr_factor*inj_curr
		run_sim(circuit.name,op_volt,circuit.op_frequencies[op_volt],no_of_sim,group,using_logger,inj_curr,just_checking_log_flag=0)
		save_sim_results(circuit.name,op_volt,circuit.op_frequencies[op_volt])

def save_sim_results(circuit,op_volt,glitch_curr):
	results_dir = "../../sim_%s/spice_results"%(circuit)
	new_results_dir = "../../sim_%s/results_sim"%(circuit) 
	volt_results_dir = "%s/volt_%s"%(new_results_dir,op_volt)
	if not os.path.exists(new_results_dir):
		os.makedirs(new_results_dir)	
	if not os.path.exists(volt_results_dir):
		os.makedirs(volt_results_dir)	
	os.system('mv %s/taxonomy_summary_FFs* %s/%s_taxonomy_summary_FFs_%s_%s.csv'%(results_dir,volt_results_dir,glitch_curr,circuit,op_volt))
	os.system('mv %s/taxonomy_summary_gates* %s/%s_taxonomy_summary_gates_%s_%s.csv'%(results_dir,volt_results_dir,glitch_curr,circuit,op_volt))

def csv_to_dictionary(csv_file):
	ret_dict = {}
	with open(csv_file, 'rb') as csvfile:
		readfile = csv.reader(csvfile, delimiter=',')
		for row in readfile:
			ret_dict[row[0]] = row[1:]
	return ret_dict

######## Main program #########
parser = OptionParser("This utility takes mode as an argument\n")

parser.add_option("-m", "--mod",dest='mode', help='mode can be either "sim" or "sanity"')
(options, args) = parser.parse_args()
mode=options.mode

using_logger = log_file_manager()
using_logger.clean_logs()

op_voltages = ['1.0','0.9','0.8','0.7','0.6','0.5','0.4']
#op_voltages = ['1.0']
no_of_sim_arr = [5,10,100]
group = 8
resolution = 100.0
circuits = ['decoder']
for ckt in circuits:
	using_logger.open_logs()
	sim_ckt = circuit(ckt,op_voltages,1000.0)
	if mode == 'sanity':
		using_logger.write_to_log2("%s :"%(sim_ckt.name))
		sanity_check(no_of_sim_arr,group,sim_ckt,resolution,using_logger,inj_curr=0.0)
	else:
		no_of_sim = 32
		using_logger.write_to_log2("%s :"%(sim_ckt.name))
		current_dict = csv_to_dictionary('input_files/current.csv')
		ckt_dict = csv_to_dictionary('input_files/%s.csv'%(ckt))

		for op_volt in sim_ckt.op_voltages:
			for glitch_current in current_dict[op_volt]:
#				using_logger.write_to_log2("%s : %s MHz with %s mA"%(op_volt,ckt_dict[op_volt][0],glitch_current))
#				run_sim(circuit_name,op_volt,op_freq,no_of_sim,group,using_logger,inj_curr,just_checking_log_flag=0,simulator='ngspice')
				run_sim(sim_ckt.name,op_volt,ckt_dict[op_volt][0],no_of_sim,group,using_logger,glitch_current,just_checking_log_flag=0)
				save_sim_results(sim_ckt.name,op_volt,glitch_current)

		using_logger.close_logs()
