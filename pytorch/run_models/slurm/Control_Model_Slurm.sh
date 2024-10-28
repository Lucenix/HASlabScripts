#!/bin/sh
#SBATCH --job-name=install_pytorch    # job name
#SBATCH --account=haslab
#SBATCH --time=48:00:00 
#SBATCH --partition=rtx4060

#{ time python3 $MAIN_PATH --epochs $N_EPOCHS --batch_size $BATCH_SIZE $DATA_DIR > $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY.out ; } 2>> $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY.out ;

srun setup_single_node.sh

head_node_ip=$(srun --nodes=1 hostname --ip-address | uniq)

{ time srun torchrun \
--nnodes 2 \
--nproc_per_node 1 \
--rdzv_id $RANDOM \
--rdzv_backend c10d \
--rdzv_endpoint $head_node_ip:29500 \
$MAIN_PATH --epochs $N_EPOCHS --save_every 1 $DATA_DIR > $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY\_$SLURMD_NODENAME.out ; } 2>> $STAT_DIR/$MODEL\_$N_NODES\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY\_$SLURMD_NODENAME.out ;

srun clean_single_node.sh

#python3 ../../dstat.py -cdnm --output ./dstat_arm_output