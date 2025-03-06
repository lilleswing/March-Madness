import hashlib
import os
import numpy as np
import json
from calibrate import load_transformers, make_predictions
from featurize_data import NumpyDataset


def get_team_fvs(year):
    fnames = os.listdir('raw_data')
    fnames = [x for x in fnames if x.endswith('json')]
    X = []
    team_names = []
    for fname in fnames:
        if fname.find(year) == -1:
            continue
        path = os.path.join('raw_data', fname)
        with open(path, 'r') as fin:
            d = json.loads(fin.read())
        X.append(d['fv'])
        team_names.append(d['team'])
    X = np.array(X)
    transformers = load_transformers()
    u_x = transformers['u_x'][:X.shape[1]]
    std_x = transformers['std_x'][:X.shape[1]]
    X = (X - u_x) / std_x
    return X, team_names


def create_dataset(year):
    fvs, team_names = get_team_fvs(year)
    X = []
    for i, t1 in enumerate(team_names):
        for j, t2 in enumerate(team_names):
            if j <= i:
                continue
            fv1 = np.concatenate([fvs[i], fvs[j]])
            fv2 = np.concatenate([fvs[j], fvs[i]])
            X.append(fv1)
            X.append(fv2)
    ds = NumpyDataset(np.array(X), None)
    return ds


def make_prediction_all_folds(ds, model_key):
    all_preds = []
    for fold in range(5):
        preds = make_predictions(ds, fold, model_key)
        all_preds.append(preds)

    retval = np.mean(all_preds, axis=0)
    print(f"Predictions shape {retval.shape}")
    return retval


def convert_to_games(predictions, year):
    fvs, team_names = get_team_fvs(year)
    games = []
    for i, t1 in enumerate(team_names):
        for j, t2 in enumerate(team_names):
            if j <= i:
                continue
            games.append((t1, t2))

    results = {}
    index = 0
    while index < len(predictions):
        v1, v2 = predictions[index], predictions[index + 1]
        v2 *= -1
        average = (v1 + v2) / 2

        t1, t2 = games[index // 2]
        results[f"{t1}:{t2}"] = float(average)
        results[f"{t2}:{t1}"] = float(average * -1)
        index += 2
    return results


def get_probability(v, bounds, probs):
    for b, p in zip(bounds, probs):
        if b > v:
            return p
    print("Game off the rails!")
    return probs[-1]


def prob_predictions(predictions):
    if not os.path.exists('model_results/probs_and_bounds.json'):
        return None
    my_prob_predictions = dict(predictions)
    d = json.loads(open('model_results/probs_and_bounds.json').read())
    for k, v in predictions.items():
        my_prob = get_probability(v, d['bounds'], d['probs'])
        my_prob_predictions[k] = my_prob
    return my_prob_predictions


def play_year(year):
    with open('models/best_params.json', 'r') as fin:
        best_params = json.loads(fin.read())
    model_key = hashlib.md5(str(best_params).encode('utf-8')).hexdigest()

    ds = create_dataset(year)
    predictions = make_prediction_all_folds(ds, model_key)
    predictions = convert_to_games(predictions, year)
    os.makedirs('model_results', exist_ok=True)
    with open(f'model_results/results_{year}.json', 'w') as fout:
        fout.write(json.dumps(predictions, indent=4, sort_keys=True))

    my_prob_predictions = prob_predictions(predictions)
    if my_prob_predictions is None:
        return
    with open(f'model_results/results_probs_{year}.json', 'w') as fout:
        fout.write(json.dumps(my_prob_predictions, indent=4, sort_keys=True))


def main():
    for year in ['2024']:
        print(f"Playing {year}")
        play_year(year)


if __name__ == "__main__":
    main()
