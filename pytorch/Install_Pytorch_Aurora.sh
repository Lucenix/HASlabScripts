#!/bin/sh
if [ -z "$1" ]
    then
        echo "Correct usage is sh Install_Pytorch_Aurora.sh <absolute_path_to_install>"
    else
        #rm -rf "$1/pytorch/"
        mv pytorch $1

        cd $1/pytorch/scripts/fujitsu
        sh ./1_python.sh   
        sh ./3_venv.sh          
        sh ./4_numpy_scipy.sh   
        sh ./5_pytorch.sh       
        sh ./6_vision.sh        
        sh ./7_horovod.sh       
        sh ./8_libtcmalloc.sh
fi