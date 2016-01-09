#####################################################################################################################
#TOOL  : File comparison Tool
#Author: Sriram Kumar
#Date  : 10/7/2015
#####################################################################################################################
from sys import argv
import os
import shutil
import csv
import commands
import logging
import sys

def compare_log():
	
	LOG_FILENAME = 'compare_log.out'
	logging.basicConfig(filename=LOG_FILENAME,
	                    level=logging.DEBUG,
                    )

#####################################################################################################################
#Beautify!!!
#####################################################################################################################

def formatter():
        print "*" * 100
        print "*" * 100

def gui():
#####################################################################################################################
#function get the file comparison inputs from the user
#####################################################################################################################

	global in_file_1
	global in_file_2
	global in_keys
	global in_delimiter
	global in_num_column
	global col_num
	global reduced_col_num
	
	##beautify
        formatter()
        print  "*" * 40 , " File comparison" , "*" * 40
        formatter()

        print "\n Please enter the file names to be compared"
        

        in_file_1 = raw_input("\nFile1 : ")
        in_file_2 = raw_input("\nFile2 : ")
        
        in_delimiter = raw_input("\nDelimiter : ")
        
        in_keys = raw_input("\nkey columns (as 1,2 etc): ")
	
	in_ex_columns = raw_input("\ncolumns to be excluded (as 1,2 etc, 0 if all columns are to be considered):")
	
	in_ex_col_list = [int(i)+1 for i in in_ex_columns.split(',')]
	
	source = open(in_file_1)
	line =  source.readline()
	
	in_num_column = line.count(in_delimiter) + 2
	
	for i in range(2,in_num_column+1):
	       
	        if i not in in_ex_col_list:
	
	                if i == 2:
	                        col_num = str(i)
	                else:
	                        col_num = col_num + "," + str(i)
	
	#logic to handle excluded columns
	if in_ex_columns == '0':                         
		reduced_col_num = in_num_column
	else:
		reduced_col_num = in_num_column - len(in_ex_col_list)
		
		print reduced_col_num
        
