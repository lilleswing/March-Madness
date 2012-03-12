#zips stats from 4 different csv files into a single unified csv file
import sys
import re
import os

def UpdateTeamStats(TeamStats, data_type, year):
	
os.chdir(sys.argv[1])
files = os.listdir(sys.argv[1])

TeamStats = dict()
for fp in files:
	lines = open(fp,'r').readlines()
	data_type = re.findall("(?P<dtype>\w+)_",fp)[0]
	year = re.findall("(?P<year>\d\d\d\d)\.csv",fp)[0]
	#print "%s,%s" % (data_type, year)
	TeamStats = UpdateTeamStats(TeamStats, data_type, year)
