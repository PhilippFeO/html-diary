import pytest

from tests.vars import (
    TEST_BILDER_DIR,
    TEST_DIARY_DIR,
)
from utils import assemble_new_entry, create_dir_and_file, create_stump


def test_create_dir_and_file():
    entry = create_stump('cdaf')
    day_dir = TEST_DIARY_DIR/'2024/06-Juni/27-06-2024-Donnerstag-cdaf'

    create_dir_and_file(entry, day_dir)

    assert day_dir.is_dir()
    assert (day_dir/f'{day_dir.name}.html').is_file()


@pytest.mark.parametrize("location", ['Erde', ''])
def test_assemble_new_entry(location):
    day = '27'
    month = '06'
    year = '2024'
    href = str(TEST_BILDER_DIR / 'u-assemble_new_entry')

    day_dir, html = assemble_new_entry(day, month, year, location, href)

    assert day_dir == TEST_DIARY_DIR/f"2024/06-Juni/27-06-2024-Donnerstag{f'-{location}' if location != '' else ''}"
    assert html.head
    assert html.head.title
    assert html.head.title.string == f"Donnerstag, {day}. Juni {year}{f': {location}' if location != '' else ''}"
    assert html.head.base
    assert html.head.base.get('href') == href
