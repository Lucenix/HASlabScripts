#!/bin/sh

HOSTNAME=$(hostname --ip-address)
echo "I am $HOSTNAME!"
# deactivate grafana agents
sudo systemctl stop pmcd
sudo systemctl stop pmlogger
sudo systemctl stop pmproxy

module load Python/3.11.2-GCCcore-12.2.0-bare CUDA/11.7.0 ncurses

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

# activate venv
source "${VENV_DIR}/bin/activate"
# spawn dstat
spawn_dstat_process dstat $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY\_$HOSTNAME.csv
# spawn nvidia
spawn_nvidia_process nvidia $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY\_$HOSTNAME\_gpu.csv