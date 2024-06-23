import datetime
import logging
import subprocess
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


def helper(html_file: Path, dir_path: Path) -> str:
    """Add media files in `dir_path` to diary entry."""
    logging.info("helper()\n\t%s\n\t%s", html_file, dir_path)
    tags = add_media_files_dir_file(html_file, dir_path)
    logging.info('Media files added')
    html_content = Path(html_file).read_text(encoding='utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')
    if (pre_tag := soup.find('pre')):
        pre_tag.insert_after(*tags)
    with tempfile.NamedTemporaryFile(delete=False) as html_tmp_file:
        html_tmp_file.write(bytes(soup.prettify(encoding='utf-8')))
        html_tmp_file.flush()
        return html_tmp_file.name


def read_base_href(html_file: Path) -> Path | None:
    """Retrieve the value of `head.base.href` from a HTML entry."""
    logging.info('read_base_href(%s)', html_file)
    if '.tagebuch' in html_file.parts:
        html_content = Path(html_file).read_text(encoding='utf-8')
        soup = BeautifulSoup(html_content, 'html.parser')
        logging.info('Parsed: %s', html_file)
        if soup.head and soup.head.base and (href := soup.head.base.get('href')):
            if isinstance(href, str):
                # Remove prefix 'file://' from base.href
                # Replace '~' by 'Path.home()'
                dir_path = Path(href[len('file://'):].replace('~', str(Path.home())))
                logging.info('dir_path = %s', dir_path)
                return dir_path
            logging.error("'href' is not of type 'str' but 'list[str] | None'.")
        else:
            logging.info("Either no 'head', 'head.base' or 'href' attribute within 'head.base'.")
    return None


if __name__ == "__main__":
    import sys
    html_file = sys.argv[1]
    prefix = 'file://'
    html_file = Path(html_file[len(prefix):])
    if (dir_path := read_base_href(html_file)):
        html_file = helper(html_file, dir_path)
    subprocess.run(['/usr/bin/firefox', html_file], check=False)
