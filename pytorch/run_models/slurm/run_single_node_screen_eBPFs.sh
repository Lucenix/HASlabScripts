#!/bin/sh

HOSTNAME=$(hostname | cut -d '.' -f 1)
echo "I am $HOSTNAME!"

module load Python/3.11.2-GCCcore-12.2.0-bare CUDA/11.7.0 ncurses

RESULT_DIR="$SCRATCH/statistics/$TEST_NAME/$TEST_TITLE/$HOSTNAME"
RELATIVE_PLOT_DIR=$TEST_NAME/$TEST_TITLE/$HOSTNAME

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
# start eBPFs
$SCRIPT_DIR/pytorch/run_models/slurm/run-eBPF-tools.sh start $RESULT_DIR

{ time torchrun \
--nnodes $N_NODES \
--nproc_per_node 1 \
--rdzv_id $2 \
--rdzv_backend c10d \
--rdzv_endpoint $1:29500 \
$MAIN_PATH --dist true --model $MODEL --epochs $N_EPOCHS --save_every $SAVE_EVERY --batch_size $BATCH_SIZE --enable_log $LOG $DATA_DIR > $RESULT_DIR/out.out ; } 2>> $RESULT_DIR/out.out ;

join_process() 
{
        echo "utils::join_process"
        $SCREEN_PATH -X -S $1 stuff "^C"
}

join_process dstat
join_process nvidia
$SCRIPT_DIR/pytorch/run_models/slurm/run-eBPF-tools.sh stop $RESULT_DIR

cd $PLOTTER_DIR

python ./parse-res.py $RESULT_DIR $RELATIVE_PLOT_DIR