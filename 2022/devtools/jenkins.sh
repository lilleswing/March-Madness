#!/bin/bash
export DATA_VERSION="5"
bash devtools/install.sh
export PATH=$(pwd)/anaconda/bin:$PATH
source activate ml_starter


scp -r boltio:/nfs/working/deep_learn/leswing/madness/2022/featurized/${DATA_VERSION}/datasets ./
scp -r boltio:/nfs/working/deep_learn/leswing/madness/2022/featurized/${DATA_VERSION}/team_fvs.json ./
scp -r boltio:/nfs/working/deep_learn/leswing/madness/2022/featurized/${DATA_VERSION}/transformers.pkl ./

python train_models.py
python calibrate.py
python get_win_percentages.py
python play_bracket.py brackets/bracket_2022.json model_results/results_probs_2022.json

ssh boltio 'mkdir -p /nfs/working/deep_learn/leswing/madness/models/${BUILD_NUMBER}'
scp -r models boltio:/nfs/working/deep_learn/leswing/madness/models/${BUILD_NUMBER}
scp -r model_results boltio:/nfs/working/deep_learn/leswing/madness/models/${BUILD_NUMBER}

echo "DATASET_VERSION=${DATA_VERSION}" > params.in
echo "NUMBER_OF_MODELS=${NUMBER_OF_MODELS}" >> params.in
scp params.in boltio:/nfs/working/deep_learn/leswing/madness/models/${BUILD_NUMBER}
