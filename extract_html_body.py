# Extract the <body> of the submitted diary entry (html file)
# argv[1]   diary entry as html file; body is extracted from this file
# argv[2]   index of (line) "which" past is parsed, s. past_dates.txt
# argv[3]   formatted date for heading according to argv[2]

# TODO: Add "vor 6 Monaten" <29-04-2023>


import logging
from datetime import datetime

from bs4 import BeautifulSoup, NavigableString, Tag
from num2words import num2words


def extract_html_body(html_file,
                      past_date: str) -> BeautifulSoup:
    """Extracts the <pre>, <img> and <video> tags from `html_file`, assembles it with a heading indicating how far in the past the day is."""

    with open(html_file) as fp:
        entry_soup = BeautifulSoup(fp, 'html.parser')

    this_year = int(datetime.today().strftime('%Y'))
    diff = this_year - (past_date_year := int(past_date.split('.')[-1]))
    assert diff > 0, f'Difference between {this_year} and {past_date_year} is {diff} <0. Should be >=0.'
    match diff:
        case 0:
            h2 = f"... {past_date}<h2>"
        case 1:
            h2 = f"<h2>... {past_date}, vor einem Jahr</h2>"
        case _:
            h2 = f"<h2>... {past_date}, vor {num2words(diff, lang='de')} Jahren</h2>"
    new_soup = BeautifulSoup(h2, 'html.parser')

    # Extract description
    pre = entry_soup.find('pre')
    if isinstance(pre, Tag) and new_soup.h2:
        new_soup.h2.insert_after(pre)
    elif isinstance(pre, NavigableString):
        logging.error(f'Type of "pre" variable is "NavigableString". Should be "Tag". The affected file is {html_file}.')
    else:
        logging.warning(f'No Text, ie. no <pre>-tag in {html_file}.')

    # Extract images/fotos
    imgs = entry_soup.find_all('img')
    for img in imgs:
        br = new_soup.new_tag('br')
        if new_soup.pre:
            new_soup.pre.insert_after(img, br)
    # Extract videos
    videos = entry_soup.find_all('video')
    for video in videos:
        br = new_soup.new_tag('br')
        if new_soup.pre:
            new_soup.pre.insert_after(video, br)

    return new_soup


if __name__ == "__main__":
    extract_html_body('2020/09-September/13-Bamberg/2020-09-13_Bamberg.html', '13.09.2020')
