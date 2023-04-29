#!/bin/bash
# Open diary entry of past dates.
# Past dates are specified in past_dates.txt


past_dates=( $(date --file=past_dates.txt +%F) )

for past_date in ${past_dates[@]}; do
	today_past=$(date --date="$past_date" "+%F-%A")
	month_past=$(date --date="$past_date" "+%m-%B")
	year_past=$(date --date="$past_date" "+%Y")

	path=~/.tagebuch/$year_past/$month_past/$today_past

	# Only execute when there is a folder/file corresponding to the past date
	if [ -d $path ]; then
		today_heading_past=$(date --date="$past_date" "+%A, %d. %B %Y")
		zenity --question --text="Tagebucheintrag vom $today_heading_past, lesen?" --ok-label="Ja" --cancel-label="Nein" --timeout=10

		if [ $? -eq 0 ]; then
			# Wildcard expansion doesn't work in script, so it has to be triggered beforehand.
			# This is done by using an array and indexing the first field. There is exactly one, because one html-file was generated.
			# Taken from
			#	https://unix.stackexchange.com/questions/663257/bin-sh-wildcard-expansion-does-not-work-in-script
			files=("$path/$today_past*.html") 
			firefox --new-window ${files[0]}
		fi
	fi
done


