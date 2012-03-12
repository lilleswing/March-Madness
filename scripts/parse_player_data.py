import os
import sys
import re

def SaveToFile(data):
	filename = "%s%s" % ("../player_csv/",data[0][0])
	strdata = []
	#print data
	for i in xrange(2,len(data),2):
		temp = data[i][0]
		for j in data[i+1]:
			temp = "%s,%s" % (temp,j)
		strdata.append(temp)
	f = open(filename,'w')
	for line in strdata:
		f.write("%s\n" % line)
	f.close()

def ParsePlayerHTML(lines):
	rules = [">(?P<stat>\d*?\.\d*?)<","Advanced stats profile for (?P<name>.*?)<", "comps-player\"><td>(?P<year>\d*?)<"]
	data = []
	for line in lines:
		for rule in rules:
			#print rule
			m = re.findall(rule,line)
			if(len(m) != 0):
				data.append(m)
	if(len(data) != 0):
		SaveToFile(data)


os.chdir(sys.argv[1])
playerHTMLS = os.listdir(sys.argv[1])

for playerHTML in playerHTMLS:
	lines = open(playerHTML,'r').readlines()
	if(len(lines) != 126):
		ParsePlayerHTML(lines)
