#!/home/philipp/.tagebuch/.venv/tagebuch/bin/python3
"""Called manually/explictly."""

# Necessary because returned values are in English
# Can't stay in main because also needed during testing
import locale
import logging
from glob import glob
from pathlib import Path
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, Tag

from entry import Entry
from utils import (
    count_directories,
    get_date_created,
)

if TYPE_CHECKING:
    from date import Date

locale.setlocale(locale.LC_ALL, '')


def collect_dates(foto_dir: Path) -> set['Date']:
    """Collect the dates of the fotos and return a `set` of all creation dates.

    Since the 'greatest common path' is collected, the function is aware that fotos with the same creation date may appear in different subfolders.

    Inverse function: `add_media_files.py::collect_fotos()`.
    """
    dates: set[Date] = set()  # dates are in format 'yyyy:mm:dd'
    for file in foto_dir.iterdir():
        # Recursion if 'file' is another subdir of fotos
        if Path.is_dir(file):
            # in-place union of sets
            dates |= collect_dates(file)
        # Read Metadata to retrieve creation date
        elif Path.is_file(file) and (date_created := get_date_created(file)):
            dates.add(date_created)
    return dates


def folder_to_diary(foto_dir: Path,
                    location: str = ''):
    """Add a `head.base.href` attribute to a diary entry for the submitted `foto_dir`.

    The `foto_dir` is searched for any media file. Then, the creation date is saved. For any date, the `foto_dir` is inserted in a diary entry via the `head.base.href` attribute or a new entry is created with a `head.base.href` attribute.

    `foto_dir`: Directory containing fotos.
    """
    dates: set[Date] = collect_dates(foto_dir)
    assert len(dates) > 0, f'No dates collected. "dates" is empty: {dates}.'
    logging.info('Collected Date:\n%s', '\n\t'.join(str(date) for date in dates))
    for date in dates:
        # Check if there is a dir matching the date
        # year, month, day = date_str.split(':')
        matching_dirs = count_directories(date)
        match len(matching_dirs):
            # No entry exists for the selected date => Create one
            case 0:
                # day_dir, html_entry = assemble_new_entry(date, location, href=f'file://{foto_dir}')
                # create_dir_and_file(html_entry, day_dir)
                entry = Entry(new_entry=(date, location, f'file://{foto_dir}'))
            # Add base.href to an already existing entry
            # Entry may or may have not a base.href attribute
            case 1:
                # Open according entry
                day_dir = matching_dirs[0]
                html_files = glob(f'{day_dir}/*.html')
                # Assert entry exists (glob pattern checks for directory but no directory is created without entry)
                assert len(html_files) == 1, f'"{day_dir}" contains {len(html_files)} HTML files. There should be exactly 1.'
                entry_file = html_files[0]
                entry = BeautifulSoup(Path(entry_file).read_text(encoding='utf-8'), 'html.parser')
                # No base tag (=> No base.href attribute)
                # Add base.href to an already existing diary entry
                assert entry.head, f"No 'head' in '{entry_file}'."  # Should not happen
                href = f'file://{foto_dir}'
                if not entry.head.base:
                    base_tag = entry.new_tag('base', href=href)
                    entry.head.append(base_tag)
                    pre = entry.find('pre')
                    assert pre is not None, f'<pre> not found. File: {entry_file}'
                    assert isinstance(pre, Tag), f'<pre> is not of Type "Tag". File: {entry_file}'
                    # assert isinstance(pre.string, str), f'<pre> is empty. File {entry_file} {type(pre.string)}'
                    pre.string = pre.string + f'\n\nOrt: {location}' if pre.string is not None else f'Ort: {location}'
                    Path(entry_file).write_text(entry.prettify())
                # base.href already exists
                else:
                    href_value = entry.head.base.get('href')
                    # In case they differ, utter a warning but don't edit anything.
                    if href_value != href:
                        msg = f"base.href is '{href_value}' in '{entry_file}'. Can't add '{href}'."
                        logging.warning(msg)
                    pre = entry.find('pre')
                    if isinstance(pre, Tag) and isinstance(pre.string, str):
                        description = pre.string
                        if 'Ort: ' in description:
                            logging.warning("'%s' already contains 'Ort: '", entry_file)
                        else:
                            pre.string = description + f'\n\nOrt: {location}'
                    else:
                        msg = f"Either <pre> is not of Type 'Tag' or 'pre.string' is None. File: {entry_file}"
                        raise Exception(msg)
                # if both are equal, there is nothing to do
            # >= 2 matching directories for a day
            case _:
                logging.warning(
                    f"Found {len(matching_dirs)} matching Directories obeying '{date.year}/{date.month}-*/{date.day}-*'. There should be exactly 1. The Directories are:\n{', '.join(matching_dirs)}")


if __name__ == "__main__":
    CWD = Path.cwd()
    assert 'Bilder' in CWD.parts, f'Not in ~/Bilder, {CWD = }'
    # location = input('Ort: ')
    # folder_to_diary(CWD, location)
    folder_to_diary(CWD)
    # import subprocess
    # subprocess.run(f'notfiy-send {CWD}'.split())
