#!/usr/bin/env bash
# Tagebuch-Automatik


today=$(date +%F)
month=$(date +%B)
year=$(date +%Y)

path=~/.tagebuch/$year/$month/$today
mkdir -p $path

# nemo ~/Bilder/Handy-Fotos/

pagename=$(zenity --entry --title="Heutiger Seitenname")
today_heading=$(date "+%d. %B %Y")
filename=""

# is $pagename is not empty, append given $pagename to path
if [ -n "$pagename" ]; then
    filename="$path/$today $pagename.html"
    touch $filename
    echo "<h1>$today_heading: $pagename</h1><br />\n\n\n" >> "$filename"
else
    filename="$path/$today.html"
    touch $filename
    echo "<h1>$today_heading</h1><br />\\n\\n\\n" >> $filename
fi

# insert all images in directory
for img in *.jpg *.jpeg *.JPG *.JPEG; do
    if [ -f $img ]; then
        # echo "[$img]($path/$img)" >> $filename
        echo '<img src="'$path/$img'" width="700" hspace="20" vspace="10"><br />' >> "$filename"
    fi
done

# nvim "$filename"

# HTML-Grundstruktur aus Wikipedia übernehmen
# Dazu ist wasl. printf hilfreich
# <p>…<p/> für Text
# TODO Listen
# Für nvim: "+call cursor(<LINE>, <COLUMN>)"
