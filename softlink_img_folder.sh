#!/bin/sh

path=$1

folder=$(zenity --file-selection --directory)

for img in $folder/*.jpg $folder/*.JPG $folder/*.png $folder/*.PNG; do
	if [ -f "$img" ]; then
		ln -s "$img" "$path/$img"
	fi
done
