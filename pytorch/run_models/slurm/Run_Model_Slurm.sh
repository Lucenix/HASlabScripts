#!/bin/sh
#SBATCH --job-name=install_pytorch    # job name
#SBATCH --account=haslab
#SBATCH --time=48:00:00 
#SBATCH --partition=rtx4060

#{ time python3 $MAIN_PATH --epochs $N_EPOCHS --batch_size $BATCH_SIZE $DATA_DIR > $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY.out ; } 2>> $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY.out ;

module load Python/3.11.2-GCCcore-12.2.0-bare CUDA/11.7.0 ncurses
source "${VENV_DIR}/bin/activate"
head_node_ip=$(srun --nodes=1 hostname --ip-address | uniq)

srun ${SINGLE_NODE_SCRIPT} $head_node_ip $RANDOM

#srun clean_single_node.sh

#python3 ../../dstat.py -cdnm --output ./dstat_arm_output
