import glob
import logging
import os
from pathlib import Path

from bs4 import BeautifulSoup, Tag

import vars
from utils import get_date_created

# {Januar: 01, Februar: 02, ..., Dezember: 12}
MONTH_NUM: dict[str, str] = {month: str(num + 1).zfill(2) for num, month in enumerate((
    'Januar',
    'Februar',
    'März',
    'April',
    'Mai',
    'Juni',
    'Juli',
    'August',
    'September',
    'Oktober',
    'November',
    'Dezember',
))}


def get_date_entry(html: BeautifulSoup) -> str | None:
    """Retrieve the date of the entry from it's HTML, ie. from the `<title>` tag.

    `<title>` has the following scheme: `[d]d. Monthname yyyy: …`
    """
    logging.info("%s(html = <SKIP>)", __name__)
    if html.head and html.head.title:
        # title = Weekday, [d]d. Monthname yyyy: Lorem Ipsum
        title = html.head.title.text
        logging.info("Title to retrieve the date from: %s", title)
        # 1. split(): [d]d. Monthname yyyy: Lorem Ipsum
        # 2. split(): [d]d. Monthname yyyy
        date_month_name = title.split(',')[1] \
            .split(':')[0] \
            .strip()
        day, monthname, year = date_month_name.split()
        # handle [d]d.
        day = str(day[:-1]).zfill(2)
        month_num = MONTH_NUM[monthname]
        return f'{year}:{month_num}:{day}'
    msg = f'Impossible to retrieve the date from HTML:\n{html.prettify()}'
    raise Exception(msg)


def collect_fotos(media_dir: Path,
                  html: BeautifulSoup,
                  tags: list[Tag]) -> list[Tag]:
    """Traverse directory recursively and search for media files. Return a list of `<img>` and `<br>` Tags where the `<img>` Tags are Fotos taken on the same Date as the Date of the Entry. The Entry's Date is awkwardly retrieved from the title.

    For a visual test, s. `tests/look_into_the_past_test.py::test_litp_base_href()`.

    Inverse function: `folder_to_diary.py::collect_dates()`.

    `media_dir`: Directory containing the media files to be embedded in `html`.
    `html`: HTML contents of a diary entry.
    `tags`: List with already created `Tag`s (necessary for recursion).
    """
    logging.info("%s(foto_dir = %s, html = <SKIP>, tags = <SKIP>)", __name__, media_dir)
    date_entry = get_date_entry(html)
    for media_file in media_dir.iterdir():
        if Path.is_dir(media_file):
            _ = collect_fotos(media_file, html, tags)
        else:
            logging.info("Process %s", media_file)
            match media_file.suffix:
                # Add <img src='...'/> tag for each foto
                case '.jpg' | '.jpeg' | '.JPG' | '.JPEG' | '.png' | '.PNG':
                    # Create and add tag of 'file' if it's creation date is eqaul to the entry date
                    if get_date_created(media_file) == date_entry:
                        new_img = html.new_tag('img', src=vars.DIARY_DIR/media_file)
                        # LIFO data structure, ie '<br/>' is the first element
                        tags.append(new_img)
                        tags.append(html.new_tag('br'))
                        logging.info("Added Foto: '%s'", media_file)
                # Add <video controls loop><source src='...'/></video>
                case '.mp4' | '.MP4':
                    # Create and add tag of 'file' if it's creation date is eqaul to the entry date
                    if get_date_created(media_file) == date_entry:
                        # Empty string == True
                        #   To be precise, any value equals True, for False, attribute has to be absent
                        # becomes <video controls loop>
                        new_video = html.new_tag('video', controls="", loop="")
                        new_source = html.new_tag('source', src=vars.DIARY_DIR/media_file)
                        # Append the <source> tag to the <video> tag
                        new_video.append(new_source)
                        # LIFO data structure, ie '<br/>' is the first element
                        tags.append(new_video)
                        tags.append(html.new_tag('br'))
                        logging.info("Added Video: '%s'", media_file)
                # Skip html complete_file_path
                case '.html':
                    logging.info("(Obviously) Skipping the HTML Entry: '%s'", media_file)
                case _:
                    logging.warning("There is a new File Type in '%s': '%s'", media_dir, media_file)
    return tags


def create_tags(diary_file: Path,
                media_dir: Path) -> list[Tag]:
    """Return a list with the tags to be inserted after the `<pre>`-tag.

    `diary_file`: Path to the diary html file to add media files to
    `media_dir`: Should be the value of a `base.href` attribute or the 'day directory'. In `add_media_files()` it's the 'day directory', in `look_into_the_past.py::look_into_the_past()` it's the value of `head.base.href`.
    """
    logging.info('%s(diary_file = %s, media_dir = %s)', __name__, diary_file, media_dir)

    html_content = diary_file.read_text(encoding='utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')
    pre_tag = soup.find('pre')

    # Insert the new elements after the <pre> tag
    if pre_tag:  # pre_tag may be None, insert_after() doesn't work on None
        # When called with the intent to temporarly embed fotos from a folder, it is not guaranteed that this folder exists (I may have renamed it).
        if Path.is_dir(media_dir):
            return collect_fotos(media_dir, soup, [])
        logging.error("'%s' is no directory", media_dir)
        # Add visual feedback
        b = soup.new_tag('b')
        b.append(f'{media_dir} EXISTIERT NICHT')
        return [b, soup.new_tag('br')]
    return []


# TODO: Add media files via 'head.base.href' <23-06-2024>
def add_media_files(directories: set[Path]) -> None:
    """Add media files to a diary entry.

    `directories` contains the directories into which media files were moved but not yet embedded into the HTML file laying in the same directory. This function iterates over all files in each directory, creates the according HTML tag and adds it to the diary entry. Most of the time, the directories in `directories` are the directories of a day.
    """
    logging.info('%s(%s)', __name__, directories)
    for day_dir in directories:
        # Load HTML file
        if len(html_files := glob.glob(os.path.join(day_dir, '*.html'))) == 1:
            html_file = Path(html_files[0])
        else:
            logging.error("There are '%d' in '%s'. There should be exactly 1.", len(html_files), day_dir)
            continue
        logging.info("Add Media Files in '%s' to '%s' ...", day_dir, html_file)

        # Insert tags after pre-tag
        tags = create_tags(html_file, day_dir)
        html = BeautifulSoup(html_file.read_text(encoding='utf-8'),
                             'html.parser')
        if (pre_tag := html.find('pre')):
            pre_tag.insert_after(*tags)
        html_file.write_text(html.prettify(), encoding='utf-8')
