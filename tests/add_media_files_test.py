from add_media_files import add_media_files_dir_file, collect_fotos
from bs4 import BeautifulSoup
from tests.vars import TEST_BILDER_DIR, test_diary_dir


def test_add_media_files_dir_file():
    diary_html = test_diary_dir/'2024/06-Juni/05-06-2024-Mittwoch-Test-add_media_files_day_dir/05-06-2024-Mittwoch-Test-add_media_files_day_dir.html'
    not_existent_foto_dir = test_diary_dir/'lorem_ipsum/'

    tags = add_media_files_dir_file(diary_html, not_existent_foto_dir)

    assert len(tags) == 2
    assert tags[0].name == 'b'
    assert tags[0].string == f'{not_existent_foto_dir} EXISTIERT NICHT'
    assert tags[1].name == 'br'


def test_collect_fotos():
    """Test 'collect_fotos()' by retrieving all photos in 'base.href'."""
    foto_dir = TEST_BILDER_DIR / 'amf-collect_photos 2024-05'
    soup = BeautifulSoup('', 'html.parser')

    tags_result = collect_fotos(foto_dir, soup, [])

    nmb_imgs_in_foto_dir = 4
    nmb_br_in_foto_dir = 4

    assert len(tags_result) == nmb_imgs_in_foto_dir + nmb_br_in_foto_dir
    assert len(tuple(tag for tag in tags_result if tag.name == 'img')) == nmb_imgs_in_foto_dir
    assert len(tuple(tag for tag in tags_result if tag.name == 'br')) == nmb_br_in_foto_dir
