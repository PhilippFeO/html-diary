import glob
import os
import subprocess
from typing import TYPE_CHECKING

from transfer_files import transfer_files

from fixtures_transfer_files import (
    copy_fotos,
    copy_video,
    create_day_dir_fotos,
    create_day_dir_video,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_transfer_files(create_dirs: tuple['Path', 'Path'],
                        copy_fotos: tuple['Path', 'Path'],
                        copy_video: 'Path',
                        create_day_dir_fotos: 'Path',
                        create_day_dir_video: 'Path'):
    """Tests if one foto is copied correctly from `tmp_dir` to it's corresponding `day_dir_{fotos, video}`."""
    tmp_dir, tagebuch_dir = create_dirs
    foto_1, foto_2 = copy_fotos
    video_1 = copy_video

    # Has to exists for transfer_files to work properly
    day_dir_fotos = create_day_dir_fotos
    day_dir_video = create_day_dir_video

    # Change directory for glob.glob() call
    # Otherwise it will search ~/.tagebuch
    os.chdir(tagebuch_dir)

    directories: set[Path] = transfer_files(tmp_dir, tagebuch_dir)

    assert os.path.isfile(day_dir_fotos/foto_1.name)
    assert os.path.isfile(day_dir_fotos/foto_2.name)
    assert os.path.isfile(day_dir_video/video_1.name)
    assert len(directories) == 2


def test_transfer_files_no_day_dir(create_dirs: tuple['Path', 'Path'],
                                   copy_fotos: tuple['Path', 'Path']):
    """Test if an Exception is raised if the corresponding `day_dir` is absent."""
    _, test_tagebuch_dir = create_dirs
    foto_1, _ = copy_fotos

    exif_output = subprocess.check_output(["exif", "-t", "0x9003", "--ifd=EXIF", foto_1])
    exif_lines = exif_output.decode("utf-8").splitlines()
    date_created = exif_lines[-1].split()[1]
    year, month, day = date_created.split(":", 2)

    # Change directory for glob.glob() call
    # Otherwise it will search ~/.tagebuch
    os.chdir(test_tagebuch_dir)

    # Find matching directories
    matching_dirs = glob.glob(f"{year}/{month}-*/{day}-{month}-{year}-*")
    assert len(matching_dirs) == 0


def test_transfer_files_two_day_dir(create_dirs: tuple['Path', 'Path'],
                                    copy_fotos: tuple['Path', 'Path'],
                                    create_day_dir_fotos: 'Path'):
    """Test if two directories for the same day exists, here '2020/09-September/13-Bamberg' and '2020/09-September/13-Nicht-Bamberg'"""
    _, test_tagebuch_dir = create_dirs
    foto_1, _ = copy_fotos
    _ = create_day_dir_fotos

    # Create second day_dir
    day_dir2: Path = test_tagebuch_dir/'2020/09-September/13-09-2020-Nicht-Bamberg'
    os.makedirs(day_dir2)

    exif_output = subprocess.check_output(["exif", "-t", "0x9003", "--ifd=EXIF", foto_1])
    exif_lines = exif_output.decode("utf-8").splitlines()
    date_created = exif_lines[-1].split()[1]
    year, month, day = date_created.split(":", 2)

    # Change directory for glob.glob() call
    # Otherwise it will search ~/.tagebuch
    os.chdir(test_tagebuch_dir)

    # Find matching directories
    matching_dirs = glob.glob(f"{year}/{month}-*/{day}-{month}-{year}-*")
    assert len(matching_dirs) == 2
