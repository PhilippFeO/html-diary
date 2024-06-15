import logging
from datetime import datetime
from glob import glob
from pathlib import Path

from bs4 import BeautifulSoup

import vars


def create_stump(title: str) -> str:
    return (
        "<!DOCTYPE html>"
        '<html>'
        '  <head>'
        f'	<title>{title}</title>'
        '	<!-- weitere Kopfinformationen -->'
        '	<!-- Styles für <pre> -->'
        '	<link rel="stylesheet" href="/home/philipp/.tagebuch/style.css">'
        '  </head>'
        '  <body>'
        f'	<h1>{title}</h1>'
        '  </body>'
        '</html>'
    )


def count_directories(day: str, month: str, year: str) -> list[str]:
    return glob(f"{vars.DIARY_DIR}/{year}/{month}-*/{day}-{month}-{year}-*")


def create_dir_file(html_entry: BeautifulSoup,
                    day_dir: "Path",
                    day: str,
                    month: str,
                    year: str) -> None:
    Path.mkdir(day_dir, parents=True)
    logging.info(f"Created Directory: '{day_dir}'")
    # Write the HTML (media files are added later as usual)
    day_entry = day_dir/f'{day}-{month}-{year}.html'
    Path(day_entry).write_text(html_entry.prettify())
    logging.info(f'Created no-description Entry for {year}-{month}-{day}: "{day_entry}"')


def make_new_entry(day: str, month: str, year: str) -> tuple["Path", BeautifulSoup]:
    # Create new empty entry
    # Media files were added if there was an entry fitting the created date.
    # Some media files have no according entry for their created date. In this block,
    # the (empty) entry is created to avoid remaining media files in .tmp/.
    date_obj = datetime.strptime(f'{year}:{month}:{day}', '%Y:%m:%d').date()
    weekday = date_obj.strftime('%A')
    title = f"{weekday}, {date_obj.strftime('%d. %B %Y')}"
    html_skeleton = create_stump(title)
    entry = BeautifulSoup(html_skeleton, 'html.parser')
    # For the sake of consistency, add an (empty) pre-tag
    # consistency: Every entry has one and add_media_files(…) logic is based on the existence of this pre-tag
    empty_pre_tag = entry.new_tag('pre')
    if (h1_tag := entry.find('h1')):
        h1_tag.insert_after(empty_pre_tag)
        month_name = date_obj.strftime('%B')
        # Create entry with empty pre-tag
        day_dir: Path = vars.DIARY_DIR/year/f'{month}-{month_name}/{day}-{month}-{year}-{weekday}'
        return day_dir, entry
    logging.error(msg := 'Parsing HTML Skeleton in `make_new_entry` went wrong. No h1-Tag.')
    raise Exception(msg)
