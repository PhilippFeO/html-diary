#!/bin/bash
# Place Neovim and Firefox next to each other using wmctrl

# $1 date formatted accoirding to "+%d-%m-%Y-%A", f.i. 28-04-2023-Freitag 
# $2 heading for today's diary entry

# TODO: Redirect error to /dev/null/ <29-04-2023>

today=$1
today_heading=$2

# wait until windows are opened
while true; do
	if wmctrl -l | grep "$today" > /dev/null; then
		if wmctrl -l | grep "$today_heading" > /dev/null; then
		   break
		fi
	fi
done

# sleep 1
# wmctrl -r "$today_heading" -b remove,maximized_vert,maximized_horz
# wmctrl -r "$today_heading" -e 0,960,0,960,1080
# wmctrl -r $today.html -e 0,0,0,960,1080

# The following is heavily inspired by
# https://unix.stackexchange.com/questions/53150/how-do-i-resize-the-active-window-to-50-with-wmctrl
SCREEN_WIDTH=$(xwininfo -root | awk '$1=="Width:" {print $2}')
SCREEN_HEIGHT=$(xwininfo -root | awk '$1=="Height:" {print $2}')

# New width and height
W=$(( $SCREEN_WIDTH / 2 ))
H=$SCREEN_HEIGHT

# Change to move left or right
# moving to the left
LEFT_HALF=0; 
# moving to the right half of the screen
RIGHT_HALF=$(( $SCREEN_WIDTH / 2 ))

Y=0

# Firefox
wmctrl -r "$today_heading" -b remove,maximized_vert,maximized_horz
wmctrl -r "$today_heading" -e 0,$RIGHT_HALF,$Y,$W,$H

# Editor
wmctrl -r "$today" -e 0,$LEFT_HALF,$Y,$W,$H
wmctrl -R "$today" # Refocus Editor
