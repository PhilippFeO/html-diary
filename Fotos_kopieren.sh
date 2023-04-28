#!/usr/bin/env bash
# nemo script for hard linking selected fotos into the according diary folder

today=$(date "+%F-%A")
month=$(date "+%m-%B")
year=$(date +%Y)

path=~/.tagebuch/$year/$month/$today

# If directory exists, hard link marked images into it
for img in $NEMO_SCRIPT_SELECTED_FILE_PATHS; do
	ln $img $path
done

nemo --quit
