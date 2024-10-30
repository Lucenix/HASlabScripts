#!/bin/sh

HOSTNAME=$(hostname | cut -d '.' -f 1)
echo "I am $HOSTNAME!"

# deactivate grafana agents
sudo systemctl stop pmcd
sudo systemctl stop pmlogger
sudo systemctl stop pmproxy

module load Python/3.11.2-GCCcore-12.2.0-bare CUDA/11.7.0 ncurses

# create statistics directory
export STAT_DIR="/projects/a97485/statistics/eBPFs_subset"
mkdir $STAT_DIR
mkdir $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY

#spawn process
# --$1: process identifier
# --$2: path to the output file
spawn_dstat_process () 
{
        echo "utils::spawn_dstat_process"
        echo $2
        $SCREEN_PATH -S $1 -d -m $DSTAT_PATH -tcdrnmg --noheaders --output $2
}

spawn_nvidia_process () 
{
        echo "utils::spawn-nvidia_smi_process"
        echo $2
        $SCREEN_PATH -S $1 -d -m nvidia-smi --query-gpu=timestamp,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.free,memory.used --format=csv,nounits -f $2 -l 1
}

# activate venv
source "${VENV_DIR}/bin/activate"
# spawn dstat
spawn_dstat_process dstat $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY/$HOSTNAME.csv
# spawn nvidia
spawn_nvidia_process nvidia $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY/$HOSTNAME\_gpu.csv
# start eBPFs
./run-eBPF-tools.sh start $MODEL\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY

{ time torchrun \
--nnodes $N_NODES \
--nproc_per_node 1 \
--rdzv_id $2 \
--rdzv_backend c10d \
--rdzv_endpoint $1:29500 \
$MAIN_PATH --epochs $N_EPOCHS --save_every 1 $DATA_DIR > $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY/$HOSTNAME.out ; } 2>> $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY/$HOSTNAME.out ;

join_process() 
{
        echo "utils::join_process"
        $SCREEN_PATH -X -S $1 stuff "^C"
}

join_process dstat
join_process nvidia
./run-tools.sh stop
