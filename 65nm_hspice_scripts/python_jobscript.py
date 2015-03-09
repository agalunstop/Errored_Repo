#!/usr/bin/env python
import re,os,sys
import time

def run_sim(volt,freq,sim):
	time.sleep(1)
	os.system('python python_utility2_hspice_2cycles_time0_65.py -m decoder_op_ip -p /home/users/guptasonal/Fault_Project/Simulation/sim_65nm/sim_decoder_1000_1 -d sim_decoder_1000_1 -t 65 -n %s --group 3 --clk %s --volt %s --curr 0.4 --scripts_path /home/users/guptasonal/Fault_Project/Simulation/sim_65nm/scripts/65nm_hspice_scripts >/dev/null 2&>log_sim_%s_%s' %(sim,freq,volt,freq,volt))
#	os.system('echo Probability of atleast one flip is: 0.0000 > log_sim_%s_%s' %(freq,volt))
	os.system('cp /home/users/guptasonal/Fault_Project/Simulation/sim_65nm/sim_decoder_1000_1/spice_results/taxonomy_summary_FFs_decoder_op_ip.csv /home/users/guptasonal/Fault_Project/Simulation/sim_65nm/sim_decoder_1000_1/sim_results/taxonomy_%s_%s_summary_FFs_decoder_op_ip.csv' %(freq,volt))
	os.system('cp /home/users/guptasonal/Fault_Project/Simulation/sim_65nm/sim_decoder_1000_1/spice_results/taxonomy_summary_gates_decoder_op_ip.csv /home/users/guptasonal/Fault_Project/Simulation/sim_65nm/sim_decoder_1000_1/sim_results/taxonomy_%s_%s_summary_gates_decoder_op_ip.csv' %(freq,volt))

def check_log(log_sim):
	fail = 1
	no_of_prob = 0
	for line in open('%s' %(log_sim)):
		if "Probability of atleast one flip is" in line:
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
op_cond_dict = {1   : 2382,
				0.9 : 1706,
				0.8 : 936,
				0.7 : 295,
				0.6 : 53,
				0.5 : 6,
				}
op_cond_dict_min = {1   : 1383,
				0.9 : 1000,
				0.8 : 836,
				0.7 : 195,
				0.6 : 40,
				0.5 : 1,
				}
for volt in reversed(sorted(op_cond_dict.keys())):
	output_file=sys.stdout
	no_of_sim = 3000
	exit = 0
	freq = op_cond_dict[volt]
#	while exit == 0:
	output_file.write('Running %s simulations at voltage = %s, frequency = %s\n' %(no_of_sim,volt,freq))
	run_sim(volt,freq,no_of_sim)
	output_file.write('Created log_sim_%s_%s\n' %(freq,volt))
	log_sim = 'log_sim_%s_%s' %(freq,volt)
	err_stat = check_log(log_sim)
#		if err_stat == 0:				#passed
#			output_file.write('%s passed\n' %(log_sim))
#			op_cond_dict_min[volt] = freq
#		elif err_stat == 1:				#failed
#			output_file.write('%s failed\n' %(log_sim))
#			op_cond_dict[volt] = freq
#		else:
#			output_file.write('%s invalid\n' %(log_sim))
#			op_cond_dict[volt] = freq
#		if (op_cond_dict[volt] - op_cond_dict_min[volt]) > 1:
#			freq = freq - 1
##			freq = (op_cond_dict[volt]+op_cond_dict_min[volt])/2
#		else:
#			exit = 1
			
