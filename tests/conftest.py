import pytest
import shutil
import vars
from tests.vars import test_diary_dir, test_tmp_dir


@pytest.fixture(autouse=True)
def mock_diary_dir(monkeypatch) -> None:
    monkeypatch.setattr(vars, 'DIARY_DIR', test_diary_dir)


@pytest.fixture(autouse=True)
def mock_tmp_dir(monkeypatch) -> None:
    monkeypatch.setattr(vars, 'TMP_DIR', test_tmp_dir)


@pytest.fixture(scope='session', autouse=True)
def setup_diary():
    """Copy the test diary `test/test_tagebuch.original` to `tests/test_tagebuch`.

    Executed once per session, ie. once per `pytest` call.

    Not using any sort of pytest's `tmp_path` fixture because then the paths to the media files in the HTML files point to files outside of `tmp_path` which is not the point of the test. The generated HTML summary would show place holders for the media files. The paths work now."""
    # shutil.copytree() returns destination directory but this is static variable anyway
    _ = shutil.copytree(vars.DIARY_DIR/'tests/test_tagebuch.original',
                        test_diary_dir,
                        ignore=lambda src, names: ('README.md',))
    yield
    # TODO: Analogue to look_into_the_past_test.py: Only if CLI arg was passed <27-05-2024>
    # Without sleeping, the generated HTML summary doesn't show media files because they were deleted too early
    # import time
    # time.sleep(1)
    shutil.rmtree(test_diary_dir)
