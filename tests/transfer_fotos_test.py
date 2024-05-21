import os
import pytest

from transfer_fotos import transfer_fotos
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def test_transfer_fotos(create_dirs, copy_fotos, create_day_dir):
    """Tests if one foto is copied correctly from `tmp_dir` to it's corresponding `day_dir`

    TODO: Enhance to multiple media files."""
    tmp_dir, tagebuch_dir = create_dirs
    foto_1, foto_2 = copy_fotos

    # Has to exists for transfer_fotos to work properly
    # day_dir: Path = tagebuch_dir/'2020/09-September/13-Bamberg'
    # os.makedirs(day_dir)
    day_dir = create_day_dir

    # Change directory for glob.glob() call
    # Otherwise it will search ~/.tagebuch
    os.chdir(tagebuch_dir)

    directories: set[str] = transfer_fotos(tmp_dir, tagebuch_dir)

    assert os.path.isfile(day_dir/foto_1.name)
    assert os.path.isfile(day_dir/foto_2.name)
    assert len(directories) == 1


def test_transfer_fotos_no_day_dir(create_dirs, copy_fotos):
    """Test if an Exception is raised if the corresponding `day_dir` is absent."""
    tmp_dir, tagebuch_dir = create_dirs
    _ = copy_fotos

    # Change directory for glob.glob() call
    # Otherwise it will search ~/.tagebuch
    os.chdir(tagebuch_dir)

    with pytest.raises(Exception) as e:
        transfer_fotos(tmp_dir, tagebuch_dir)
    assert e.type == Exception


def test_transfer_fotos_two_day_dir(create_dirs, copy_fotos, create_day_dir):
    """Test if two directories for the same day exists, here '2020/09-September/13-Bamberg' and '2020/09-September/13-Nicht-Bamberg'"""
    tmp_dir, tagebuch_dir = create_dirs
    _ = copy_fotos
    _ = create_day_dir

    # Create second day_dir
    day_dir2: Path = tagebuch_dir/'2020/09-September/13-Nicht-Bamberg'
    os.makedirs(day_dir2)

    # Change directory for glob.glob() call
    # Otherwise it will search ~/.tagebuch
    os.chdir(tagebuch_dir)

    with pytest.raises(Exception) as e:
        transfer_fotos(tmp_dir, tagebuch_dir)
    os.rmdir(day_dir2)
    assert e.type == Exception
