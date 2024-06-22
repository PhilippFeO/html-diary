import glob
import logging
import os
from pathlib import Path

from bs4 import BeautifulSoup, Tag

from vars import DIARY_DIR


def collect_fotos(foto_dir: Path,
                  html: BeautifulSoup,
                  tags: list[Tag]) -> list[Tag]:
    """Traverse directory recursively and search for media files."""
    for file in foto_dir.iterdir():
        if Path.is_dir(file):
            _ = collect_fotos(file, html, tags)
        else:
            complete_file_path = foto_dir / file
            match complete_file_path.suffix:
                # Add <img src='...'/> tag for each foto
                case '.jpg' | '.jpeg' | '.JPG' | '.JPEG' | '.png' | '.PNG':
                    new_img = html.new_tag('img', src=DIARY_DIR/complete_file_path)
                    # LIFO data structure, ie '<br/>' is the first element
                    tags.append(new_img)
                    tags.append(html.new_tag('br'))
                    logging.info("Added Foto: '%s'", complete_file_path)
                # Add <video controls loop><source src='...'/></video>
                case '.mp4' | '.MP4':
                    # Empty string == True
                    #   To be precise, any value equals True, for False, attribute has to be absent
                    # becomes <video controls loop>
                    new_video = html.new_tag('video', controls="", loop="")
                    new_source = html.new_tag('source', src=DIARY_DIR/complete_file_path)
                    # Append the <source> tag to the <video> tag
                    new_video.append(new_source)
                    # LIFO data structure, ie '<br/>' is the first element
                    tags.append(new_video)
                    tags.append(html.new_tag('br'))
                    logging.info("Added Video: '%s'", complete_file_path)
                # Skip html complete_file_path
                case '.html':
                    logging.info("(Obviously) Skipping the HTML Entry: '%s'", complete_file_path)
                case _:
                    logging.warning("There is a new complete_file_path Type in '%s': '%s'", foto_dir, complete_file_path)
    return tags


def add_media_files_dir_file(html_file: str | Path, foto_dir: str | Path):
    """Return a list with the tags to be inserted after the pre-tag."""
    logging.info('add_media_files_dir_file(%s, %s)', html_file, foto_dir)
    html_file = Path(html_file)
    foto_dir = Path(foto_dir)

    html_content = html_file.read_text(encoding='utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')
    pre_tag = soup.find('pre')

    # Insert the new elements after the <pre> tag
    if pre_tag:  # pre_tag may be None, insert_after() doesn't work on None
        # When called with the intent to temporarly embed fotos from a folder, it is not guaranteed that this folder exists (I may have renamed it).
        if not Path.is_dir(foto_dir):
            logging.error("'%s' is no directory", foto_dir)
            # Add visual feedback
            b = soup.new_tag('b')
            b.append(f'{foto_dir} EXISTIERT NICHT')
            tags = []
            tags.append(b)
            tags.append(soup.new_tag('br'))
            return tags
        return collect_fotos(foto_dir, soup, [])
    return []


def add_media_files(directories: set[Path]) -> None:
    """Add media files to a diary entry, ie. `directories` contains the directories to which media files were added but not yet embedded into the HTML file laying in the same directory. This function iterates over all files in each directory, creates the according HTML tag and adds it to the diary entry."""
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
        tags = add_media_files_dir_file(html_file, day_dir)
        html = BeautifulSoup(html_file.read_text(encoding='utf-8'),
                             'html.parser')
        if (pre_tag := html.find('pre')):
            pre_tag.insert_after(*tags)
        html_file.write_text(html.prettify(), encoding='utf-8')
