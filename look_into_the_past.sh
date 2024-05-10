#!/bin/bash
# Open diary entry of past dates.
# Past dates are specified in past_dates.txt

# copied into /etc/cron.daily/ (while being in this directory, not from "outside")

# Notwendig, damit GUIs funktionieren, zB. zenity, nemo, kitty/nvim
export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus

configure_html_skeleton() {
	# Formats the html skeleton for a diary entry
	# $1 formatted heading
	# Heute, $tag, $date, vor...
	title="Heute, $(date "+%A, %d. %B %Y"), vor..."
	html_skeleton="<!DOCTYPE html>
<html>
  <head>
	<title>$title</title>
	<!-- weitere Kopfinformationen -->
	<!-- Styles für <pre> -->
	<link rel=\"stylesheet\" href=\"/home/philipp/.tagebuch/style.css\">
  </head>
  <body>
	<h1>$title</h1><br /> 
	$1
  </body>
</html>"
}

zenity_width=1000
zenity_height=150
zenity_font_size=30

past_entries=""
html_skeleton=""

asked=1 # Variable to control that user is asked once, default is 1="Failure"="true"
answer=1 # save answer of zenity --question

past_dates=( $(date --file=/home/philipp/.tagebuch/past_dates.txt +%F) )
ctr=0
for past_date in ${past_dates[@]}; do
	today_past=$(date --date="$past_date" "+%d-%m-%Y-%A")
	month_past=$(date --date="$past_date" "+%m-%B")
	year_past=$(date --date="$past_date" "+%Y")

	paths=(~/.tagebuch/$year_past/$month_past/$today_past*)
	path=${paths[0]}

	# Only execute if there is a folder/file corresponding to the past date
	# ...and the user wants to look into the past
	if [ -d "$path" ]; then
		if [ $asked -eq 1 ]; then
			zenity --question --text="<span font='$zenity_font_size'>In die Vergangenheit blicken?</span>" --ok-label="Ja" --cancel-label="Nein" --width=$zenity_width --height=$zenity_height --timeout=10
			answer=$?
			if [ $answer -eq 1 ]; then
				break
			fi
			asked=0 # Set $asked to prevent repeating questions in case user wants to look into the past
		fi

		today_heading_past=$(date --date="$past_date" "+%A, %d. %B %Y")
		# Wildcard expansion doesn't work in script, so it has to be triggered beforehand.
		# This is done by using an array and indexing the first field. There is exactly one, because one html-file was generated.
		# Taken from
		#	https://unix.stackexchange.com/questions/663257/bin-sh-wildcard-expansion-does-not-work-in-script
		files=("$path/$today_past*.html") 
		past_entries="$past_entries $(python3 ~/.tagebuch/extract_html_body.py ${files[0]} $ctr "$today_heading_past")"
		ctr=$((ctr + 1))
	fi
done

# Only when user wants to look into the past
if [ $answer -eq 0 ]; then
	configure_html_skeleton "$past_entries"
	echo $html_skeleton > /tmp/past.html
	firefox --new-window /tmp/past.html &
fi
