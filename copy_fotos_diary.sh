#!/bin/bash
# nemo action for hard linking selected fotos into the apropiate folder of the diary

today=$(date "+%F-%A")
month=$(date "+%m-%B")
year=$(date +%Y)

path=~/.tagebuch/$year/$month/$today

# If directory exists, hard link selected images into it
if [ -d "$path" ]; then
	for img in "$@"; do
		ln $img $path
	done
fi

nemo --quit
