import os
import shutil
from typing import TYPE_CHECKING

import pytest
from tests.vars import (
    foto_1_name,
    foto_2_name,
    test_tmp_dir,
    tests_dir,
    test_diary_dir,
    tf_foto_no_day_dir,
    tf_foto_two_day_dir,
    video_1_name,
)

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def copy_fotos_tmp_dir(request):
    # Get the parameter for the current test function
    param_map: dict[str, tuple[Path, ...]] = {
        'test_transfer_files': (tests_dir / foto_1_name,
                                tests_dir / foto_2_name,
                                tests_dir / video_1_name),
        'test_transfer_files_no_day_dir': (tests_dir / tf_foto_no_day_dir,),
        'test_transfer_files_two_day_dir': (tests_dir /
                                            tf_foto_two_day_dir,)
    }
    param = param_map[request.node.name]
    for media_file in param:
        shutil.copy(media_file, test_tmp_dir)
    # TODO: yield und teardown nötig? <28-05-2024>
    # yield
    # for media_file in os.listdir(test_transfered_dir):
    #     os.remove(test_transfered_dir / media_file)


@pytest.fixture
def create_second_day_dir():
    day_dir2: Path = test_diary_dir/'2020/09-September/13-09-2020-Nicht-Bamberg'
    os.makedirs(day_dir2)
    yield
    shutil.rmtree(day_dir2)
