import datetime
import glob
import logging
import os
import shutil
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup

from add_media_files import add_media_files


# Define the path to the directory containing the files
tagebuch_dir = Path.home()/'.tagebuch'
tmp_dir = tagebuch_dir/'.tmp'

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s: %(asctime)s] %(message)s',
                    # Mit Datum: %d.%m.%Y
                    datefmt=' %Y.%m.%d  %H:%M:%S',
                    filename=tagebuch_dir/'.logs/transfer_files_add_media_files.log.txt',
                    filemode='a')
length = 20
logging.info(f'{"-" * length} {datetime.datetime.today()} {"-" * length}')


def copy_helper(media_file: Path,
                day_dir: Path,
                tagebuch_dir: Path):
    shutil.copy(media_file,
                tagebuch_dir/day_dir/media_file.name)
    logging.info(f"Copied '{media_file}' to '{tagebuch_dir/day_dir/media_file.name}'")
    shutil.move(media_file,
                (transfered_dir := tagebuch_dir/'.tmp/transfered'))
    logging.info(f"Moved '{media_file}' to '{transfered_dir}'.")


def transfer_files(tmp_dir: Path,
                   tagebuch_dir: Path) -> set[Path]:
    """Copies Media files from .tmp to the according directory of the created date.

    To test this function, `tagebuch_dir` has to be parameter. Via pytest, I create a fake Tagebuch under `tmp_path`."""
    directories: set[Path] = set()
    # Loop through files in the directory
    for f in os.listdir(tmp_dir):
        media_file = tmp_dir/f
        if os.path.isfile(media_file):
            # Extract creation date from EXIF data
            exif_output: bytes = bytes()
            date_created: str = ''
            match media_file.suffix:
                case '.mp4' | '.MP4':
                    exif_output = subprocess.check_output(["exiftool", "-CreateDate", media_file])
                    # Retrieve date from following line:
                    # Create Date                     : 2023:05:12 13:58:16
                    date_created = exif_output.decode('utf-8').split(' : ')[-1].split(' ')[0]
                case '.jpg' | '.jpeg' | '.png' | '.MP4' | '.JPG' | '.JPEG':
                    try:
                        exif_output = subprocess.check_output(["exif", "-t", "0x9003", "--ifd=EXIF", media_file])
                        exif_lines = exif_output.decode("utf-8").splitlines()
                        date_created = exif_lines[-1].split()[1]
                    except subprocess.CalledProcessError:
                        logging.error(f"Foto '{media_file}' has no Tag with ID 0x9003 in it's exif data.")
                    # PANO*.jpg
                    if date_created is None:
                        try:
                            # Panorama images dont have anything like 'date created', hence I have to use 'GPS Date Stamp':
                            # GPS Date Stamp                  : 2024:05:22
                            exif_output = subprocess.check_output(["exiftool", "-GPSDateStamp", media_file])
                            # In comparison to the mp4 usecase, exif_output has a trailing \n which has to be removed
                            date_created = exif_output.decode('utf-8').rstrip().split(' : ')[-1]
                        except subprocess.CalledProcessError:
                            logging.error(f"Foto '{media_file}' has no 'GPSDateStamp' Tag in it's exif data.")
                case _:
                    logging.warning(f"Nothing done for File Type: '{media_file.suffix}'. Full path: '{media_file}'")
                    continue
            # split 'yyyy:mm:dd'
            year, month, day = date_created.split(":", 2)

            # Find matching directories
            matching_dirs = glob.glob(f"{year}/{month}-*/{day}-{month}-{year}-*")

            # Move/Copy the media files to their corresponding diary entry.
            # Ie the entry fitting their created date.
            match (count := len(matching_dirs)):
                case 1:
                    # Transfer image to directory
                    day_dir = Path(matching_dirs[0])
                    copy_helper(media_file,
                                day_dir,
                                tagebuch_dir)
                    directories.add(day_dir)
                    logging.info(f"Added '{day_dir}' to `directories`.")
                case 0:
                    # Create new empty entry
                    # Media files were added if there was an entry fitting the created date.
                    # Some media files have no according entry for their created date. In this block,
                    # the (empty) entry is created to avoid remaining media files in .tmp/.
                    date_obj = datetime.datetime.strptime(date_created, '%Y:%m:%d').date()
                    # Necessary because returned values are in English
                    import locale
                    locale.setlocale(locale.LC_ALL, '')
                    weekday = date_obj.strftime('%A')
                    title = f"{weekday}, {date_obj.strftime('%d. %B %Y')}"
                    html_skeleton = "<!DOCTYPE html>" + \
                        '<html>' + \
                        '  <head>' + \
                        f'	<title>{title}</title>' + \
                        '	<!-- weitere Kopfinformationen -->' + \
                        '	<!-- Styles für <pre> -->' + \
                        '	<link rel="stylesheet" href="/home/philipp/.tagebuch/style.css">' + \
                        '  </head>' + \
                        '  <body>' + \
                        f'	<h1>{title}</h1>' + \
                        '  </body>' + \
                        '</html>'
                    entry = BeautifulSoup(html_skeleton, 'html.parser')
                    # For the sake of consistency, add an (empty) pre-tag
                    # consistency: Every entry has one and add_media_files(…) logic is based on the existence of this pre-tag
                    empty_pre_tag = entry.new_tag('pre')
                    if (h1_tag := entry.find('h1')):
                        h1_tag.insert_after(empty_pre_tag)
                        month_name = date_obj.strftime('%B')
                        # Create entry with empty pre-tag
                        day_dir: Path = Path.home()/f'.tagebuch/{year}/{month}-{month_name}/{day}-{month}-{year}-{weekday}'
                        os.makedirs(day_dir)
                        logging.info(f"Created Directory: '{day_dir}'")
                        # Write the HTML (media files are added later as usual)
                        day_entry = day_dir/f'{day}-{month}-{year}.html'
                        with open(day_entry, 'w') as f:
                            f.write(entry.prettify())
                        logging.info(f'Created no-description Entry for {year}-{month}-{day}: "{day_entry}"')
                        copy_helper(media_file,
                                    day_dir,
                                    tagebuch_dir)
                        directories.add(day_dir)
                        logging.info(f"Added '{day_dir}' to `directories`.")
                    else:
                        logging.error('No h1-tag in `html_skeleton`.')
                case _:
                    logging.warning(
                        f"Found {count} matching Directories obeying '{year}/{month}-*/{day}-*'. There should be exactly 1. The Directories are:\n{', '.join(matching_dirs)}")
    return directories


if __name__ == "__main__":
    directories: set[Path] = transfer_files(tmp_dir, tagebuch_dir)
    add_media_files(directories)