def compare_gen_script():
#####################################################################################################################
#function to create the shell script for comparison
#####################################################################################################################

	file = open( 'compare.sh' , 'w')

	file.write("#!/bin/bash\n")

	file.write("in_file_1=$1\n")

	file.write("in_file_2=$2\n")

	file.write("in_delimiter=$3\n")
	
	file.write("in_keys=$4\n")
	
	file.write("in_num_column=$5\n")
		
	file.write("######################################################GET THE KEY VLAUES AS 1 KEY###############################################################################\n")

	file.write("###concatenate the keys\n")
	file.write("cut -f$in_keys -d $in_delimiter $in_file_1> file_1_tmp_key.cmp\n")
	
	file.write("sed -i 's#%s##g' file_1_tmp_key.cmp\n" % in_delimiter)

	file.write("###concatenate to original file\n")
	file.write("paste -d$in_delimiter $in_file_1 file_1_tmp_key.cmp> file_1_tmp_key_cat.cmp\n")

	file.write("######################################################GET THE KEY VLAUES AS 1 KEY###########################################################\n")
	file.write("###concatenate the keys\n")
	file.write("cut -f$in_keys -d $in_delimiter $in_file_2> file_2_tmp_key.cmp\n")
	file.write("sed -i 's#%s##g' file_2_tmp_key.cmp\n" % in_delimiter)

	file.write("###concatenate to original file\n")
	file.write("paste -d$in_delimiter $in_file_2 file_2_tmp_key.cmp> file_2_tmp_key_cat.cmp\n")


	file.write("######################################################GET THE MATCHED VALUES#############################################################\n")
	file.write("###join based on keys\n")
	file.write("join -t$in_delimiter -1 $in_num_column -2 $in_num_column <(sort -t$in_delimiter -k$in_num_column file_1_tmp_key_cat.cmp) <(sort -t$in_delimiter -k$in_num_column file_2_tmp_key_cat.cmp)|cut -f1 -d $in_delimiter >cmp_match_key.cmp\n")

	file.write("######################################################GET THE UNMATCHED##################################################################\n")

	
	file.write("###get the files which match keys (remove the matched)\n")
	
	file.write("join -t$in_delimiter -1 $in_num_column -2 1 -v1 <(sort -t$in_delimiter -k$in_num_column file_1_tmp_key_cat.cmp) <(sort -t$in_delimiter -k1 cmp_match_key.cmp)|cut -f2-$in_num_column -d $in_delimiter> unmatch_file_1_cct.cmp\n")
	
	file.write("###get the files which match keys (remove the matched)\n")
	
	file.write("join -t$in_delimiter -1 $in_num_column -2 1 -v1 <(sort -t$in_delimiter -k$in_num_column file_2_tmp_key_cat.cmp) <(sort -t$in_delimiter -k1 cmp_match_key.cmp)|cut -f2-$in_num_column -d $in_delimiter> unmatch_file_2_cct.cmp\n")

	file.write("sed -i -e 's/^/file_1%s/' unmatch_file_1_cct.cmp\n" % in_delimiter)
	file.write("sed -i -e 's/^/file_2%s/' unmatch_file_2_cct.cmp\n" % in_delimiter)
	
	file.write("cat unmatch_file_1_cct.cmp unmatch_file_2_cct.cmp| sort -t$in_delimiter -k1 >compare_output_unmatched.txt\n")

	file.write("######################################################GET THE MATCHED##################################################################\n")


	file.write("###get the files which match keys (remove the unmatched)\n")

	file.write("join -t$in_delimiter -1 $in_num_column -2 1 <(sort -t$in_delimiter -k$in_num_column file_1_tmp_key_cat.cmp) <(sort -t$in_delimiter -k1 cmp_match_key.cmp)|cut -f%s -d $in_delimiter> match_file_1_cct.cmp\n" % col_num)

	file.write("###get the files which match keys (remove the unmatched)\n")

	file.write("join -t$in_delimiter -1 $in_num_column -2 1 <(sort -t$in_delimiter -k$in_num_column file_2_tmp_key_cat.cmp) <(sort -t$in_delimiter -k1 cmp_match_key.cmp)|cut -f%s -d $in_delimiter> match_file_2_cct.cmp\n" % col_num)
	
	file.write("#############################################################################################################################################\n")
	
	file.write("###concatenate the columns\n")
	file.write("sed 's#%s##g' match_file_1_cct.cmp>file_1_tmp_column.cmp\n" % in_delimiter)


	file.write("##concatenate to original file\n")
	file.write("paste -d$in_delimiter match_file_1_cct.cmp file_1_tmp_column.cmp> file_1_tmp_col_cat.cmp\n")
	file.write("sed -i 's|9999||g' file_1_tmp_col_cat.cmp\n")

	file.write("#############################################################################################################################################\n")


	file.write("###concatenate the columns\n")
	file.write("sed 's#%s##g' match_file_2_cct.cmp>file_2_tmp_column.cmp\n" % in_delimiter)

	file.write("##concatenate to original file\n")
	file.write("paste -d$in_delimiter match_file_2_cct.cmp file_2_tmp_column.cmp> file_2_tmp_col_cat.cmp\n")
	file.write("sed -i 's|9999||g' file_2_tmp_col_cat.cmp\n")

	file.write("#############################################################################################################################################\n")
	file.write("###find differences in file based on column values\n")

	file.write("join -t$in_delimiter -1 %s -2 %s -v1 <(sort -t$in_delimiter -k%s file_1_tmp_col_cat.cmp) <(sort -t$in_delimiter -k%s file_2_tmp_col_cat.cmp)|cut -f2-%s -d $in_delimiter  > file_1_compare_diff.cmp\n" % (reduced_col_num, reduced_col_num,reduced_col_num,reduced_col_num,reduced_col_num))

	file.write("join -t$in_delimiter -1 %s -2 %s -v2 <(sort -t$in_delimiter -k%s file_1_tmp_col_cat.cmp) <(sort -t$in_delimiter -k%s file_2_tmp_col_cat.cmp)|cut -f2-%s -d $in_delimiter  > file_2_compare_diff.cmp\n" % (reduced_col_num, reduced_col_num,reduced_col_num,reduced_col_num,reduced_col_num))

	file.write("sed -i -e 's/^/file_1%s/' file_1_compare_diff.cmp\n" % in_delimiter)
	file.write("sed -i -e 's/^/file_2%s/' file_2_compare_diff.cmp\n" % in_delimiter)

	file.write("#############################################################################################################################################\n")

	file.write("cat file_1_compare_diff.cmp file_2_compare_diff.cmp| sort -t$in_delimiter -k2 >compare_output_diff.txt\n")

	file.close()

	    
