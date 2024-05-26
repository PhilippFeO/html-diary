import os
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from look_into_the_past import look_into_the_past


@pytest.fixture
def setup_entries(create_dirs):
    _, test_tagebuch_dir = create_dirs
    tests_dir = Path.home()/'.tagebuch'/'tests'
    for year in (f'202{x}' for x in {0, 1, 2, 3}):
        os.symlink(tests_dir/year, test_tagebuch_dir/year)
    yield test_tagebuch_dir.parent


def test_look_into_the_past(monkeypatch, setup_entries):
    tagebuch_dir = Path.home()/'.tagebuch'

    date = '23.05.2024'
    monkeypatch.setattr('look_into_the_past.check', lambda _: True)

    # Define a custom function to return a fake object
    def mock_home() -> Path:
        return setup_entries
    # Use monkeypatch to replace Path.home with the custom function
    monkeypatch.setattr(Path, 'home', mock_home)

    past_entries, html = look_into_the_past(date)
    assert past_entries

    # Change back for other tests
    os.chdir(tagebuch_dir)

    # html_path = Path('/tmp/look_into_the_past.html')
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
    tagebuch_dir = Path.home()/'.tagebuch'
    os.chdir(tagebuch_dir/'tests')

    date = '32.05.2024'
    past_entries, _ = look_into_the_past(date)

    # Change back for other tests
    os.chdir(tagebuch_dir)

    assert not past_entries
