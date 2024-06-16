#!/home/philipp/.tagebuch/.venv/tagebuch/bin/python3
"""Called manually/explictly."""

# Necessary because returned values are in English
# Can't stay in main because also needed during testing
import locale
import logging
from glob import glob
from pathlib import Path

from bs4 import BeautifulSoup

from utils import (
    assemble_new_entry,
    count_directories,
    create_dir_and_file,
    get_date_created,
)

locale.setlocale(locale.LC_ALL, '')


def collect_dates_paths(directory: Path) -> set[tuple[str, Path]]:
    dates_paths: set[tuple[str, Path]] = set()  # dates are in format 'yyyy:mm:dd'
    for file in directory.iterdir():
        if Path.is_dir(file):
            folder_to_diary(file)
        elif Path.is_file(file):
            # Read Metadata to retrieve creation date
            if date_created := get_date_created(file):
                dates_paths.add((date_created, file.parent))
            else:
                continue
    return dates_paths


def folder_to_diary(directory: Path):
    dates_paths: set[tuple[str, Path]] = collect_dates_paths(directory)
    assert len(dates_paths) > 0, f'No dates collected. "dates" is empty: {dates_paths}.'
    for date, foto_dir_path in dates_paths:
        # Schauen, ob Datei für Datum existiert
        year, month, day = date.split(':')
        matching_dirs = count_directories(day, month, year)
        match len(matching_dirs):
            # No entry exists for the selected date => Create one
            case 0:
                day_dir, html_entry = assemble_new_entry(day, month, year, href=f'file://{foto_dir_path}')
                create_dir_and_file(html_entry, day_dir, day, month, year)
            # Add base.href to an entry
            case 1:
                # Open according entry
                day_dir = matching_dirs[0]
                html_files = glob(f'{day_dir}/*.html')
                # Assert entry exists (glob pattern checks for directory but no directory is created without entry)
                assert len(html_files) == 1, f'"{day_dir}" contains {len(html_files)} HTML files. There should be exactly 1.'
                entry_file = html_files[0]
                entry = BeautifulSoup(Path(entry_file).read_text(encoding='utf-8'), 'html.parser')
                # No base tag (=> base.href attribute)
                # Add base.href
                assert entry.head, f"No 'head' in '{entry_file}'."  # Should not happen
                href = f'file://{foto_dir_path}'
                if not entry.head.base:
                    base_tag = entry.new_tag('base', href=href)
                    entry.head.append(base_tag)
                    Path(entry_file).write_text(entry.prettify())
                # base.href already exists
                else:
                    href_value = entry.head.base.get('href')
                    # In case they differ, utter a warning but don't edit anything.
                    if href_value != href:
                        msg = f"base.href is '{href_value}' in '{entry_file}'. Can't add '{href}'."
                        logging.warning(msg)
                    # if both are equal, there is nothing to do
            # >= 2 matching directories for a day
            case _:
                logging.warning(
                    f"Found {len(matching_dirs)} matching Directories obeying '{year}/{month}-*/{day}-*'. There should be exactly 1. The Directories are:\n{', '.join(matching_dirs)}")


if __name__ == "__main__":
    CWD = Path.cwd()
    assert 'Bilder' in CWD.parents, 'Not in ~/Bilder.'
    folder_to_diary(CWD)
