from bs4 import BeautifulSoup
from add_media_files import add_media_files_dir_file, collect_fotos
from tests.vars import TEST_BILDER_DIR, test_diary_dir
from collections import Counter


def test_add_media_files_dir_file():
    diary_html = test_diary_dir/'2024/06-Juni/05-06-2024-Mittwoch-Test-add_media_files_day_dir/05-06-2024-Mittwoch-Test-add_media_files_day_dir.html'
    not_existent_foto_dir = test_diary_dir/'lorem_ipsum/'

    tags = add_media_files_dir_file(diary_html, not_existent_foto_dir)

    assert len(tags) == 2
    assert tags[0].name == 'b'
    assert tags[0].string == f'{not_existent_foto_dir} EXISTIERT NICHT'
    assert tags[1].name == 'br'
