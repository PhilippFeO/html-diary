#!/bin/bash

cd /home/philipp/.tagebuch
source /home/philipp/.tagebuch/.venv/tagebuch/bin/activate
# echo $1 >> ~/.tagebuch/.logs/handler.log.txt
python3 my_html_handler.py "$1"
deactivate
