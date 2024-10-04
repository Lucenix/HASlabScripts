#!/bin/sh
#SBATCH --job-name=collector_over_tensorflow    # job name
#SBATCH --nodes=1            # number of nodes
#SBATCH --ntasks-per-node=1  # number of MPI task per node
#SBATCH --account=i20240002g
#SBATCH --time=48:00:00
#SBATCH --partition=normal-a100-80

rm -r /tmp/openimages_tfrecords/
rm -r /tmp/middleware_output
module load CUDA/11.3.1 Boost/1.76.0 hwloc/2.4.1 NCCL/2.10.3 cuDNN/8.2.1 cmake/3.21.3 GCCcore/10.3.0 GDB

MODEL_NUMBER=2
BATCH_SIZE=512
N_EPOCHS=1

DATA_DIR="/projects/I20240002/franeves08/train"
VENV_DIR="/projects/I20240002/andrelucena/tensorflow-venv2"
MODEL_DIR="/projects/I20240002/andrelucena/TensorflowScripts/models/official-models-2.1.0/official/vision/image_classification"
COLLECTOR_DIR="/projects/I20240002/andrelucena/trace-collector/build"

export PYTHONPATH=$PYTHONPATH:/projects/I20240002/andrelucena/TensorflowScripts/models/official-models-2.1.0

source "${VENV_DIR}/bin/activate"
echo "PYTHONPATH is ${PYTHONPATH}"

if [ $MODEL_NUMBER == 0 ]
then
	MODEL="sns_vgg19.py"

elif [ $MODEL_NUMBER == 1 ]
then
    MODEL="sns_inceptionv3.py"

elif [ $MODEL_NUMBER == 2 ]
then
    MODEL="sns_shufflenet.py"

elif [ $MODEL_NUMBER == 3 ]
then
    MODEL="sns_resnet18.py"

elif [ $MODEL_NUMBER == 4 ]
then
    MODEL="sns_lenet.py"

elif [ $MODEL_NUMBER == 5 ]
then
    MODEL="sns_alexnet.py"

fi
# correr o teste
gdb -x collector.gdb --args python $MODEL_DIR/$MODEL --skip_eval --train_epochs=$N_EPOCHS --model_dir="/tmp/checkpointing" --data_dir=$DATA_DIR --task_index=0 --num_gpus=1