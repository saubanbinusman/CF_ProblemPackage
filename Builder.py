#!/bin/python

import os
import csv
import sys
import json
import random
import shutil
import zipfile
import requests

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

			submission_id = row[2][row[2].rindex("/") + 1:]

			session_id = "314BCC085FA3A5660ED6C598FA518048-n1"  # Change with your JSESSIONID cookie
			csrf_token = "b419345ea7f5e2f3d7037660abe69bfb"  # Change with your csrf token

			submission_api = "https://codeforces.com/data/submitSource"
			web_header = {
				"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0",
				"accept": "*/*",
				"Cookie":  "JSESSIONID=" + session_id,
				"X-Csrf-Token": csrf_token
			}

			submission_data = requests.post(submission_api, data={ "submissionId": submission_id }, headers=web_header).json()

			test_count = int(submission_data["testCount"])

			ins  = [s.replace("\r", "") for s in [submission_data["input#"  + str(i)] for i in range(1, test_count + 1)]]
			outs = [s.replace("\r", "") for s in [submission_data["answer#" + str(i)] for i in range(1, test_count + 1)]]

			i = 1
			
			for a, b in zip(ins, outs):
				with open(dir_tests + "/" + repr(i) + ".in", "w") as inFile:
					inFile.write(a)
				
				with open(dir_tests + "/" + repr(i) + ".ans", "w") as outFile:
					outFile.write(b)
				
				i = i + 1
			
			print("Fetched " + str(test_count) + " TCs. Zipping ...")
			
			files_to_zip = retrieve_file_paths(dir_main)
			
			with zipfile.ZipFile(problem_id + ".zip", "w") as zip_file:
				for file in files_to_zip:
					zip_file.write(file, file.replace(dir_main, ""))
			
			shutil.rmtree(dir_main)