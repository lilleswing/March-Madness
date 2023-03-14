# March Madness

This repo represents a pipeline which gathers data, featurizes, trains, and predicts for march madness.

## Workflow

### `python grab_raw_data.py {cookie}`
This grabs the html files from kenpom.com and creates the folder `raw_data`

### `python featurize_data.py`

This creates `datasets`, `team_fvs.json`, `transformers.pkl`.
This extracts the data from `raw_data` and creates featurized data ready for model training.

### `python train_models.py`

This creates `models` which is artifacts for making new predictions
This does hyper parameter smashing over `datasets` for 5 fold cross validation

### `python calibrate.py`

This creates `model_results/probs_and_bounds.json`
This is a mapping over cross validation data of point differential predicted to probability of winning.

### `python python get_win_percentages.py`

This creates `model_results/results_{year}.json` and `model_results/results_probs_{year}.json`
This will simulate n^2 games for each year of data amongst all teams.
`results_{year}.json` will store the point differential.
`results_probs_{year}.json` will store the probability of winning.


### `python play_bracket.py {bracket_file} {result_probs_file}`

This creates `model_results/{year}_expected.json` and `model_results/round_probabilities_{year}.json`

`{year}_expected.json` takes the predicted winner for each game and plays out the bracket.
`round_probabilities_{year}.csv` simulates the bracket many times and outputs the monte carlo probability of teams making it to a certain round

## Backlog

#### Engineering QOL
* Grab list of teams per year from yearly landing page
  * New teams don't exist in previous years and old teams don't exist now
* Sanity checks for the data at different levels
  * is calibration monotonically increasing and roughly symmetric?
  * does team_fvs.json have teams from all years
  * Reasonable championship probabilities for #1 seeds in previous years brackets

#### Model Improvements
* Add new features KenPom has calculated since I originally wrote the scrapping code
* Time weighting of games (What have you done recently)
* Home Field Advantage
