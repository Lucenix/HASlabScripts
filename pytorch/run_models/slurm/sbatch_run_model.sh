#!/bin/sh

export SCRATCH="/projects/a97485"
export SCRIPT_DIR="$SCRATCH/HASLabScripts"
export DSTAT_PATH="$SCRIPT_DIR/pytorch/python/dstat.py"
export MAIN_PATH="$SCRIPT_DIR/pytorch/python/main_simple_ult.py"
export SCREEN_PATH="$SCRATCH/bin/screen"
export DATA_DIR="$SCRATCH/imagenet_subset"
export VENV_DIR="$SCRATCH/pytorch_venv"
export PLOT_PATH="$SCRATCH/HASLabScripts/eBPFs-tools/parser/parse-res.py"

if [ -z $1 ] ; then
        export MODEL="resnet50"
else
        export MODEL=$1
fi
if [ -z $2 ] ; then
        export N_NODES=2
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
if [ -z $6 ] ; then
        export LOG="false"
else
        export LOG=$6
fi
if [ -z $7 ] ; then
        export SINGLE_NODE_SCRIPT="$SCRATCH/HASLabScripts/pytorch/run_models/slurm/run_single_node_screen.sh"
else
        export SINGLE_NODE_SCRIPT=$7
fi

SLURM_NUMBER="$(sbatch -n $N_NODES -N $N_NODES Run_Model_Slurm.sh | awk '{print $4}')"

#sleep 1

#tail -f slurm-$SLURM_NUMBER.out
