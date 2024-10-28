#!/bin/sh
sbatch <<EOT
#!/bin/sh
#SBATCH --job-name=install_pytorch    # job name
#SBATCH --nodes=1                # number of nodes
#SBATCH --ntasks-per-node=1         # number of MPI task per node
#SBATCH --account=haslab
#SBATCH --time=48:00:00 

module load Python/3.11.2-GCCcore-12.2.0-bare CUDA/11.7.0
python -m venv $1/pytorch_venv
source $1/pytorch_venv/bin/activate
pip install --upgrade pip
python -m pip install -r pytorch_venv_requirements.txt
EOT