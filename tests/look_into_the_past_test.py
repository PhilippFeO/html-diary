from bs4 import BeautifulSoup
from look_into_the_past import look_into_the_past
from tests.vars import test_diary_dir


def test_look_into_the_past(monkeypatch, setup_diary):
    _ = setup_diary
    date = '23.05.2024'
    monkeypatch.setattr('look_into_the_past.check', lambda _: True)

    past_entries, html = look_into_the_past(date, test_diary_dir)
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


def test_no_past_entries(setup_diary):
    date = '32.05.2024'
    past_entries, _ = look_into_the_past(date, setup_diary)

    assert not past_entries


def test_base_href(monkeypatch, setup_diary):
    _ = setup_diary
    date = '04.06.2024'
    monkeypatch.setattr('look_into_the_past.check', lambda _: True)

    past_entries, html = look_into_the_past(date, test_diary_dir)
    assert past_entries

    # TODO: Use CLI arg for pytest to trigger this block <27-05-2024>
    html_path = '/tmp/look_into_the_past.html'
    with open(html_path, 'w') as html_file:
        html_file.write(html)
    import subprocess
    subprocess.run(['firefox', html_path])

    result = BeautifulSoup(html, 'html.parser')
    assert len(result.find_all('img')) == 3
