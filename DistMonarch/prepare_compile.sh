#!/bin/sh
MONARCH_DIR=/projects/I20240002/andrelucena/DistMonarch
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

module load cmake/3.21.3
module load GCC/10.3.0
module load Boost/1.76.0
cd $MONARCH_DIR
if [ ! -d ./build ]; then
    mkdir build
fi
cd build