#!/bin/sh

SCRATCH="/home/gsd/andrelucena/imagenet"
SCRIPT_DIR="$(dirname -- "$0")"
echo "Script found in $SCRIPT_DIR"

unzip imagenet-object-localization-challenge.zip
mv ILSVRC/Data/CLS-LOC/* $SCRATCH
cd $SCRATCH/val
sh $SCRIPT_DIR/structure_val_folder.sh
rm LOC*
rm -rf ILSVRC