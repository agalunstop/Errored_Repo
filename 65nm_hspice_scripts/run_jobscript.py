#!/usr/bin/env python
#Author : Sonal Gupta
#Readability is what I strive for

######## Main program #########
from python_jobscript import *
parser = OptionParser("This utility takes mode as an argument\n")

parser.add_option("-m", "--mod",dest='mode', help='mode can be either "sim" or "sanity"')
(options, args) = parser.parse_args()
mode=options.mode


op_voltages = ['1.0','0.9','0.8','0.7','0.6','0.5','0.4']
#op_voltages = ['1.0']
#no_of_sim_arr = [8,16,56,96]
no_of_sim_arr = [96]
group = 8
resolution = 100.0
circuits = ['decoder']
for ckt in circuits:
	using_logger = log_file_manager(log_file1="sanity_%s.log"%(ckt),log_file2="result_sanity_%s.log"%(ckt))
	using_logger.clean_logs()
	using_logger.open_logs()
	sim_ckt = circuit(ckt,op_voltages,4000.0)
	if mode == 'sanity':
		using_logger.write_to_log2("%s :"%(sim_ckt.name))
		ckt_dict = csv_to_dictionary('input_files/%s.csv'%(ckt))
		for key in ckt_dict.keys():
			if not ckt_dict[key][0].isalpha():
			#	print ckt_dict[key][0]
				sim_ckt.max_op_freq_dict[key] = float(ckt_dict[key][0])
		sanity_check(no_of_sim_arr,group,sim_ckt,resolution,using_logger,inj_curr=0.0,use_freq_array=1)
	else:
		no_of_sim = 32
		using_logger.write_to_log2("%s :"%(sim_ckt.name))
		current_dict = csv_to_dictionary('input_files/current.csv')
		ckt_dict = csv_to_dictionary('input_files/%s.csv'%(ckt))

		for op_volt in sim_ckt.op_voltages:
			for glitch_current in current_dict[op_volt]:
				run_sim(sim_ckt.name,op_volt,ckt_dict[op_volt][0],no_of_sim,group,using_logger,glitch_current,just_checking_log_flag=0)
				save_sim_results(sim_ckt.name,op_volt,glitch_current)

		using_logger.close_logs()
