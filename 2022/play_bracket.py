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
    d = {f"t{i}": x for i, x in enumerate(first_four_winners)}
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
    df.to_csv(f"model_results/round_probabilities_{year}.csv", index=None)


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


if __name__ == "__main__":
    create_probability_table(sys.argv[1], sys.argv[2])
    create_expected_value(sys.argv[1])
