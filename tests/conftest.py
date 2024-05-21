import os
import shutil
from pathlib import Path

import pytest


@pytest.fixture
def create_day_dir(create_dirs):
    _, tagebuch_dir = create_dirs
    os.makedirs((day_dir := tagebuch_dir/'2020/09-September/13-Bamberg'))
    yield day_dir
    # os.rmdir() raises Exception because it isn't empty after test_transfer_fotos()
    shutil.rmtree(day_dir)


@pytest.fixture
def create_dirs(tmp_path):
    tmp_dir = tmp_path
    tagebuch_dir = tmp_path/'.tagebuch'
    os.mkdir(tagebuch_dir)
    yield tmp_dir, tagebuch_dir
    # Revert directory change after each test
    os.chdir(Path.home()/'.tagebuch')


@pytest.fixture
def copy_fotos(create_dirs):
    tmp_dir, _ = create_dirs
    # Copy fotos into 'test .tmp dir'
    shutil.copy((foto_1 := Path('./tests/transfer_fotos_1.jpg')),
                tmp_dir)
    shutil.copy((foto_2 := Path('./tests/transfer_fotos_2.jpg')),
                tmp_dir)
    yield foto_1, foto_2
