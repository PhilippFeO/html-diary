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


def collect_dates_paths(directory: Path) -> dict[str, Path]:
    """Collect the dates of the fotos and return a mapping between `date` and `Path` of the foto."""
    dates_paths: dict[str, Path] = {}  # dates are in format 'yyyy:mm:dd'
    for file in directory.iterdir():
        # Recursion if 'file' is another subdir of fotos
        if Path.is_dir(file):
            # in-place union of sets
            dates_paths |= collect_dates_paths(file)
        elif Path.is_file(file):
            # Read Metadata to retrieve creation date
            if date_created := get_date_created(file):
                # Remove everythin after '~/Bilder/Subfolder/', ie
                # ~/Bilder/Sub1/Sub2 -> ~/Bilder/Sub1
                # Complicated, because using 'Path.parents[IDX]' doesn't work. I simply
                # don't know how to monkeypatch the '[IDX]'/__getitem__ call.
                base_dir = Path(
                    *file.parts[
                        :file.parts.index('Bilder') + 2])
                dates_paths[date_created] = base_dir
            else:
                continue
    return dates_paths


def folder_to_diary(foto_dir: Path):
    """Add a 'base.href' attribute to a diary entry for the submitted foto directory."""
    dates_paths: dict[str, Path] = collect_dates_paths(foto_dir)
    assert len(dates_paths) > 0, f'No dates collected. "dates" is empty: {dates_paths}.'
    for date in dates_paths:
        # Check if there is a dir matching the date
        year, month, day = date.split(':')
        matching_dirs = count_directories(day, month, year)
        match len(matching_dirs):
            # No entry exists for the selected date => Create one
            case 0:
                day_dir, html_entry = assemble_new_entry(day, month, year, href=f'file://{dates_paths[date]}')
                create_dir_and_file(html_entry, day_dir, day, month, year)
            # Add base.href to an already existing entry
            # Enty may or may have not a base.href attribute
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
                href = f'file://{dates_paths[date]}'
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
