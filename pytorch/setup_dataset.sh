#!/bin/sh

SCRATCH="/home/gsd/andrelucena/imagenet"
SCRIPT_DIR="$(dirname -- "$0")"
echo "Script found in $SCRIPT_DIR"

cd $SCRATCH
unzip imagenet-object-localization-challenge.zip
mv ILSVRC/Data/CLS-LOC/* ./
cd val
sh $SCRIPT/structure_val_folder.sh
rm LOC*
rm -rf ILSVRC