#!/bin/sh
#SBATCH --job-name=test_mercury
#SBATCH --time=48:00:00
#SBATCH --account=i20240002g

module load cmake/3.21.3
module load GCC/10.3.0
module load Boost/1.76.0

cd mercury-2.3.1/build/
ctest -W .
