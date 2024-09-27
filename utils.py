import logging
import subprocess
from glob import glob
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

import vars
from date import Date

if TYPE_CHECKING:
    from pathlib import Path


def create_stump(
        title: str,
        location: str = '') -> BeautifulSoup:
    """Create a HTML stump for a new entry and the overview when looking into the past.

    Used in Entry.__init__() and look_into_the_past.py.
    """
    html: str = (
        "<!DOCTYPE html>"
        '<html>'
        '  <head>'
        f'    <title>{title}</title>'
        '    <link rel="stylesheet" href="/home/philipp/.tagebuch/style.css">'
        '  </head>'
        '  <body>'
        f'   <h1>{title}</h1>'
        '      <pre>'
        f"{f'Ort: {location}' if location != '' else ''}"
        '</pre>'
        '  </body>'
        '</html>'
    )
    return BeautifulSoup(html, 'html.parser')


def count_directories(date: Date) -> list[str]:
    return glob(f"{vars.DIARY_DIR}/{date.year}/{date.month}-*/{date.day}-{date.month}-{date.year}-*")


def read_metadata(cmd: str, file: 'Path') -> str | None:
    """Execute `cmd` (it's a `exif*` command) and return UTF-8 decoded string."""
    # TODO: Test with 'file' containing whitespace <27-06-2024>
    # TODO: Log exception? <16-06-2024>
    try:
        output = subprocess.check_output([*cmd.split(), f'{file}'])
        return output.decode('utf-8')
    except subprocess.CalledProcessError:
        logging.error("'%s \"%s\"' failed.", cmd, file)
        return None


def get_date_created(media_file: 'Path') -> Date | None:
    """Extract creation date in the format `yyyy:mm:dd` from EXIF data."""
    match media_file.suffix:
        case '.jpg' | '.jpeg' | '.png' | '.mp4' | '.JPG' | '.JPEG' | '.mp4' | '.MP4':
            cmd = '/usr/bin/exiftool -CreateDate'
            if exif_output := read_metadata(cmd, media_file):
                # Retrieve date from following line:
                # Create Date                     : 2023:05:12 13:58:16
                # ' : ' on purpose, to split at the very first ':'
                date_str = exif_output.split(' : ')[-1].split()[0]
                return Date(date_str)
            logging.info("File '%s' has no '-CreateDate' in it's EXIF data.", media_file)
            # PANO*.jpg
            cmd = '/usr/bin/exiftool -GPSDateStamp'
            if (exif_output := read_metadata(cmd, media_file)):
                # ' : ' on purpose, to split at the very first ':'
                date_str = exif_output.rstrip().split(' : ')[-1]
                return Date(date_str)
            logging.error("\t%s\nfailed. Probably, Foto '%s' has no 'GPSDateStamp' in it's exif data.", cmd, media_file)
            return None
        case _:
            logging.warning("Nothing done for File Type: '%s'. Full path:\n\t%s", media_file.suffix, media_file)
            return None
