#!/bin/bash
# nemo action for moving fotos into the apropiate folder of the diary, i.e. fotos are removed from their original location
# folder name is read from pipe ~/.tagebuch/transfer_date and written by ~/.tagebuch/make_new_entry.sh

# read from pipe
path=$(<~/.tagebuch/transfer_date)

# If directory exists, move files into it, i.e. files are "deleted" from their source folder
if [ -d "$path" ]; then # "if" not explicitly necessary but prevents accidentally hard linking when not writing a diary entry
	for img in "$@"; do
		mv "$img" "$path"
	done

	nemo --quit
fi
