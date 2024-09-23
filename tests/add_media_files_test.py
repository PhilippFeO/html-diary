from add_media_files import collect_fotos, create_tags, get_date_entry
from bs4 import BeautifulSoup
from date import Date
from entry import Entry
from tests.vars import TEST_DIARY_DIR


def test_create_tags():
    """Test `create_tags()` when the provided `foto_dir` doesn't exists.

    The other outcomes of `add_media_files_dir_file()` are either obvious or tested in other tests, fi. `test_collect_fotos()`.
    """
    diary_file = TEST_DIARY_DIR/'2024/06-Juni/05-06-2024-Mittwoch-Test-add_media_files_day_dir/05-06-2024-Mittwoch-Test-add_media_files_day_dir.html'
    not_existent_foto_dir = TEST_DIARY_DIR/'lorem_ipsum/'

    tags = create_tags(diary_file, not_existent_foto_dir)

    num_tags_expected = 2

    assert len(tags) == num_tags_expected
    assert tags[0].name == 'b'
    assert tags[0].string == f'{not_existent_foto_dir} EXISTIERT NICHT'
    assert tags[1].name == 'br'


# TODO: Add test of 'collect_fotos()' with a video file <23-06-2024>
def test_collect_fotos():
    """Test 'collect_fotos()' by retrieving all photos in 'base.href' which have the same creation date as the date of the diary entry.

    For a visual test, s `tests/look_into_the_past_test.py::test_litp_base_href()`.
    """
    entry = Entry('2024', '06', '22')

    foto_dir = entry.base_href
    assert foto_dir is not None

    tags_result = collect_fotos(foto_dir, entry.soup, [])

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
    date_expected = Date('2024:06:22')

    entry_path = TEST_DIARY_DIR / '2024/06-Juni/22-06-2024-Mittwoch-amf_collect_photos_specific_date/22-06-2024-Mittwoch-amf_collect_photos_specific_date.html'
    html = BeautifulSoup(entry_path.read_text(encoding='utf-8'), 'html.parser')

    date = get_date_entry(html)

    assert date == date_expected


def test_get_entry_date_single_digit():
    date_expected = Date('2024:06:04')

    entry_path = TEST_DIARY_DIR / '2024/06-Juni/04-06-2024-Mittwoch-base.href-litp/04-06-2024-Mittwoch-base.href-litp.html'
    html = BeautifulSoup(entry_path.read_text(encoding='utf-8'), 'html.parser')

    date = get_date_entry(html)

    assert date == date_expected
