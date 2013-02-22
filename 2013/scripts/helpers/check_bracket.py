import string

__author__ = 'karl_leswing'
data_dir = '../../data'


def check_bracket(teams_path, bracket_path):
    teams_list = open(teams_path).readlines()
    bracket = open(bracket_path).readlines()
    team_dict = dict()
    for team in teams_list:
        team = team.split(',')
        vals = map(float, team[1:])
        team_dict[team[0]] = vals
    bracket = map(string.strip, bracket)
    for team_name in bracket:
        if team_name not in team_dict:
            print team_name


if __name__ == '__main__':
    check_bracket(data_dir + '/data.txt', data_dir + '/bracketkenpom.txt')
