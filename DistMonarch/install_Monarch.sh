#!/bin/sh
# dependencies must be in install_dir
export INSTALL_DIR="$1/DistMonarch/dependencies/"
export SCRIPT_DIR="$(dirname -- "$0")"
echo "Script found in $SCRIPT_DIR"

# monarch
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
git clone git@github.com:franl08/DistMonarch.git
cd DistMonarch
git checkout mercury-integration
cd ..

# abseil-cpp
git clone https://github.com/abseil/abseil-cpp.git
# yaml-cpp
git clone https://github.com/jbeder/yaml-cpp.git

# mercury
sh $SCRIPT_DIR/../Mercury/Download_Mercury.sh

sbatch <<EOT
#!/bin/sh
#SBATCH --job-name=install_monarch
#SBATCH --time=48:00:00
#SBATCH --account=i20240002g
#SBATCH --partition=normal-a100-80

module load cmake/3.21.3
module load GCC/10.3.0
module load Boost/1.76.0

rm -rf "$1/DistMonarch/"
mv DistMonarch $1
mkdir $INSTALL_DIR

cd abseil-cpp
git checkout 20210324.2
mkdir build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR -DCMAKE_POSITION_INDEPENDENT_CODE=TRUE -DCMAKE_CXX_STANDARD=17 -DCMAKE_CXX_STANDARD_REQUIRED=ON -DCMAKE_CXX_EXTENSIONS=OFF
cmake --build . --target install
cd ../..
rm -rf abseil-cpp

cd yaml-cpp
git checkout yaml-cpp-0.6.3
mkdir build 
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR -DCMAKE_POSITION_INDEPENDENT_CODE=TRUE
make install
cd ../..
rm -rf yaml-cpp

sh $SCRIPT_DIR/../Mercury/Install_Mercury_Slurm.sh

cd $1
cd DistMonarch/pastor
mkdir build 
cd build
cmake ..
make
export MONARCH_DIR=$(pwd)
EOT