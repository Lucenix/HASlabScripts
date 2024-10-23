#!/bin/sh

if [ -z "$1" ]
    then
        echo "Correct usage is sh screen_local_install.sh <absolute_path_to_install_prefix>"
    else
    wget "https://ftp.gnu.org/gnu/screen/screen-4.8.0.tar.gz" #download screen
    SLURM_RESULT=$(sbatch <<EOT
#!/bin/sh
#SBATCH --job-name=install_local_screen    # job name
#SBATCH --nodes=1                # number of nodes
#SBATCH --ntasks-per-node=1         # number of MPI task per node
#SBATCH --account=haslab
#SBATCH --time=48:00:00

module load ncurses/6.3
PREFIX=$1

tar xzvf screen-4.8.0.tar.gz
rm screen-4.8.0.tar.gz
mkdir $1/etc # for install below
cd screen-4.8.0

./configure --prefix=$1
make install &&
install -m 644 ./etc/etcscreenrc $1/etc/screenrc
rm -rf screen-4.8.0
EOT
)
    SLURM_NUMBER="$(echo $SLURM_RESULT | awk '{print $4}')"
    while [ ! -e "./slurm-$SLURM_NUMBER.out" ]
    do
    done
    tail -f slurm-$SLURM_NUMBER.out
fi

