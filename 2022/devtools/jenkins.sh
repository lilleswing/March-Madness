#!/bin/bash
bash devtools/install.sh

export PATH=$(pwd)/anaconda/bin:$PATH
source activate ml_starter

python my_experiment.py

ssh boltio 'mkdir -p /nfs/working/deep_learn/leswing/madness/models/${BUILD_NUMBER}'
scp -r models boltio:/nfs/working/deep_learn/leswing/madness/models/${BUILD_NUMBER}
