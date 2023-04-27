#!/usr/bin/env bash

today=$(date +%F)
month_nmb=$(date +%m)
month_name=$(date +%B)
year=$(date +%Y)

# Create directory for today
path=~/.tagebuch/$year/$month_nmb-$month_name/$today

for img in $NEMO_SCRIPT_SELECTED_FILE_PATHS; do
	cp $img $path
	echo $img
done

nemo --quit
