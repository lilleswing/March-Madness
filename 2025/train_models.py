from featurize_data import NumpyDataset
import uuid
import json
import hashlib
import pickle

from sklearn.metrics import r2_score, mean_squared_error
from ax.service.managed_loop import optimize

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os


class NeuralNetworkModel:
    def __init__(self, input_dim, layer_sizes=None, output_dim=1, learning_rate=3e-4, dropout_rate=0.5):
        """
        Initialize a neural network model with configurable layers.

        Args:
            input_dim (int): Dimension of input features
            layer_sizes (list): List of hidden layer sizes (default: None, which creates a simple linear model)
            output_dim (int): Dimension of output (default: 1 for regression)
            learning_rate (float): Learning rate for optimizer
            dropout_rate (float): Dropout probability (default: 0.5)
        """
        self.input_dim = input_dim
        self.layer_sizes = layer_sizes if layer_sizes is not None else []
        self.output_dim = output_dim
        self.learning_rate = learning_rate
        self.dropout_rate = dropout_rate
        self._build_model()
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)

    def _build_model(self):
        """Build the neural network with the specified architecture."""
        layers = []
        prev_size = self.input_dim
        for size in self.layer_sizes:
            layers.append(nn.Linear(prev_size, size))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(self.dropout_rate))
            prev_size = size
        layers.append(nn.Linear(prev_size, self.output_dim))
        self.model = nn.Sequential(*layers)

    def train(self, X, y, epochs=100, batch_size=32, verbose=True):
        """
        Train the model using L2 loss.

        Args:
            X (numpy.ndarray): Input features
            y (numpy.ndarray): Target values
            epochs (int): Number of training epochs
            batch_size (int): Batch size for training
            verbose (bool): Whether to print training progress

        Returns:
            list: Training losses
        """
        X_tensor = torch.FloatTensor(X)
        y_tensor = torch.FloatTensor(y.reshape(-1, self.output_dim))

        dataset = torch.utils.data.TensorDataset(X_tensor, y_tensor)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        losses = []
        self.model.train()
        for epoch in range(epochs):
            epoch_loss = 0.0
            for batch_X, batch_y in dataloader:
                # Forward pass
                outputs = self.model(batch_X)
                loss = self.criterion(outputs, batch_y)

                # Backward pass and optimize
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                epoch_loss += loss.item()

            avg_epoch_loss = epoch_loss / len(dataloader)
            losses.append(avg_epoch_loss)

            if verbose and (epoch + 1) % (epochs // 10 or 1) == 0:
                print(f'Epoch [{epoch + 1}/{epochs}], Loss: {avg_epoch_loss:.6f}')

        return losses

    def predict(self, X):
        """
        Make predictions with the trained model.

        Args:
            X (numpy.ndarray): Input features

        Returns:
            numpy.ndarray: Predicted values
        """
        self.model.eval()
        X_tensor = torch.FloatTensor(X)
        with torch.no_grad():
            predictions = self.model(X_tensor)
        return predictions.numpy()

    def save(self, path):
        """
        Save the model to a file.

        Args:
            path (str): Path to save the model
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)

        state = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'input_dim': self.input_dim,
            'layer_sizes': self.layer_sizes,
            'output_dim': self.output_dim,
            'learning_rate': self.learning_rate,
            'dropout_rate': self.dropout_rate
        }
        torch.save(state, path)
        print(f"Model saved to {path}")

    @staticmethod
    def load(path):
        """
        Load the model from a file.
        Args:
            path (str): Path to load the model from
        Returns:
            NeuralNetworkModel: Loaded model instance
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"No model found at {path}")

        state = torch.load(path)

        # Create a new model instance with the saved parameters
        model = NeuralNetworkModel(
            input_dim=state['input_dim'],
            layer_sizes=state['layer_sizes'],
            output_dim=state['output_dim'],
            learning_rate=state['learning_rate'],
            dropout_rate=state['dropout_rate']
        )

        # Load the model and optimizer states
        model.model.load_state_dict(state['model_state_dict'])
        model.optimizer.load_state_dict(state['optimizer_state_dict'])

        print(f"Model loaded from {path}")
        return model


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
    def eval_model(extra_params):
        model_key = hashlib.md5(str(extra_params).encode('utf-8')).hexdigest()
        learning_rate = extra_params['lr_initial']
        epochs = extra_params['epochs']
        batch_size = extra_params['batch_size']
        base_folder = f"models/{model_key}"
        layer_sizes = [extra_params['hidden_size_1']]
        dropout = extra_params['dropout']
        if extra_params['num_layers'] == 2:
            layer_sizes.append(extra_params['hidden_size_2'])
        if not os.path.exists(base_folder):
            os.makedirs(base_folder, exist_ok=True)

        scores = []
        for i in range(5):
            train_ds = NumpyDataset.load(f'datasets/fold_{i}_train.npz')
            test_ds = NumpyDataset.load(f'datasets/fold_{i}_test.npz')
            model = NeuralNetworkModel(input_dim=train_ds.X.shape[1], layer_sizes=layer_sizes, output_dim=1,
                                       learning_rate=learning_rate, dropout_rate=dropout)
            losses = model.train(train_ds.X, train_ds.y, epochs=epochs, batch_size=batch_size)
            model.save(f"{base_folder}/model_{i}.pt")
            valid_preds = model.predict(test_ds.X)
            scores.append(r2_score(test_ds.y, valid_preds))
        print(f"finished training {global_number_of_models[0]}")
        global_number_of_models[0] += 1
        v1, v2 = np.mean(scores), np.std(scores)
        value = _t_test_90(np.mean(scores), np.std(scores))
        with open('models/results.txt', 'a') as fout:
            fout.write(f"{model_key},{v1},{v2},{value}\n")
        return value

    return eval_model


def run_training():
    num_models = int(os.environ.get("NUMBER_OF_MODELS", 2))
    best_parameters, values, experiment, model = optimize(
        parameters=[
            {"name": "hidden_size_1", "type": "range", "bounds": [32, 256]},
            {"name": "hidden_size_2", "type": "range", "bounds": [32, 256]},
            {"name": "num_layers", "type": "choice", "values": [1, 2]},
            {"name": "dropout", "type": "range", "bounds": [0.0, 0.95]},
            {"name": "epochs", "type": "range", "bounds": [10, 200]},
            {"name": "batch_size", "type": "range", "bounds": [32, 256]},
            {"name": "lr_initial", "type": "range", "bounds": [0.00001, 0.01]},
        ],
        evaluation_function=eval_model_closure(),
        objective_name='r2_score',
        minimize=False,
        total_trials=num_models
    )
    with open('models/best_params.json', 'w') as fout:
        fout.write(json.dumps(best_parameters, indent=4))

    model_key = hashlib.md5(str(best_parameters).encode('utf-8')).hexdigest()
    with open('models/best_model.txt', 'w') as fout:
        fout.write(f"{model_key}\n")


def main():
    run_training()


if __name__ == "__main__":
    main()
