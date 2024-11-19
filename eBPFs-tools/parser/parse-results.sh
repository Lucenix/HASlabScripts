#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 /path/to/directory"
  exit 1
fi

input_directory="$1"

for folder in "$input_directory"/*; do
  if [ -d "$folder" ]; then
    folder_name=$(basename "$folder")
    
    python parse-res.py "$folder" "$folder_name"
    
    if [ $? -ne 0 ]; then
      echo "!!Error parsing $folder_name"
    else
      echo "--Parsed $folder_name"
    fi
  fi
done
