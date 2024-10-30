#!/bin/sh

export SCRATCH="/home/lucenix"
export DSTAT_PATH="$SCRATCH/HASlabScripts/pytorch/python/dstat.py"
export DATA_DIR="/projects/a97485/imagenet_subset"
export VENV_DIR="$SCRATCH/pytorch_venv"
export STAT_DIR="/projects/a97485/statistics/control_subset"
export SCREEN_PATH="$SCRATCH/bin/screen"
export SINGLE_NODE_SCRIPT="$SCRATCH/HaslabScripts/pytorch/run_models/slurm/run_single_node_screen_eBPFs.sh"
# model is defined in main
if [ -z $1 ] ; then
        export MODEL="resnet50"
else
        export MODEL=$1
fi
if [ -z $2 ] ; then
        export N_NODES=4
else
        export N_NODES=$2
fi
if [ -z $3 ] ; then
        export N_EPOCHS=2
else
        export N_EPOCHS=$3
fi
if [ -z $4 ] ; then
        export BATCH_SIZE=64
else
        export BATCH_SIZE=$4
fi
if [ -z $5 ] ; then
        export SAVE_EVERY=1
else
        export SAVE_EVERY=$5
fi
export MAIN_PATH="$SCRATCH/HASlabScripts/pytorch/python/main_simple_dist_$MODEL.py"

SLURM_NUMBER="$(sbatch -n $N_NODES -N $N_NODES Run_Model_Slurm.sh | awk '{print $4}')"

sleep 1

tail -f slurm-$SLURM_NUMBER.out
