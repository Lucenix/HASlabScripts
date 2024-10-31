#!/bin/sh

# drop cache
echo 1 > /proc/sys/vm/drop_caches

HOSTNAME=$(hostname | cut -d '.' -f 1)
echo "I am $HOSTNAME!"

module load Python/3.11.2-GCCcore-12.2.0-bare CUDA/11.7.0 ncurses

# create statistics directory
mkdir -p $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY\_$LOG

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
spawn_dstat_process dstat $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY\_$LOG/$HOSTNAME/dstat.csv
# spawn nvidia
spawn_nvidia_process nvidia $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY\_$LOG/$HOSTNAME/gpu.csv
# start eBPFs
./run-eBPF-tools.sh start $STAT_DIR/$MODEL\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY\_$LOG/$HOSTNAME

{ time torchrun \
--nnodes $N_NODES \
--nproc_per_node 1 \
--rdzv_id $2 \
--rdzv_backend c10d \
--rdzv_endpoint $1:29500 \
$MAIN_PATH --dist true --model $MODEL --epochs $N_EPOCHS --save_every $SAVE_EVERY --batch_size $BATCH_SIZE --log $LOG $DATA_DIR > $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY\_$LOG/$HOSTNAME/out.out ; } 2>> $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY\_$LOG/$HOSTNAME/out.out ;

join_process() 
{
        echo "utils::join_process"
        $SCREEN_PATH -X -S $1 stuff "^C"
}

join_process dstat
join_process nvidia
./run-tools.sh stop
