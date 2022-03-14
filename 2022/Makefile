.PHONY: clean

upload-dataset:  ## Clean up and removing virtualenv
	scp boltio:/nfs/working/deep_learn/leswing/madness/2022/featurized/3/datasets/default_params.json datasets
	scp -r datasets boltio:/nfs/working/deep_learn/leswing/madness/2022/featurized/${BUILD_NUMBER}
	scp -r team_fvs.json boltio:/nfs/working/deep_learn/leswing/madness/2022/featurized/${BUILD_NUMBER}
	scp -r transformers.pkl boltio:/nfs/working/deep_learn/leswing/madness/2022/featurized/${BUILD_NUMBER}



clean:  ## Clean up and removing virtualenv
	rm -rf datasets
	rm -rf models
	rm -fr model_results
	rm transformers.pkl
	rm team_fvs.json
	rm round_probabilities.csv

