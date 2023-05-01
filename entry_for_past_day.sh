#!/bin/bash

zenity_width_cal=750
zenity_font_size=30
year=2022

past_date=$(zenity --calendar --date-format=%Y-%m-%d --year=$year --text="<span font='$zenity_font_size'>Wähle Datum aus dem Jahr $year:\n\n</span>" --width=$zenity_width_cal)

# Only proceed on "OK"
if [ $? -eq 0 ]; then
	~/.tagebuch/make_new_entry.sh $past_date ""
fi
