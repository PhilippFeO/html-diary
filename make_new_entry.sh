#!/bin/bash

# $1 date of the day to create an entry for, (in the %F format, i. e. yyyy-mm-dd)
# $2 Path to path_fotos; can be empty

date_entry=$1
path_fotos=$2

day=$(date --date="$date_entry" "+%d-%m-%Y-%A")
month=$(date --date="$date_entry" "+%m-%B")
year=$(date --date="$date_entry" +%Y)
day_heading=$(date --date="$date_entry" "+%A, %d. %B %Y")

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
		pagename_cleaned=$(echo $pagename | tr ' ' '-' | tr -d ',')
		day_dir="$day_dir-$pagename_cleaned"
		day_file="$day_dir/$day-$pagename_cleaned.html"
		heading="$heading: $pagename"
	fi

	mkdir -p "$day_dir"
	# write to pipe, so nemo actions/scripts have access to the directory of the selected date (past or today)
	named_pipe=~/.tagebuch/transfer_path
	if [ ! -p $named_pipe ]; then
		mkfifo $named_pipe
	fi

	# Open nemo to hard link path_fotos via
	#   nemo script Fotos_kopieren.sh or
	#   nemo action copy_fotos_diary.sh
	# Fotos are synced via syncthing between cellphone and computer
		# TODO: Doesn't work if there is already a nemo instance running <29-04-2023>
		#   I.e. script doesn't wait until nemo was closed because the already running instance is not ascociated to the script. The script proceeds and queries for the pagename.
		#   Workaround #1: --quit but then all open nemo instances are closed, i.e. could infere with current workflow but propably so rare that it is more convenient than closing nemo manually as in Workaround #2
	nemo --quit
	nemo ~/Bilder/$path_fotos &
		#   Workaround #2: Using --existing-window but then automatically closing nemo via nemo scripts & actions doesn't work
		# nemo --existing-window ~/Bilder/Handy-Fotos/

	# Inter process communication: Provide scripts in nemo/ with the apropiate path to link/move the files
	echo "$day_dir" > ~/.tagebuch/transfer_path
	cat < ~/.tagebuch/transfer_path

	html_skeleton=$(~/.tagebuch/configure_html_skeleton.sh "$heading" "$day_dir" $date_entry)

	echo "$html_skeleton" > "$day_file"

	# Open firefox and Neovim
	firefox --new-window "$day_file" &

	# Open Neovim with the cursor between the <pre>-tags and start insert mode
	#   $EDITOR doesn't make sense due to cursor setting syntax
	kitty --title "Tagebucheintrag" nvim "+call cursor(11, 1) | startinsert" "$day_file" &

	~/.tagebuch/arrange_editor_firefox.sh "$day_heading"
fi
