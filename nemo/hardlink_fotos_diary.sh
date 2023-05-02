#!/bin/bash
# nemo action for hard linking selected fotos into the apropiate folder of the diary
# folder name is read from pipe ~/.tagebuch/transfer_date and written by ~/.tagebuch/make_new_entry.sh

# read from pipe
path=$(<~/.tagebuch/transfer_date)

# If directory exists, hard link selected images into it
# Not explicitly necessary but prevents accidentally hard linking when not writing a diary entry
if [ -d "$path" ]; then
	for img in "$@"; do
		ln "$img" "$path"
	done

	nemo --quit
fi