def compare_summary():
#####################################################################################################################
#get the populate the file contents to a temp table
#####################################################################################################################

	#generate the comparison summary details
	file_1_tot_cmd = "cat %s|wc -l" % in_file_1
	file_2_tot_cmd = "cat %s|wc -l" % in_file_2
			
	status_1, file_1_total = commands.getstatusoutput(file_1_tot_cmd)
	status_2, file_2_total = commands.getstatusoutput(file_2_tot_cmd)
	
	################################################################################################################################
	
	file_1_diff_cmd = "cat file_1_compare_diff.cmp|wc -l" 
	file_2_diff_cmd = "cat file_2_compare_diff.cmp|wc -l" 
		
	status_1, file_1_diff = commands.getstatusoutput(file_1_diff_cmd)
	status_2, file_2_diff = commands.getstatusoutput(file_2_diff_cmd)
	
	################################################################################################################################
	
	file_1_unmatched_cmd = "cat unmatch_file_1_cct.cmp|wc -l" 
	file_2_unmatched_cmd = "cat unmatch_file_2_cct.cmp|wc -l" 
			
	status_1, file_1_unmatched = commands.getstatusoutput(file_1_unmatched_cmd)
	status_2, file_2_unmatched = commands.getstatusoutput(file_2_unmatched_cmd)
	
	################################################################################################################################
	file_1_equal = int(file_1_total) - (int(file_1_diff) + int(file_1_unmatched))
	file_2_equal = int(file_2_total) - (int(file_2_diff) + int(file_2_unmatched))
	
	summary_list = []
	
	summary_list.append(["Source", "Equal", "Difference" , "Unmatched" ,"Total"])	
	summary_list.append(["File 1",str(file_1_equal),str(file_1_diff),str(file_1_unmatched),str(file_1_total)]) 
	summary_list.append(["File 2",str(file_2_equal),str(file_2_diff),str(file_2_unmatched),str(file_2_total)])
	
	print "+" * 74

	for i in range(0,3):

		print "+" * 74
		print "++            ++            ++            ++            ++              ++"
		
		for j in range(0,5):
			summary_str = "++" + " " + summary_list[i][j]
			
			buff = 10 - len(summary_list[i][j])						
			print summary_str + " " * buff,
			
			
			
		print "\n++            ++            ++            ++            ++              ++"
		print "+" * 74
			
	print "+" * 74
	
	print "File 1: %s " % in_file_1
	print "File 2: %s " % in_file_2
	
def execute():
#####################################################################################################################
#The main execution function
#####################################################################################################################
	
	
	##start logging
	compare_log()
	
	os.system('clear')
	
	###Invoke the GUI
	gui()

	##beautify!!
	os.system('clear')
	formatter()
	print  "*" * 10 , " File comparison Initiated!!!" , "*" * 10 
	logging.info("File comparison Initiated!!!.................")
	
	compare_gen_script()
	
	cmp_cmd = "nohup bash compare.sh %s %s '%s' %s %s" % (in_file_1, in_file_2, in_delimiter, in_keys ,in_num_column)
	
	os.system(cmp_cmd)
		
	##Print the compare summary
	formatter()
	print  "*" * 37 , "Compare Summary!!!" , "*" * 43
	print "\n"
	compare_summary()
	
	##beautify!!
	print  "*" * 10 , " File comparison Complete!!!" , "*" * 10
	print "\n"
	
	logging.info("File comparison Complete.................")	        
        print "\nPlease refer the following files for the comparison results\n"
        print "\nDifference: compare_output_diff.txt\n"
        print "\nUnmatched : compare_output_unmatched.txt\n"
        print "\nCompare Summary: summary.txt\n"
        
        sys.stdout = open("summary.txt", "w")
	compare_summary()
	sys.stdout.close()
        
        os.system('rm *.cmp')        
        
        os.system("echo '\nPlease refer the following files for details:\n\n\nDifferences:  compare_output_diff.txt\nUnmatched:  compare_output_unmatched.txt'|mailx -s 'File Compare Report' -a summary.txt sriram.kumar@freddiemac.com")       
            

try:		
	execute()	
except:
	logging.exception("Oops:")
	
	
