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
    result = BeautifulSoup(html, 'html.parser')
    assert len(result.find_all('img')) == 7
    assert len(result.find_all('pre')) == 4
    assert len(result.find_all('video')) == 2


def test_no_past_entries():
    date = '32.05.2024'
    past_entries, _ = look_into_the_past(date)

    assert not past_entries


def test_base_href():
    date = '04.06.2024'

    past_entries, html = look_into_the_past(date)
    assert past_entries

    # TODO: Use CLI arg for pytest to trigger this block <27-05-2024>
    # html_path = '/tmp/look_into_the_past.html'
    # with open(html_path, 'w') as html_file:
    #     html_file.write(html)
    # import subprocess
    # subprocess.run(['firefox', html_path])

    result = BeautifulSoup(html, 'html.parser')
    assert len(result.find_all('img')) == 3
