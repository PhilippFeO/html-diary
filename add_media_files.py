import logging
from pathlib import Path
from typing import TYPE_CHECKING

import vars
from utils import get_date_created

if TYPE_CHECKING:
    from bs4 import Tag

    from entry import Entry


def collect_fotos(media_dir: Path,
                  entry: "Entry",
                  tags: list["Tag"]) -> list["Tag"]:
    """Traverse directory recursively and search for media files. Return a list of `<img>` and `<br>` Tags where the `<img>` Tags are Fotos taken on the same Date as the Date of the Entry. The Entry's Date is awkwardly retrieved from the title.

    For a visual test, s. `tests/look_into_the_past_test.py::test_litp_base_href()`.

    Inverse function: `folder_to_diary.py::collect_dates()`.

    `media_dir`: Directory containing the media files to be embedded in the diary entry file.
    `entry`: The diary entry.
    `tags`: List with already created `Tag`s (necessary for recursion).
    """
    logging.info("Args: media_dir = %s, html = <SKIP>, tags = <SKIP>", media_dir)
    for media_file in media_dir.iterdir():
        if Path.is_dir(media_file):
            _ = collect_fotos(media_file, entry, tags)
        else:
            logging.info("Process %s", media_file)
            match media_file.suffix:
                # Add <img src='...'/> tag for each foto
                case '.jpg' | '.jpeg' | '.JPG' | '.JPEG' | '.png' | '.PNG':
                    # Create and add tag of 'file' if it's creation date is eqaul to the entry date
                    if (date_created := get_date_created(media_file)) == entry.date:
                        new_img = entry.soup.new_tag('img', src=vars.DIARY_DIR/media_file)
                        # LIFO data structure, ie '<br/>' is the first element
                        tags.append(new_img)
                        tags.append(entry.soup.new_tag('br'))
                        logging.info("Added Foto: '%s'", media_file)
                    else:
                        logging.warning("Date mismatch: %s (media_file) != %s (entry). Nothing done for '%s'", date_created, entry.date, media_file)
                # Add <video controls loop><source src='...'/></video>
                case '.mp4' | '.MP4':
                    # Create and add tag of 'file' if it's creation date is eqaul to the entry date
                    if (date_created := get_date_created(media_file)) == entry.date:
                        # Empty string == True
                        #   To be precise, any value equals True, for False, attribute has to be absent
                        # becomes <video controls loop>
                        new_video = entry.soup.new_tag('video', controls="", loop="")
                        new_source = entry.soup.new_tag('source', src=vars.DIARY_DIR/media_file)
                        # Append the <source> tag to the <video> tag
                        new_video.append(new_source)
                        # LIFO data structure, ie '<br/>' is the first element
                        tags.append(new_video)
                        tags.append(entry.soup.new_tag('br'))
                        logging.info("Added Video: '%s'", media_file)
                    else:
                        logging.warning("Date mismatch: %s (media_file) != %s (entry). Nothing done for '%s'", date_created, entry.date, media_file)
                # Skip html complete_file_path
                case '.html':
                    logging.info("(Obviously) Skipping the HTML Entry: '%s'", media_file)
                case _:
                    logging.warning("There is a new File Type in '%s': '%s'", media_dir, media_file)
    return tags


def create_tags(entry: "Entry",
                media_dir: Path) -> list["Tag"]:
    """Return a list with the tags to be inserted after the `<pre>`-tag.

    `diary_file`: Path to the diary html file to add media files to
    `media_dir`: The directory containing the media files to embed in the entry. Should be the value of a `base.href` attribute or the 'day directory'. In `add_media_files()` it's the 'day directory', ie. the parent dir of `entry`, in `look_into_the_past.py::look_into_the_past()` it's the value of `head.base.href`.
    """
    logging.info('Args: entry.file = %s, media_dir = %s', entry.file, media_dir)
    pre_tag = entry.soup.find('pre')

    # Insert the new elements after the <pre> tag
    if pre_tag is not None:  # pre_tag may be None, insert_after() doesn't work on None
        # When called with the intent to temporarly embed fotos from a folder, it is not guaranteed that this folder exists (I may have renamed it).
        if Path.is_dir(media_dir):
            return collect_fotos(media_dir, entry, [])
        logging.error("'%s' is no directory", media_dir)
        # Add visual feedback
        b = entry.soup.new_tag('b')
        b.append(f'{media_dir} EXISTIERT NICHT')
        return [b, entry.soup.new_tag('br')]
    return []


# TODO: Add media files via 'head.base.href' <23-06-2024>
def add_media_files(entries: set["Entry"]) -> None:
    """Add media files to a diary entry.

    `directories` contains the directories into which media files were moved but not yet embedded into the HTML file laying in the same directory. This function iterates over all files in each directory, creates the according HTML tag and adds it to the diary entry. Most of the time, the directories in `directories` are the directories of a day.
    """
    logging.info('Args: %s', entries)
    for entry in entries:
        logging.info("Add Media Files in '%s' to '%s' ...", entry.file.parent, entry.file)

        # Insert tags after pre-tag
        tags = create_tags(entry, entry.file.parent)
        if (pre_tag := entry.soup.find('pre')) is not None:
            pre_tag.insert_after(*tags)
        entry.file.write_text(entry.soup.prettify(), encoding='utf-8')
