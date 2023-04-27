#!/usr/bin/env bash
# Tagebuch-Automatik


today=$(date +%F)
month_nmb=$(date +%m)
month_name=$(date +%B)
year=$(date +%Y)

# Create directory for today
path=~/.tagebuch/$year/$month_nmb-$month_name/$today
mkdir -p $path
cd $path

# nemo ~/Bilder/Handy-Fotos/

# query for pagename/heading for the day
# Can be left empty
pagename=$(zenity --entry --title="Heutiger Seitenname")
today_heading=$(date "+%d. %B %Y") # Proper date formatting for heading

filename=""
html_skeleton="" # Set in configure_html_skeleton()

configure_html_skeleton() {
    # Formats the html skeleton for a diary entry
    # $1 formatted heading
    html_skeleton="<!DOCTYPE html>
<html>
  <head>
    <title>$1</title>
    <!-- weitere Kopfinformationen -->
    <!-- Styles für <pre> -->
    <link rel=\"stylesheet\" href=\"/home/philipp/.tagebuch/style.css\">
  </head>
  <body>
    <h1 style=\"font-family: 'Fira Code'\">$1</h1><br /> 
    <pre style=\"font-family: 'Fira Code'; font-size: 30px\">

    </pre>"
    # insert all images in directory
    for img in *.jpg *.jpeg *.JPG *.JPEG; do
        if [ -f $img ]; then
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
    touch "$filename"
    configure_html_skeleton "$today_heading: $pagename"
    echo "$html_skeleton" >> "$filename"
else
    filename="$path/$today.html"
    touch $filename
    configure_html_skeleton "$today_heading"
    echo "$html_skeleton" >> "$filename"
fi

# open Neovim with the cursor between the <pre>-tags and start insert mode
nvim  "+call cursor(12, 0) | start" "$filename"
