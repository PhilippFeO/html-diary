import datetime

# Necessary because returned values are in English
# Can't stay in main because also needed during testing
import locale
import logging
import os
import shutil
import subprocess
from pathlib import Path

from add_media_files import add_media_files
from utils import count_directories, create_dir_file, make_new_entry

import vars

locale.setlocale(locale.LC_ALL, '')

# TODO: in ifmain <26-05-2024>
# Define the path to the directory containing the files

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s: %(asctime)s] %(message)s',
                    # Mit Datum: %d.%m.%Y
                    datefmt=' %Y.%m.%d  %H:%M:%S',
                    filename=vars.DIARY_DIR/'.logs/transfer_files_add_media_files.log.txt',
                    filemode='a')
length = 20
logging.info(f'{"-" * length} {datetime.datetime.today()} {"-" * length}')


def copy_helper(media_file: Path,
                day_dir: Path,
                tagebuch_dir: Path):
    shutil.copy(media_file,
                day_dir/media_file.name)
    logging.info(f"Copied '{media_file}' to '{tagebuch_dir/day_dir/media_file.name}'")
    shutil.move(media_file,
                (transfered_dir := tagebuch_dir/'.tmp/transfered'))
    logging.info(f"Moved '{media_file}' to '{transfered_dir}'.")


# def transfer_files(tmp_dir: Path,
#                    tagebuch_dir: Path) -> set[Path]:
def transfer_files() -> set[Path]:
    """Copy Media files from .tmp to the according directory of the created date.

    To test this function, `tagebuch_dir` has to be parameter. Via pytest, I create a fake Tagebuch under `tmp_path`.
    """
    directories: set[Path] = set()
    # Loop through files in the directory
    for f in os.listdir(vars.TMP_DIR):
        media_file = vars.TMP_DIR/f
        if Path.is_file(media_file):
            # Extract creation date from EXIF data
            exif_output: bytes = b''
            date_created: str = ''
            match media_file.suffix:
                case '.mp4' | '.MP4':
                    exif_output = subprocess.check_output(["/usr/bin/exiftool", "-CreateDate", media_file])
                    # Retrieve date from following line:
                    # Create Date                     : 2023:05:12 13:58:16
                    date_created = exif_output.decode('utf-8').split(' : ')[-1].split(' ')[0]
                case '.jpg' | '.jpeg' | '.png' | '.MP4' | '.JPG' | '.JPEG':
                    try:
                        exif_output = subprocess.check_output(["/usr/bin/exif", "-t", "0x9003", "--ifd=EXIF", media_file])
                        exif_lines = exif_output.decode("utf-8").splitlines()
                        date_created = exif_lines[-1].split()[1]
                    except subprocess.CalledProcessError:
                        logging.error(f"Foto '{media_file}' has no Tag with ID 0x9003 in it's exif data.")
                    # PANO*.jpg
                    if date_created == '':
                        try:
                            # Panorama images dont have anything like 'date created', hence I have to use 'GPS Date Stamp':
                            # GPS Date Stamp                  : 2024:05:22
                            exif_output = subprocess.check_output(["/usr/bin/exiftool", "-GPSDateStamp", media_file])
                            # In comparison to the mp4 usecase, exif_output has a trailing \n which has to be removed
                            date_created = exif_output.decode('utf-8').rstrip().split(' : ')[-1]
                        except subprocess.CalledProcessError:
                            logging.error(f"Foto '{media_file}' has no 'GPSDateStamp' Tag in it's exif data.")
                case _:
                    logging.warning(f"Nothing done for File Type: '{media_file.suffix}'. Full path: '{media_file}'")
                    continue
            # split 'yyyy:mm:dd'
            year, month, day = date_created.split(":", 2)

            matching_dirs = count_directories(day, month, year)
            # matching_dirs = count_directories(tagebuch_dir, day, month, year)

            # Move/Copy the media files to their corresponding diary entry.
            # Ie the entry fitting their created date.
            match len(matching_dirs):
                case 1:
                    # Transfer image to directory
                    day_dir = Path(matching_dirs[0])
                    copy_helper(media_file,
                                day_dir,
                                vars.DIARY_DIR)
                    directories.add(day_dir)
                    logging.info(f"Added '{day_dir}' to `directories`.")
                # TODO: Add Test for this case <26-05-2024>
                case 0:
                    day_dir, html_entry = make_new_entry(day, month, year)
                    create_dir_file(html_entry, day_dir, day, month, year)
                    copy_helper(media_file,
                                day_dir,
                                vars.DIARY_DIR)
                    directories.add(day_dir)
                    logging.info(f"Added '{day_dir}' to `directories`.")
                case _:
                    logging.warning(
                        f"Found {len(matching_dirs)} matching Directories obeying '{year}/{month}-*/{day}-*'. There should be exactly 1. The Directories are:\n{', '.join(matching_dirs)}")
    return directories


if __name__ == "__main__":
    directories: set[Path] = transfer_files()
    add_media_files(directories)
