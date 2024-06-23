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

imgs=~/Bilder/Handy-Fotos/

# Check for existence because the script is run as a cronjob from 18-21 and I want to avoid getting asked if the job is already done.
path=~/.tagebuch/$year/$month/$today
if ~/.tagebuch/check_today_dir_exists.sh "$path"; then
    # Ask for new diary entry
    # Proper date formatting for heading, f.i. Mittwoch, 5. Juni 2024
    # sed 's/ 0/ /' removey the leading 0 of a single digit day
    today_date_for_heading=$(date "+%A, %d. %B %Y" | sed 's/ 0/ /') 
    # Answer saved in $?
    zenity --question --text="<span font='$zenity_font_size'>Tagebucheintrag für heute, $today_date_for_heading, anlegen?</span>" --ok-label="Ja" --cancel-label="Nein" --width=$zenity_width --height=$zenity_height --timeout=10

    # If "Ja" (==0), then start diary routine
    if [ $? -eq 0 ]; then
        # Query for pagename/heading for the day
        # Can be left empty
        pagename=$(zenity --entry --title="Neuer Tagebucheintrag" --text="Heutiger Seitenname:" --width=$zenity_width --height=$zenity_height)
        # If $pagename was provided replace every space by -
        # Precaution, having no spaces prevents troubles in case of escaping or iterating over files/folders
        if [ -n "$pagename" ]; then
            pagename_no_spaces=$(echo "$pagename" | tr ' ' '-')
            heading="$today_date_for_heading: $pagename"
        else
            pagename_no_spaces=$pagename
            heading="$today_date_for_heading"
        fi

        today_dir="$path-$pagename_no_spaces"
        mkdir -p "$today_dir"

        with_media_files=false
        if [ "$with_media_files" = true ]; then

            # Open nemo to hard link fotos via
            #   nemo script Fotos_kopieren.sh or
            #   nemo action copy_fotos_diary.sh
            # Fotos are synced via syncthing between cellphone and computer
                # TODO: Doesn't work if there is already a nemo instance running <29-04-2023>
                #   I.e. script doesn't wait until nemo was closed because the already running instance is not ascociated to the script. The script proceeds and queries for the pagename.
                #   Workaround #1: --quit but then all open nemo instances are closed, i.e. could infere with current workflow but propably so rare that it is more convenient than closing nemo manually as in Workaround #2
            # nemo --quit
            # nemo $imgs
            # Move/Copy/Link files into .tagebuch/.tmp
            nemo $imgs
                #   Workaround #2: Using --existing-window but then automatically closing nemo via nemo scripts & actions doesn't work
                # nemo --existing-window ~/Bilder/Handy-Fotos/

            # Move files in .tmp into $today_dir
            for f in .tmp/*; do
                mv "$f" "$today_dir"
            done

            # Craft HTML skeleton
            html_skeleton=$(~/.tagebuch/configure_html_skeleton.sh "$heading" "$today_dir" true)
        # HTML skeleton without media files, ie. plain text.
        # Media files will be added later by another step.
        else
            # Mit Beautiful Soup Medien hinzufügen
            html_skeleton=$(~/.tagebuch/configure_html_skeleton.sh "$heading" "$today_dir" false)
        fi
        today_file="$today_dir/$today-$pagename_no_spaces.html"
        echo "$html_skeleton" > "$today_file"

        # Setup enviornment to edit entry
        firefox --new-window "$today_file" &
        # Open Neovim with the cursor between the <pre>-tags and start insert mode
        #   $EDITOR doesn't make sense due to cursor setting syntax
        #   Hilft vllt: -i, dann HEX für -r
        /home/philipp/.local/bin/kitty --title "Tagebucheintrag" nvim "+call cursor(10, 0) | startinsert" "$today_file" &

        ~/.tagebuch/arrange_editor_firefox.sh "$heading"
    fi
fi
