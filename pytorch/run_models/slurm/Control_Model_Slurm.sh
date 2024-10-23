#!/bin/sh
#SBATCH --job-name=install_pytorch    # job name
#SBATCH --ntasks-per-node=1         # number of MPI task per node
#SBATCH --account=haslab
#SBATCH --time=48:00:00 
#SBATCH --partition=rtx4060

# deactivate grafana agents
sudo systemctl stop pmcd
sudo systemctl stop pmlogger
sudo systemctl stop pmproxy

module load Python/3.11.2-GCCcore-12.2.0-bare CUDA/11.7.0

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
spawn_dstat_process dstat $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY.csv
# spawn nvidia
spawn_nvidia_process nvidia $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY\_gpu.csv

{ time python3 $MAIN_PATH --epochs $N_EPOCHS --batch_size $BATCH_SIZE $DATA_DIR > $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY.out ; } 2>> $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY.out ;

# join processes
join_process dstat
join_process nvidia

#python3 ../../dstat.py -cdnm --output ./dstat_arm_output

SLURM_NUMBER="$(echo $SLURM_RESULT | awk '{print $4}')"

sleep 5

tail -f slurm-$SLURM_NUMBER.out