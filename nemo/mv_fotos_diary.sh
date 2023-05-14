#!/bin/bash
# nemo action for moving fotos into the apropiate folder of the diary, i.e. fotos are removed from their original location
# folder name is read from pipe ~/.tagebuch/transfer_path and written by ~/.tagebuch/make_new_entry.sh

# read from pipe
path=$(<~/.tagebuch/transfer_path)
# notify-send "Pfad = $path"

# If directory exists, move files into it, i.e. files are "deleted" from their source folder
if [ -d "$path" ]; then # "if" not explicitly necessary but prevents accidentally hard linking when not writing a diary entry
	for img in "$@"; do
		# notify-send "img = $img"
		mv "$img" "$path"
	done

	nemo --quit
	echo "Image(s) moved." > ~/.tagebuch/transfer_path
fi
