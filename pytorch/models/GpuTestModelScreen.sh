#!/bin/bash

SCRATCH="/home/gsd/andrelucena"
MODEL_DIR="$SCRATCH/DL_pytorch_models"
DATA_DIR="$SCRATCH/imagenet"
VENV_DIR="$SCRATCH/pytorch_venv"
STAT_DIR="$SCRATCH/statistics/control/"
MODEL="resnet152"
N_EPOCHS=3
BATCH_SIZE=32

#spawn dstat process
# --$1: process identifier
# --$2: path to the output file
function spawn-dstat-process {
        echo "utils::spawn-dstat-process"
        screen -S $1 -d -m $MODEL_DIR/dstat.py -tcdrnmg --noheaders --output $2
}

# Join dstat process
# --$1: process identifier
function join-dstat-process {
        echo "utils::join-dstat-process"
        screen -X -S $1 stuff "^C"
}

source "${VENV_DIR}/bin/activate"
echo "PYTHONPATH is ${PYTHONPATH}"

# spawn dstat
spawn-dstat-process run $STAT_DIR/$MODEL\_$N_EPOCHS\_$BATCH_SIZE.csv

time python3 $MODEL_DIR/main.py -a $MODEL --epochs $N_EPOCHS --batch-size $BATCH_SIZE $DATA_DIR > $STAT_DIR/$MODEL\_$N_EPOCHS\_$BATCH_SIZE.out

# join dstat
join-dstat-process run

#python3 ../../dstat.py -cdnm --output ./dstat_arm_output