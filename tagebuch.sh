#!/bin/bash
# Tagebuch-Automatik

# TODO: Datei laden, wenn gespeichert wird <27-04-2023>

# DONE: Leerzeichen im Namen zu - <29-04-2023>
# DONE: Nemo-Action und Tastaturkürzel hinzufügen <27-04-2023>
#   https://stackoverflow.com/questions/41381003/how-to-add-keyboard-shortcut-for-custom-nemo-action
#       Vergleiche Beispiel in der Antwort: Name=Open in _Atom
#       => Der Unterstrich kommt in den Namen
#   https://wiki.archlinux.org/title/Nemo#Nemo_Actions
#   Ausführliches Beispiel mit Erklärungen: https://github.com/linuxmint/nemo/blob/master/files/usr/share/nemo/actions/sample.nemo_action
# DONE: Neovim und Firefox Seite an Seite öffnen <27-04-2023>


# Notwendig, damit GUIs funktionieren, zB. zenity, nemo, kitty/nvim
export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus

zenity_width=1000
zenity_height=150
zenity_font_size=30

today=$(date "+%d-%m-%Y-%A") # f.i. 28-04-2023-Freitag
month=$(date "+%m-%B") # f.i. 04-April
year=$(date +%Y)

# Check for existence because the script is run as a cronjob from 18-21 and I want to avoid getting asked if the job is already done.
path=~/.tagebuch/$year/$month/$today
~/.tagebuch/check_today_dir_exists.sh $path # return value captured in $?

if [ $? -eq 0 ]; then
    # Ask for new diary entry
    today_heading=$(date "+%A, %d. %B %Y") # Proper date formatting for heading, f.i. Freitag, 29. April 2023
    # Answer saved in $?
    zenity --question --text="<span font='$zenity_font_size'>Tagebucheintrag für heute, $today_heading, anlegen?</span>" --ok-label="Ja" --cancel-label="Nein" --width=$zenity_width --height=$zenity_height --timeout=10

    # If "Ja" (==0), then start diary routine
    if [ $? -eq 0 ]; then
        ~/.tagebuch/make_new_entry.sh $(date +%F) "Handy-Fotos/"
    fi
fi
