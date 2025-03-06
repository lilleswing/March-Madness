import json
import re
from collections import defaultdict
import random
import sys

import pandas as pd


def play_first_four(first_four, probs):
    return play_round(first_four, probs)


def template_bracket(top64, first_four_winners):
    top64 = list(top64)
    d = {f"_t{i}": x for i, x in enumerate(first_four_winners)}
    for i in range(len(top64)):
        if top64[i] in d:
            top64[i] = d[top64[i]]
    return top64


def play_round(teams, probs):
    results = []
    for i in range(0, len(teams), 2):
        t1, t2 = teams[i], teams[i + 1]
        l = [t1, t2]
        random.shuffle(l)
        t1, t2 = l

        key = f"{t1}:{t2}"
        if key not in probs:
            raise ValueError(f"{key} not in lookup")
        win_prob = probs[key]
        r = random.random()
        if r >= win_prob:
            results.append(t2)
        else:
            results.append(t1)
    return results


def play_round_deterministic(teams, lookup):
    results = []
    for i in range(0, len(teams), 2):
        t1, t2 = teams[i], teams[i + 1]
        key = f"{t1}:{t2}"
        if key not in lookup:
            raise ValueError(f"{key} not in lookup")
        points = lookup[key]
        if points > 0:
            results.append(t1)
        else:
            results.append(t2)
    return results


def play_tourney(bracket, probs):
    first_four = bracket['first_four']
    if len(first_four) > 0:
        first_four_winners = play_first_four(first_four, probs)
        top_64 = template_bracket(bracket['tourney'], first_four_winners)
    else:
        top_64 = bracket['tourney']
    top_32 = play_round(top_64, probs)
    top_16 = play_round(top_32, probs)
    top_8 = play_round(top_16, probs)
    top_4 = play_round(top_8, probs)
    top_2 = play_round(top_4, probs)
    top_1 = play_round(top_2, probs)

    return [top_32, top_16, top_8, top_4, top_2, top_1]


def create_probability_table(bracket_file, prob_file):
    year = re.match(".*(\d\d\d\d)\.json", bracket_file).groups(0)[0]

    bracket = json.loads(open(bracket_file).read())
    probs = json.loads(open(prob_file).read())

    counters = [defaultdict(int) for x in range(6)]
    num_samples = 100_000
    for i in range(num_samples):
        results = play_tourney(bracket, probs)
        for r, c in zip(results, counters):
            for team in r:
                c[team] += 1

    all_teams = bracket['first_four'] + bracket['tourney']
    table = []
    for team in all_teams:
        row = [team]
        for c in counters:
            row.append(c[team] / num_samples)
        table.append(row)

    df = pd.DataFrame(table, columns=["Team Name", "Top32", "Top16", "Top8", "Top4", "Top2", "Top1"])
    df = df.sort_values(["Top1", "Top2", "Top4", "Top8", "Top16", "Top32"], ascending=False)
    df.to_csv(f"model_results/round_probabilities_{year}.csv", index=False)


def create_expected_value(bracket_file):
    year = re.match(".*(\d\d\d\d)\.json", bracket_file).groups(0)[0]
    points_file = f'model_results/results_{year}.json'
    lookup = json.loads(open(points_file).read())
    bracket = json.loads(open(bracket_file).read())

    first_four = bracket['first_four']
    if len(first_four) > 0:
        first_four_winners = play_round_deterministic(first_four, lookup)
        top_64 = template_bracket(bracket['tourney'], first_four_winners)
    else:
        top_64 = bracket['tourney']

    top_32 = play_round_deterministic(top_64, lookup)
    top_16 = play_round_deterministic(top_32, lookup)
    top_8 = play_round_deterministic(top_16, lookup)
    top_4 = play_round_deterministic(top_8, lookup)
    top_2 = play_round_deterministic(top_4, lookup)
    top_1 = play_round_deterministic(top_2, lookup)

    results = {
        "Top32": top_32,
        "Top16": top_16,
        "Top8": top_8,
        "Top4": top_4,
        "Top2": top_2,
        "Top1": top_1
    }
    with open(f'model_results/{year}_expected.json', 'w') as fout:
        fout.write(json.dumps(results, indent=4))


def play_round_set(teams):
    results = []
    for i in range(0, len(teams), 2):
        t1 = list(teams[i])
        t2 = list(teams[i + 1])
        all_teams = set(t1 + t2)
        results.append(all_teams)
    return results


def to_set(s):
    if isinstance(s, str):
        return set([s])
    return s


def get_most_probable_winner(team_list, team_set):
    for t in team_list:
        if t in team_set:
            return t


def update_rounds_with_pick(rounds, pick):
    for i in range(len(rounds)):
        for j in range(len(rounds[i])):
            if pick in rounds[i][j]:
                rounds[i][j] = set([pick])


def convert_round_sets_to_str(rounds):
    for i in range(len(rounds)):
        for j in range(len(rounds[i])):
            rounds[i][j] = list(rounds[i][j])[0]


def make_greedy_probabiliy_bracket(bracket_file, prob_file):
    probs = json.loads(open(prob_file).read())
    year = re.match(".*(\d\d\d\d)\.json", bracket_file).groups(0)[0]
    df = pd.read_csv(f"model_results/round_probabilities_{year}.csv")
    bracket = json.loads(open("brackets/bracket_2022.json").read())
    bracket['first_four'] = [set([x]) for x in bracket['first_four']]
    first_four = play_round(bracket['first_four'])
    top64 = template_bracket(bracket['tourney'], first_four)
    top64 = [to_set(x) for x in top64]

    teams_left = list(top64)
    rounds = []
    while len(teams_left) > 1:
        teams_left = play_round_set(teams_left)
        rounds.append(teams_left)

    pick_order = []
    for i in range(len(rounds)):
        for j in range(len(rounds[i])):
            pick_order.append((i, j))
    pick_order = pick_order[::-1]

    prob_column_order = ['Top32', 'Top16', 'Top8', 'Top4', 'Top2', 'Top1']
    for round_pick, game_pick in pick_order:
        my_df = df.sort_values(prob_column_order[round_pick], ascending=False)
        my_winner = get_most_probable_winner(my_df['Team Name'], rounds[round_pick][game_pick])
        update_rounds_with_pick(rounds, my_winner)
    convert_round_sets_to_str(rounds)
    d = {}
    for k, v in zip(prob_column_order, rounds):
        d[k] = v

    with open(f'model_results/greedy_prob_{year}.json', 'w') as fout:
        fout.write(json.dumps(d, indent=4))


if __name__ == "__main__":
    create_probability_table(sys.argv[1], sys.argv[2])
    create_expected_value(sys.argv[1])
    #make_greedy_probabiliy_bracket(sys.argv[1])