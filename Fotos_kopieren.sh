#!/usr/bin/env bash

today=$(date +%F)
month=$(date +%B)
year=$(date +%Y)

path=~/.tagebuch/$year/$month/$today

for img in $NEMO_SCRIPT_SELECTED_FILE_PATHS; do
	cp $img $path
	echo $img
done

nemo --quit
