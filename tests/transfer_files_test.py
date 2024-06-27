import glob
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.vars import (
    TEST_DIARY_DIR,
    TEST_DIR,
    TEST_TMP_DIR,
    TEST_TRANSFERED_DIR,
)
from transfer_files import transfer_files

FOTO_1_NAME: Path = Path('transfer_files_foto_1.jpg')
FOTO_2_NAME: Path = Path('transfer_files_foto_2.jpg')
TF_FOTO_NO_DAY_DIR: Path = Path('transfer_files_no_day_dir.jpg')
TF_FOTO_TWO_DAY_DIR: Path = Path('transfer_files_two_day_dir.jpg')
VIDEO_1_NAME: Path = Path('transfer_files_video_1.mp4')

# ─── Fixtures ──────────


@pytest.fixture(autouse=True)
def _copy_fotos_tmp_dir(request):
    """Copy media files necessary for a test into the .tmp/ directory of the test diary."""
    media_files = request.node.get_closest_marker('media_files').args[0]
    for media_file in media_files:
        shutil.copy(media_file, TEST_TMP_DIR)


@pytest.fixture
def _create_second_day_dir():
    day_dir2: Path = TEST_DIARY_DIR/'2020/09-September/13-09-2020-Nicht-Bamberg'
    Path.mkdir(day_dir2, parents=True)
    yield
    # Remove second day dir to avoid disturbing other tests
    # Reminder: setup_diary is only executed once: scope='session'
    shutil.rmtree(day_dir2)


# ─── Tests ──────────

@pytest.mark.usefixtures('_copy_fotos_tmp_dir')
@pytest.mark.media_files((TEST_DIR / FOTO_1_NAME,
                          TEST_DIR / FOTO_2_NAME,
                          TEST_DIR / VIDEO_1_NAME))
def test_transfer_files():
    """Tests if media files are copied correctly from `.tmp/` to it's corresponding 'day_dir_{fotos, video}'. This directory must exists for `transfer_files()` to work properly."""
    directories: set[Path] = transfer_files()
    nmb_different_day_dirs = 2
    assert len(directories) == nmb_different_day_dirs

    day_dir_fotos = TEST_DIARY_DIR/'2020/09-September/13-09-2020-Bamberg-tf'
    day_dir_video = TEST_DIARY_DIR/'2023/05-Mai/12-05-2023-Eisbachwelle-tf'

    assert Path.is_file(day_dir_fotos / FOTO_1_NAME)
    assert Path.is_file(day_dir_fotos / FOTO_2_NAME)
    assert Path.is_file(day_dir_video / VIDEO_1_NAME)
    # Assert media files were moved to 'tmp/transfered/'
    assert not Path.is_file(TEST_TMP_DIR / FOTO_1_NAME)
    assert not Path.is_file(TEST_TMP_DIR / FOTO_2_NAME)
    assert not Path.is_file(TEST_TMP_DIR / VIDEO_1_NAME)
    assert Path.is_file(TEST_TRANSFERED_DIR / FOTO_1_NAME)
    assert Path.is_file(TEST_TRANSFERED_DIR / FOTO_2_NAME)
    assert Path.is_file(TEST_TRANSFERED_DIR / VIDEO_1_NAME)


@pytest.mark.usefixtures('_copy_fotos_tmp_dir')
@pytest.mark.media_files((TEST_DIR / TF_FOTO_NO_DAY_DIR,))
def test_transfer_files_no_day_dir():
    """Test if the directory for the foto and an HTML entry are created, if there is was none beforehand."""
    foto_1 = TEST_TMP_DIR / TF_FOTO_NO_DAY_DIR

    exif_output = subprocess.check_output(["/usr/bin/exif", "-t", "0x9003", "--ifd=EXIF", foto_1])
    exif_lines = exif_output.decode("utf-8").splitlines()
    # 2024, 05, 13
    date_created = exif_lines[-1].split()[1]
    year, month, day = date_created.split(":", 2)

    # Find matching directories -> should be emtpy before transfer_files()
    matching_dirs = glob.glob(f"{TEST_DIARY_DIR}/{year}/{month}-*/{day}-{month}-{year}-*")
    assert len(matching_dirs) == 0

    directories: set[Path] = transfer_files()

    # Assert newly created diary is added
    assert len(directories) == 1
    # Assert 1 day dir was created
    day_dirs = glob.glob(str(TEST_DIARY_DIR / f'{year}/{month}-*/{day}-{month}-{year}-*'))
    assert len(day_dirs) == 1
    day_dir = Path(day_dirs[0])
    assert Path.is_dir(day_dir)
    # Assert 1 html entry for the day was created
    html_entries = glob.glob(os.path.join(day_dir, f'{day}-{month}-{year}*.html'))
    assert len(html_entries) == 1
    assert Path.is_file(Path(html_entries[0]))
    # Assert that foto was copied correctly to day dir
    assert Path.is_file(day_dir/TF_FOTO_NO_DAY_DIR)
    # Assert foto was moved from .tmp/ to .tmp/transfered/
    assert not Path.is_file(foto_1)
    assert Path.is_file(TEST_TRANSFERED_DIR / TF_FOTO_NO_DAY_DIR)


@pytest.mark.usefixtures('_create_second_day_dir')
@pytest.mark.media_files((TEST_DIR / TF_FOTO_TWO_DAY_DIR,))
def test_transfer_files_two_day_dir():
    """Test if two directories for the same day exists, here '2020/09-September/13-Bamberg' and '2020/09-September/13-Nicht-Bamberg'."""
    foto_1 = TEST_TMP_DIR / TF_FOTO_TWO_DAY_DIR

    exif_output = subprocess.check_output(["/usr/bin/exif", "-t", "0x9003", "--ifd=EXIF", foto_1])
    exif_lines = exif_output.decode("utf-8").splitlines()
    # 2020, 05, 13
    date_created = exif_lines[-1].split()[1]
    year, month, day = date_created.split(":", 2)

    directories: set[Path] = transfer_files()

    # Assert no directory was added (for further processing)
    assert len(directories) == 0
    # Assert there are 2 dirs for the date
    matching_dirs = glob.glob(f"{TEST_DIARY_DIR}/{year}/{month}-*/{day}-{month}-{year}-*")
    nmb_equal_day_dirs = 2
    assert len(matching_dirs) == nmb_equal_day_dirs
    # Assert foto was not move from .tmp/ to .tmp/transfered
    assert Path.is_file(foto_1)
    assert not Path.is_file(TEST_TRANSFERED_DIR / TF_FOTO_TWO_DAY_DIR)
