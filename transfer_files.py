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
            match file_path.suffix:
                case '.mp4' | '.MP4':
                    exif_output = subprocess.check_output(["exiftool", "-CreateDate", file_path])
                    exif_output = exif_output.decode('utf-8')
                    # Retrieve date from following line:
                    # Create Date                     : 2023:05:12 13:58:16
                    date_created = exif_output.split(' : ')[-1].split(' ')[0]
                case '.jpg' | '.jpeg' | '.png' | '.MP4' | '.JPG' | '.JPEG':
                    exif_output = subprocess.check_output(["exif", "-t", "0x9003", "--ifd=EXIF", file_path])
                    exif_lines = exif_output.decode("utf-8").splitlines()
                    date_created = exif_lines[-1].split()[1]
                case _:
                    logging.error(f"Nothing done for new File Type: {file_path}")
                    continue
            # split 'yyyy:mm:dd'
            year, month, day = date_created.split(":", 2)

            # Find matching directories
            matching_dirs = glob.glob(f"{year}/{month}-*/{day}-*")
            count = len(matching_dirs)

            if count == 1:
                # Transfer image to directory
                target_dir = matching_dirs[0]
                shutil.copy(file_path,
                            tagebuch_dir/target_dir/file_path.name)

                logging.info(f"Copied '{file_path}' to '{tagebuch_dir/target_dir/file_path.name}'")
                directories.add(target_dir)
                logging.info(f"Added '{target_dir}' to `directories`")
            else:
                logging.error(
                    f"Found {count} matching Directories obeying '{year}/{month}-*/{day}-*'. There should be exactly 1. The Directories are:\n{', '.join(matching_dirs)}")
                raise Exception('Check Log-File')
    return directories


if __name__ == "__main__":
    directories: set[str] = transfer_files(tmp_dir, tagebuch_dir)
    add_media_files(directories)
