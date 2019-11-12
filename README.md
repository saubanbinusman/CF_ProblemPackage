# CF_ProblemPackage

Create a file named input.csv in the same directory (example file included in the repository) and run the script. The script will download test cases and sample solution for all the problems in the file and prepare them for direct upload as a problem package onto DOMJudge (based on Kattis Problem Package format).

It's very quick and dirty and there's an issue with this script. It parses the submission page of a solution and collects test data, but codeforces does not render test data which exceeds 500 characters. You might want to keep an eye for problems like that.

## Known Limitations
- Only C++ submissions are currently supported. Submissions in other languages will be saved with .cpp extension in the Problem Package File.