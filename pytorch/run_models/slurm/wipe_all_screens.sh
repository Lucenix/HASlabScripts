#!/bin/sh

module load ncurses
SCRATCH="/projects/a97485"
$SCRATCH/bin/screen -S alloc -d -m salloc -N4 -A haslab

for node in "aurora03" "aurora04" "aurora05" "aurora06"
do
    echo $node
    ssh $node "module load ncurses; /projects/a97485/bin/screen -wipe"
done
scancel --user=lucenix
screen -S alloc -X stop