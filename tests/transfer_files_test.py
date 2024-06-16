import glob
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.vars import (
    foto_1_name,
    foto_2_name,
    test_diary_dir,
    test_tmp_dir,
    test_transfered_dir,
    test_dir,
    tf_foto_no_day_dir,
    tf_foto_two_day_dir,
    video_1_name,
)
from transfer_files import transfer_files

# ─── Fixtures ──────────


@pytest.fixture(autouse=True)
def _copy_fotos_tmp_dir(request):
    """Copy media files necessary for a test into the .tmp/ directory of the test diary."""
    media_files = request.node.get_closest_marker('media_files').args[0]
    for media_file in media_files:
        shutil.copy(media_file, test_tmp_dir)


@pytest.fixture
def _create_second_day_dir():
    day_dir2: Path = test_diary_dir/'2020/09-September/13-09-2020-Nicht-Bamberg'
    Path.mkdir(day_dir2, parents=True)
    yield
    # Remove second day dir to avoid disturbing other tests
    # Reminder: setup_diary is only executed once: scope='session'
    shutil.rmtree(day_dir2)


# ─── Tests ──────────

@pytest.mark.usefixtures('_copy_fotos_tmp_dir')
@pytest.mark.media_files((test_dir / foto_1_name,
                          test_dir / foto_2_name,
                          test_dir / video_1_name))
def test_transfer_files():
    """Tests if media files are copied correctly from `.tmp/` to it's corresponding 'day_dir_{fotos, video}'. This directory must exists for `transfer_files()` to work properly."""
    directories: set[Path] = transfer_files()
    nmb_different_day_dirs = 2
    assert len(directories) == nmb_different_day_dirs

    day_dir_fotos = test_diary_dir/'2020/09-September/13-09-2020-Bamberg-tf'
    day_dir_video = test_diary_dir/'2023/05-Mai/12-05-2023-Eisbachwelle-tf'

    assert Path.is_file(day_dir_fotos / foto_1_name)
    assert Path.is_file(day_dir_fotos / foto_2_name)
    assert Path.is_file(day_dir_video / video_1_name)
    # Assert media files were moved to 'tmp/transfered/'
    assert not Path.is_file(test_tmp_dir / foto_1_name)
    assert not Path.is_file(test_tmp_dir / foto_2_name)
    assert not Path.is_file(test_tmp_dir / video_1_name)
    assert Path.is_file(test_transfered_dir / foto_1_name)
    assert Path.is_file(test_transfered_dir / foto_2_name)
    assert Path.is_file(test_transfered_dir / video_1_name)


@pytest.mark.usefixtures('_copy_fotos_tmp_dir')
@pytest.mark.media_files((test_dir / tf_foto_no_day_dir,))
def test_transfer_files_no_day_dir():
    """Test if the directory for the foto and an HTML entry are created, if there is was none beforehand."""
    foto_1 = test_tmp_dir / tf_foto_no_day_dir

    exif_output = subprocess.check_output(["/usr/bin/exif", "-t", "0x9003", "--ifd=EXIF", foto_1])
    exif_lines = exif_output.decode("utf-8").splitlines()
    # 2024, 05, 13
    date_created = exif_lines[-1].split()[1]
    year, month, day = date_created.split(":", 2)

    # Find matching directories -> should be emtpy before transfer_files()
    matching_dirs = glob.glob(f"{test_diary_dir}/{year}/{month}-*/{day}-{month}-{year}-*")
    assert len(matching_dirs) == 0

    directories: set[Path] = transfer_files()

    # Assert newly created diary is added
    assert len(directories) == 1
    # Assert 1 day dir was created
    day_dirs = glob.glob(str(test_diary_dir / f'{year}/{month}-*/{day}-{month}-{year}-*'))
    assert len(day_dirs) == 1
    day_dir = Path(day_dirs[0])
    assert Path.is_dir(day_dir)
    # Assert 1 html entry for the day was created
    html_entries = glob.glob(os.path.join(day_dir, f'{day}-{month}-{year}*.html'))
    assert len(html_entries) == 1
    assert Path.is_file(Path(html_entries[0]))
    # Assert that foto was copied correctly to day dir
    assert Path.is_file(day_dir/tf_foto_no_day_dir)
    # Assert foto was moved from .tmp/ to .tmp/transfered/
    assert not Path.is_file(foto_1)
    assert Path.is_file(test_transfered_dir / tf_foto_no_day_dir)


@pytest.mark.usefixtures('_create_second_day_dir')
@pytest.mark.media_files((test_dir / tf_foto_two_day_dir,))
def test_transfer_files_two_day_dir():
    """Test if two directories for the same day exists, here '2020/09-September/13-Bamberg' and '2020/09-September/13-Nicht-Bamberg'."""
    foto_1 = test_tmp_dir / tf_foto_two_day_dir

    exif_output = subprocess.check_output(["/usr/bin/exif", "-t", "0x9003", "--ifd=EXIF", foto_1])
    exif_lines = exif_output.decode("utf-8").splitlines()
    # 2020, 05, 13
    date_created = exif_lines[-1].split()[1]
    year, month, day = date_created.split(":", 2)

    directories: set[Path] = transfer_files()

    # Assert no directory was added (for further processing)
    assert len(directories) == 0
    # Assert there are 2 dirs for the date
    matching_dirs = glob.glob(f"{test_diary_dir}/{year}/{month}-*/{day}-{month}-{year}-*")
    nmb_equal_day_dirs = 2
    assert len(matching_dirs) == nmb_equal_day_dirs
    # Assert foto was not move from .tmp/ to .tmp/transfered
    assert Path.is_file(foto_1)
    assert not Path.is_file(test_transfered_dir / tf_foto_two_day_dir)
