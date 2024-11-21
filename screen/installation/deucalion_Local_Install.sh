#!/bin/sh

if [ -z "$1" ]
    then
        echo "Correct usage is sh screen_local_install.sh <absolute_path_to_install_prefix>"
    else
    SCRIPT_DIR="$(dirname -- "$0")"
    sh screen_Download.sh
    sh ncurses_Download.sh
    SLURM_RESULT=$(sbatch <<EOT
#!/bin/sh
#SBATCH --job-name=install_local_screen    # job name
#SBATCH --nodes=1                # number of nodes
#SBATCH --ntasks-per-node=1         # number of MPI task per node
#SBATCH --account=I202400002g
#SBATCH --partition=normal-a100-80
#SBATCH --time=48:00:00

tar zvxf ncurses-6.1.tar.gz
rm ncurses-6.1.tar.gz
cd ncurses-6.1

./configure --prefix=$1 # or $HOME/.local
make
make install
cd $SCRIPT_DIR
rm -rf ncurses-6.1

tar xzvf screen-4.8.0.tar.gz
rm screen-4.8.0.tar.gz
mkdir $1/etc # for install below
cd screen-4.8.0

./configure --prefix=$1
make install &&
install -m 644 ./etc/etcscreenrc $1/etc/screenrc
cd $SCRIPT_DIR
rm -rf screen-4.8.0
EOT
)
    SLURM_NUMBER="$(echo $SLURM_RESULT | awk '{print $4}')"
    while [ ! -e "./slurm-$SLURM_NUMBER.out" ]
    do
    done
    tail -f slurm-$SLURM_NUMBER.out
fi

