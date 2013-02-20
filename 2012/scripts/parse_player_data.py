import os
import sys
import re
def CleanUpHeight(data):
	i = 0
	indexes = list()
	while(i < len(data)):
		if(re.match("20\d\d",data[i])):
			indexes.append(i)
		i += 1
	cleandata = list()
	for i in xrange(1,len(indexes)):
		cleandata.append(data[indexes[i-1]:indexes[i]])
	cleandata.append(data[indexes[-1]:])
	#print cleandata
	for year in xrange(0,len(cleandata)):
		yeardata = cleandata[year]
		if(len(yeardata)%22 != 0):
			happyear = yeardata[0]
			padded = [happyear,0,0,0]
			padded.extend(yeardata[1:])
			#print padded
			cleandata[year] = padded
	for year in xrange(0,len(cleandata)):
		yeardata = cleandata[year]
		tstr = yeardata[0]
		for i in xrange(1,len(yeardata)):
			tstr = "%s,%s" % (tstr,yeardata[i])
		cleandata[year] = tstr
	return cleandata

				
def SaveToFile(data):
	filename = "%s%s" % ("../player_csv/",data[0])
	data = data[2:]
	data = CleanUpHeight(data)
	f = open(filename,'w')
	for line in data:
		f.write("%s\n" % line)
	f.close()

def ParsePlayerHTML(lines):
	rules = [">(?P<stat>\d*?\.\d*?)<","Advanced stats profile for (?P<name>.*?)<", "comps-player\"><td>(?P<year>\d*?)<","<td>(?P<Height>\d+-\d+)</td>","<td>(?P<Weight>\d\d\d)</td>","<td>(?P<experience>Fr|So|Jr|Sr)</td>"]
	data = []
	for line in lines:
		for rule in rules:
			#print rule
			m = re.findall(rule,line)
			if(len(m) != 0):
				data.extend(m)
	if(len(data) != 0):
		SaveToFile(data)


os.chdir(sys.argv[1])
playerHTMLS = os.listdir(sys.argv[1])

for playerHTML in playerHTMLS:
	lines = open(playerHTML,'r').readlines()
	if(len(lines) != 126):
		ParsePlayerHTML(lines)
