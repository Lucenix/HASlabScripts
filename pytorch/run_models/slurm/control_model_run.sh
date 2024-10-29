#!/bin/sh

export SAVE_EVERY=1
export N_NODES=4
export SCRATCH="/home/lucenix"
export MAIN_PATH="$SCRATCH/HASlabScripts/pytorch/python/main_simple_dist.py"
export DSTAT_PATH="$SCRATCH/HASlabScripts/pytorch/python/dstat.py"
export DATA_DIR="/projects/a97485/imagenet_subset"
export VENV_DIR="$SCRATCH/pytorch_venv"
export STAT_DIR="/projects/a97485/statistics/control_subset"
export SCREEN_PATH="$SCRATCH/bin/screen"
# model is defined in main
export MODEL="resnet50"
export N_EPOCHS=2
export BATCH_SIZE=64

SLURM_NUMBER="$(sbatch -n $N_NODES -N $N_NODES Control_Model_Slurm.sh | awk '{print $4}')"

sleep 1

tail -f slurm-$SLURM_NUMBER.out