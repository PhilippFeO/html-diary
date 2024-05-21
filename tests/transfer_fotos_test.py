import os
from typing import TYPE_CHECKING

import pytest

from transfer_fotos import transfer_fotos

if TYPE_CHECKING:
    from pathlib import Path


def test_transfer_fotos(create_dirs: tuple['Path', 'Path'],
                        copy_fotos: tuple['Path', 'Path'],
                        copy_video: 'Path',
                        create_day_dir_fotos: 'Path',
                        create_day_dir_video: 'Path'):
    """Tests if one foto is copied correctly from `tmp_dir` to it's corresponding `day_dir_{fotos, video}`."""
    tmp_dir, tagebuch_dir = create_dirs
    foto_1, foto_2 = copy_fotos
    video_1 = copy_video

    # Has to exists for transfer_fotos to work properly
    day_dir_fotos = create_day_dir_fotos
    day_dir_video = create_day_dir_video

    # Change directory for glob.glob() call
    # Otherwise it will search ~/.tagebuch
    os.chdir(tagebuch_dir)

    directories: set[str] = transfer_fotos(tmp_dir, tagebuch_dir)

    assert os.path.isfile(day_dir_fotos/foto_1.name)
    assert os.path.isfile(day_dir_fotos/foto_2.name)
    assert os.path.isfile(day_dir_video/video_1.name)
    assert len(directories) == 2


def test_transfer_fotos_no_day_dir(create_dirs: tuple['Path', 'Path'],
                                   copy_fotos: tuple['Path', 'Path']):
    """Test if an Exception is raised if the corresponding `day_dir` is absent."""
    tmp_dir, tagebuch_dir = create_dirs
    _ = copy_fotos

    # Change directory for glob.glob() call
    # Otherwise it will search ~/.tagebuch
    os.chdir(tagebuch_dir)

    with pytest.raises(Exception) as e:
        transfer_fotos(tmp_dir, tagebuch_dir)
    assert e.type == Exception


def test_transfer_fotos_two_day_dir(create_dirs: tuple['Path', 'Path'],
                                    copy_fotos: tuple['Path', 'Path'],
                                    create_day_dir_fotos: 'Path'):
    """Test if two directories for the same day exists, here '2020/09-September/13-Bamberg' and '2020/09-September/13-Nicht-Bamberg'"""
    tmp_dir, tagebuch_dir = create_dirs
    _ = copy_fotos
    _ = create_day_dir_fotos

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
