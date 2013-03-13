__author__ = 'karl_leswing'

import re

data = open('2010_data.html').read()
m = re.search('target="_parent">(?P<team1>.*?) (?P<score1>\d+), (?P<team2>.*?) (?P<score2>\d+)</a>', data)
print m
print m.group('team1')
print m.group('team2')
print m.group('score1')
print m.group('score2')
