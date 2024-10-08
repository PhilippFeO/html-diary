# Necessary because returned values are in English
# Can't stay in main because also needed during testing
import locale
import logging
import os
import shutil
from pathlib import Path

import vars
from add_media_files import add_media_files
from utils import (
    assemble_new_entry,
    count_directories,
    create_dir_and_file,
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


def transfer_files() -> set[Path]:
    """Copy Media files from .tmp to the according directory of the created date.

    To test this function, `tagebuch_dir` has to be parameter. Via pytest, I create a fake Tagebuch under `tmp_path`.
    """
    directories: set[Path] = set()
    # Loop through files in the directory
    for f in os.listdir(vars.TMP_DIR):
        media_file = vars.TMP_DIR/f
        if Path.is_file(media_file):
            if not (date_created := get_date_created(media_file)):
                continue
            matching_dirs = count_directories(date_created)

            # Move/Copy the media files to their corresponding diary entry.
            # Ie the entry fitting their created date.
            match len(matching_dirs):
                # TODO: Add Test for this case <26-05-2024>
                case 0:
                    day_dir, html_entry = assemble_new_entry(date_created)
                    create_dir_and_file(html_entry, day_dir)
                    copy_helper(media_file,
                                day_dir,
                                vars.DIARY_DIR)
                    directories.add(day_dir)
                    logging.info("Added '%s' to `directories`.", day_dir)
                case 1:
                    # Transfer image to directory
                    day_dir = Path(matching_dirs[0])
                    copy_helper(media_file,
                                day_dir,
                                vars.DIARY_DIR)
                    directories.add(day_dir)
                    logging.info("Added '%s' to `directories`.", day_dir)
                case _:
                    msg = f"Found {len(matching_dirs)} matching Directories obeying '{date_created.year}/{date_created.month}-*/{date_created.day}-*'. There should be exactly 1. The Directories are:\n{', '.join(matching_dirs)}"
                    logging.warning(msg)
    return directories


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format=vars.LOG_FORMAT,
                        datefmt=vars.LOG_DATEFMT,
                        filename=vars.LOG_FILE,
                        filemode='a')
    logging.info('%s %s %s', vars.HLINE, 'transfer_files.py', vars.HLINE)
    directories: set[Path] = transfer_files()
    add_media_files(directories)
