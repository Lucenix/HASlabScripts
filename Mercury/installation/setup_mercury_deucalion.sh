#!/bin/sh
if [ -z "$1" ]
    then
        echo "Correct usage is sh setup_mercury_deucalion.sh <absolute_path_to_install>"
    else
        sh download_mercury.sh
        export INSTALL_DIR="$1"
        sbatch Install_Mercury_Deucalion.sh
fi