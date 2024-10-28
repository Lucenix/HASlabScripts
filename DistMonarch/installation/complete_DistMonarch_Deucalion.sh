#!/bin/sh
if [ -z "$1" ]
    then
        echo "Correct usage is sh complete_DistMonarch_Deucalion.sh <absolute_path_to_install>"
    else
        sh Install_Monarch.sh $1
fi