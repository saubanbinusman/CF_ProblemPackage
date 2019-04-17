#!/bin/python

import os
import csv
import sys
import random
import shutil
import zipfile
import requests

from bs4 import BeautifulSoup

def retrieve_file_paths(dirName):
	filePaths = []
	
	for root, directories, files in os.walk(dirName):
		for filename in files:
			filePath = os.path.join(root, filename)
			filePaths.append(filePath)
	
	return filePaths

with open("input.csv", "r") as input_csv:
	csv_reader = csv.reader(input_csv, delimiter=',')
	line_count = 0
	
	for row in csv_reader:
		if (line_count == 0):
			line_count += 1
		else:
			print(row[0] + " " + row[1] + " " + row[2], end=" --- ")
			
			dir_main = "temp"
			os.makedirs(dir_main, exist_ok=True)
			
			problem_id = row[0] + "_" + row[1]
			problem_name = row[3]
			time = row[4]
			
			problem_desc = "probid = \"{}\"\nname = \"{}\"\nallow_submit = 1\nallow_judge = 1\ntimelimit = {}\ncolor = {}"
			
			r = lambda: random.randint(0,255)
			color = "#{:02x}{:02x}{:02x}".format(random.randint(0,255), random.randint(0,255), random.randint(0,255))
			
			problem_desc = problem_desc.format(problem_id, problem_name, time, color)
			
			with open(dir_main + "/domjudge-problem.ini", "w") as descFile:
				descFile.write(problem_desc)
			
			dir_tests = dir_main + "/data/secret"
			os.makedirs(dir_tests, exist_ok=True)
			
			dir_sol = dir_main + "/submissions/accepted"
			os.makedirs(dir_sol, exist_ok=True)
			
			soup = BeautifulSoup(requests.get(row[2]).text, "html.parser")
			
			with open(dir_sol + "/sol.cpp", "w") as codeFile:
				codeFile.write(soup.find_all("pre", {"id": "program-source-text"})[0].contents[0])
			
			ins = [a.find_all("div", "text") for a in soup.find_all("div", "file input-view")]
			outs = [a.find_all("div", "text") for a in soup.find_all("div", "file output-view")]
			
			assert(len(ins) == len(outs))
			
			i = 1
			
			for a, b in zip(ins, outs):
				with open(dir_tests + "/" + repr(i) + ".in", "w") as inFile:
					inFile.write(a[0].pre.contents[0])
				
				with open(dir_tests + "/" + repr(i) + ".ans", "w") as outFile:
					outFile.write(b[0].pre.contents[0])
				
				i = i + 1
			
			print("Fetched " + str(len(ins)) + " TCs. Zipping ...")
			
			files_to_zip = retrieve_file_paths(dir_main);
			
			with zipfile.ZipFile(problem_id + ".zip", "w") as zip_file:
				for file in files_to_zip:
					zip_file.write(file, file.replace(dir_main, ""))
			
			shutil.rmtree(dir_main)