import re
import shutil
import unicodedata

import os
import pandas as pd
import pickle
import json
import re
from ligand_ml.data import NumpyDataset
from ligand_ml.data import DiskDataset
from ligand_ml.trans.transformers import NormalizationTransformer
from ligand_ml.data.splitters import k_fold

import numpy as np

feature_names = [
    '3P%', '3P%.Rank', '2P%', '2P%.Rank', 'FT%',
    'FT%.Rank', 'Blk%', 'Blk%.Rank', 'Stl%', 'Stl%.Rank', 'A%', 'A%.Rank',
    '3PA%', '3PA%.Rank', 'AdjOE_x', 'AdjOE.Rank_x', 'AdjTempo',
    'AdjTempo.Rank', 'AdjOE_y', 'AdjOE.Rank_y', 'Off-eFG%', 'Off-eFG%.Rank',
    'Off-TO%', 'Off-TO%.Rank', 'Off-OR%', 'Off-OR%.Rank', 'Off-FTRate',
    'Off-FTRate.Rank', 'AdjDE', 'AdjDE.Rank', 'Def-eFG%', 'Def-eFG%.Rank',
    'Def-TO%', 'Def-TO%.Rank', 'Def-OR%', 'Def-OR%.Rank', 'Def-FTRate',
    'Def-FTRate.Rank', 'Tempo-Adj', 'Tempo-Adj.Rank', 'Tempo-Raw',
    'Tempo-Raw.Rank', 'Avg. Poss Length-Offense',
    'Avg. Poss Length-Offense.Rank', 'Avg. Poss Length-Defense',
    'Avg. Poss Length-Defense.Rank', 'Off. Efficiency-Adj',
    'Off. Efficiency-Adj.Rank', 'Off. Efficiency-Raw',
    'Off. Efficiency-Raw.Rank', 'Def. Efficiency-Adj',
    'Def. Efficiency-Adj.Rank', 'Def. Efficiency-Raw',
    'Def. Efficiency-Raw.Rank'
]


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD',
                                      value).encode('ascii',
                                                    'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def parse_win_losses(df, year):
    """
    return feature_vector, list of (oppenent, +- score)
    """
    # fv = get_feature_vector(html_str, fname)

    opps = df['Opponent Name']
    results = df['Result']
    wl = []
    for opp, result in zip(opps, results):
        opp = slugify(opp) + f"_{year}"
        m = re.match("(.), (\d+)-(\d+)", result)
        if m is None:
            continue
        is_win, p1, p2 = m.groups()
        delta = abs(int(p1) - int(p2))
        if is_win == 'L':  # Only do wins then do data augmentation
            continue
        wl.append((opp, delta))
    return wl


def to_numpy(ds):
    return NumpyDataset(ds.X, ds.y, ds.w, ds.ids)


def create_full_dataset(d):
    X = []
    ys = []
    for k, v in d.items():
        my_fv = v[0]
        oppenents = v[1]
        for opp in oppenents:
            if opp[0] not in d:
                print(opp[0])
                continue
            their_fv = d[opp[0]][0]
            fv = my_fv + their_fv
            y = opp[1]
            X.append(fv)
            ys.append(y)
    DiskDataset.from_numpy(np.array(X), np.array(ys), None, None, data_dir='datasets/combined')


def augment_ds(ds):
    X = ds.X
    y = ds.y
    rev_y = ds.y * -1

    n_features = X.shape[1] // 2
    t1 = X[:, :n_features]
    t2 = X[:, n_features:]
    rev_x = np.concatenate([t2, t1], axis=1)

    full_x = np.concatenate([X, rev_x], axis=0)
    full_y = np.concatenate([y, rev_y], axis=0)
    return NumpyDataset(full_x, full_y)


def create_transformers(ds):
    X = ds.X
    n_features = X.shape[1] // 2
    t1 = X[:, :n_features]

    win_loss_x = np.concatenate([t1, t1], axis=1)
    win_loss_x = np.concatenate([win_loss_x, win_loss_x], axis=0)
    win_loss_y = np.concatenate([ds.y, ds.y * -1], axis=0)
    win_loss_ds = NumpyDataset(win_loss_x, win_loss_y)
    transformers = [
        NormalizationTransformer(transform_X=True, dataset=win_loss_ds),
        NormalizationTransformer(transform_y=True, dataset=win_loss_ds)
    ]

    pickle.dump(transformers, open('transformers.pkl', 'wb'))
    return transformers


def main():
    win_loss_files = os.listdir('raw_data2')

    win_store = {}
    for win_loss_file in win_loss_files:
        if win_loss_file.startswith("team_fvs"):
            continue
        if not win_loss_file.endswith(".csv"):
            continue
        df = pd.read_csv(f"raw_data2/{win_loss_file}")
        year = re.match(".*(20\d\d).*", win_loss_file).group(1)
        team_name = win_loss_file[:-4]
        try:
            win_store[team_name] = parse_win_losses(df, year)
        except Exception as e:
            print(f"Unable to parse win_loss for {team_name}")

    feature_store = {}
    for feature_file in win_loss_files:
        if not feature_file.startswith("team_fvs"):
            continue
        if not feature_file.endswith(".csv"):
            continue
        year = re.match(".*(20\d\d).*", feature_file).group(1)
        df = pd.read_csv(f"raw_data2/{feature_file}")
        features = df[feature_names].values
        teams = df['Team'].values.tolist()
        for i, team_name in enumerate(teams):
            team_name = slugify(team_name) + f"_{year}"
            team_feat = features[i, :].tolist()
            feature_store[team_name] = [float(x) for x in team_feat]

    team_fvs = {}
    for feature_key in feature_store.keys():
        if feature_key not in win_store.keys():
            continue
        team_fvs[feature_key] = (feature_store[feature_key], win_store[feature_key])

    with open("team_fvs.json", 'w') as fout:
        s = json.dumps(team_fvs, indent=4, sort_keys=True)
        fout.write(s)

    create_full_dataset(team_fvs)
    ds = to_numpy(DiskDataset('datasets/combined'))
    transformers = create_transformers(ds)

    for trans in transformers:
        ds = trans.transform(ds)

    k_fold(ds, "datasets")
    for i in range(5):
        fname = f'datasets/fold{i}'
        train_idx = np.load(f'{fname}/train_indices.npy')
        valid_idx = np.load(f'{fname}/valid_indices.npy')

        train_ds = ds.select(train_idx)
        train_ds = augment_ds(train_ds)

        fname = 'datasets/full_folds/train%s' % i
        DiskDataset.from_numpy(train_ds.X, train_ds.y, train_ds.w, train_ds.ids, data_dir=fname)

        valid_ds = ds.select(valid_idx)
        valid_ds = augment_ds(valid_ds)
        fname = 'datasets/full_folds/valid%s' % i
        DiskDataset.from_numpy(valid_ds.X, valid_ds.y, valid_ds.w, valid_ds.ids, data_dir=fname)

    shutil.copy("default_hyper_params.json", "datasets/default_params.json")

if __name__ == "__main__":
    main()
