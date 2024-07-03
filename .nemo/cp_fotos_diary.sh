#!/bin/bash
# nemo action for copying fotos in $@ into ~/.tagebuch/.tmp 

for img in "$@"; do
	# notify-send "img = $img"
	cp "$img" ~/.tagebuch/.tmp/
done
