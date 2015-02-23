---------files needed-----------------

design folder: <design>.vhd, <testbench>.vhd, hspice_65nm_models folder
(included in the scripts folder). This design folder can be anywhere, and is
independent of the scripts folder

You need to have the spice library file “CORE65GPSVT_all_vdd_gnd_WL_ad_noR.txt” 
one level up from your scripts folder, to generate the glitch library. 

---------pnr script simulation steps---------

This script is to be run on vlsi lab machines. It has been tested on vlsi29
machine.

Top level script: utility_python_top_level_65.py, Usage given in the script
itself. This script generates the reference spice file. Several options can be
specified in the script. Elaborate documentation is provided within each
script.

The top level script should be run from the scripts folder.
On getting the "encounter>" prompt, type exit and the script will continue
running.

NOTE: The rtl2gds tool does not take the voltage specified in the script with
option -v . Thus, do not trust the slack okay information if you want to
simulate the circuit at non-ideal voltage for 65nm (i.e. 1.1V). The slack will
always be calculated for operating voltage of 1.1V and the frequency specified
by you in the script.

*******************************************************************************************

----------deck creation and simulation script--------

The previous script must have created the following files in your design
folder:
drain_areas.txt
glitch_CORE65GPSVT_selected_lib_vg.sp
reference_spice.sp
spice_results/headers.csv

If any of the above files are missing then the script has not run properly.

Next, we have to run the jobscript.txt script file present in the scripts
folder. This jobscript is not presently created by the script thus has to be
modified manually. This has to be copied to the design folder and run from the design 
folder to run the script python_utility2_hspice_2cycles_time0_65.py 

Modify the parameters in the jobscript.txt. Before launching thousands of jobs, do a test-run with just few jobs- say 4 to 5. This text file will run the script “python_utility2_hspice_2cycles_time0_65.py" on the lab machine to run hspice

Changes done to scripts:

perl_spice_netlist_format_65.pl script updated- .ic statements: Oct 24 2014 

Changes to be done:
1) -v option to be added to change operating voltage in reference_spice and add
to the jobscript to be taken by compare scripts to compare with correct values
of voltages.

2) jobscript to be generated using the script

3) compare scripts to be modified to take the voltages as a parameter


Usage:

You need to have the spice library file “CORE65GPSVT_all_vdd_gnd_WL_ad_noR.txt” one level up from your scripts folder, to generate the glitch library. 

Copy the hspice_65nm_models directory from this directory to your design directory

Have your design (vhd) file and test bench in a design folder

Copy all the scripts in the “65nm_cdac_scripts” to a directory.

cd to the scripts directory and run the script “utility_python_top_level_yuva_65.py” on the vlsi lab machine- to generate the spice reference file. Three example usages are given inside the script itself (at the beginning)

Now, copy your design folder to Pune CDAC cluster. I suggest that you do not copy the directory named ‘work’ created by modelsim (its size is huge and takes a long time to copy)

Modify the parameters in the jobscript.txt. Before launching thousands of jobs, do a test-run with just few jobs- say 4 to 5. This text file will run the script “python_utility2_ngspice_yuva_65.py” on the cluster


Changes done to scripts:

########## changes done by sonal #####################

perl_deckgen.pl : To be done: should be able to change op voltage, frequency
and current injected in each file generated; put an option sanity when sanity
check is done with current zero and report is generated; without sanity
option, list of op voltages and frequencies should be taken and separate spice
results folder should be generated.

########### changes done by nanditha ##################
perl_spice_netlist_format_noR_65.pl script updated- .ic statements: Oct 24 2014 

utility_python_top_level_yuva_65.py: #Created a parameter scripts_path - Oct 20 2014
python_utility2_ngspice_yuva_65.py: #Created a parameter scripts_path - Oct 20 2014

perl_glitchLibGen_65.pl: #The condition of distinct drains is removed: (($dlist=~m/$drain/) is deleted : Oct 20 2014

perl_spice_netlist_format_noR_65.pl script is updated: #updated all .ic statements with new initialisation node names. DFPQX4 and DFPQX9 have different .ic node names- Oct 20 2014

python_create_jobscript_65.py: #Updated with scripts_path: Oct 20 2014


python_FF_strike_taxonomy_65.py and python_gate_strike_taxonomy_65.py : #Added few if conditions to solve zero division error: Oct 18 2014

python_combine_pdfs_yuva_65.py created: Oct 18 2014
