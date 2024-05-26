import pytest
import os
from pathlib import Path


@pytest.fixture
def create_dirs(tmp_path):
    test_tagebuch_dir = tmp_path/'.tagebuch'
    test_tmp_dir = test_tagebuch_dir/'.tmp'
    os.mkdir(test_tagebuch_dir)
    os.mkdir(test_tmp_dir)
    os.mkdir(test_tmp_dir/'transfered')
    yield test_tmp_dir, test_tagebuch_dir
    # Revert directory change after each test
    os.chdir(Path.home()/'.tagebuch')
