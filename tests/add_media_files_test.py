from add_media_files import add_media_files_dir_file
from tests.vars import test_diary_dir


def test_add_media_files_dir_file(setup_diary):
    _ = setup_diary
    diary_html = test_diary_dir/'2024/06-Juni/05-06-2024-Mittwoch-Test-add_media_files_day_dir/05-06-2024-Mittwoch-Test-add_media_files_day_dir.html'
    not_existent_foto_dir = test_diary_dir/'lorem_ipsum/'

    soup = add_media_files_dir_file(diary_html, not_existent_foto_dir)

    # TODO: Use CLI arg for pytest to trigger this block <27-05-2024>
    # html_path = Path('/tmp/add_media_files_dir_file.html')
    # with open(html_path, 'w') as html_file:
    #     html_file.write(soup.prettify())
    # import subprocess
    # subprocess.run(['firefox', html_path])

    b_tag = soup.find('b')
    if b_tag and b_tag.string:
        assert f'{not_existent_foto_dir} EXISTIERT NICHT' in b_tag.string
    else:
        assert False, '`b_tag` or `b_tag.string` is False'
