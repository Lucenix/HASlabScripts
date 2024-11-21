#!/bin/bash

 if [ -z $1 -o -z $2 ] ; then
     echo "Usage: $0 <absolute path for script to run> <output dir name relative to statistics dir in machine>"
 else
     for model in "alexnet" "resnet50"
     do
         for n_epoch in 2
         do
             for batch_size in 32 64
             do
                 for save_every in 0 1
                 do
                     for log in true false
                     do
                         $1 $2 $model $n_epoch $batch_size $save_every $log
                     done
                 done
             done
         done
     done
 fi
