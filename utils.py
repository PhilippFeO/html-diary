import logging
import subprocess
from glob import glob
from pathlib import Path

from bs4 import BeautifulSoup
from date import Date

import vars


def create_stump(title: str,
                 location: str = '') -> BeautifulSoup:
    html: str = (
        "<!DOCTYPE html>"
        '<html>'
        '  <head>'
        f'    <title>{title}</title>'
        '    <link rel="stylesheet" href="/home/philipp/.tagebuch/style.css">'
        '  </head>'
        '  <body>'
        f'    <h1>{title}</h1>'
        '    <pre>'
        f"{f'Ort: {location}' if location != '' else ''}"
        '</pre>'
        '  </body>'
        '</html>'
    )
    return BeautifulSoup(html, 'html.parser')


def count_directories(date: Date) -> list[str]:
    return glob(f"{vars.DIARY_DIR}/{date.year}/{date.month}-*/{date.day}-{date.month}-{date.year}-*")


def read_metadata(cmd: str, file: Path) -> str | None:
    """Execute `cmd` (it's a `exif*` command) and return UTF-8 decoded string."""
    # TODO: Test with 'file' containing whitespace <27-06-2024>
    # TODO: Log exception? <16-06-2024>
    try:
        output = subprocess.check_output([*cmd.split(), f'{file}'])
        return output.decode('utf-8')
    except subprocess.CalledProcessError:
        logging.error("'%s \"%s\"' failed.", cmd, file)
        return None


def get_date_created(file: Path) -> Date | None:
    """Extract creation date in the format `yyyy:mm:dd` from EXIF data."""
    match file.suffix:
        case '.mp4' | '.MP4':
            cmd = '/usr/bin/exiftool -CreateDate'
            if exif_output := read_metadata(cmd, file):
                # Retrieve date from following line:
                # Create Date                     : 2023:05:12 13:58:16
                # ' : ' on purpose, to split at the very first ':'
                date_str = exif_output.split(' : ')[-1].split()[0]
                return Date(date_str)
            logging.error("Probably, Video '%s' has no 'CreateDate' in it's EXIF data.", file)
            return None
        case '.jpg' | '.jpeg' | '.png' | '.MP4' | '.JPG' | '.JPEG':
            cmd = '/usr/bin/exiftool -CreateDate'
            if exif_output := read_metadata(cmd, file):
                # Retrieve date from following line:
                # Create Date                     : 2023:05:12 13:58:16
                # ' : ' on purpose, to split at the very first ':'
                date_str = exif_output.split(' : ')[-1].split()[0]
                return Date(date_str)
            logging.info("Foto '%s' has no '-CreateDate' in it's EXIF data.", file)
            # PANO*.jpg
            cmd = '/usr/bin/exiftool -GPSDateStamp'
            if (exif_output := read_metadata(cmd, file)):
                # ' : ' on purpose, to split at the very first ':'
                date_str = exif_output.rstrip().split(' : ')[-1]
                return Date(date_str)
            logging.error("\t%s\nfailed. Probably, Foto '%s' has no 'GPSDateStamp' in it's exif data.", cmd, file)
            return None
        case _:
            logging.warning("Nothing done for File Type: '%s'. Full path:\n\t%s", file.suffix, file)
            return None


def create_dir_and_file(html_entry: BeautifulSoup,
                        day_dir: "Path") -> None:
    """Create the directory of the day and the html file of the entry."""
    Path.mkdir(day_dir, parents=True)
    logging.info("Created Directory: '%s'", day_dir)
    day_entry = day_dir/f'{day_dir.name}.html'
    # Write the HTML (media files are added later as usual)
    Path(day_entry).write_text(html_entry.prettify())
    logging.info('Created no-description Entry: %s', day_entry)


def assemble_new_entry(
    date: Date,
    location: str = '',
    href: str | None = None,
) -> tuple["Path", BeautifulSoup]:
    """Create new empty entry. See method body for more information.

    Return `day_dir` for convenience. The name of the month and day have to be retrieved here anyway. This information is also necessary in `create_dir_and_file()`. Be returning `day_dir`, it doesn't have to be calculated twice.
    """
    # Create new empty entry
    # Media files were added if there was an entry fitting the created date.
    # Some media files have no according entry for their created date. In this block,
    # the (empty) entry is created to avoid remaining media files in .tmp/.
    title = f"{date.weekday}, {date.title_fmt}{f': {location}' if location != '' else ''}"
    entry = create_stump(title, location)
    assert entry.head, "No 'head' in the HTML skeleton."  # Should not happen
    if href:
        base_tag = entry.new_tag('base', href=href)
        entry.head.append(base_tag)
    day_dir: Path = vars.DIARY_DIR/date.year / \
        f"{date.month}-{date.monthname}/{date.day}-{date.month}-{date.year}-{date.weekday}{f'-{location}' if location != '' else ''}"
    return day_dir, entry
