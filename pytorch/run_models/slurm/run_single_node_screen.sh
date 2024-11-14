#!/bin/sh

# drop cache
HOSTNAME=$(hostname | cut -d '.' -f 1)
echo "I am $HOSTNAME!"

module load Python/3.11.2-GCCcore-12.2.0-bare CUDA/11.7.0 ncurses

TEST_TITLE=$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY\_$LOG
RESULT_DIR=$STAT_DIR/$TEST_TITLE/$HOSTNAME

# create statistics directory
rm -r $RESULT_DIR
mkdir -p $RESULT_DIR

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
spawn_dstat_process dstat $RESULT_DIR/dstat.csv
# spawn nvidia
spawn_nvidia_process nvidia $RESULT_DIR/gpu.csv

{ time torchrun \
--nnodes $N_NODES \
--nproc_per_node 1 \
--rdzv_id $2 \
--rdzv_backend c10d \
--rdzv_endpoint $1:29500 \
$MAIN_PATH --epochs $N_EPOCHS --model $MODEL --enable_log $LOG --batch_size $BATCH_SIZE --save_every $SAVE_EVERY $DATA_DIR > $RESULT_DIR/out.out ; } 2>> $RESULT_DIR/out.out ;

join_process() 
{
        echo "utils::join_process"
        $SCREEN_PATH -X -S $1 stuff "^C"
}

join_process dstat
join_process nvidia

cd $PLOT_DIR

python $PLOT_DIR/parse-res.py $RESULT_DIR $TEST_TITLE