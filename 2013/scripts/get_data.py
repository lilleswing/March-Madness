import DAO.godDAO
import re
import requests
#lines = open("index.php", 'r').readlines()
headers = {
    'User-agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Cookie': ''
}
point_map = {
    0: 0.0,
    1: 0.5,
    2: 0.5,
    3: 0.5,
    4: 0.5,
    5: 0.9,
    6: 0.9,
    7: 0.9,
    8: 0.9,
    9: 0.9,
    10: 1.3,
    11: 1.3,
    12: 1.3,
    13: 1.3,
    14: 1.3,
    15: 2,
}


def clean_name(name):
    return name.replace("&amp;", "&")


def get_team_data(team_list):
    rules = ["team.php\?team=(?P<date>.*?)\"", ", (?P<score>\d+?-\d+?)<"]
    for team in team_list:
        url = 'http://kenpom.com/' + team + '&y=2013'
        print url
        data = list()
        lines = requests.get(url, headers=headers).text.split('\n')
        for line in lines:
            for rule in rules:
                m = re.findall(rule, line)
                if len(m) != 0:
                    data.extend(m)
        if len(data) > 5:
            print data


def define_win_size(entries):
    for entry in entries:
        if entry[2] > 15:
            entry[2] = 2
        else:
            entry[2] = point_map[entry[2]]
    return entries


def game_extractor_2013(year, game):
    html = requests.get('http://kenpom.com/box.php?g=%s' % game, headers=headers).text
    m = re.search('<h2>.*?</span>(?P<team1>.*?)<span.*?</span>(?P<team2>.*?)<span.*?</h2>', html)
    g1 = m.group('team1').strip().strip(',').rsplit(' ', 1)
    g2 = m.group('team2').strip().strip(',').rsplit(' ', 1)
    return g1[0], g2[0], int(g1[1]), int(g2[1])


def game_extractor_pre_2013(year, game):
    html = requests.get('http://kenpom.com/wp2.php?g=%s&y=%s' % (game, year), headers=headers).text
    m = re.search('target="_parent">(?P<team1>.*?) (?P<score1>\d+), (?P<team2>.*?) (?P<score2>\d+)</a>', html)
    l = clean_name(m.group('team1')), clean_name(m.group('team2')), int(m.group('score1')), int(m.group('score2'))
    if l[2] == 0 and l[3] == 0:
        raise BaseException
    return l


def get_training_data(year, num_games=6000):
    entries = list()
    avg_points = dict()
    for i in xrange(1, num_games + 1):
        try:
            if year == 2013:
                team1, team2, score1, score2 = game_extractor_2013(year, i)
            else:
                team1, team2, score1, score2 = game_extractor_pre_2013(year, i)
            entries.append([team1, team2, score1 - score2])

            if team1 not in avg_points:
                avg_points[team1] = (0, 0, 0)
            if team2 not in avg_points:
                avg_points[team2] = (0, 0, 0)
            p1 = avg_points[team1]
            avg_points[team1] = (float(score1) + p1[0], float(score2) + p1[1], p1[2] + 1)

            p2 = avg_points[team2]
            avg_points[team2] = (float(score2) + p2[0], float(score1) + p2[1], p2[2] + 1)
            print "success"
        except:
            print "FAILURE"

    entries = define_win_size(entries)
    DAO.godDAO.add_games(year, entries)

    for g in avg_points.keys():
        t = avg_points[g]
        points_for = float(t[0]) / float(t[2])
        points_against = float(t[1]) / float(t[2])
        DAO.godDAO.add_avgpoints(year, [g, points_for, points_against])


def meanstdv(x):
    from math import sqrt

    n, mean, std = len(x), 0, 0
    for a in x:
        mean = mean + a
    mean /= float(n)
    for a in x:
        std += (a - mean) ** 2
    std = sqrt(std / float(n - 1))
    return mean, std


def get_mass_data():
    for year in [2010, 2011, 2012, 2013]:
    #for year in [2013]:
        #print year
        get_year_data(year)


def get_year_data(year):
    urls = ['http://kenpom.com/getdata.php?file=offense',
            'http://kenpom.com/getdata.php?file=defense',
            'http://kenpom.com/getdata.php?file=misc',
            'http://kenpom.com/getdata.php?file=summary']
    urls = map(lambda x: x + str(year)[2:], urls)
    data = dict()
    for url in urls:
        rows = requests.get(url, headers=headers).text.split('\n')
        for row in rows:
            row = row.split(',')
            if row[0] not in data:
                data[row[0]] = list()
            if url.count('summary') >= 1:
                data[row[0]].extend(["0"] + row[1:])
            else:
                data[row[0]].extend(row[1:])
    matrix_data = list()
    name_list = list()
    if 'TeamName' in data:
        del data['TeamName']
    for i in data.keys():
        data[i] = map(lambda x: float(x.strip("\"")), data[i][::2])
        print data[i]
        matrix_data.append(data[i])
        name_list.append(i)

    matrix_data = matrix_data[1:]
    name_list = name_list[1:]
    normalizers = list()
    for i in xrange(0, len(matrix_data[0])):
        curdata = map(lambda x: x[i], matrix_data)
        mean, std = meanstdv(curdata)
        normalizers.append([mean, std])
    for i in xrange(0, len(matrix_data[0])):
        for j in xrange(0, len(matrix_data)):
            matrix_data[j][i] = (matrix_data[j][i] - normalizers[i][0]) / normalizers[i][1]
    for i in xrange(0, len(name_list)):
        DAO.godDAO.add_team(year, name_list[i], matrix_data[i])
    return data


def get_team_names():
    lines = requests.get('http://kenpom.com').text.split('\n')
    names = list()
    for line in lines:
        m = re.search(r"team\.php\?.*?\"", line)
        if m:
            names.append(m.group(0)[0:-1])
    return names


if __name__ == '__main__':
    for i in xrange(2010, 2014):
        records = get_training_data(i, 6000)
    #data = get_mass_data()
