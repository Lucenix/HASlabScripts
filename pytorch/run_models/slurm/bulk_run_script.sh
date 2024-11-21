#!/bin/bash

 if [ -z $1 -o -z $2 ] ; then
     echo "Usage: $0 <absolute path for script to run> <output dir name relative to statistics dir in machine>"
 else
    for model in "alexnet" "resnet50"
    do
        for n_nodes in 4
        do
            for n_epoch in 2
            do
                for batch_size in 32 64
                do
                    for save_every in 0 1
                    do
                        for log in true false
                        do
<<<<<<< HEAD
                            ./sbatch_run_model.sh $model $n_nodes $n_epoch $batch_size $save_every $log $1
=======
                            ./sbatch_run_model.sh $1 $2 $model $n_nodes $n_epoch $batch_size $save_every $log
>>>>>>> e867054bf39c3a8ab05140002a3cf9fbe723c593
                        done
                    done
                done
            done
        done
    done
fi