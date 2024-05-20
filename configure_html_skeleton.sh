#!/bin/bash
# Formats the html skeleton for a diary entry
# Output can be captured via $(congfigure_html_skeleton $1 $2)

# $1 formatted heading
# $2 path to folder of the day

# Datei autmatisch alle 3 Sekunden aktualisieren:
#   <!-- <meta http-equiv=\"refresh\" content=\"3\"> -->

# KEEP THE HTML DOCUMENT AS SIMPLE AS POSSIBLE
# Every tweak only applies to future diary entries NOT to old ones
# To enable changes there, every day has to be modiefied by hand.
# TODO: Write a script that applies changes to past entries <29-04-2023>
html_skeleton="<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<title>$1</title>\n\t\t<link rel=\"stylesheet\" href=\"/home/philipp/.tagebuch/style.css\">\n\t</head>\n\t<body>\n\t\t<h1>$1</h1>\n\t\t<pre>\n\n\t\t</pre>"

# insert all images in today's directory
for img in $2/*.jpg $2/*.jpeg $2/*.JPG $2/*.JPEG $2/*.png $2/*.PNG; do
    if [ -f "$img" ]; then
        html_skeleton=$html_skeleton'\n\t\t<img src="'"$img"'">\n\t\t<br/>'
    fi
done
for video in $2/*.mp4 $2/*.MP4; do
    if [ -f "$video" ]; then
        # controls (boolean): show video control buttons
        # loop (boolean): play video in loop
        html_skeleton=$html_skeleton'\n\t\t<video controls loop>\n\t\t\t<source src="'$video'" type="video/mp4">\n\t\t</video>\n\t\t<br/>'
    fi
done

html_skeleton=$html_skeleton"\n\t</body>\n</html>"

echo -e "$html_skeleton"
