#!/bin/bash

SCRATCH=/projects/I20240002/andrelucena
module load Python/3.9.5-GCCcore-10.3.0

VENV_DIR="${SCRATCH}/tensorflow-venv2"

rm -rf $VENV_DIR

python3 -m venv $VENV_DIR

source $VENV_DIR/bin/activate

pip3 install --upgrade pip

echo "export PYTHONPATH=$PYTHONPATH:$SCRATCH/TensorflowScripts/models/official-models-2.1.0"
export PYTHONPATH=$PYTHONPATH:$SCRATCH/TensorflowScripts/models/official-models-2.1.0

pip3 install -r ./reqs.txt --no-cache-dir
