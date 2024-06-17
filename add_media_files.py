import glob
import logging
import os
from pathlib import Path

from bs4 import BeautifulSoup

from vars import DIARY_DIR


def add_media_files_dir_file(html_file: str | Path, foto_dir: str | Path):
    """Return a list with the tags to be inserted after the pre-tag."""
    logging.info('add_media_files_dir_file(%s, %s)', html_file, foto_dir)
    html_file = Path(html_file)
    foto_dir = Path(foto_dir)
    tags = []

    html_content = html_file.read_text(encoding='utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')
    pre_tag = soup.find('pre')

    # Insert the new elements after the <pre> tag
    if pre_tag:  # pre_tag may be None, insert_after() doesn't work on None
        # When called with the intent to temporarly embed fotos from a folder, it is not guaranteed that this folder exists (I may have renamed it).
        if not Path.is_dir(foto_dir):
            logging.error("'%s' doesn't exists", foto_dir)
            # Add visual feedback
            b = soup.new_tag('b')
            b.append(f'{foto_dir} EXISTIERT NICHT')
            tags.append(b)
            tags.append(soup.new_tag('br'))
            return tags
        for filename in foto_dir.iterdir():
            f = foto_dir / filename
            match f.suffix:
                # Add <img src='...'/> tag for each foto
                case '.jpg' | '.jpeg' | '.JPG' | '.JPEG' | '.png' | '.PNG':
                    new_img = soup.new_tag('img', src=DIARY_DIR/f)
                    # LIFO data structure, ie '<br/>' is the first element
                    tags.append(new_img)
                    tags.append(soup.new_tag('br'))
                    logging.info("Added Foto: '%s'", f)
                # Add <video controls loop><source src='...'/></video>
                case '.mp4' | '.MP4':
                    # Empty string == True
                    #   To be precise, any value equals True, for False, attribute has to be absent
                    # becomes <video controls loop>
                    new_video = soup.new_tag('video', controls="", loop="")
                    new_source = soup.new_tag('source', src=DIARY_DIR/f)
                    # Append the <source> tag to the <video> tag
                    new_video.append(new_source)
                    # LIFO data structure, ie '<br/>' is the first element
                    tags.append(new_video)
                    tags.append(soup.new_tag('br'))
                    logging.info("Added Video: '%s'", f)
                # Skip html file
                case '.html':
                    logging.info("(Obviously) Skipping the HTML Entry: '%s'", f)
                case _:
                    logging.warning("There is a new File Type in '%s': '%s'", foto_dir, f)
    return tags


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
        soup = None
        with Path.open(html_file, 'r') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            if (pre_tag := soup.find('pre')):
                pre_tag.insert_after(*tags)
        with Path.open(html_file, 'w') as file:
            file.write(soup.prettify())
