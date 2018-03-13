import deepchem as dc
import numpy as np
import pickle
import json
import os
import re

keywords = [
    'RankAdjOE',
    'RankAdjDE',
    'RankAdjTempo',
    'RankAPL_Off',
    'RankAPL_Def',
    'RankeFG_Pct',
    'RankDeFG_Pct',
    'RankTO_Pct',
    'RankDTO_Pct',
    'RankOR_Pct',
    'RankDOR_Pct',
    'RankFT_Rate',
    'RankDFT_Rate',
    'RankDFT_Rate',
    'RankFG3Pct',
    'RankFG3Pct&od=d',
    'RankFG2Pct',
    'RankFG2Pct&od=d',
    'RankFTPct',
    'RankFTPct&od=d',
    'RankBlockPct',
    'RankBlockPct&od=d',
    'RankStlRate',
    'RankStlRate&od=d',
    'RankF3GRate',
    'RankF3GRate&od=d',
    'RankARate',
    'RankARate&od=d',
    'RankOff_3',
    'RankDef_3',
    'RankOff_2',
    'RankDef_2',
    'RankOff_1',
    'RankDef_1',
    'RankSOSO',
    'RankSOSD',
    'ExpRank',
    'SizeRank',
]

def get_feature_vector(html_str):
    fv = []
    for keyword in keywords:
        pattern = '%s.*>(\d+\.\d+)' % keyword
        val = re.findall(pattern, html_str)[-1]
        fv.append(float(val))
    return fv

def score_to_diff(s, neg=False):
    s = [float(x) for x in s.split('-')]
    v = abs(s[0] - s[1])
    if neg:
        return -1 * v
    return v

def get_wins_losses(html_str):
    pat = 'team.php.*?=(.*?)".*>W<.* (\d+-\d+).*\n'
    wins = re.findall(pat, html_str)
    wins = [(x[0], score_to_diff(x[1])) for x in wins]

    pat = 'team.php.*?=(.*?)".*>L<.* (\d+-\d+).*\n'
    losses = re.findall(pat, html_str)
    losses = [(x[0], score_to_diff(x[1], True)) for x in losses]
    return wins + losses

def parse_html_file(html_str):
    """
    return feature_vector, list of (oppenent, +- score)
    """
    fv = get_feature_vector(html_str)
    wl = get_wins_losses(html_str)
    return fv, wl

def get_team_dict():
    html_files = os.listdir('raw_data')
    html_files = list(filter(lambda x: x.find('2017') == -1, html_files))
    d = {}
    for html_file in html_files:
        html_str = open('raw_data/%s' % html_file).read()
        team_name = html_file[:-5]
        d[team_name] = parse_html_file(html_str)
    return d

def get_transformers():
    transformers = pickle.load(open('transformers.pkl', 'rb'))
    return transformers

def play_game(t1, t2, team_dict, keys=['27_all_data']):
    fv1 = team_dict[t1][0]
    fv2 = team_dict[t2][0]
    g1 = fv1 + fv2
    g2 = fv2 + fv1
    ds = dc.data.NumpyDataset(np.array([g1,g2]))
    for trans in get_transformers():
        ds = trans.transform(ds)
    y_pred = max_min_ensemble(predict(keys, ds))[:,0]
    final_score = y_pred[0] + -1 * y_pred[1]
    print(final_score)
    if final_score > 0:
        return t1, abs(final_score)
    return t2, abs(final_score)

def play_tourney(bracket):
    team_dict = get_team_dict()
    teams_left = bracket
    all_winners, all_scores = list(), list()
    while len(teams_left) > 1:
        print(len(teams_left))
        winners = []
        scores = []
        for i in range(0, len(teams_left), 2):
            t1, t2 = teams_left[i], teams_left[i+1]
            winner, score = play_game(t1, t2, team_dict)
            winners.append(winner)
            scores.append(score)
        teams_left = winners
        all_winners.append(winners)
        all_scores.append(scores)
    return all_winners, all_scores

def predict(keys, ds):
    retval = None
    for key in keys:
        for fold in range(5):
            model_dir = 'models/%s/%s' % (key, fold)
            model = dc.models.TensorGraph.load_from_dir(model_dir)
            y_pred = model.predict(ds)
            y_pred = np.reshape(y_pred, newshape=(y_pred.shape[0], 1))
            if retval is None:
                retval = y_pred
            else:
                retval = np.concatenate([retval, y_pred], axis=1)
    return retval

def max_min_ensemble(y_pred):
  results = []
  for row in range(y_pred.shape[0]):
    r_dat = y_pred[row, :].tolist()
    r_dat.remove(max(r_dat))
    r_dat.remove(min(r_dat))
    mean = np.mean(r_dat)
    std = np.std(r_dat)
    results.append((mean, std))
  return np.array(results)

def get_bracket(year=208):
    bracket = [
        'Virginia',
        'UMBC',
        'Creighton',
        'Kansas+St.',
        'Kentucky',
        'Davidson',
        'Arizona',
        'Buffalo',
        'Miami+FL',
        "Loyola+Chicago",
        'Tennessee',
        'Wright+St.',
        'Nevada',
        'Texas',
        'Cincinnati',
        'Georgia+St.',

        'Xavier',
        'Texas+Southern',
        'Missouri',
        'Florida+St.',
        'Ohio+St.',
        'South+Dakota+St.',
        'Gonzaga',
        'UNC+Greensboro',
        'Houston',
        'San+Diego+St.',
        'Michigan',
        'Montana',
        'Texas+A%26M',
        'Providence',
        'North+Carolina',
        'Lipscomb',

        'Villanova',
        'Radford',
        'Virginia+Tech',
        'Alabama',
        'West+Virginia',
        'Murray+St.',
        'Wichita+St.',
        'Marshall',
        'Florida',
        'UCLA',
        'Texas+Tech',
        'Stephen+F.+Austin',
        'Arkansas',
        'Butler',
        'Purdue',
        'Cal+St.+Fullerton',

        'Kansas',
        'Penn',
        'Seton+Hall',
        'North+Carolina+St.',
        'Clemson',
        'New+Mexico+St.',
        'Auburn',
        'College+of+Charleston',
        'TCU',
        'Arizona+St.',
        'Michigan+St.',
        'Bucknell',
        'Rhode+Island',
        'Oklahoma',
        'Duke',
        'Iona'
    ]
    return bracket

def run_full_bracket():
    bracket = get_bracket()
    all_winners, all_scores = play_tourney(bracket)
    print(all_winners)
    print(all_scores)
    with open('2018_final_winners.json', 'w') as fout:
        s = json.dumps(all_winners)
        fout.write(s)
    with open('2018_final_scores.json', 'w') as fout:
        s = json.dumps(all_scores)
        fout.write(s)

def play_one_game(t1, t2):
    team_dict = get_team_dict()
    retval = play_game(t1, t2, team_dict)
    return retval[0], retval[1] * 16.0


if __name__ == "__main__":
    #run_full_bracket()
    #print(play_one_game('Virginia', 'Arizona'))
    #print(play_one_game('Virginia', 'Kentucky'))
    #print(play_one_game('Duke', 'Michigan+St.'))
    #print(play_one_game('Duke', 'Kansas'))
    print(play_one_game('Radford', 'LIU+Brooklyn'))
    print(play_one_game('Arizona+St.', 'Syracuse'))
    print(play_one_game('St.+Bonaventure', 'UCLA'))
    print(play_one_game('North+Carolina+Central', 'Texas+Southern'))


