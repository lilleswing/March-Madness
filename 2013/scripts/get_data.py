import re
import requests
#lines = open("index.php", 'r').readlines()
headers = {
    'User-agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Cookie': 'PHPSESSID=teiiglehj473eom37bk1b501h6; exp_last_visit=1045926002; exp_last_activity=1361286002; exp_tracker=a%3A1%3A%7Bi%3A0%3Bs%3A5%3A%22index%22%3B%7D; __utma=8968239.1643745358.1361247091.1361284235.1361288720.3; __utmb=8968239.11.10.1361288720; __utmc=8968239; __utmz=8968239.1361247091.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'
}


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


def get_training_data(num_games=6000):
    fout = open('../data/training.txt', 'w')
    for i in xrange(1, num_games + 1):
        try:
            html = requests.get('http://kenpom.com/box.php?g=%s' % i, headers=headers).text
            m = re.search('<h2>.*?</span>(?P<team1>.*?)<span.*?</span>(?P<team2>.*?)<span.*?</h2>', html)
            g1 = m.group('team1').strip().strip(',').rsplit(' ', 1)
            g2 = m.group('team2').strip().strip(',').rsplit(' ', 1)
            fout.write("%s,%s,%s\n" % (g1[0], g2[0], int(g1[1]) - int(g2[1])))
        except:
            print "FAILURE"
    fout.close()


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
    urls = ['http://kenpom.com/getdata.php?file=offense13',
            'http://kenpom.com/getdata.php?file=defense13',
            'http://kenpom.com/getdata.php?file=misc13',
            'http://kenpom.com/getdata.php?file=summary13']
    data = dict()
    for url in urls:
        rows = requests.get(url, headers=headers).text.split('\n')
        for row in rows:
            row = row.split(',')
            if row[0] not in data:
                data[row[0]] = list()
            data[row[0]].extend(row[1:])
    matrix_data = list()
    name_list = list()
    for i in data.keys():
        data[i] = map(float, data[i][::2])
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
    fout = open('../data/data.txt', 'w')
    for i in xrange(0, len(name_list)):
        fout.write("%s,%s\n" % (name_list[i], ",".join(map(lambda x: str(x), matrix_data[i]))))
    fout.close()
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
    records = get_training_data(4450)
    data = get_mass_data()
