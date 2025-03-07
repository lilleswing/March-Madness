import hashlib
from copy import deepcopy
import pandas as pd
import os
import numpy as np
import pickle
import json
from featurize_data import NumpyDataset


from train_models import NeuralNetworkModel


def load_transformers():
    with open('datasets/big_params.json', 'r') as fin:
        return json.loads(fin.read())


def make_predictions(ds, fold, model_key):
    transformers = load_transformers()
    path = os.path.join('models', model_key, f"model_{fold}.pt")
    print(path)
    model = NeuralNetworkModel.load(path)
    preds = model.predict(ds.X)
    preds = (preds * transformers['std_y']) + transformers['u_y']
    preds = preds.reshape(-1)
    return preds


def get_fold_df(fold, model_key):
    transformers = load_transformers()
    ds = NumpyDataset.load(f'datasets/fold_{fold}_test.npz')
    preds = make_predictions(ds, fold, model_key)
    num_games = ds.X.shape[0] // 2
    avg_results = []
    for i in range(num_games):
        v = (preds[i] + preds[i + num_games] * -1) / 2
        avg_results.append(v)
    other_way_games = np.array(avg_results) * -1
    y_avg = np.concatenate([avg_results, other_way_games])
    true_points = (ds.y * transformers['std_y']) + transformers['u_y']
    df = pd.DataFrame(list(zip(true_points, y_avg)), columns=["y_true", "y_pred"])
    return df


def get_all_games(model_key):
    dfs = []
    for i in range(5):
        df = get_fold_df(i, model_key)
        dfs.append(df)
    return pd.concat(dfs)


def get_probability_map(df):
    bounds = [-10_000, -20, -15, -10, -5, -4, -3, -2, -1, -0.5, 0.5, 1, 2, 3, 4, 5, 10, 15, 20, 10_000]
    probs = [0]
    for i in range(1, len(bounds)):
        my_df = deepcopy(df)
        my_df['is_more'] = my_df['y_pred'] > bounds[i - 1]
        my_df['is_less'] = my_df['y_pred'] < bounds[i]
        my_df = my_df[my_df['is_more']]
        my_df = my_df[my_df['is_less']]

        my_df['has_won'] = my_df['y_true'] > 0

        print(bounds[i-1], bounds[i])
        # is_wrong = len(my_df) - sum(my_df['is_correct'])
        if len(my_df) == 0:
            print(f"No Values for {bounds[i]}")
            probs.append(0)
        else:
            probs.append(sum(my_df['has_won']) / len(my_df))
    return bounds, probs


def main():
    with open('models/best_params.json', 'r') as fin:
        best_params = json.loads(fin.read())
    model_key = hashlib.md5(str(best_params).encode('utf-8')).hexdigest()
    all_game_df = get_all_games(model_key)
    bounds, probs = get_probability_map(all_game_df)
    d = {
        "probs": probs,
        "bounds": bounds
    }
    os.makedirs('model_results', exist_ok=True)
    with open('model_results/probs_and_bounds.json', 'w') as fout:
        fout.write(json.dumps(d, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
