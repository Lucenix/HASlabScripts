#!/bin/sh

SCRATCH="/home/gsd/andrelucena"
MAIN_PATH="$SCRATCH/scripts/pytorch/python/main_full.py"
DSTAT_PATH="$SCRATCH/scripts/pytorch/python/dstat.py"
DATA_DIR="/home/gsd/goncalo/imagenet_subset"
VENV_DIR="$SCRATCH/pytorch_venv"
STAT_DIR="$SCRATCH/statistics/control_subset"
MODEL="resnet50"
N_EPOCHS=2
BATCH_SIZE=64

# deactivate grafana agents
sudo systemctl stop pmcd
sudo systemctl stop pmlogger
sudo systemctl stop pmproxy

# create statistics directory
mkdir $STAT_DIR

#spawn process
# --$1: process identifier
# --$2: path to the output file
spawn_dstat_process () 
{
        echo "utils::spawn_dstat_process"
        $SCREEN_PATH -S $1 -d -m $DSTAT_PATH -tcdrnmg --noheaders --output $2
}

spawn_nvidia_process () 
{
        echo "utils::spawn-nvidia_smi_process"
        $SCREEN_PATH -S $1 -d -m nvidia-smi --query-gpu=timestamp,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.free,memory.used --format=csv,nounits -f $2 -l 1
}

# Join process
# --$1: process identifier
join_process() 
{
        echo "utils::join_process"
        $SCREEN_PATH -X -S $1 stuff "^C"
}

# activate venv
source "${VENV_DIR}/bin/activate"

# spawn dstat
spawn_dstat_process dstat $STAT_DIR/$MODEL\_$N_EPOCHS\_$BATCH_SIZE.csv
# spawn nvidia
spawn_nvidia_process nvidia $STAT_DIR/$MODEL\_$N_EPOCHS\_$BATCH_SIZE\_gpu.csv

{ time python3 $MAIN_PATH -a $MODEL --epochs $N_EPOCHS --batch-size $BATCH_SIZE $DATA_DIR > $STAT_DIR/$MODEL\_$N_EPOCHS\_$BATCH_SIZE.out ; } 2>> $STAT_DIR/$MODEL\_$N_EPOCHS\_$BATCH_SIZE.out ;

# join processes
join_process dstat
join_process nvidia

#python3 ../../dstat.py -cdnm --output ./dstat_arm_output