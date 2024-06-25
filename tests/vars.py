
from typing import TYPE_CHECKING

import vars

if TYPE_CHECKING:
    from pathlib import Path

TEST_DIR = vars.DIARY_DIR / 'tests'
TEST_DIARY_DIR: 'Path' = TEST_DIR / 'test_tagebuch'
TEST_TMP_DIR: 'Path' = TEST_DIARY_DIR / '.tmp'
TEST_TRANSFERED_DIR: 'Path' = TEST_TMP_DIR / 'transfered'
TEST_BILDER_DIR: 'Path' = TEST_DIR / 'Bilder'
