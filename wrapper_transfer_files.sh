#!/bin/bash
# This is a wrapper script for running 'transfer_files.py' and 'add_media_files.py' in a cronjob.
# Necessary because I need the 'tagebuch' venv activated.

source /home/philipp/.tagebuch/.venv/tagebuch/bin/activate
python3 /home/philipp/.tagebuch/transfer_files.py
deactivate
