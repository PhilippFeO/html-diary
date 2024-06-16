from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from folder_to_diary import collect_dates_paths, folder_to_diary
from tests.vars import test_diary_dir, tests_dir


def test_collect_dates():
    dates_expected = ('2024:05:29', '2024:05:30', '2024:05:31', '2024:06:01', '2024:06:02')
    directory = Path(tests_dir / 'Location 2024-05')
    dates_paths_expected = {(date, directory) for date in dates_expected}

    dates_paths = collect_dates_paths(directory)

    assert dates_paths_expected == dates_paths


def test_ftd_add_base_href():
    """Part of 'case 1': if."""
    expected_path = Path(tests_dir / 'Location 2024-05')

    folder_to_diary(expected_path)

    location_entry = test_diary_dir / '2024/05-Mai/30-05-2024-Donnerstag-base-href-hinzugefuegt-ftd/30-05-2024-Donnerstag-base-href-hinzugefuegt-ftd.html'

    entry = BeautifulSoup(location_entry.read_text(), 'html.parser')

    assert entry.head
    assert entry.head.base
    assert entry.head.base.get('href') == 'file://' + str(expected_path)


def test_ftd_href_differs(caplog):
    """Part of 'case 1': else."""
    dir_path = Path(tests_dir / 'Location 2024-05')

    folder_to_diary(dir_path)

    href_value = 'file:///home/philipp/test/test_tagebuch/Location 2024-05/'
    entry_file = test_diary_dir / '2024/05-Mai/31-05-2024-Mittwoch-base-href-schon-vorhanden-ftd/31-05-2024-Mittwoch-base-href-schon-vorhanden-ftd.html'
    href = f'file://{dir_path}'

    msg_expected = f"base.href is '{href_value}' in '{entry_file}'. Can't add '{href}'."
    assert msg_expected in caplog.text
