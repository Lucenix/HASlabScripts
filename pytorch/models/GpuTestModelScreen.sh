#!/bin/bash

SCRATCH="/home/gsd/andrelucena"
MODEL_DIR="$SCRATCH/DL_pytorch_models"
DATA_DIR="/home/gsd/goncalo/imagenet_subset"
VENV_DIR="$SCRATCH/pytorch_venv"
STAT_DIR="$SCRATCH/statistics/control_subset"
MODEL="alexnet"
N_EPOCHS=2
BATCH_SIZE=1024

# deactivate grafana agents
sudo systemctl stop pmcd

# create statistics directory
mkdir $STAT_DIR

#spawn process
# --$1: process identifier
# --$2: path to the output file
function spawn-dstat-process {
        echo "utils::spawn-dstat-process"
        screen -S $1 -d -m $MODEL_DIR/dstat.py -tcdrnmg --noheaders --output $2
}

function spawn-nvidia-process {
        echo "utils::spawn-nvidia-smi-process"
        screen -S $1 -d -m nvidia-smi --query-gpu=timestamp,name,pci.bus_id,temperature.gpu,utilization.gpu,utilization.memory --format=csv -f $2 -l 1
}

# Join process
# --$1: process identifier
function join-process {
        echo "utils::join-process"
        screen -X -S $1 stuff "^C"
}

# activate venv
source "${VENV_DIR}/bin/activate"

# spawn dstat
spawn-dstat-process dstat $STAT_DIR/$MODEL\_$N_EPOCHS\_$BATCH_SIZE.csv
# spawn nvidia
spawn-nvidia-process nvidia $STAT_DIR/$MODEL\_$N_EPOCHS\_$BATCH_SIZE\_gpu.csv

{ time python3 $MODEL_DIR/main.py -a $MODEL --epochs $N_EPOCHS --batch-size $BATCH_SIZE $DATA_DIR > $STAT_DIR/$MODEL\_$N_EPOCHS\_$BATCH_SIZE.out ; } 2>> $STAT_DIR/$MODEL\_$N_EPOCHS\_$BATCH_SIZE.out ;

# join processes
join-process dstat
join-process nvidia

#python3 ../../dstat.py -cdnm --output ./dstat_arm_output