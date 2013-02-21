import string

__author__ = 'karl_leswing'
from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure import TanhLayer
import make_bracket

team_dict = dict()

def play_game(team1, team2):
    l = [i1 - i2 for i1, i2 in zip(team1, team2)]
    return tuple(l)


def get_training_data(games_path, teams_path):
    teams_list = open(teams_path).readlines()
    games = open(games_path).readlines()
    for team in teams_list:
        team = team.split(',')
        vals = map(float, team[1:])
        team_dict[team[0]] = vals
    ds = SupervisedDataSet(30, 1)
    count = 0
    for game in games:
        try:
            game = game.split(',')
            team1 = team_dict[game[0]]
            team2 = team_dict[game[1]]
            game1 = play_game(team1, team2)
            game2 = play_game(team2, team1)

            ds.addSample(game1, (1,))
            ds.addSample(game2, (-1,))
        except:
            count += 1
            #print game
    print("%s games not added to training" % count)
    return ds


def play_tourney(bracket_file, iteration, net):
    bracket = map(string.strip, open(bracket_file).readlines())
    winners = list()
    while len(bracket) > 1:
        team1 = bracket.pop(0)
        team2 = bracket.pop(0)
        game = play_game(team_dict[team1], team_dict[team2])
        i = net.activate(game)[0]
        if i > 0:
            bracket.append(team1)
            winners.append(team1)
        else:
            bracket.append(team2)
            winners.append(team2)
    make_bracket.make_bracket(winners, "../data/images/time-series/%s.png" % (iteration))

if __name__ == '__main__':
    net = buildNetwork(30, 50, 1, hiddenclass=TanhLayer, bias=True)
    ds = get_training_data('../data/training.txt', '../data/data.txt')
    trainer = BackpropTrainer(net, ds)
    print "starting training"
    iteration = 0
    while True:
        play_tourney('../data/bracket2012.txt', iteration, net)
        print(trainer.train())
        iteration += 1


