import datetime
import logging
import subprocess
import sys
import tempfile
from pathlib import Path

from bs4 import BeautifulSoup

from add_media_files import add_media_files_dir_file
from vars import DIARY_DIR

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s: %(asctime)s] %(message)s',
                    datefmt=' %d.%m.%Y  %H:%M:%S',
                    filename=DIARY_DIR/'.logs/handler.log.txt',
                    filemode='a')
length = 20
logging.info('%s %s %s', bar := '-' * length, datetime.datetime.today(), bar)


def helper(html_file, dir_path):
    """Add media files in dir_path to diary entry."""
    tags = add_media_files_dir_file(html_file, Path(dir_path))
    logging.info('Media files added')
    # with open(html_file, 'r') as file:
    #     html_content = file.read()
    html_content = Path(html_file).read_text(encoding='utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')
    if (pre_tag := soup.find('pre')):
        pre_tag.insert_after(*tags)
    with tempfile.NamedTemporaryFile(delete=False) as html_tmp_file:
        html_tmp_file.write(bytes(soup.prettify(encoding='utf-8')))
        html_tmp_file.flush()
        logging.info('Open %s', html_tmp_file.name)
        html_file = html_tmp_file.name
    subprocess.run(['/usr/bin/firefox', html_file], check=False)


def read_base_href(html_file) -> Path | None:
    logging.info('read_base_href( % s)', html_file)
    if '.tagebuch' in html_file:
        # Retrieve head.base.href attribute to embed images
        # with open(html_file, 'r') as file:
        #     html_content = file.read()
        html_content = Path(html_file).read_text(encoding='utf-8')
        soup = BeautifulSoup(html_content, 'html.parser')
        logging.info('Parsed: %s', html_file)
        if soup.head and soup.head.base and (href := soup.head.base.get('href')):
            if isinstance(href, str):
                # Remove file:// from base.href
                dir_path = Path(href[len('file://'):].replace('~', str(Path.home())))
                logging.info('%s = ', dir_path)
                return dir_path
            logging.error('`href` is not of type `str` but `list[str] | None`.')
        else:
            logging.info('Either no `head`, `head.base` or `href` attribute within `head.base`.')
    return None


if __name__ == "__main__":
    html_file = sys.argv[1]
    prefix = 'file://'
    html_file = html_file[len(prefix):]
    if (dir_path := read_base_href(html_file)):
        helper(html_file, dir_path)
    else:
        subprocess.run(['/usr/bin/firefox', html_file], check=False)
