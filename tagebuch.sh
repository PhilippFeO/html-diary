#!/usr/bin/env bash
# Tagebuch-Automatik


today=$(date +%F)
month=$(date +%B)
year=$(date +%Y)

path=~/.tagebuch/$year/$month/$today
mkdir -p $path

