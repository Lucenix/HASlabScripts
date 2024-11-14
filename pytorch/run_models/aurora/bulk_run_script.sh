#!/bin/bash

# if [ -z $1 ] ; then
#     echo "First argument needed: script to bulk run for each combination"
# else
# 
#     for model in "alexnet" "resnet50"
#     do
#         for n_epoch in 2 3
#         do
#             for batch_size in 32 64
#             do
#                 for save_every in 0 1
#                 do
#                     for log in true false
#                     do
#                         $1 $model $n_epoch $batch_size $save_every $log
#                     done
#                 done
#             done
#         done
#     done
# fi

if [ -z $1 ] ; then
    echo "First argument needed: script to bulk run for each combination"
else

    for model in "resnet50"
    do
        for n_epoch in 2
        do
            for batch_size in 64
            do
                for save_every in 0 1
                do
                    for log in true false
                    do
                        $1 $model $n_epoch $batch_size $save_every $log
                    done
                done
            done
        done
    done
fi
