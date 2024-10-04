#!/bin/sh

SCRATCH="/home/gsd/andrelucena/imagenet"

cd $SCRATCH
unzip imagenet-object-localization-challenge.zip
mv ILSVRC/Data/CLS-LOC/* ./
cd val
wget -qO- https://raw.githubusercontent.com/soumith/imagenetloader.torch/master/valprep.sh > run.sh
sh run.sh
rm run.sh
rm LOC*
rm -rf ILSVRC