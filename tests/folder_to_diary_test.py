from pathlib import Path

from bs4 import BeautifulSoup
from folder_to_diary import collect_dates_paths, folder_to_diary
from tests.vars import test_diary_dir, tests_dir


def test_collect_dates():
    dates_expected = ('2024:05:29', '2024:05:30', '2024:05:31', '2024:06:01', '2024:06:02')
    directory = Path(tests_dir / 'Bibione 2024-05')
    dates_paths_expected = {(date, directory) for date in dates_expected}

    dates_paths = collect_dates_paths(directory)

    assert dates_paths_expected == dates_paths


def test_folder_to_diary():
    bibione_fotos = Path(tests_dir / 'Bibione 2024-05')

    folder_to_diary(bibione_fotos)

    bibione1 = test_diary_dir / '2024/05-Mai/30-05-2024-Donnerstag-base-href-hinzugefuegt-ftd/30-05-2024-Donnerstag-base-href-hinzugefuegt-ftd.html'

    entry = BeautifulSoup(bibione1.read_text(), 'html.parser')

    assert entry.head
    assert entry.head.base
    assert entry.head.base.get('href') == 'file://' + str(bibione_fotos)
