from sklearn.metrics import r2_score
import deepchem as dc
import numpy as np
import itertools
import random

def p_r2(y_true, y_pred):
    return r2_score(y_true, y_pred)

def eval_hprams(model, epochs, train_ds, valid_ds):
    model.fit(train_ds, nb_epoch=epochs)
    model.save()
    y_pred = model.predict(valid_ds)
    return p_r2(valid_ds.y, np.squeeze(y_pred))

def eval_model(hps, key, folds):
    vals = []
    layer_sizes, dropout, epochs = hps[key]['layer_sizes'], hps[key]['dropout'], hps[key]['epochs']
    for i, fold in enumerate(folds):
        train, valid = fold
        model_path = 'models/%s/%s' % (key, i)
        model = dc.models.MultiTaskRegressor(1, n_features=train.X.shape[-1],
                                             layer_sizes=layer_sizes, dropout=dropout,
                                            model_dir=model_path)
        retval = eval_hprams(model, epochs, train, valid)
        vals.append(retval)
    return np.mean(vals), np.std(vals)

def gen_hps():
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
    index = 0
    for ls, dr, ep in itertools.product(layer_sizes, dropouts, epochs):
        hps['%s_all_data' % index] = {
            'layer_sizes': ls,
            'dropout': dr,
            'epochs': ep
        }
        index += 1
    return hps

def to_numpy(ds):
    return dc.data.NumpyDataset(ds.X, ds.y, ds.w, ds.ids)

def train_all():
    folds = [
        (dc.data.DiskDataset(data_dir='datasets/2018_2017_folds/train%s' % x),
         dc.data.DiskDataset(data_dir='datasets/2018_2017_folds/valid%s' % x)
        ) for x in range(5)
    ]
    hps = gen_hps()
    key_order = list(hps.keys())
    random.shuffle(key_order)
    print(key_order)
    for key in key_order:
        retval = eval_model(hps, key, folds)
        print(key, retval)
        with open('metrics/results.txt', 'a') as fout:
            fout.write("%s,%s,%s\n" % (key, retval[0], retval[1]))

if __name__ == "__main__":
    train_all()
