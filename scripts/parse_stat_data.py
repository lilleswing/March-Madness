import sys
import os
import re
#arguments to call this file --
#folder containing the files
#number of columns associated with each team
#type of data being saved
def SaveToFile(data, num_col, year,data_type):
	#print data
	filename = "%s%s_%s.csv" % ("../../stat_csv/broken",data_type,year)
	i = 0
	f = open(filename,'w')
	while(i < len(data)):
		row = data[i]
		for j in xrange(0,num_col):
			i += 1
			row = "%s,%s" % (row, data[i])
		i += 1
		#print row
		f.write("%s\n" % row)
	
	f.close()

def ParseTeamHTML(html):
	rules = ["divide\">(?P<stat>\d*?\.\d+)<",
		 "divide\">(?P<stat>[\+-]\d*?\.\d+)<",
		 "<td>(?P<stat>\d+\.\d)</td>",
		 "<td class=\"bold-bottom\">(?P<stat>\d+\.\d)</td>",
		 "team.php\?team=.+?\">(?P<team_name>.+?)<"]
	i = 0
	data = []
	#print len(html)
	while(i < len(html)):
		line = html[i]
		for rule in rules:
			#print rule
			m = re.findall(rule,line)
			if(len(m) != 0):
				data.extend(m)
			
		i += 1
	return data


os.chdir(sys.argv[1])
statHTMLS = os.listdir(sys.argv[1])

for statHTML in statHTMLS:
	lines = open(statHTML,'r').readlines()
	year = re.findall("y=(?P<year>\d+)",statHTML)[0]
	data = ParseTeamHTML(lines)
	SaveToFile(data,int(sys.argv[2]),year,sys.argv[3])
