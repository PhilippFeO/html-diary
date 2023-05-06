#!/bin/bash
# Formats the html skeleton for a diary entry
# Output can be captured via $(congfigure_html_skeleton $1 $2)

# $1 formatted heading
# $2 path to folder of the day
# $3 date of the day to create an entry for (in the %F format)

passed_date=$3

# Determine if passed date is a past date by formatting it and today's date as yyyy-ww (where ww is the leading 0 week number)
# The difference between these two dates is
#   =0, if the dates are in the same week
#   >0, if passed date is at least one week in the past
#       (heuristically, at a sonday monday transfer this fails but it's a simple solution and meant for entries far more in the past, f. i. last year's holidays)
year_week_entry=$(date --date="$passed_date" "+%G%V")
year_week_today=$(date "+%G%V")
year_week_diff=$((year_week_today - year_week_entry))

if [ $year_week_diff -gt 0 ]; then
    retrospecitve_entry="\n\n[Nachträglich aufgeschrieben]"
else
    retrospecitve_entry=""
fi

# Datei autmatisch alle 3 Sekunden aktualisieren:
#   <!-- <meta http-equiv=\"refresh\" content=\"3\"> -->

# KEEP THE HTML DOCUMENT AS SIMPLE AS POSSIBLE
# Every tweak only applies to future diary entries NOT to old ones
# To enable changes there, every day has to be modiefied by hand.
# TODO: Write a script that applies changes to past entries <29-04-2023>
html_skeleton="<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<title>$1</title>\n\t\t<!-- Styles für h1, pre -->\n\t\t<link rel=\"stylesheet\" href=\"/home/philipp/.tagebuch/style.css\">\n\t</head>\n\t<body>\n\t\t<h1>$1</h1><br/>\n\t\t<pre>\n$retrospecitve_entry\n\t\t</pre>"

# insert all images in today's directory
for img in $2/*.jpg $2/*.jpeg $2/*.JPG $2/*.JPEG $2/*.png $2/*.PNG; do
    if [ -f "$img" ]; then
        html_skeleton=$html_skeleton'
    \n\t\t<img src="'"$img"'" width="900" hspace="20" vspace="10"><br/>'
    fi
done

html_skeleton=$html_skeleton"\n\t</body>\n</html>"

echo -e $html_skeleton
