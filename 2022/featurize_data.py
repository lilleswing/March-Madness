import os
import pickle
import json
import re
from ligand_ml.data import NumpyDataset
from ligand_ml.data import DiskDataset
from ligand_ml.trans.transformers import NormalizationTransformer
from ligand_ml.data.splitters import k_fold

import numpy as np

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
    'RankFG3Pct.*&od=d',
    'RankFG2Pct',
    'RankFG2Pct.*&od=d',
    'RankFTPct',
    'RankFTPct.*&od=d',
    'RankBlockPct',
    'RankBlockPct.*&od=d',
    'RankStlRate',
    'RankStlRate.*&od=d',
    'RankF3GRate',
    'RankF3GRate.*&od=d',
    'RankARate',
    'RankARate.*&od=d',
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


def get_feature_vector(html_str, fname):
    fv = []
    for keyword in keywords:
        try:
            pattern = '%s.*>(\d+\.\d+)' % keyword
            val = re.findall(pattern, html_str)[-1]
            fv.append(float(val))
        except Exception as e:
            print(fname, keyword)
            print(e)
            raise e
    year = re.findall(".*=(\d+).*", fname)[0]
    return fv + [float(year)]


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
    # Only return wins and then data augment after doing splits
    return wins


def parse_html_file(html_str, fname):
    """
    return feature_vector, list of (oppenent, +- score)
    """
    fv = get_feature_vector(html_str, fname)
    wl = get_wins_losses(html_str)
    return fv, wl


def to_numpy(ds):
    return NumpyDataset(ds.X, ds.y, ds.w, ds.ids)


def create_full_dataset(d):
    X = []
    ys = []
    for k, v in d.items():
        my_fv = v[0]
        oppenents = v[1]
        for opp in oppenents:
            if opp[0].find("&y") == -1:
                opp_name = opp[0] + "&y=2022"
                opp = (opp_name, opp[1])
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
    win_loss_y = np.concatenate([ds.y, ds.y * -1], axis=0)
    win_loss_ds = NumpyDataset(win_loss_x, win_loss_y)
    transformers = [
        NormalizationTransformer(transform_X=True, dataset=win_loss_ds),
        NormalizationTransformer(transform_y=True, dataset=win_loss_ds)
    ]

    pickle.dump(transformers, open('transformers.pkl', 'wb'))
    return transformers


def main():
    html_files = os.listdir('raw_data')

    d = {}
    for html_file in html_files:
        html_str = open('raw_data/%s' % html_file).read()
        if len(html_str) == 0:
            continue
        team_name = html_file[:-5]
        try:
            d[team_name] = parse_html_file(html_str, html_file)
        except Exception as e:
            print(f"Unable to parse {team_name}")

    with open("team_fvs.json", 'w') as fout:
        s = json.dumps(d, indent=4, sort_keys=True)
        fout.write(s)

    create_full_dataset(d)
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


if __name__ == "__main__":
    main()
