#!/usr/bin/env bash
# nemo script for hard linking selected fotos into the according diary folder

today=$(date +%F)
month_nmb=$(date +%m)
month_name=$(date +%B)
year=$(date +%Y)

path=~/.tagebuch/$year/$month_nmb-$month_name/$today

# If directory exists, hard link marked images into it
for img in $NEMO_SCRIPT_SELECTED_FILE_PATHS; do
	ln $img $path
done

nemo --quit
