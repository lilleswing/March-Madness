import json
import os
import re
import sys
import unicodedata

import numpy as np
from bs4 import BeautifulSoup

fieldnames = [
    "RankAdjOE",
    "RankAdjDE",
    "RankAdjTempo",
    "RankAPL_Off",
    "RankAPL_Def",
    "RankeFG_Pct",
    "RankDeFG_Pct",
    "RankTO_Pct",
    "RankDTO_Pct",
    "RankOR_Pct",
    "RankDOR_Pct",
    "RankFT_Rate",
    "RankDFT_Rate",
    "RankFG3Pct",
    "RankFG3Pct",
    "RankFG2Pct",
    "RankFG2Pct",
    "RankFTPct",
    "RankFTPct",
    "RankBlockPct",
    "RankBlockPct",
    "RankStlRate",
    "RankStlRate",
    "RankNSTRate",
    "RankNSTRate",
    "RankF3GRate",
    "RankF3GRate",
    "RankARate",
    "RankARate",
    "RankOff_3",
    "RankDef_3",
    "RankOff_2",
    "RankDef_2",
    "RankOff_1",
    "RankDef_1",
]
regexes = [f".*{x}.*?>(.+?)<.*?seed..>(.+?)<.*$" for x in fieldnames]


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


class NumpyDataset:
    """
    A dataset class for handling feature and label data as NumPy arrays.
    Automatically performs z-scale whitening (standardization) on initialization.
    Provides functionality to save and load datasets to/from files.
    """

    def __init__(self, X, y, eps=1e-8):
        """
        Initialize the dataset with features X and labels y and perform whitening.

        Parameters:
        -----------
        X : numpy.ndarray
            Feature data, where rows are samples and columns are features.
        y : numpy.ndarray
            Label data, typically a 1D array with one label per sample.
        eps : float
            Small constant to add to standard deviation to avoid division by zero.
        """
        self.X = X
        self.y = y

    def __len__(self):
        """Return the number of samples in the dataset."""
        return len(self.X)

    def __getitem__(self, idx):
        """Get a specific sample or subset of samples (original data)."""
        return self.X[idx], self.y[idx]

    def save(self, filepath):
        """
        Save the dataset to a file, including original data, whitened data, and whitening parameters.

        Parameters:
        -----------
        filepath : str
            Path where the dataset will be saved.
        """
        # Create directory if it doesn't exist
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # Save all data and parameters
        np.savez_compressed(
            filepath,
            X=self.X,
            y=self.y,
        )
        print(f"Dataset saved to {filepath}.npz")

    @classmethod
    def load(cls, filepath):
        """
        Load a dataset from a file.

        Parameters:
        -----------
        filepath : str
            Path to the saved dataset file.

        Returns:
        --------
        NumpyDataset
            A new dataset instance with the loaded data.
        """
        # Handle the case where the .npz extension was already added
        if not filepath.endswith('.npz'):
            filepath = f"{filepath}.npz"

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No dataset found at {filepath}")

        data = np.load(filepath)
        dataset = cls.__new__(cls)  # Create instance without calling __init__
        dataset.X = data['X']
        dataset.y = data['y']
        return dataset

def extract_win_loss(html_content, year):
    """
    Extracts the scouting report table and win/loss results from the HTML content.

    Args:
        html_content: A string containing the HTML content.

    Returns:
        A dictionary containing:
            'scouting_report': A dictionary of scouting report data (category: values).
            'game_results': A list of dictionaries, each representing a game
                            with 'date', 'opponent', 'result', 'location', and 'conference'.
    """

    soup = BeautifulSoup(html_content, 'html.parser')

    game_results = []
    schedule_table = soup.find('table', id='schedule-table')
    if schedule_table:
        for row in schedule_table.find_all('tr', class_=re.compile(r'^(w|l)')):  # Match rows with class 'w' or 'l'
            cells = row.find_all('td')
            if len(cells) >= 9:  # Check we have all the columns
                date = cells[0].text.strip()
                opponent_name_cell = cells[3]
                opponent = opponent_name_cell.text.strip()
                opponent = f"{opponent}_{year}"
                result = cells[4].text.strip()
                location = cells[7].text.strip()
                conference = cells[9].text.strip()

                win_loss = 'Win' if 'w' in row['class'] else 'Loss'

                match = re.search(r'([WL]),\s*(\d+-\d+)', result)
                score = match.group(2) if match else ""
                if score == "":
                    continue
                score_ints = [int(x) for x in score.split('-')]
                delta = abs(score_ints[0] - score_ints[1])
                if win_loss == 'Loss':
                    delta = -1 * delta

                game_results.append({
                    'date': date,
                    'opponent': opponent,
                    'result': delta,
                    'location': location,
                    'conference': conference
                })

    return game_results


def extract_values(html_content, pattern):
    retval = []
    for line in html_content.split('\n'):
        m = re.match(pattern, line)
        if m is not None:
            retval.extend(m.groups())
    return retval


def to_team_fv(html_content):
    retval = []
    for r in regexes:
        v = extract_values(html_content, r)
        retval.extend(v)
    return [float(x) for x in retval]

