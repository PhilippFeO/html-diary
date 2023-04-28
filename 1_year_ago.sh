#!/bin/bash
# Open diary entry from 1 year ago.

today_1_year_ago=$(date -d 'now - 1 year' "+%F-%A")
month_1_year_ago=$(date -d 'now - 1 year' "+%m-%B")
year_1_year_ago=$(date -d 'now - 1 year' "+%Y")

path=~/.tagebuch/$year_1_year_ago/$month_4_weeks_ago/$today_4_weeks_ago

# Only execute when there is a folder/file corresponding to the date 1 year ago
if [ -d $path ]; then
	today_heading_1_year_ago=$(date -d 'now - 1 year' "+%A, %d. %B %Y")
	zenity --question --text="Tagebucheintrag vom $today_heading_1_year_ago, lesen?" --ok-label="Ja" --cancel-label="Nein" --timeout=10

	if [ $? -eq 0 ]; then
		# Wildcard expansion doesn't work in script, so it has to be triggered beforehand.
		# This is done by using an array and indexing the first field. There is exactly one, because one html-file was generated.
		# Taken from
		#	https://unix.stackexchange.com/questions/663257/bin-sh-wildcard-expansion-does-not-work-in-script
		files=("$path/$today_1_year_ago*.html") 
		firefox --new-window ${files[0]}
	fi
fi
