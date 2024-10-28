#!/bin/sh
sbatch <<EOT
#!/bin/sh
#SBATCH --job-name=install_pytorch    # job name
#SBATCH --nodes=1                # number of nodes
#SBATCH --ntasks-per-node=1         # number of MPI task per node
#SBATCH --account=i20240002a
#SBATCH --time=48:00:00 
#SBATCH --partition=normal-arm

module load Python/3.11.3-GCCcore-12.3.0
module load cmake/3.21.3
set -e

rm -rf "$1/pytorch/"
mv pytorch $1

cd $1/pytorch/scripts/fujitsu
sh ./1_python.sh   
sh ./3_venv.sh          
sh ./4_numpy_scipy.sh   
sh ./5_pytorch.sh       
sh ./6_vision.sh        
sh ./7_horovod.sh       
sh ./8_libtcmalloc.sh
EOT