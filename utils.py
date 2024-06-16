import logging
import subprocess
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


def read_metadata(cmd: str, file: Path) -> str | None:
    """Execute `cmd` (it's a `exif*` command) and return UTF-8 decoded string."""
    # TODO: Log exception? <16-06-2024>
    try:
        output = subprocess.check_output([*cmd.split(), f'{file}'])
        return output.decode('utf-8')
    except subprocess.CalledProcessError:
        logging.error(f"'{cmd} \"{file}\"' failed.")
        return None


def get_date_created(file: Path) -> str | None:
    """Extract creation date in the format `yyyy:mm:dd` from EXIF data."""
    match file.suffix:
        case '.mp4' | '.MP4':
            cmd = '/usr/bin/exiftool -CreateDate'
            if exif_output := read_metadata(cmd, file):
                # Retrieve date from following line:
                # Create Date                     : 2023:05:12 13:58:16
                return exif_output.split(' : ')[-1].split()[0]
            logging.error(f"Probably, Video '{file}' has no 'CreateDate' in it's EXIF data.")
            return None
        case '.jpg' | '.jpeg' | '.png' | '.MP4' | '.JPG' | '.JPEG':
            cmd = '/usr/bin/exif -t 0x9003 --ifd=EXIF'
            if (exif_output := read_metadata(cmd, file)):
                return exif_output.splitlines()[-1].split()[1]
            logging.error(f"Probably, Foto '{file}' has no Tag '9003' in it's EXIF data.")
            # PANO*.jpg
            cmd = '/usr/bin/exiftool -GPSDateStamp'
            if (exif_output := read_metadata(cmd, file)):
                return exif_output.rstrip().split(' : ')[-1]
            msg = f"\t{cmd}\nfailed. Probably, Foto '{file}' has no 'GPSDateStamp' in it's exif data."
            logging.error(msg)
            return None
        case _:
            logging.warning(f"Nothing done for File Type: '{file.suffix}'. Full path:\n\t{file}")
            return None


def create_dir_and_file(html_entry: BeautifulSoup,
                        day_dir: "Path",
                        day: str,
                        month: str,
                        year: str) -> None:
    """Create the directory of the day and the html file of the entry."""
    Path.mkdir(day_dir, parents=True)
    logging.info(f"Created Directory: '{day_dir}'")
    # Write the HTML (media files are added later as usual)
    day_entry = day_dir/f'{day}-{month}-{year}.html'
    Path(day_entry).write_text(html_entry.prettify())
    logging.info(f'Created no-description Entry for {year}-{month}-{day}: "{day_entry}"')


def assemble_new_entry(day: str, month: str, year: str) -> tuple["Path", BeautifulSoup]:
    """Create new empty entry. See method body for more information.

    Return `day_dir` for convenience. The name of the month and day have to be retrieved here anyway. This information is also necessary in `create_dir_and_file()`. Be returning `day_dir`, it don't have to be calculated twice.
    """
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
    # consistency: Every entry has one and add_files(…) logic is based on the existence of this pre-tag
    empty_pre_tag = entry.new_tag('pre')
    if (h1_tag := entry.find('h1')):
        h1_tag.insert_after(empty_pre_tag)
        month_name = date_obj.strftime('%B')
        # Create entry with empty pre-tag
        day_dir: Path = vars.DIARY_DIR/year/f'{month}-{month_name}/{day}-{month}-{year}-{weekday}'
        return day_dir, entry
    logging.error(msg := 'Parsing HTML Skeleton in `make_new_entry` went wrong. No h1-Tag.')
    raise Exception(msg)
