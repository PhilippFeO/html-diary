#!/bin/bash
# Function because I work with return values
# Return values are stored in $?

check_today_dir_exists() {
    # $1 path to search
    for dir in "$1"*; do
        if [ -d $dir ]; then
            return 1 # Failure, directory for today already exists
        fi
    done
    return 0 # Success, directory for today DOESN'T exists
}

check_today_dir_exists $1
