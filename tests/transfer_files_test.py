import vars
import glob
import shutil
import pytest
import os
import subprocess
from typing import TYPE_CHECKING

from tests.vars import (
    foto_1_name,
    foto_2_name,
    tf_foto_no_day_dir,
    tf_foto_two_day_dir,
    video_1_name,
    tests_dir,
    test_diary_dir,
    test_tmp_dir,
    test_transfered_dir,
)
from transfer_files import transfer_files

if TYPE_CHECKING:
    from pathlib import Path


# ─── Fixtures ──────────

@pytest.fixture
def copy_fotos_tmp_dir(request):
    """Copy media files necessary for a test into the .tmp/ directory of the test diary."""
    media_files = request.node.get_closest_marker('media_files').args[0]
    for media_file in media_files:
        shutil.copy(media_file, test_tmp_dir)


@pytest.fixture
def create_second_day_dir():
    day_dir2: Path = test_diary_dir/'2020/09-September/13-09-2020-Nicht-Bamberg'
    os.makedirs(day_dir2)
    yield
    # Remove second day dir to avoid disturbing other tests
    # Reminder: setup_diary is only executed once: scope='session'
    shutil.rmtree(day_dir2)


# ─── Tests ──────────

@pytest.mark.media_files((tests_dir / foto_1_name,
                          tests_dir / foto_2_name,
                          tests_dir / video_1_name))
def test_transfer_files(copy_fotos_tmp_dir, monkeypatch):
    """Tests if media files are copied correctly from `.tmp/` to it's corresponding 'day_dir_{fotos, video}'. This directory must exists for `transfer_files()` to work properly."""
    _ = copy_fotos_tmp_dir
    monkeypatch.setattr(vars, 'tagebuch_dir', test_diary_dir)

    directories: set[Path] = transfer_files(test_tmp_dir, test_diary_dir)
    assert len(directories) == 2

    day_dir_fotos = test_diary_dir/'2020/09-September/13-09-2020-Bamberg-tf'
    day_dir_video = test_diary_dir/'2023/05-Mai/12-05-2023-Eisbachwelle-tf'

    assert os.path.isfile(day_dir_fotos / foto_1_name)
    assert os.path.isfile(day_dir_fotos / foto_2_name)
    assert os.path.isfile(day_dir_video / video_1_name)
    # Assert media files were moved to 'tmp/transfered/'
    assert not os.path.isfile(test_tmp_dir / foto_1_name)
    assert not os.path.isfile(test_tmp_dir / foto_2_name)
    assert not os.path.isfile(test_tmp_dir / video_1_name)
    assert os.path.isfile(test_transfered_dir / foto_1_name)
    assert os.path.isfile(test_transfered_dir / foto_2_name)
    assert os.path.isfile(test_transfered_dir / video_1_name)


@pytest.mark.media_files((tests_dir / tf_foto_no_day_dir,))
def test_transfer_files_no_day_dir(monkeypatch, copy_fotos_tmp_dir):
    """Test if the directory for the foto and an HTML entry are created, if there is was none beforehand."""
    _ = copy_fotos_tmp_dir
    monkeypatch.setattr(vars, 'tagebuch_dir', test_diary_dir)

    foto_1 = test_tmp_dir / tf_foto_no_day_dir

    exif_output = subprocess.check_output(["exif", "-t", "0x9003", "--ifd=EXIF", foto_1])
    exif_lines = exif_output.decode("utf-8").splitlines()
    # 2024, 05, 13
    date_created = exif_lines[-1].split()[1]
    year, month, day = date_created.split(":", 2)

    # Find matching directories -> should be emtpy before transfer_files()
    matching_dirs = glob.glob(f"{test_diary_dir}/{year}/{month}-*/{day}-{month}-{year}-*")
    assert len(matching_dirs) == 0

    directories: set[Path] = transfer_files(test_tmp_dir, test_diary_dir)

    # Assert newly created diary is added
    assert len(directories) == 1
    # Assert 1 day dir was created
    day_dirs = glob.glob(str(test_diary_dir / f'{year}/{month}-*/{day}-{month}-{year}-*'))
    assert len(day_dirs) == 1
    assert os.path.isdir((day_dir := day_dirs[0]))
    # Assert 1 html entry for the day was created
    html_entries = glob.glob(os.path.join(day_dir, f'{day}-{month}-{year}*.html'))
    assert len(html_entries) == 1
    assert os.path.isfile(html_entries[0])
    # Assert that foto was copied correctly to day dir
    assert os.path.isfile(day_dir/tf_foto_no_day_dir)
    # Assert foto was moved from .tmp/ to .tmp/transfered/
    assert not os.path.isfile(foto_1)
    assert os.path.isfile(test_transfered_dir / tf_foto_no_day_dir)


@pytest.mark.media_files((tests_dir / tf_foto_two_day_dir,))
def test_transfer_files_two_day_dir(monkeypatch, copy_fotos_tmp_dir, create_second_day_dir):
    """Test if two directories for the same day exists, here '2020/09-September/13-Bamberg' and '2020/09-September/13-Nicht-Bamberg'."""
    _ = copy_fotos_tmp_dir
    _ = create_second_day_dir
    monkeypatch.setattr(vars, 'tagebuch_dir', test_diary_dir)

    foto_1 = test_tmp_dir / tf_foto_two_day_dir

    exif_output = subprocess.check_output(["exif", "-t", "0x9003", "--ifd=EXIF", foto_1])
    exif_lines = exif_output.decode("utf-8").splitlines()
    # 2020, 05, 13
    date_created = exif_lines[-1].split()[1]
    year, month, day = date_created.split(":", 2)

    directories: set[Path] = transfer_files(test_tmp_dir, test_diary_dir)

    # Assert no directory was added (for further processing)
    assert len(directories) == 0
    # Assert there are 2 dirs for the date
    matching_dirs = glob.glob(f"{test_diary_dir}/{year}/{month}-*/{day}-{month}-{year}-*")
    assert len(matching_dirs) == 2
    # Assert foto was not move from .tmp/ to .tmp/transfered
    assert os.path.isfile(foto_1)
    assert not os.path.isfile(test_transfered_dir / tf_foto_two_day_dir)
