#!/bin/bash
JOB_NUMBER="$(sbatch $1 | awk '{print $4}')"
sleep 5
tail -f slurm-$JOB_NUMBER.out