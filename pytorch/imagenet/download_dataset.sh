#!/bin/sh
pip install kaggle
kaggle competitions download -c imagenet-object-localization-challenge
sh setup_dataset.sh