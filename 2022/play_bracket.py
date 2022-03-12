import hashlib
import os
import numpy as np
import pickle
import json

from ligand_ml.data import NumpyDataset
from ligand_ml.models.torchm.model_mechanics import DenseModel


def load_transformers():
    with open('transformers.pkl', 'rb') as fin:
        return pickle.load(fin)


def get_team_fvs(year):
    d = json.loads(open('team_fvs.json').read())

    X = []
    team_names = []
    for k, v in d.items():
        if k.find(year) == -1:
            continue
        X.append(v[0])
        team_names.append(k)

    print(len(team_names))
    ds = NumpyDataset(X, np.ones(len(X)), np.ones(len(X)), range(len(X)))

    return ds.X, team_names


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
    print(np.array(X).shape)
    ds = NumpyDataset(X, np.ones(len(X)), np.ones(len(X)), range(len(X)))
    transformers = load_transformers()
    for trans in transformers:
        ds = trans.transform(ds)
    return ds


def make_predictions(ds, model_key):
    all_preds = []
    for fold in range(5):
        path = os.path.join('models', model_key, str(fold))
        d = DenseModel(path, mode='regression')
        preds = np.squeeze(d.predict(ds))
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
        results[f"{t1}:{t2}"] = average
        results[f"{t2}:{t1}"] = average * -1
        index += 2
    return results


def play_year(year):
    with open('models/best_params.json', 'r') as fin:
        best_params = json.loads(fin.read())
    model_key = hashlib.md5(str(best_params).encode('utf-8')).hexdigest()

    ds = create_dataset(year)
    predictions = make_predictions(ds, model_key)
    predictions = convert_to_games(predictions, year)
    with open(f'results_{year}.json', 'w') as fout:
        fout.write(json.dumps(predictions, indent=4, sort_keys=True))


def main():
    for year in ["2016", "2017", "2018", "2019", "2020", "2021", "2022"]:
        print(f"Playing {year}")
        play_year(year)


if __name__ == "__main__":
    main()