def check_for_broken_html_files():
    if os.path.exists('datasets/big.npz'):
        return
    raw_files = os.listdir('raw_data')
    fv_lengths = -1
    broken_files = []
    for fname in raw_files:
        if not fname.endswith('.html'):
            continue
        out_fname = f'raw_data/{fname[:-5]}.json'
        if os.path.exists(out_fname):
            continue
        path = f'raw_data/{fname}'
        with open(path, 'r') as fin:
            html_content = fin.read()
        fv = to_team_fv(html_content)
        if fv_lengths == -1:
            fv_lengths = len(fv)
        if len(fv) != fv_lengths:
            print("Error: FV lengths do not match")
            print(fv_lengths, len(fv))
            broken_files.append(fname)
    if len(broken_files) > 0:
        print(f"Broken files: {broken_files}")
        raise ValueError()

def create_team_json_files():
    """
    Team json files will have their feature vector and win/loss record stored in them.
    feature vectors will not be normalized
    :return:
    """
    raw_files = os.listdir('raw_data')
    fv_lengths = -1
    for fname in raw_files:
        if not fname.endswith('.html'):
            continue
        out_fname = f'raw_data/{fname[:-5]}.json'
        if os.path.exists(out_fname):
            continue
        year = re.match(".*(\d\d\d\d).*", fname).group(1)
        path = f'raw_data/{fname}'
        with open(path, 'r') as fin:
            html_content = fin.read()
        fv = to_team_fv(html_content)
        if fv_lengths == -1:
            fv_lengths = len(fv)
        if len(fv) != fv_lengths:
            print("Error: FV lengths do not match")
            print(fv_lengths, len(fv))
            print(fname)
            sys.exit(1)
        win_loss = extract_win_loss(html_content, year)
        d = {
            'team': slugify(fname[:-5]),
            'fv': fv,
            'record': win_loss
        }
        with open(out_fname, 'w') as fout:
            s = json.dumps(d, indent=4, sort_keys=True)
            fout.write(s)

def augment_ds(ds):
    X = ds.X
    y = ds.y
    new_y = np.concatenate([y, -1 * y])
    left_team = X[:, :X.shape[1] // 2]
    right_team = X[:, X.shape[1] // 2:]
    X2 = np.concatenate([right_team, left_team], axis=1)
    new_X = np.concatenate([X, X2], axis=0)
    return NumpyDataset(new_X, new_y)

def create_big_dataset():
    if os.path.exists('datasets/big.npz'):
        return
    team_files = os.listdir('raw_data')
    team_files = [x for x in team_files if x.endswith('.json')]
    team_fvs = {}
    for team_file in team_files:
        with open(f'raw_data/{team_file}', 'r') as fin:
            d = json.load(fin)
            team_fvs[d['team']] = (d['fv'], d['record'])
    X = []
    y = []
    for team, (fv, record) in team_fvs.items():
        for game in record:
            opp = slugify(game['opponent'])
            if game['result'] < 0:
                continue
            if opp not in team_fvs:
                print(f"Opponent {opp} not found")
                continue
            opp_fv = team_fvs[opp][0]
            new_fv = fv + opp_fv
            X.append(new_fv)
            y.append(game['result'])
    X = np.array(X)
    y = np.array(y)
    ds = NumpyDataset(X, y)
    if not os.path.exists('datasets'):
        os.makedirs('datasets')
    ds.save("datasets/big")

    aug_ds = augment_ds(ds)
    u_x = np.mean(aug_ds.X, axis=0)
    u_y = np.mean(aug_ds.y)
    std_x = np.std(aug_ds.X, axis=0)
    std_y = np.std(aug_ds.y)
    with open('datasets/big_params.json', 'w') as fout:
        fout.write(json.dumps({
            'u_x': u_x.tolist(),
            'u_y': u_y,
            'std_x': std_x.tolist(),
            'std_y': std_y
        }, indent=4))

    whitened_X = (ds.X - u_x) / (std_x + 1e-8)
    whitened_y = (ds.y - u_y) / (std_y + 1e-8)
    whitened_ds = NumpyDataset(whitened_X, whitened_y)
    whitened_ds.save("datasets/big_whitened")


def fold_dataset():
    """
    run 5 fold cross validation save datasets as fold_{x}_train, fold_{x}_test
    :return:
    """
    if os.path.exists('datasets/fold_0_train.npz'):
        return
    ds = NumpyDataset.load("datasets/big_whitened")
    n_samples = len(ds)
    indices = np.arange(n_samples)
    np.random.shuffle(indices)
    n_folds = 5
    fold_size = n_samples // n_folds
    for i in range(n_folds):
        test_indices = indices[i * fold_size:(i + 1) * fold_size]
        train_indices = np.concatenate([indices[:i * fold_size], indices[(i + 1) * fold_size:]])
        train_ds = NumpyDataset(ds.X[train_indices], ds.y[train_indices])
        train_ds = augment_ds(train_ds)
        test_ds = NumpyDataset(ds.X[test_indices], ds.y[test_indices])
        test_ds = augment_ds(test_ds)
        train_ds.save(f"datasets/fold_{i}_train")
        test_ds.save(f"datasets/fold_{i}_test")


def main():
    check_for_broken_html_files()
    create_team_json_files()
    create_big_dataset()
    fold_dataset()


if __name__ == "__main__":
    main()
