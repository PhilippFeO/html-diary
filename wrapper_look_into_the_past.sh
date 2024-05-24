#!/bin/bash
# This is a wrapper script for running 'transfer_files.py' and 'add_media_files.py' in a cronjob.
# Necessary because I need the 'tagebuch' venv activated.

# Notwendig, damit GUIs funktionieren, zB. zenity, nemo, kitty/nvim
export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus

source /home/philipp/.tagebuch/.venv/tagebuch/bin/activate
python3 /home/philipp/.tagebuch/look_into_the_past.py
deactivate
