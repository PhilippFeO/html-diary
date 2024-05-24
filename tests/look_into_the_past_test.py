import os
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup
from look_into_the_past import look_into_the_past


def test_look_into_the_past():
    tagebuch_dir = Path.home()/'.tagebuch'
    os.chdir(tagebuch_dir/'tests')

    date = '23.05.2024'
    past_entries, html = look_into_the_past(date)
    assert past_entries

    # Change back for other tests
    os.chdir(tagebuch_dir)

    html_path = Path('/tmp/look_into_the_past.html')
    with open(html_path, 'w') as html_file:
        html_file.write(html)
    # subprocess.run(['firefox', html_path])

    # TODO: Was besseres einfallen lassen <24-05-2024>
    result = BeautifulSoup(html, 'html.parser')
    assert len(result.find_all('img')) == 6
    assert len(result.find_all('pre')) == 3
    assert len(result.find_all('video')) == 1


def test_no_past_entries():
    tagebuch_dir = Path.home()/'.tagebuch'
    os.chdir(tagebuch_dir/'tests')

    date = '32.05.2024'
    past_entries, _ = look_into_the_past(date)

    # Change back for other tests
    os.chdir(tagebuch_dir)

    assert not past_entries
