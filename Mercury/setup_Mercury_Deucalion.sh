#!/bin/sh
if [ -z "$1" ]
    then
        echo "Correct usage is sh setup_Mercury_Deucalion <absolute_path_to_install>"
    else
        sh Download_Mercury.sh
        export INSTALL_DIR="$1"
        sbatch Install_Mercury_Deucalion.sh
fi