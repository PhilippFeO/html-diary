#!/usr/bin/env bash
# Tagebuch-Automatik

# TODO: Datei laden, wenn gespeichert wird <27-04-2023>


today=$(date +%F)
month_nmb=$(date +%m)
month_name=$(date +%B)
year=$(date +%Y)

# Create directory for today
# Check for existence because the script is run as a cronjob from 18-21 and I want to avoid getting asked if the job is already done.
path=~/.tagebuch/$year/$month_nmb-$month_name/$today
if [ ! -d "$path" ]; then
    mkdir -p $path
    cd $path

    # open nemo do copy fotos via nemo script Fotos_kopieren.sh
    # Fotos are synced via syncthing
    nemo ~/Bilder/Handy-Fotos/

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
        <!-- <meta http-equiv="refresh" content="3"> -->
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

    # query for pagename/heading for the day
    # Can be left empty
    pagename=$(zenity --entry --title="Heutiger Seitenname")
    today_heading=$(date "+%d. %B %Y") # Proper date formatting for heading
    filename=""

    # is $pagename is not empty, append given $pagename to path
    if [ -n "$pagename" ]; then
        filename="$path/$today $pagename.html"
        touch "$filename"
        configure_html_skeleton "$today_heading: $pagename"
        echo "$html_skeleton" >> "$filename"
    # no $pagename was provided
    else
        filename="$path/$today.html"
        touch $filename
        configure_html_skeleton "$today_heading"
        echo "$html_skeleton" >> "$filename"
    fi

    # open Neovim with the cursor between the <pre>-tags and start insert mode
    nvim  "+call cursor(13, 0) | start" "$filename"
fi
