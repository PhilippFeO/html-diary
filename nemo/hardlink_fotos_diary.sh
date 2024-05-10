#!/bin/bash
# nemo action for hard linking selected fotos into the apropiate folder of the diary
# folder name is read from pipe ~/.tagebuch/transfer_path and written by ~/.tagebuch/make_new_entry.sh

# read from pipe
path=$(<~/.tagebuch/transfer_path)

# If directory exists, hard link selected images into it
# Not explicitly necessary but prevents accidentally hard linking when not writing a diary entry
if [ -d "$path" ]; then
	for img in "$@"; do
		ln "$img" "$path"
	done

	nemo --quit
	echo "Image(s) linked" > ~/.tagebuch/transfer_path
fi
