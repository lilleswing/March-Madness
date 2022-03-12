#!/bin/bash
export DATA_VERSION="1"
bash devtools/install.sh
export PATH=$(pwd)/anaconda/bin:$PATH
source activate ml_starter


scp -r boltio:/nfs/working/deep_learn/leswing/madness/2022/featurized/${DATA_VERSION}/datasets ./
scp -r boltio:/nfs/working/deep_learn/leswing/madness/2022/featurized/${DATA_VERSION}/team_fvs.json ./
scp -r boltio:/nfs/working/deep_learn/leswing/madness/2022/featurized/${DATA_VERSION}/transformers.pkl ./

python train_models.py

ssh boltio 'mkdir -p /nfs/working/deep_learn/leswing/madness/models/${BUILD_NUMBER}'
scp -r models boltio:/nfs/working/deep_learn/leswing/madness/models/${BUILD_NUMBER}
