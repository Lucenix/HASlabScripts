#!/bin/sh

SCRATCH="/home/gsd/andrelucena"
PLOT_DIR="$SCRATCH/scripts/eBPFs-tools/parser"

if [ -z $1 ] ; then
        MODEL="resnet50"
else
        MODEL=$1
fi
if [ -z $2 ] ; then
        N_EPOCHS=2
else
        N_EPOCHS=$2
fi
if [ -z $3 ] ; then
        BATCH_SIZE=64
else
        BATCH_SIZE=$3
fi
if [ -z $4 ] ; then
        SAVE_EVERY=1
else
        SAVE_EVERY=$4
fi
if [ -z $5 ] ; then
        LOG="false"
else
        LOG=$5
fi

TEST_TITLE=$MODEL\_$N_EPOCHS\_$BATCH_SIZE\_$SAVE_EVERY\_$LOG
RESULT_DIR=$STAT_DIR/$TEST_TITLE

cd $PLOT_DIR

python $PLOT_DIR/parse-res.py $RESULT_DIR $TEST_TITLE