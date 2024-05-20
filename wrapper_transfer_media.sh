#!/bin/bash
# This is a wrapper script for running 'transfer_fotos.py' and 'add_media_files.py' in a cronjob.


source /home/philipp/.tagebuch/.venv/tagebuch/bin/activate
python3 /home/philipp/.tagebuch/transfer_fotos.py
deactivate
