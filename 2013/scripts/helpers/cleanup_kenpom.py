import string

data_dir = '../../data'


def cleanup_kenpom(filename):
    w = open(data_dir + '/' + filename).readlines()

    w = map(lambda x: x.split("\t")[1], w)
    for line in w:
        print line


def place_in_bracket_order(filename):
    order = [1, 16, 9, 8, 5, 12, 13, 4, 3, 14, 6, 11, 7, 10, 2, 15]
    order = map(lambda x: x - 1, order)

    rankings = map(string.strip, open(data_dir + '/' + filename).readlines())
    for i in xrange(0, 4):
        for index in order:
            print rankings[i + index * 4]


if __name__ == '__main__':
    i = 1
    #cleanup_kenpom('kenpomrankings.txt')
    #place_in_bracket_order('kenpomrankings.txt')
