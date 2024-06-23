#!/bin/bash

cd /home/philipp/.tagebuch
source /home/philipp/.tagebuch/.venv/tagebuch/bin/activate
# echo $1 >> ~/.tagebuch/.logs/handler.log.txt
python3 open_diary_entry.py "$1"
deactivate
