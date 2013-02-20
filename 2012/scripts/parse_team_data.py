import sys
import os
import re

def SaveToFile(data):
	#print data
	filename = "%s%s_%s.csv" % ("../team_csv/",data[1],data[0])
	#print filename
	strdata = data[0]
	#print data
	for i in xrange(1,len(data)):
		strdata = "%s,%s" % (strdata, data[i])
	f = open(filename,'w')
	f.write("%s\n" % strdata)
	f.close()

def ParseTeamHTML(html):
	rules = ["<TITLE>(?P<year>\d\d\d\d)", "Head coach:.*?>(?P<name>\w+ \w+)<", "Mostly Man","Inconclusive","Some Zone","Mostly Zone", "fanmatch.php\?=(?P<date>.*?)\"", ", (?P<score>\d+?-\d+?)<", "Home", "Away", "Neutral", "scouting report for (?P<name>.+?)<", "winprob\.php\?g=\d+?\"><b>(?P<result>\w+)<"]
	i = 0
	data = []
	#print len(html)
	while(i < len(html)):
		line = html[i]
		for rule in rules:
			m = re.findall(rule,line)
			if(len(m) != 0):
				data.extend(m)
			
		i += 1
	if(len(data) > 5):
		SaveToFile(data)


os.chdir(sys.argv[1])
teamHTMLS = os.listdir(sys.argv[1])

for teamHTML in teamHTMLS:
	lines = open(teamHTML,'r').readlines()
	ParseTeamHTML(lines)
