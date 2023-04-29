#!/bin/bash
# Open diary entry of past dates.
# Past dates are specified in past_dates.txt


zenity --question --text="In die Vergangenheit blicken?" --ok-label="Ja" --cancel-label="Nein" --timeout=10

if [ $? -eq 0 ]; then
	past_entries=""

	html_skeleton=""

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

	past_dates=( $(date --file=past_dates.txt +%F) )
	ctr=0
	for past_date in ${past_dates[@]}; do
		today_past=$(date --date="$past_date" "+%F-%A")
		month_past=$(date --date="$past_date" "+%m-%B")
		year_past=$(date --date="$past_date" "+%Y")

		path=~/.tagebuch/$year_past/$month_past/$today_past

		# Only execute when there is a folder/file corresponding to the past date
		if [ -d $path ]; then
			today_heading_past=$(date --date="$past_date" "+%A, %d. %B %Y")
			# Wildcard expansion doesn't work in script, so it has to be triggered beforehand.
			# This is done by using an array and indexing the first field. There is exactly one, because one html-file was generated.
			# Taken from
			#	https://unix.stackexchange.com/questions/663257/bin-sh-wildcard-expansion-does-not-work-in-script
			files=("$path/$today_past*.html") 
			past_entries="$past_entries $(python3 /home/philipp/.tagebuch/extract_html_body.py ${files[0]} $ctr "$today_heading_past")"
			ctr=$((ctr + 1))
		fi
	done

	configure_html_skeleton "$past_entries"
	echo $html_skeleton > /tmp/past.html
	firefox --new-window /tmp/past.html &
fi
