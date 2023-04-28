#!/bin/bash
# Tagebuch-Automatik

# TODO: Nemo-Action und Tastaturkürzel hinzufügen <27-04-2023>
#   https://stackoverflow.com/questions/41381003/how-to-add-keyboard-shortcut-for-custom-nemo-action
#       Vergleiche Beispiel in der Antwort: Name=Open in _Atom
#       => Der Unterstrich kommt in den Namen
#   https://wiki.archlinux.org/title/Nemo#Nemo_Actions
#   Ausführliches Beispiel mit Erklärungen: https://github.com/linuxmint/nemo/blob/master/files/usr/share/nemo/actions/sample.nemo_action
# TODO: Datei laden, wenn gespeichert wird <27-04-2023>
# DONE: Neovim und Firefox Seite an Seite öffnen <27-04-2023>


# Notwendig, damit GUIs funktionieren, zB. zenity, nemo, kitty\nvim
export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus


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
    <h1>$1</h1><br /> 
    <pre>

    </pre>"
    # insert all images in directory
    for img in *.jpg *.jpeg *.JPG *.JPEG; do
        if [ -f $img ]; then
            html_skeleton=$html_skeleton'
    <img src="'./$img'" width="900" hspace="20" vspace="10"><br />'
        fi
    done
    html_skeleton=$html_skeleton"
  </body>
</html>"
}

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

        firefox --new-window "$filename" &

        # open Neovim with the cursor between the <pre>-tags and start insert mode
        kitty $EDITOR "+call cursor(13, 0) | start" "$filename" &

        # Place Neovim and Firefox next to each other using wmctrl
        while true; do
            if wmctrl -l | grep $today.html > /dev/null; then
                if wmctrl -l | grep "$today_heading" > /dev/null; then
                   break
                fi
            fi
        done

        # sleep 1
        # wmctrl -r "$today_heading" -b remove,maximized_vert,maximized_horz
        # wmctrl -r "$today_heading" -e 0,960,0,960,1080
        # wmctrl -r $today.html -e 0,0,0,960,1080

        # The following is heavily inspired by
        # https://unix.stackexchange.com/questions/53150/how-do-i-resize-the-active-window-to-50-with-wmctrl
        SCREEN_WIDTH=$(xwininfo -root | awk '$1=="Width:" {print $2}')
        SCREEN_HEIGHT=$(xwininfo -root | awk '$1=="Height:" {print $2}')

        # new width and height
        W=$(( $SCREEN_WIDTH / 2 ))
        H=$SCREEN_HEIGHT

        # Change to move left or right
        # moving to the left
        LEFT_HALF=0; 
        # moving to the right half of the screen
        RIGHT_HALF=$(( $SCREEN_WIDTH / 2 ))

        Y=0

        # Firefox
        wmctrl -r "$today_heading" -b remove,maximized_vert,maximized_horz
        wmctrl -r "$today_heading" -e 0,$RIGHT_HALF,$Y,$W,$H

        # Neovim
        wmctrl -r $today.html -e 0,$LEFT_HALF,$Y,$W,$H
        wmctrl -R $today.html
    fi
fi
