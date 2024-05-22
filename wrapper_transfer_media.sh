#!/bin/bash
# This is a wrapper script for running 'transfer_files.py' and 'add_media_files.py' in a cronjob.


source /home/philipp/.tagebuch/.venv/tagebuch/bin/activate
python3 /home/philipp/.tagebuch/transfer_files.py
deactivate
