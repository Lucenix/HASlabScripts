#!/bin/sh
#SBATCH --job-name=install_pytorch    # job name
#SBATCH --nodes=1                # number of nodes
#SBATCH --ntasks-per-node=1         # number of MPI task per node
#SBATCH --account=haslab
#SBATCH --time=48:00:00 

export SCRIPT_DIR="$(dirname -- "$0")"
SCRATCH="/home/lucenix"
MAIN_PATH="$SCRATCH/HASlabScripts/pytorch/python/main_simple.py"
DSTAT_PATH="$SCRATCH/HASlabScripts/pytorch/python/dstat.py"
DATA_DIR="/projects/a97485/imagenet_subset"
VENV_DIR="$SCRATCH/pytorch_venv"
STAT_DIR="$SCRATCH/statistics/control_subset"
# model is defined in main
MODEL=resnet50
N_EPOCHS=2
BATCH_SIZE=64

# deactivate grafana agents
sudo systemctl stop pmcd

module load Python/3.11.2-GCCcore-12.2.0-bare CUDA/11.7.0

# create statistics directory
mkdir $STAT_DIR

#spawn process
# --$1: process identifier
# --$2: path to the output file
spawn-dstat-process() {
        echo "utils::spawn-dstat-process"
        screen -S $1 -d -m $DSTAT_PATH -tcdrnmg --noheaders --output $2
}

spawn-nvidia-process() {
        echo "utils::spawn-nvidia-smi-process"
        screen -S $1 -d -m nvidia-smi --query-gpu=timestamp,name,pci.bus_id,temperature.gpu,utilization.gpu,utilization.memory --format=csv -f $2 -l 1
}

# Join process
# --$1: process identifier
join-process() {
        echo "utils::join-process"
        screen -X -S $1 stuff "^C"
}

# activate venv
source "${VENV_DIR}/bin/activate"
# spawn dstat
#spawn-dstat-process dstat $STAT_DIR/$MODEL\_$N_EPOCHS\_$BATCH_SIZE.csv
# spawn nvidia
#spawn-nvidia-process nvidia $STAT_DIR/$MODEL\_$N_EPOCHS\_$BATCH_SIZE\_gpu.csv

{ time python3 $MAIN_PATH --epochs $N_EPOCHS --batch_size $BATCH_SIZE $DATA_DIR > $STAT_DIR/$MODEL\_$N_EPOCHS\_$BATCH_SIZE.out ; } 2>> $STAT_DIR/$MODEL\_$N_EPOCHS\_$BATCH_SIZE.out ;

# join processes
#join-process dstat
#join-process nvidia

#python3 ../../dstat.py -cdnm --output ./dstat_arm_output