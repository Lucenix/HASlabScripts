#!/bin/sh
git clone https://github.com/fujitsu/pytorch.git
mv pytorch 
cd pytorch # From now on, we'll call this directory PYTORCH_TOP
git checkout -b fujitsu_v1.10.1_for_a64fx origin/fujitsu_v1.10.1_for_a64fx
# Fix env.src
cd scripts/fujitsu
sed -i 's/fjenv_offline_install:=[^}]*/fjenv_offline_install:=true/' env.src 
sed -i 's/TCSDS_PATH=[^\n]*/TCSDS_PATH=\/opt\/FJSVstclanga\/cp-1.0.21.02a\t# CP  (FX700)/' env.src
./1_python.sh        download        # Download Python
./3_venv.sh          download        # Download Python modules for PyTorch
./4_numpy_scipy.sh   download        # Download NumPy and SciPy
./5_pytorch.sh       download        # Download Modules for PyTorch build
./6_vision.sh        download        # Download TorchVision
./7_horovod.sh       download        # Download Horovod
./8_libtcmalloc.sh   download        # Download tcmalloc
cd ../..