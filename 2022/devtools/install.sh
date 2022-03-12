#!/bin/bash

INSTALL_MODE=${1:-install}

export DATE=`date +%Y-%m-%d`
export ENV_NAME=${ENV_NAME:-ml_starter}
export CPU_ONLY=${CPU_ONLY:-0}
export CONDA_URL=https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh

unamestr=`uname`
if [[ "$unamestr" == 'Darwin' ]];
then
    echo "Using OSX Conda"
    export CONDA_URL=https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-x86_64.sh
    export CPU_ONLY=1
    export ENVIRONMENT_YML="devtools/environment-cpu.yml"
else
    export ENVIRONMENT_YML="devtools/environment.yml"
fi

export CONDA_EXISTS=`which conda`
if [[ "$CONDA_EXISTS" = "" ]];
then
    wget ${CONDA_URL} -O anaconda.sh;
    bash anaconda.sh -b -p `pwd`/anaconda
    export PATH=`pwd`/anaconda/bin:$PATH
else
    echo "Using Existing Conda"
fi

# Install Libraries
wget https://tentacruel.bb.schrodinger.com/public/ligand_ml/master/environment.yml
conda env create --name=${ENV_NAME} -f environment.yml
source activate ${ENV_NAME}
pip install https://tentacruel.bb.schrodinger.com/public/ligand_ml/master/ligand_ml-0.0.0-py3-none-any.whl
echo "Installed $ENV_NAME conda environment"

scp -r boltio:/nfs/working/deep_learn/leswing/madness/2022/datasets ./
scp -r boltio:/nfs/working/deep_learn/leswing/madness/2022/team_fvs.json ./
scp -r boltio:/nfs/working/deep_learn/leswing/madness/2022/transformers.pkl ./
