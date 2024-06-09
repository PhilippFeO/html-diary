import datetime
import logging
import subprocess
import sys
import tempfile
from pathlib import Path

from bs4 import BeautifulSoup

from add_media_files import add_media_files_dir_file
from vars import tagebuch_dir

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s: %(asctime)s] %(message)s',
                    # Mit Datum: %d.%m.%Y
                    datefmt=' %Y.%m.%d  %H:%M:%S',
                    filename=tagebuch_dir/'.logs/handler.log.txt',
                    filemode='a')
length = 20
logging.info(f'{"-" * length} {datetime.datetime.today()} {"-" * length}')


def helper(html_file, dir_path):
    soup = add_media_files_dir_file(html_file, Path(dir_path))
    logging.info('Media files added')
    with tempfile.NamedTemporaryFile(delete=False) as html_file:
        html_file.write(bytes(soup.encode('utf-8')))
        html_file.flush()
        logging.info(f'Open {html_file.name}')
        html_file = html_file.name
    subprocess.run(['open', html_file])


def read_base_href(html_file):
    logging.info(f"open_file('{html_file}')")
    if '.tagebuch' in html_file:
        # look_into_the_past.py calls the function without 'file://'
        # 'file://' is only part of param when called via the nemo action
        # Remove file:// from html_file
        len_prefix = len(prefix) if (prefix := 'file://') in html_file else 0
        html_file = html_file[len_prefix:]
        # Retrieve head.base.href attribute to embed images
        with open(html_file, 'r') as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        logging.info(f'Parsed: {html_file}')
        if soup.head and soup.head.base and (href := soup.head.base.get('href')):
            if isinstance(href, str):
                # Remove file:// from base.href
                dir_path = href[len(prefix):].replace('~', str(Path.home()))
                logging.info(f'{dir_path = }')
                # Add media files in dir_path to diary entry
                return dir_path
            else:
                logging.error('`href` is not of type `str` but `list[str] | None`.')
        else:
            logging.info('Either no `head`, `head.base` or `href` attribute within `head.base`.')
    return None


if __name__ == "__main__":
    dir_path = read_base_href((html_file := sys.argv[1]))
    helper(html_file, dir_path)
