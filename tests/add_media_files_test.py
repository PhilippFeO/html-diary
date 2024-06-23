from bs4 import BeautifulSoup

from add_media_files import add_media_files_dir_file, collect_fotos, get_entry_date
from my_html_handler import read_base_href
from tests.vars import test_diary_dir


def test_add_media_files_dir_file():
    """Test `add_media_files_dir_file()` when the provided `foto_dir` doesn't exists.

    The other outcomes of `add_media_files_dir_file()` are either obvious or tested in other tests, fi. `test_collect_fotos()`.
    """
    diary_file = test_diary_dir/'2024/06-Juni/05-06-2024-Mittwoch-Test-add_media_files_day_dir/05-06-2024-Mittwoch-Test-add_media_files_day_dir.html'
    not_existent_foto_dir = test_diary_dir/'lorem_ipsum/'

    tags = add_media_files_dir_file(diary_file, not_existent_foto_dir)

    num_tags_expected = 2

    assert len(tags) == num_tags_expected
    assert tags[0].name == 'b'
    assert tags[0].string == f'{not_existent_foto_dir} EXISTIERT NICHT'
    assert tags[1].name == 'br'


def test_collect_fotos():
    """Test 'collect_fotos()' by retrieving all photos in 'base.href' which have the same creation date as the date of the diary entry.

    For a visual test, s `tests/look_into_the_past_test.py::test_litp_base_href()`.
    """
    entry_path = test_diary_dir / '2024/06-Juni/22-06-2024-Mittwoch-amf_collect_photos_specific_date/22-06-2024-Mittwoch-amf_collect_photos_specific_date.html'
    soup = BeautifulSoup(entry_path.read_text(encoding='utf-8'),
                         'html.parser')

    foto_dir = read_base_href(entry_path)
    assert foto_dir
    tags_result = collect_fotos(foto_dir, soup, [])

    nmb_imgs_in_foto_dir = 3
    nmb_br_in_foto_dir = 3

    assert len(tags_result) == nmb_imgs_in_foto_dir + nmb_br_in_foto_dir
    assert len(tuple(tag for tag in tags_result if tag.name == 'img')) == nmb_imgs_in_foto_dir
    assert len(tuple(tag for tag in tags_result if tag.name == 'br')) == nmb_br_in_foto_dir

    # Check values of the 'src' attribute
    for foto in 'Bildschirmfoto vom 2024-06-22 19-19-07.png', \
                'Bildschirmfoto vom 2024-06-22 19-20-13.png', \
                'Bildschirmfoto vom 2024-06-22 19-22-50.png':
        assert any(foto in str(tag.get('src'))
                   for tag in tags_result if tag.name == 'img')


def test_get_entry_date_double_digit():
    date_expected = '2024:06:22'

    entry_path = test_diary_dir / '2024/06-Juni/22-06-2024-Mittwoch-amf_collect_photos_specific_date/22-06-2024-Mittwoch-amf_collect_photos_specific_date.html'
    html = BeautifulSoup(entry_path.read_text(encoding='utf-8'), 'html.parser')

    date = get_entry_date(html)

    assert date == date_expected


def test_get_entry_date_single_digit():
    date_expected = '2024:06:04'

    entry_path = test_diary_dir / '2024/06-Juni/04-06-2024-Mittwoch-base.href-litp/04-06-2024-Mittwoch-base.href-litp.html'
    html = BeautifulSoup(entry_path.read_text(encoding='utf-8'), 'html.parser')

    date = get_entry_date(html)

    assert date == date_expected
