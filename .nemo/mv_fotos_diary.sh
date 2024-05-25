#!/bin/bash
# nemo action for moving fotos into ~/.tagebuch/.tmp

for img in "$@"; do
	# notify-send "img = $img"
	mv "$img" ~/.tagebuch/.tmp/
done
