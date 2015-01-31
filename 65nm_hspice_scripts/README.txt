Usage:

NOTE: Do not forget to ssh into the machine using -X option since the script
opens many tools in gui

---------files needed-----------------

design folder: <design>.vhd, <testbench>.vhd, hspice_65nm_models folder
(included in the scripts folder). This design folder can be anywhere, and is
independent of the scripts folder

You need to have the spice library file “CORE65GPSVT_all_vdd_gnd_WL_ad.sp” 
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

cd to the scripts directory and run the script “utility_python_top_level_65.py” on the vlsi lab machine- to generate the spice reference file. Three example usages are given inside the script itself (at the beginning)

Now, copy your design folder to Pune CDAC cluster. I suggest that you do not copy the directory named ‘work’ created by modelsim (its size is huge and takes a long time to copy)

If you want to run the spice simulations on VLSI lab machine then the
65_nm_scripts folder should be used and python_utility2_hspice_2cycles_time0_65.py
as hspice does not run on pune cluster.

If you want to run the spice simulations on pune cluster then the folder
65nm_cdac_scripts present inside current folder whould be copied to the pune
server and script python_utility2_ngspice_yuva_65.py should be run in that
folder. This will run ngspice.

The jobscript should be run from the corresponding scripts folder

Modify the parameters in the jobscript.txt. Before launching thousands of jobs, do a test-run with just few jobs- say 4 to 5. This text file will run the script “python_utility2_hspice_2cycles_time0_65.py" on the lab machine to run hspice


Changes done to scripts:

perl_spice_netlist_format_65.pl script updated- .ic statements: Oct 24 2014 

