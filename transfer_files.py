import datetime
import glob
import logging
import os
import shutil
import subprocess
from pathlib import Path

from add_media_files import add_media_files

# Define the path to the directory containing the files
tagebuch_dir = Path.home()/'.tagebuch'
tmp_dir = tagebuch_dir/'.tmp'


# Use different Log file when executed as test
logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s: %(asctime)s] %(message)s',
                    # Mit Datum: %d.%m.%Y
                    datefmt=' %Y.%m.%d  %H:%M:%S',
                    filename=tagebuch_dir/'.logs/transfer_files_add_media_files.log.txt',
                    filemode='a')
length = 20
logging.info(f'{"-" * length} {datetime.datetime.today()} {"-" * length}')


def transfer_files(tmp_dir: Path,
                   tagebuch_dir: Path) -> set[str]:
    directories: set[str] = set()
    # Loop through files in the directory
    for f in os.listdir(tmp_dir):
        file_path = tmp_dir/f
        if os.path.isfile(file_path):
            # Extract creation date from EXIF data
            exif_output: bytes = bytes()
            date_created: str = ''
            match file_path.suffix:
                case '.mp4' | '.MP4':
                    exif_output = subprocess.check_output(["exiftool", "-CreateDate", file_path])
                    # Retrieve date from following line:
                    # Create Date                     : 2023:05:12 13:58:16
                    date_created = exif_output.decode('utf-8').split(' : ')[-1].split(' ')[0]
                case '.jpg' | '.jpeg' | '.png' | '.MP4' | '.JPG' | '.JPEG':
                    try:
                        exif_output = subprocess.check_output(["exif", "-t", "0x9003", "--ifd=EXIF", file_path])
                        exif_lines = exif_output.decode("utf-8").splitlines()
                        date_created = exif_lines[-1].split()[1]
                    except subprocess.CalledProcessError:
                        logging.error(f"Foto '{file_path}' has no Tag with ID 0x9003 in it's exif data.")
                    # PANO*.jpg
                    if date_created is None:
                        try:
                            # Panorama images dont have anything like 'date created', hence I have to use 'GPS Date Stamp':
                            # GPS Date Stamp                  : 2024:05:22
                            exif_output = subprocess.check_output(["exiftool", "-GPSDateStamp", file_path])
                            # In comparison to the mp4 usecase, exif_output has a trailing \n which has to be removed
                            date_created = exif_output.decode('utf-8').rstrip().split(' : ')[-1]
                        except subprocess.CalledProcessError:
                            logging.error(f"Foto '{file_path}' has no 'GPSDateStamp' Tag in it's exif data.")
                case _:
                    logging.error(f"Nothing done for new File Type: {file_path}")
                    continue
            # split 'yyyy:mm:dd'
            year, month, day = date_created.split(":", 2)

            # Find matching directories
            matching_dirs = glob.glob(f"{year}/{month}-*/{day}-{month}-{year}-*")

            if (count := len(matching_dirs)) == 1:
                # Transfer image to directory
                target_dir = matching_dirs[0]
                shutil.copy(file_path,
                            tagebuch_dir/target_dir/file_path.name)
                logging.info(f"Copied '{file_path}' to '{tagebuch_dir/target_dir/file_path.name}'")
                shutil.move(file_path,
                            (transfered_dir := tagebuch_dir/'.tmp/transfered'))
                logging.info(f"Moved '{file_path}' to '{transfered_dir}'.")
                directories.add(target_dir)
                logging.info(f"Added '{target_dir}' to `directories`.")
            else:
                logging.error(
                    f"Found {count} matching Directories obeying '{year}/{month}-*/{day}-*'. There should be exactly 1. The Directories are:\n{', '.join(matching_dirs)}")
    return directories


if __name__ == "__main__":
    directories: set[str] = transfer_files(tmp_dir, tagebuch_dir)
    add_media_files(directories)
