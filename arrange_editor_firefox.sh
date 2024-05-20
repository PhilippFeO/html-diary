#!/bin/bash
# Place Neovim and Firefox next to each other using wmctrl
# TODO: Redirect error to /dev/null/ <29-04-2023>

# $1 heading for today's diary entry (for checking if firefox window has opened)
today_heading=$1

# wait until windows are opened
while true; do
	# Check if nvim window is opened (title set in ./make_new_entry.sh)
	if wmctrl -l | grep "Tagebucheintrag" > /dev/null; then
		# same for firefox (title retrieved from html title tag)
		if wmctrl -l | grep "$today_heading" > /dev/null; then
		   break
		fi
	fi
	sleep 0.2
done

# The following is heavily inspired by
# https://unix.stackexchange.com/questions/53150/how-do-i-resize-the-active-window-to-50-with-wmctrl
SCREEN_WIDTH=$(xwininfo -root | awk '$1=="Width:" {print $2}')
SCREEN_HEIGHT=$(xwininfo -root | awk '$1=="Height:" {print $2}')

# New width and height
W=$(( SCREEN_WIDTH / 2 ))
H=$SCREEN_HEIGHT
Y=0

# Change to move left or right
# moving to the left
LEFT_HALF=0; 
# moving to the right half of the screen
RIGHT_HALF=$(( SCREEN_WIDTH / 2 ))

# Firefox
wmctrl -r "$today_heading" -b remove,maximized_vert,maximized_horz
wmctrl -r "$today_heading" -e 0,$RIGHT_HALF,$Y,$W,"$H"

# Neovim
wmctrl -r "Tagebucheintrag" -e 0,$LEFT_HALF,$Y,$W,"$H"
wmctrl -R "Tagebucheintrag" # Refocus Editor
