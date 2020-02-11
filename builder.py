# Import OS modules
import os
from sys import platform
import re
import csv
import sys
import json
import time
import random
import shutil
import zipfile
import requests

class CFService:
	submission_api = "https://codeforces.com/data/submitSource"

	def __init__(self):
		self.session = requests.Session()

		self.headers = {
			"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0",
		}

		# Open codeforces main page to get a JSESSIONID cookie and csrf_token from the html
		response = self.session.get("https://codeforces.com/", headers=self.headers).text
		self.csrf_token = re.search("<meta name=\"X-Csrf-Token\" content=\"([^\"]+)\"\/>", response).groups()[0]


	def get_submission(self, submission_id):
		time.sleep(0.5)  # To avoid flooding the server with requests (in case of long CSV files)

		response = self.session.post(self.submission_api, data={ "submissionId": submission_id, "csrf_token": self.csrf_token }, headers=self.headers).json()

		ac_source = response["source"]  # The source code of the submission

		test_count = int(response["testCount"])  # Total number of test cases

		test_inputs  = [s.replace("\r", "") for s in [response["input#"  + str(i)] for i in range(1, test_count + 1)]]
		test_answers = [s.replace("\r", "") for s in [response["answer#" + str(i)] for i in range(1, test_count + 1)]]

		return ac_source, test_inputs, test_answers


def retrieve_file_paths(dir_name):
	file_paths = []
	
	for root, directories, files in os.walk(dir_name):
		for filename in files:
			file_path = os.path.join(root, filename)
			file_paths.append(file_path)
	
	return file_paths

def main():
	cf_service = CFService()

	with open("input.csv", "r") as input_csv:
		csv_reader = csv.reader(input_csv)

		next(csv_reader)  # Ignore CSV headers line
		
		for row in csv_reader:
			problem_id     = row[0] + "_" + row[1]
			submission_url = row[2]
			submission_id  = submission_url[submission_url.rindex("/") + 1:]
			problem_name   = row[3]
			time_limit     = row[4]

			print(F"- {problem_id} {submission_url}")
			
			# Create a temporary directory to store Problem Package Structure
			dir_top_level = "temp"
			os.makedirs(dir_top_level, exist_ok=True)
			
			# Generate a random color '#xxxxxx' for Problem
			r = lambda: random.randint(0,255)
			color = "#{:02x}{:02x}{:02x}".format(random.randint(0,255), random.randint(0,255), random.randint(0,255))
			
			# Write Problem Description file
			problem_desc = {
				"probid": '"' + problem_id + '"',
				"name"  : '"' + problem_name + '"',
				"allow_judge": 1,
				"allow_submit": 1,
				"timelimit": time_limit,
				"color": color
			}

			with open(F"{dir_top_level}/domjudge-problem.ini", "w") as desc_file:
				for k, v in problem_desc.items():
					desc_file.write(F"{k} = {v}\n")
			
			print( "\t-- Written domjudge-problem.ini")
			
			# Create Directory for Test Cases
			dir_tests = F"{dir_top_level}/data/secret"
			os.makedirs(dir_tests, exist_ok=True)
			
			# Create Directory for AC Solution (not required, but helpful in testing)
			dir_sol = F"{dir_top_level}/submissions/accepted"
			os.makedirs(dir_sol, exist_ok=True)

			# Fetch submission data from Codeforces
			ac_source, inputs, answers = cf_service.get_submission(submission_id)
			print( "\t-- Fetched Submission Details")

			# Write AC Solution to file
			with open(dir_sol + "/sol.cpp", "w") as sol_file:
				sol_file.write(ac_source)
			
			print( "\t-- Written sol.cpp")

			written_count = 0

			# Write Test Cases to files
			for tc, inp, ans in zip(range(1, len(inputs) + 1), inputs, answers):
				with open(F"{dir_tests}/{tc}.in", "w") as inp_file, open(F"{dir_tests}/{tc}.ans", "w") as ans_file:
					# Only Write Test Case to file if it's not truncated					truncate_length = 400
					truncate_length = 400
					truncated = (len(inp) > truncate_length and inp[-3:] == "...") or (len(ans) > truncate_length and ans[-3:] == "...")
					
					if truncated:
						print(F"\t-- WARNING: Test Case # {tc} is truncated")
					
					else:
						inp_file.write(inp)
						ans_file.write(ans)
						written_count += 1
			
			print(F"\t-- Written {written_count}/{len(inputs)} Test Cases ({len(inputs) - written_count} were Truncated, thus not written)")

			# Enlist file paths to be zipped
			files_to_zip = retrieve_file_paths(dir_top_level)
			
			# Create directory to store the resulting zip files in
			dir_path = "./Problems"

			if not os.path.exists(dir_path):
				print( "Creating folder")
				os.mkdir(dir_path)
	
			problem_id = dir_path + "/" + problem_id

			# Zip files into a problem package
			with zipfile.ZipFile(problem_id + ".zip", "w") as zip_file:
				for file in files_to_zip:
					zip_file.write(file, file.replace(dir_top_level, ""))
			
			print(F"\t-- Zipped {problem_id}.zip")
			
			# Remove temporary directory
			shutil.rmtree(dir_top_level)

			print( "\t-- Cleaned Temporary Files")

			print( "\n\tProblem Package Created\n")

	if platform == 'linux' or platform == 'linux2':
		from os import listdir
		files = [ f for f in listdir('./Problems/')]
		for file in files:
			os.chmod('./Problems/' + file, 0o777)

if __name__ == "__main__":
	main()
