import os
import shutil
from pathlib import Path

import pytest

tagebuch_dir = Path.home()/'.tagebuch'


@pytest.fixture
def create_day_dir_fotos(create_dirs):
    _, test_tagebuch_dir = create_dirs
    os.makedirs((day_dir_foto := test_tagebuch_dir/'2020/09-September/13-09-2020-Bamberg'))
    yield day_dir_foto
    # os.rmdir() raises Exception because it isn't empty after test_transfer_files()
    shutil.rmtree(day_dir_foto)


@pytest.fixture
def create_day_dir_video(create_dirs):
    _, test_tagebuch_dir = create_dirs
    os.makedirs((day_dir_video := test_tagebuch_dir/'2023/05-Mai/12-05-2023-Eisbachwelle'))
    yield day_dir_video
    # os.rmdir() raises Exception because it isn't empty after test_transfer_files()
    shutil.rmtree(day_dir_video)


@pytest.fixture
def copy_fotos(create_dirs):
    tagebuch_dir = Path(Path.home()/'.tagebuch')
    test_tmp_dir, _ = create_dirs
    foto_1 = Path('transfer_files_foto_1.jpg')
    foto_2 = Path('transfer_files_foto_2.jpg')
    # Copy fotos into 'test .tmp dir'
    shutil.copy(tagebuch_dir/'tests'/foto_1,
                (foto_1 := test_tmp_dir/foto_1))
    shutil.copy(tagebuch_dir/'tests'/foto_2,
                (foto_2 := test_tmp_dir/foto_2))
    yield foto_1, foto_2


@pytest.fixture
def copy_video(create_dirs):
    test_tmp_dir, _ = create_dirs
    # Copy video into 'test .tmp dir'
    shutil.copy((video_1 := Path(f'{tagebuch_dir}/tests/transfer_files_video_1.mp4')),
                test_tmp_dir)
    yield video_1
