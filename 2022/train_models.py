import os

from ax.service.managed_loop import optimize
from ligand_ml.data import NumpyDataset
import uuid
import json
import numpy as np
from ligand_ml.data.datasets import DiskDataset
from ligand_ml.models.torchm.model_mechanics import DenseModel
import hashlib
import pickle

from sklearn.metrics import r2_score


def _t_test_90(u, std):
    return float(u) - 1.96 * float(std)


def eval_hprams(model, epochs, train_ds, valid_ds):
    model.fit(train_ds, nb_epoch=epochs)
    model.save()
    y_pred = model.predict(valid_ds)
    return r2_score(valid_ds.y, np.squeeze(y_pred))


def to_numpy(ds):
    return NumpyDataset(ds.X, ds.y, ds.w, ds.ids)


global_number_of_models = [0]
def eval_model_closure():
    params = json.loads(open('datasets/default_params.json').read())
    folds = []
    for i in range(5):
        train = DiskDataset(f'datasets/full_folds/train{i}')
        test = DiskDataset(f'datasets/full_folds/valid{i}')
        folds.append((train, test))
    folds = [(to_numpy(x[0]), to_numpy(x[1])) for x in folds]

    def eval_model(extra_params):
        model_key = hashlib.md5(str(extra_params).encode('utf-8')).hexdigest()
        vals = []
        my_params = dict(params)
        my_params.update(extra_params)

        learning_rate_str = json.loads(my_params['learning_rate'])
        learning_rate_str['initial_rate'] = extra_params['lr_initial']
        my_params['learning_rate'] = json.dumps(learning_rate_str)
        my_params['layers'] = [extra_params['hidden_size_1']]
        if my_params['num_layers'] == 2:
            my_params['layers'].append(extra_params['hidden_size_2'])

        for i, fold in enumerate(folds):
            params['fp_size'] = 0

            train, valid = fold
            params['num_features'] = train.X.shape[1]
            model_path = 'models/%s/%s' % (model_key, i)
            d = DenseModel(model_path, mode='regression', parameters=params)
            d.fit(train, extra_params['epochs'], extra_params['batch_size'])
            d.save()

            y_pred = d.predict(valid)

            vals.append(r2_score(valid.y, np.squeeze(y_pred)))
        print(f"finished training {global_number_of_models[0]}")
        global_number_of_models[0] += 1
        return _t_test_90(np.mean(vals), np.std(vals))

    return eval_model


def run_training():
    num_models = os.environ.get("NUMBER_OF_MODELS", 250)
    best_parameters, values, experiment, model = optimize(
        parameters=[
            {"name": "hidden_size_1", "type": "range", "bounds": [32, 256]},
            {"name": "hidden_size_2", "type": "range", "bounds": [32, 256]},
            {"name": "num_layers", "type": "choice", "values": [1, 2]},
            {"name": "dropout", "type": "range", "bounds": [0.0, 0.95]},
            {"name": "epochs", "type": "range", "bounds": [10, 100]},
            {"name": "batch_size", "type": "range", "bounds": [32, 256]},
            {"name": "lr_initial", "type": "range", "bounds": [0.00001, 0.01]},
        ],
        evaluation_function=eval_model_closure(),
        objective_name='r2_score',
        minimize=False,
        total_trials=num_models
    )
    with open('models/best_params.json', 'w') as fout:
        fout.write(json.dumps(best_parameters))

    pickle.dump(values, open('models/values.pkl', 'wb'))

    model_key = hashlib.md5(str(best_parameters).encode('utf-8')).hexdigest()
    with open('models/best_model.txt','w') as fout:
        fout.write(f"{model_key}\n")


def main():
    run_training()


if __name__ == "__main__":
    main()
