import pytest
import shutil
import os
from pathlib import Path
from vars import tagebuch_dir


@pytest.fixture
def create_dirs(tmp_path):
    # test_tagebuch_dir = tmp_path/'.tagebuch'
    # test_tmp_dir = test_tagebuch_dir/'.tmp'
    # os.mkdir(test_tagebuch_dir)
    # os.mkdir(test_tmp_dir)
    # os.mkdir(test_tmp_dir/'transfered')
    # yield test_tmp_dir, test_tagebuch_dir
    # # Revert directory change after each test
    # os.chdir(Path.home()/'.tagebuch')
    ...


@pytest.fixture
def setup_diary():
    """Copy the test diary `test/test_tagebuch.original` to `tests/test_tagebuch`.

    Not using any sort of pytest's `tmp_path` fixture because then the paths to the media files in the HTML files point to files outside of `tmp_path` which is not the point of the test. The generated HTML summary would show place holders for the media files. The paths work now."""
    test_diary_dir = shutil.copytree(tagebuch_dir/'tests/test_tagebuch.original',
                                     tagebuch_dir/'tests/test_tagebuch',
                                     ignore=lambda src, names: ('README.md',))
    yield test_diary_dir
    # TODO: Analogue to look_into_the_past_test.py: Only if CLI arg was passed <27-05-2024>
    # Without sleeping, the generated HTML summary doesn't show media files because they were deleted too early
    # import time
    # time.sleep(1)
    shutil.rmtree(test_diary_dir)
