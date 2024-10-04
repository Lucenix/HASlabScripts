#!/bin/sh
if [ -z "$1" ]
    then
        echo "Correct usage is sh Setup_PyTorch_Deucalion.sh <absolute_path_to_install>"
    else
        sh Download_PyTorch.sh
        sh Install_PyTorch_Deucalion.sh $1
fi