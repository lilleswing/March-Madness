import re

lines = open("index.php", 'r').readlines()
#team.php?

for line in lines:
	m = re.search(r"team\.php\?.*?\"", line)
	if(m):
		print m.group(0)[0:-1]
#print len(teams)
#print teams
