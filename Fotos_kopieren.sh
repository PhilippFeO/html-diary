#!/usr/bin/env bash
# nemo script for hard linking selected fotos into the according diary folder

today=$(date "+%d-%m-%Y-%A") # f.i. 28-04-2023-Freitag
month=$(date "+%m-%B") # f.i. 04-April
year=$(date +%Y)

# Trigger wildcard expansion via array mechanic, to get full directory name (it has a custom component, the summary of the day)
paths=(~/.tagebuch/$year/$month/$today*)
path=${paths[0]}

# If directory exists, hard link marked images into it
# Not explicitly necessary but prevents accidentally hard linking when not writing a diary entry
if [ -d "$path" ]; then
	for img in $NEMO_SCRIPT_SELECTED_FILE_PATHS; do
		ln $img $path
	done

	nemo --quit
fi
