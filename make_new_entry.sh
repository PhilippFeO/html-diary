#!/bin/bash

# $1 dd-mm-yyyy
# $2 Path to path_fotos; can be empty

path_fotos=$2

day=$(date --date="$1" "+%d-%m-%Y-%A")
month=$(date --date="$1" "+%m-%B")
year=$(date --date="$1" +%Y)
day_heading=$(date --date="$1" "+%A, %d. %B %Y")

path=~/.tagebuch/$year/$month/$day

zenity_width=1000
zenity_height=150
zenity_font_size=30

# Query for pagename/heading for the day
# Can be left empty
pagename=$(zenity --entry --text="<span font='$zenity_font_size'>Seitenname für $day_heading:</span>" --title="Neuer Tagebucheintrag" --width=$zenity_width --height=$zenity_height)

# Only proceed on "OK"
if [ $? -eq 0 ]; then
	# If $pagename was provided replace every space by -
	# Precaution, having no spaces prevents troubles in case of escaping or iterating over files/folders
	day_dir="$path"
	day_file="$day_dir/$day.html"
	heading="$day_heading"
	if [ -n "$pagename" ]; then
		pagename_no_spaces=$(echo $pagename | tr ' ' '-')
		day_dir="$day_dir-$pagename_no_spaces"
		day_file="$day_dir/$day-$pagename_no_spaces.html"
		heading="$heading: $pagename"
	fi

	mkdir -p "$day_dir"

	# Open nemo to hard link path_fotos via
	#   nemo script Fotos_kopieren.sh or
	#   nemo action copy_fotos_diary.sh
	# Fotos are synced via syncthing between cellphone and computer
		# TODO: Doesn't work if there is already a nemo instance running <29-04-2023>
		#   I.e. script doesn't wait until nemo was closed because the already running instance is not ascociated to the script. The script proceeds and queries for the pagename.
		#   Workaround #1: --quit but then all open nemo instances are closed, i.e. could infere with current workflow but propably so rare that it is more convenient than closing nemo manually as in Workaround #2
	nemo --quit
	nemo ~/Bilder/$path_fotos
		#   Workaround #2: Using --existing-window but then automatically closing nemo via nemo scripts & actions doesn't work
		# nemo --existing-window ~/Bilder/Handy-Fotos/

	html_skeleton=$(~/.tagebuch/configure_html_skeleton.sh "$heading" "$day_dir")

	# day_file="$day_dir/$day-$pagename_no_spaces.html"
	echo "$html_skeleton" > "$day_file"

	# Open firefox and Neovim
	firefox --new-window "$day_file" &

	# Open Neovim with the cursor between the <pre>-tags and start insert mode
	#   $EDITOR doesn't make sense due to cursor setting syntax
	kitty nvim "+call cursor(11, 0) | start" "$day_file" &

	~/.tagebuch/arrange_editor_firefox.sh "$day" "$day_heading"
fi
