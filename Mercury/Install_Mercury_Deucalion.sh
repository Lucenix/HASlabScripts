#!/bin/sh
#SBATCH --job-name=install_mercury
#SBATCH --time=48:00:00
#SBATCH --account=i20240002g

module load cmake/3.21.3
module load GCC/10.3.0
module load Boost/1.76.0

echo "Installing Mercury in $INSTALL_DIR" 

mkdir $INSTALL_DIR

bzip2 -dc libfabric-1.22.0.tar.bz2 | tar xvf -
rm libfabric-1.22.0.tar.bz2
cd libfabric-1.22.0
./configure --prefix=$INSTALL_DIR --disable-sockets --disable-opx --disable-psm2 --disable-psm3 --disable-tcp \
    --disable-udp --disable-usnic --disable-shm --disable-efa && make -j 32 && make install
cd ..

bzip2 -dc mercury-2.3.1.tar.bz2 | tar xvf -
rm mercury-2.3.1.tar.bz2
cd mercury-2.3.1
mkdir build 
cd build
cmake .. -DBUILD_SHARED_LIBS=ON -DBUILD_TESTING=ON -DBUILD_TESTING_PERF=OFF -DBUILD_TESTING_UNIT=ON \
    -DMERCURY_ENABLE_DEBUG=ON -DMERCURY_TESTING_ENABLE_PARALLEL=OFF -DMERCURY_USE_BOOST_PP=ON -DMERCURY_USE_CHECKSUMS=ON \
    -DMERCURY_USE_SYSTEM_BOOST=OFF -DMERCURY_USE_SYSTEM_MCHECKSUM=OFF -DMERCURY_USE_XDR=OFF -DNA_USE_DYNAMIC_PLUGINS=OFF \
    -DNA_USE_BMI=OFF -DNA_USE_MPI=OFF -DNA_USE_OFI=ON -DNA_USE_PSM=OFF -DNA_USE_PSM2=OFF -DNA_USE_SM=OFF -DNA_USE_UCX=OFF \
    -DOFI_INCLUDE_DIR=$INSTALL_DIR/include -DOFI_LIBRARY=$INSTALL_DIR/lib/libfabric.so -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR
make && make install
cd ../..
rm -r libfabric-1.22.0
rm -r mercury-2.3.1