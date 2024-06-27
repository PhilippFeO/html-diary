from pathlib import Path

from bs4 import BeautifulSoup

from folder_to_diary import collect_dates, folder_to_diary
from tests.vars import TEST_BILDER_DIR, TEST_DIARY_DIR


def test_collect_dates_paths():
    """Test `collect_dates_paths()`.

    `collect_dates_paths()` is aware that fotos with the same creation date may appear in different subfolders (s. prepared `Bilder/` directory), ie. for date `2024:05:31` is one path collected - the main one.
    """
    dates_expected = {'2024:05:29', '2024:05:30', '2024:05:31', '2024:06:01',  '2024:06:02'}

    directory = Path(TEST_BILDER_DIR / 'ftp-collect_dates_paths 2024-05')
    dates_result = collect_dates(directory)

    assert dates_expected == dates_result


def test_ftd_add_base_href():
    """Part of 'case 1': if.

    Add `head.base.href` to an already existing diary entry.
    """
    expected_path = TEST_BILDER_DIR / 'ftd-add_base_ref 2024-05'

    folder_to_diary(expected_path, 'Erde')

    location_entry = TEST_DIARY_DIR / '2024/05-Mai/30-05-2024-Donnerstag-ftp-add-base-ref/30-05-2024-Donnerstag-ftp-add-base-ref.html'

    entry = BeautifulSoup(location_entry.read_text(), 'html.parser')

    assert entry.head
    assert entry.head.base
    assert entry.head.base.get('href') == f'file://{expected_path}'
    assert entry.body
    assert entry.body.pre
    assert entry.body.pre.string
    assert 'Ort: Erde' in entry.body.pre.string


def test_ftd_href_present(caplog):
    """Part of 'case 1': else.

    Test if firectory values match.
    """
    dir_path = Path(TEST_BILDER_DIR / 'ftd-href_present 2024-05')

    folder_to_diary(dir_path, 'Erde')

    href_value = 'file:///home/philipp/.tagebuch/tests/Bilder/ftd-href_present 2024-05/'
    entry_file = TEST_DIARY_DIR / '2024/05-Mai/31-05-2024-Mittwoch-ftd-href-present/31-05-2024-Mittwoch-ftd-href-present.html'
    href = f'file://{dir_path}'

    msg_expected = f"base.href is '{href_value}' in '{entry_file}'. Can't add '{href}'."
    assert msg_expected in caplog.text


def test_ftd_create_new_entry():
    """Test 'case 0'.

    Create new diary entry and add a `head.base.href` attribute.
    """
    foto_dir = Path(TEST_BILDER_DIR / 'ftd-create_new_entry 2024-05')

    folder_to_diary(foto_dir, 'Erde')

    day_2024_06_01 = TEST_DIARY_DIR / '2024/06-Juni/01-06-2024-Samstag-Erde/01-06-2024-Samstag-Erde.html'
    day_2024_06_02 = TEST_DIARY_DIR / '2024/06-Juni/02-06-2024-Sonntag-Erde/02-06-2024-Sonntag-Erde.html'
    assert Path.is_file(day_2024_06_01)
    assert Path.is_file(day_2024_06_02)

    entry_2024_06_01 = BeautifulSoup(day_2024_06_01.read_text(), 'html.parser')
    assert entry_2024_06_01.body
    assert entry_2024_06_01.body.pre
    assert entry_2024_06_01.body.pre.string == 'Ort: Erde'
    assert entry_2024_06_01.head
    assert entry_2024_06_01.head.base
    assert entry_2024_06_01.head.base.get('href') == f'file://{foto_dir}'
    entry_2024_06_02 = BeautifulSoup(day_2024_06_02.read_text(), 'html.parser')
    assert entry_2024_06_02.head
    assert entry_2024_06_02.head.base
    assert entry_2024_06_02.head.base.get('href') == f'file://{foto_dir}'
    assert entry_2024_06_02.body
    assert entry_2024_06_02.body.pre
    assert entry_2024_06_02.body.pre.string == 'Ort: Erde'
