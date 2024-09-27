# Necessary because returned values are in English
# Can't stay in main because also needed during testing
import locale
import logging
import os
import shutil
from pathlib import Path

import vars
from add_media_files import add_media_files
from entry import Entry
from utils import (
    count_directories,
    get_date_created,
)

locale.setlocale(locale.LC_ALL, '')


def copy_helper(media_file: Path,
                day_dir: Path,
                tagebuch_dir: Path):
    shutil.copy(media_file,
                day_dir/media_file.name)
    logging.info("Copied '%s' to '%s'", media_file, tagebuch_dir/day_dir/media_file.name)
    shutil.move(media_file,
                (transfered_dir := tagebuch_dir/'.tmp/transfered'))
    logging.info("Moved '%s' to '%s'.", media_file, transfered_dir)


def transfer_files() -> set[Entry]:
    """Copy Media files from .tmp to the according directory of the created date.

    To test this function, `tagebuch_dir` has to be parameter. Via pytest, I create a fake Tagebuch under `tmp_path`.
    """
    entries: set[Entry] = set()
    # Loop through files in source image directory (currently .tmp)
    for f in os.listdir(vars.TMP_DIR):
        media_file = vars.TMP_DIR/f
        if Path.is_file(media_file):
            if (date_created := get_date_created(media_file)) is None:
                continue
            matching_dirs = count_directories(date_created)

            # Move/Copy the media files to their corresponding diary entry.
            # Ie the entry fitting their created date.
            match len(matching_dirs):
                # TODO: Add Test for this case <26-05-2024>
                case 0:
                    entry = Entry(new_entry=(date_created, '', ''))
                    copy_helper(media_file,
                                entry.file.parent,
                                vars.DIARY_DIR)
                    entries.add(entry)
                    logging.info("Added '%s' to `directories`.", entry.file.parent)
                case 1:
                    # Transfer image to directory
                    entry = Entry(path_to_parent_dir=matching_dirs[0])
                    copy_helper(media_file,
                                entry.file.parent,
                                vars.DIARY_DIR)
                    entries.add(entry)
                    logging.info("Added '%s' to `directories`.", entry.file.parent)
                case _:
                    msg = f"Found {len(matching_dirs)} matching Directories obeying '{date_created.year}/{date_created.month}-*/{date_created.day}-*'. There should be exactly 1. The Directories are:\n{', '.join(matching_dirs)}"
                    logging.warning(msg)
    return entries


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format=vars.LOG_FORMAT,
                        datefmt=vars.LOG_DATEFMT,
                        filename=vars.LOG_FILE,
                        filemode='a')
    logging.info('%s %s %s', vars.HLINE, 'transfer_files.py', vars.HLINE)
    entries: set[Entry] = transfer_files()
    add_media_files(entries)
