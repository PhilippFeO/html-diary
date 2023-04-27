#!/usr/bin/env bash
# Tagebuch-Automatik


today=$(date +%F)
month=$(date +%B)
year=$(date +%Y)

path=~/.tagebuch/$year/$month/$today
mkdir -p $path

# nemo ~/Bilder/Handy-Fotos/

# query for pagename/heading for the day
# Can be left empty
pagename=$(zenity --entry --title="Heutiger Seitenname")
today_heading=$(date "+%d. %B %Y") # Proper date formatting for heading
filename=""
html_skeleton=""

configure_html_skeleton() {
    # $1 formatted heading
    html_skeleton="<!DOCTYPE html>
<html>
  <head>
    <title>$1</title>
    <!-- weitere Kopfinformationen -->
    <!-- Kommentare werden im Browser nicht angezeigt. -->
  </head>
  <body>
    <h1>$1</h1><br /> 
    <p>Inhalt der Webseite</p>"
    # insert all images in directory
    for img in *.jpg *.jpeg *.JPG *.JPEG; do
        if [ -f $img ]; then
            # echo "[$img]($path/$img)" >> $filename
            html_skeleton=$html_skeleton'
    <img src="'$path/$img'" width="700" hspace="20" vspace="10"><br />'
        fi
    done
    html_skeleton=$html_skeleton"
  </body>
</html>"
}

# is $pagename is not empty, append given $pagename to path
if [ -n "$pagename" ]; then
    filename="$path/$today $pagename.html"
    touch $filename
    configure_html_skeleton "$today_heading: $pagename"
    echo "$html_skeleton" >> "$filename"
else
    filename="$path/$today.html"
    touch $filename
    configure_html_skeleton "$today_heading"
    echo "$html_skeleton" >> "$filename"
fi


# nvim "$filename"

# HTML-Grundstruktur aus Wikipedia übernehmen
# Dazu ist wasl. printf hilfreich
# <p>…<p/> für Text
# TODO Listen
# Für nvim: "+call cursor(<LINE>, <COLUMN>)"
