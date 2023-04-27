#!/bin/bash
# Tagebuch-Automatik

# TODO: Datei laden, wenn gespeichert wird <27-04-2023>
# TODO: Neovim und Firefox Seite an Seite öffnen -> xdotool <27-04-2023>

# Notwendig, damit GUIs funktionieren, zB. zenity, nemo, kitty\nvim
export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus

# today_heading=$(date "+%d. %B %Y") # Proper date formatting for heading
# # Answer saved in $?
# zenity --question --text="Tagebucheintrag für heute, $today_heading, anlegen?" --ok-label="Ja" --cancel-label="Nein" --timeout=10

today=$(date +%F)
month_nmb=$(date +%m)
month_name=$(date +%B)
year=$(date +%Y)

# Check for existence because the script is run as a cronjob from 18-21 and I want to avoid getting asked if the job is already done.
path=~/.tagebuch/$year/$month_nmb-$month_name/$today
if [ ! -d "$path" ]; then

    # Ask for new diary entry
    today_heading=$(date "+%d. %B %Y") # Proper date formatting for heading
    # Answer saved in $?
    zenity --question --text="Tagebucheintrag für heute, $today_heading, anlegen?" --ok-label="Ja" --cancel-label="Nein" --timeout=10

    # if "Ja" (==0), then start diary routine
    if [ $? -eq 0 ]; then
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
        pagename=$(zenity --entry --title="Neuer Tagebucheintrag" --text="Heutiger Seitenname:" --width=1000 --height=300)
        filename=""

        # is $pagename is not empty, append given $pagename to path
        if [ -n "$pagename" ]; then
            filename="$path/$today $pagename.html"
            configure_html_skeleton "$today_heading: $pagename"
        # no $pagename was provided
        else
            filename="$path/$today.html"
            configure_html_skeleton "$today_heading"
        fi
        touch "$filename"
        echo "$html_skeleton" >> "$filename"

        firefox --new-window "$filename"

        # open Neovim with the cursor between the <pre>-tags and start insert mode
        kitty nvim  "+call cursor(13, 0) | start" "$filename"
    fi
fi
