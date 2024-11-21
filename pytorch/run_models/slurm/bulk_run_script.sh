#!/bin/bash

if [ -z $1 ] ; then
    echo "First argument needed: script to run for each combination"
else

    for model in "alexnet" "resnet50"
    do
        for n_nodes in 4
        do
            for n_epoch in 2 3
            do
                for batch_size in 32 64
                do
                    for save_every in 0 1
                    do
                        for log in true false
                        do
                            ./sbatch_run_model.sh $model $n_nodes $n_epoch $batch_size $save_every $log $1
                        done
                    done
                done
            done
        done
    done
fi