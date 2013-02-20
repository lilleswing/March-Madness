#zips stats from 4 different csv files into a single unified csv file
import sys
import re
import os

def UpdateTeamStats(TeamStats, data, data_type, year):
	for line in data:
		line = line.strip()
		row = re.split(",", line)
		team = "%s_%s" % (row[0], year)
		print team
		if(team not in TeamStats):
			TeamStats[team] = dict()
		TeamStats[team][data_type] = row[1:]
	return TeamStats
os.chdir(sys.argv[1])
files = os.listdir(sys.argv[1])

TeamStats = dict()
years = dict()
for fp in files:
	lines = open(fp,'r').readlines()
	data_type = re.findall("(?P<dtype>\w+)_",fp)[0]
	year = re.findall("_(?P<year>\d\d\d\d)\.csv",fp)[0]
	#print "%s,%s" % (data_type, year)
	TeamStats = UpdateTeamStats(TeamStats, lines, data_type, year)

for team in TeamStats.iterkeys():
	teamName = re.split("_", team)[0]
	teamYear = re.split("_", team)[1]
	if(teamYear not in years):
		years[teamYear] = list()
	data = list()
	data.extend(TeamStats[team]['stats'])
	data.extend(TeamStats[team]['teamstats'])
	data.extend(TeamStats[team]['height'])
	datastr = teamName
	for datum in data:
		datastr = "%s,%s" % (datastr, datum)
	years[teamYear].append(datastr)

for year in years.iterkeys():
	fp = open("../%s.csv" % year,'w')
	data = years[year]
	for line in data:
		fp.write("%s\n" % line)
	fp.close()
