import pytest

from date import Date
from entry import Entry
from tests.vars import (
    TEST_BILDER_DIR,
    TEST_DIARY_DIR,
)

# from utils import create_stump
#
# def test_create_dir_and_file():
#     entry = create_stump('cdaf')
#     day_dir = TEST_DIARY_DIR/'2024/06-Juni/27-06-2024-Donnerstag-cdaf'
#
#     create_dir_and_file(entry, day_dir)
#
#     assert day_dir.is_dir()
#     assert (day_dir/f'{day_dir.name}.html').is_file()


@pytest.mark.parametrize("location", ['Erde', ''])
def test_assemble_new_entry(location):
    day = '27'
    monthname = 'Juni'
    year = '2024'
    date = Date('27.06.2024', sep='.')
    href = str(TEST_BILDER_DIR / 'u-assemble_new_entry')

    # day_dir, html = assemble_new_entry(date, location, href)
    entry = Entry(new_entry=(date, location, href))

    assert entry.file.parent == TEST_DIARY_DIR/f"2024/06-Juni/27-06-2024-Donnerstag{f'-{location}' if location != '' else ''}"
    assert entry.soup.head
    assert entry.soup.head.title
    assert entry.soup.head.title.string == f"Donnerstag, {day}. {monthname} {year}{f': {location}' if location != '' else ''}"
    assert entry.soup.head.base
    assert entry.soup.head.base.get('href') == href
