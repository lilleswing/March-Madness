grab-data:
	python grab_raw_data.py

train-models:
	python featurize_data.py
	python train_models.py
	python calibrate.py
	python get_win_percentages.py
	python play_bracket.py

run-all: clean grab-data train-models
	echo "All Done"

clean:
	rm -rf datasets
	rm -rf models
	rm -rf model_results
	rm raw_data/*.json
