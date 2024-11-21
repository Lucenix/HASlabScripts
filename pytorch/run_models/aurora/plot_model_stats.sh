#!/bin/sh

SCRATCH="/home/gsd/andrelucena"
PLOTTER_DIR="$SCRATCH/scripts/eBPFs-tools/parser"

if [ -z $1 ] ; then
        TEST_NAME="test"
else
        TEST_NAME="$1"
fi
if [ -z $2 ] ; then
        MODEL="resnet50"
else
        MODEL=$2
fi
if [ -z $3 ] ; then
        N_EPOCHS=2
else
        N_EPOCHS=$3
fi
if [ -z $4 ] ; then
        BATCH_SIZE=64
else
        BATCH_SIZE=$4
fi
if [ -z $5 ] ; then
        SAVE_EVERY=1
else
        SAVE_EVERY=$5
fi
if [ -z $6 ] ; then
        LOG="false"
else
        LOG=$6
fi

TEST_TITLE=$MODEL\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY\_$LOG
RESULT_DIR="$SCRATCH/statistics/$TEST_NAME/$TEST_TITLE"
RELATIVE_PLOT_DIR=$TEST_NAME/$TEST_TITLE

cd $PLOTTER_DIR

python ./parse-res.py $RESULT_DIR $RELATIVE_PLOT_DIR