import pytest
from bs4 import BeautifulSoup
from look_into_the_past import look_into_the_past

# ─── Fixtures ──────────


@pytest.fixture(autouse=True)
def _mock_check(monkeypatch) -> None:
    monkeypatch.setattr('look_into_the_past.check', lambda _: True)


# ─── Tests ──────────

def test_look_into_the_past():
    date = '23.05.2024'

    past_entries, html = look_into_the_past(date)
    assert past_entries

    # TODO: Use CLI arg for pytest to trigger this block <27-05-2024>
    # html_path = '/tmp/look_into_the_past.html'
    # with open(html_path, 'w') as html_file:
    #     html_file.write(html)
    # import subprocess
    # subprocess.run(['firefox', html_path])

    # TODO: Was besseres einfallen lassen <24-05-2024>
    #       Wie unten mit 'any()'
    result = BeautifulSoup(html, 'html.parser')
    assert len(result.find_all('img')) == 7
    assert len(result.find_all('pre')) == 4
    assert len(result.find_all('video')) == 2


def test_no_past_entries():
    date = '32.05.2024'
    past_entries, _ = look_into_the_past(date)

    assert not past_entries


def test_litp_base_href():
    """Test `look_into_the_past()` with an entry containing the `base.href` attribute."""
    date = '22.06.2024'
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
    assert len(imgs) == 3
    # Check values of the 'src' attribute
    assert any('Bildschirmfoto vom 2024-06-22 19-19-07.png' in str(tag.get('src'))
               for tag in imgs)
    assert any('Bildschirmfoto vom 2024-06-22 19-20-13' in str(tag.get('src'))
               for tag in imgs)
    assert any('Bildschirmfoto vom 2024-06-22 19-22-50' in str(tag.get('src'))
               for tag in imgs)
