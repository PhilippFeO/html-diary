import glob
import os
import logging
import sys
from pathlib import Path

from bs4 import BeautifulSoup


def add_media_files(directories: set[Path]) -> None:
    tagebuch_dir = Path.home()/'.tagebuch'
    for day_dir in directories:
        logging.info(f"Add Media Files to Directory '{day_dir}' ...")
        # Load HTML file
        if len((html_files := glob.glob(os.path.join(day_dir, '*.html')))) == 1:
            html_file = html_files[0]
        else:
            logging.error(f"There are '{len(html_files)}' in '{day_dir}'. There should be exactly 1.")
            sys.exit(1)
        with open(html_file, 'r') as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')

        pre_tag = soup.find('pre')

        # Insert the new elements after the <pre> tag
        if pre_tag:  # pre_tag may be None, insert_after() doesn't work on None
            for filename in os.listdir(day_dir):
                f = Path(os.path.join(day_dir, filename))
                match f.suffix:
                    # Add <img src='...'/> tag for each foto
                    case '.jpg' | '.jpeg' | '.JPG' | '.JPEG' | '.png' | '.PNG':
                        new_img = soup.new_tag('img', src=tagebuch_dir/f)
                        # LIFO data structure, ie '<br/>' is the first element
                        pre_tag.insert_after(new_img)
                        pre_tag.insert_after(soup.new_tag('br'))
                        logging.info(f"Add Foto: '{f}'")
                    # Add <video controls loop><source src='...'/></video>
                    case '.mp4':
                        # Empty string == True
                        #   To be precise, any value equals True, for False, attribute has to be absent
                        # becomes <video controls loop>
                        new_video = soup.new_tag('video', controls="", loop="")
                        new_source = soup.new_tag('source', src=tagebuch_dir/f)
                        # Append the <source> tag to the <video> tag
                        new_video.append(new_source)
                        # LIFO data structure, ie '<br/>' is the first element
                        pre_tag.insert_after(new_video)
                        pre_tag.insert_after(soup.new_tag('br'))
                        logging.info(f"Add Video: '{f}'")
                    # Skip html file
                    case '.html':
                        ...
                    case _:
                        logging.error(f"There is a new File Type in '{day_dir}': '{f}'")

        with open(html_file, 'w') as file:
            file.write(soup.prettify())

        logging.info(f"Media Files in '{day_dir}' added (if there were some).")
