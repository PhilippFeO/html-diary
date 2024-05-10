#!/bin/bash
# nemo action for copying fotos into the apropiate folder of the diary

for img in "$@"; do
	# notify-send "img = $img"
	cp "$img" ~/.tagebuch/.tmp/
done
