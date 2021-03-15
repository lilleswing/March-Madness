import itertools
import random
from ligand_ml.data import NumpyDataset
import json

import numpy as np
from ligand_ml.data import DiskDataset
from ligand_ml.models.torchm.model_mechanics import DenseModel
from sklearn.metrics import r2_score


def eval_hprams(model, epochs, train_ds, valid_ds):
    """
    :param model:
    :param epochs:
    :param train_ds:
    :param valid_ds:
    :return:

    will create a list of hparams and then lay out models in
    models/{key}/{fold_id}
    """
    model.fit(train_ds, nb_epoch=epochs)
    model.save()
    y_pred = model.predict(valid_ds)
    return r2_score(valid_ds.y, np.squeeze(y_pred))


def eval_model(hps, key, folds):
    vals = []
    layer_sizes, dropout, epochs = hps[key]['layer_sizes'], hps[key]['dropout'], hps[key]['epochs']
    dense_params = {
        "mode": 'regression',
        "model": "MultiTaskRegressor",
        "num_features": 78,
        "num_classes": 1,
        "layers": hps[key]['layer_sizes'],
        "dropout": hps[key]['dropout'],
        "num_tasks": 1,
        "epochs": hps[key]['epochs'],
        'learning_rate_schedule': 'custom',
        'learning_rate': hps[key]['learning_rate']
    }
    for i, fold in enumerate(folds):
        train, valid = fold
        model_path = 'models/%s/%s' % (key, i)
        model = DenseModel(model_path, mode='regression', parameters=dense_params)
        retval = eval_hprams(model, epochs, train, valid)
        vals.append(retval)
    return np.mean(vals), np.std(vals)


def to_numpy(ds):
    return NumpyDataset(ds.X, ds.y, ds.w, ds.ids)


def main():
    folds = [
        (DiskDataset(data_dir='datasets/full_folds/train%s' % x),
         DiskDataset(data_dir='datasets/full_folds/valid%s' % x)
         ) for x in range(5)
    ]
    folds = [(to_numpy(x[0]), to_numpy(x[1])) for x in folds]

    hps = {}
    layer_sizes = [
        [1000],
        [64, 64],
        [64, 32],
        [64, 32, 16],
        [256, 128]
    ]

    dropouts = [
        0.25, 0.35, 0.5, 0.0
    ]

    epochs = [
        25, 50, 100
    ]

    learning_rates = [
        0.001, 0.0005, 0.0001
    ]

    index = 0
    for ls, dr, ep, lr in itertools.product(layer_sizes, dropouts, epochs, learning_rates):
        hps[index] = {
            'layer_sizes': ls,
            'dropout': dr,
            'epochs': ep,
            "learning_rate": lr
        }
        index += 1

    key_order = list(hps.keys())
    random.shuffle(key_order)
    print(key_order)

    for key in key_order:
        retval = eval_model(hps, key, folds)
        print(key, retval)
        with open('metrics/results.txt', 'a') as fout:
            fout.write("%s,%s,%s\n" % (key, retval[0], retval[1]))

    with open('metrics/hps_0.json', 'w') as fout:
        fout.write(json.dumps(hps))


if __name__ == "__main__":
    main()
