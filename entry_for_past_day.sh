#!/bin/bash

zenity_width_cal=750
zenity_font_size=30
year=$(date +%Y)

selected_date=$(zenity --calendar --date-format=%Y-%m-%d --year="$year" --text="<span font='$zenity_font_size'>Wähle Datum aus dem Jahr $year:\n\n</span>" --width=$zenity_width_cal)

# Only proceed on "OK"
if [ $? -eq 0 ]; then
	# ~/.tagebuch/make_new_entry.sh "$past_date" ""
	python3 entry_for_past_day.py "$selected_date"
fi
