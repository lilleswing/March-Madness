import string

__author__ = 'karl_leswing'
from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure import TanhLayer
import helpers.make_bracket as make_bracket

team_dict = dict()
games = list()


def play_game(team1, team2):
    l = team1 + team2
    return tuple(l)


def get_training_data(games_path, teams_path):
    global games
    teams_list = open(teams_path).readlines()
    games = open(games_path).readlines()
    for team in teams_list:
        team = team.split(',')
        vals = map(float, team[1:])
        team_dict[team[0]] = vals
    ds = SupervisedDataSet(60, 1)
    count = 0
    for game in games:
        try:
            game = game.split(',')
            team1 = team_dict[game[0]]
            team2 = team_dict[game[1]]
            game1 = play_game(team1, team2)
            game2 = play_game(team2, team1)

            ds.addSample(game1, (float(game[2]),))
            ds.addSample(game2, (-1 * float(game[2]),))
        except:
            count += 1
            #print game
    print("%s games not added to training" % count)
    return ds


def play_tourney(bracket_file, net):
    bracket = map(string.strip, open(bracket_file).readlines())
    winners = list()
    while len(bracket) > 1:
        team1 = bracket.pop(0)
        team2 = bracket.pop(0)
        game1 = play_game(team_dict[team1], team_dict[team2])
        game2 = play_game(team_dict[team2], team_dict[team1])
        i1 = net.activate(game1)[0]
        i2 = net.activate(game2)[0]
        i = i1 - i2
        if i > 0:
            bracket.append(team1)
            winners.append(team1)
        else:
            bracket.append(team2)
            winners.append(team2)
    return winners


def get_games_won(net):
    correct = 0
    unplayable = 0
    for game in games:
        try:
            game = game.split(',')
            team1 = team_dict[game[0]]
            team2 = team_dict[game[1]]
            game1 = play_game(team1, team2)
            game2 = play_game(team2, team1)
            i1 = net.activate(game1)[0]
            i2 = net.activate(game2)[0]
            i = i1 - i2
            if i > 0:
                correct += 1
        except:
            unplayable += 1
    return correct, len(games) - unplayable, float(correct) / float(len(games) - unplayable)

if __name__ == '__main__':
    net = buildNetwork(60, 100, 100, 1, hiddenclass=TanhLayer, bias=True)
    ds = get_training_data('../data/training.txt', '../data/data.txt')
    trainer = BackpropTrainer(net, ds)
    print "starting training"
    iteration = 0
    min_error = 1
    winners = list(['Virginia'] * 63)
    while True:
        error = trainer.train()
        if error < min_error:
            min_error = error
            print error
            winners = play_tourney('../data/bracket2012.txt', net)
            print get_games_won(net)
        make_bracket.make_bracket(winners, "../data/images/time-series/%04d.png" % iteration)
        iteration += 1


