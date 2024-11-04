#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

DIR="$1"

if [ ! -d "$DIR" ]; then
    echo "Error: $DIR is not a directory."
    exit 1
fi

all_well_formatted=true
not_well_formatted=()

for file in "$DIR"/*; do
    if [ -f "$file" ]; then
        read -r first_line < "$file"
        
        if [[ "$first_line" != "#!/usr/bin/env bpftrace" ]]; then
            all_well_formatted=false
            not_well_formatted+=("$file")
        fi
    fi
done

if $all_well_formatted; then
    echo "All files have #!/usr/bin/env bpftrace"
else
    echo "Some files don't have #!/usr/bin/env bpftrace"
    for file in "${not_well_formatted[@]}"; do
        echo " - $file"
    done
fi

