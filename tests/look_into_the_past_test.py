import pytest
from bs4 import BeautifulSoup

from date import Date
from look_into_the_past import look_into_the_past

# ─── Fixtures ──────────


@pytest.fixture(autouse=True)
def _mock_check(monkeypatch) -> None:
    monkeypatch.setattr('look_into_the_past.check', lambda _: True)


# ─── Tests ──────────

def test_look_into_the_past():
    num_pre_tag_expected = 4
    date = Date('23.05.2024', sep='.')

    past_entries, html = look_into_the_past(date)
    assert past_entries

    # TODO: Use CLI arg for pytest to trigger this block <27-05-2024>
    # html_path = '/tmp/look_into_the_past.html'
    # with open(html_path, 'w') as html_file:
    #     html_file.write(html)
    # import subprocess
    # subprocess.run(['firefox', html_path])

    result = BeautifulSoup(html, 'html.parser')
    assert len(result.find_all('pre')) == num_pre_tag_expected

    imgs = result.find_all('img')
    foto_paths = ("/home/philipp/.tagebuch/tests/test_tagebuch/2021/05-Mai/23-05-2021-Sonntag-Kein-Text-litp/litp_KeinText_20220824_121400.jpg",
                  "/home/philipp/.tagebuch/tests/test_tagebuch/2022/05-Mai/23-05-2022-Mittwoch-fünf-Fotos-litp/litp_5_fotos_20220822_150119.jpg",
                  "/home/philipp/.tagebuch/tests/test_tagebuch/2022/05-Mai/23-05-2022-Mittwoch-fünf-Fotos-litp/litp_5_fotos_20220824_121350.jpg",
                  "/home/philipp/.tagebuch/tests/test_tagebuch/2022/05-Mai/23-05-2022-Mittwoch-fünf-Fotos-litp/litp_5_fotos_20220824_121400.jpg",
                  "/home/philipp/.tagebuch/tests/test_tagebuch/2022/05-Mai/23-05-2022-Mittwoch-fünf-Fotos-litp/litp_5_fotos_20220824_204148.jpg",
                  "/home/philipp/.tagebuch/tests/test_tagebuch/2022/05-Mai/23-05-2022-Mittwoch-fünf-Fotos-litp/litp_5_fotos-20220825-WA0001.jpg",
                  "/home/philipp/.tagebuch/tests/test_tagebuch/2023/05-Mai/23-05-2023-Sonntag-Text-Foto-Video-litp/litp_TextFotoVideo_20220824_121400.jpg")
    for foto in foto_paths:
        assert any(foto in str(img.get('src'))
                   for img in imgs)

    videos = result.find_all('video')
    video_paths = ("/home/philipp/.tagebuch/tests/test_tagebuch/2021/05-Mai/23-05-2021-Sonntag-Kein-Text-litp/litp_KeinText-20230319-WA0001.mp4",
                   "/home/philipp/.tagebuch/tests/test_tagebuch/2023/05-Mai/23-05-2023-Sonntag-Text-Foto-Video-litp/litp_TextFotoVideo-20230319-WA0001.mp4")
    for foto in video_paths:
        assert any(foto in str(video.source.get('src'))
                   for video in videos)


def test_no_past_entries():
    date = Date('28.05.1990', sep='.')
    past_entries, _ = look_into_the_past(date)

    assert not past_entries


def test_litp_base_href():
    """Test `look_into_the_past()` with an entry containing the `base.href` attribute."""
    num_images_expected = 3

    date = Date('22.06.2024', sep='.')
    past_entries, html = look_into_the_past(date)
    assert past_entries

    # TODO: Use CLI arg for pytest to trigger this block <27-05-2024>
    # html_path = '/tmp/look_into_the_past.html'
    # with open(html_path, 'w') as html_file:
    #     html_file.write(html)
    # import subprocess
    # subprocess.run(['firefox', html_path])

    result = BeautifulSoup(html, 'html.parser')
    imgs = result.find_all('img')
    assert len(imgs) == num_images_expected
    # Check values of the 'src' attribute
    for foto in 'Bildschirmfoto vom 2024-06-22 19-19-07.png', \
                'Bildschirmfoto vom 2024-06-22 19-20-13.png', \
                'Bildschirmfoto vom 2024-06-22 19-22-50.png':
        assert any(foto in str(img.get('src'))
                   for img in imgs)
