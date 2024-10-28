#!/bin/bash
#SBATCH --job-name=resnet50_arm # job name
#SBATCH --nodes=1 # number of nodes
#SBATCH --ntasks-per-node=1 # number of MPI task per node
#SBATCH --account=i20240002a
#SBATCH --time=48:00:00
#SBATCH --partition=normal-arm

SCRATCH="/projects/I20240002/andrelucena/pytorch"
MODEL_DIR="$SCRATCH/DL_pytorch_models"
DATA_DIR="$SCRATCH/imagenet"
VENV_DIR="$SCRATCH/pytorch_arm_venv"

module load Python/3.9.5-GCCcore-10.3.0
echo "PYTHONPATH is ${PYTHONPATH}"
source "${VENV_DIR}/bin/activate"
python3 $MODEL_DIR/dstat.py -cdnm > dstat_arm.out &
python3 $MODEL_DIR/main.py -a resnet50 --epochs 2 --batch-size 256 $DATA_DIR