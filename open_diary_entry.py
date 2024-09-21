import logging
import subprocess
import tempfile
from pathlib import Path

from bs4 import BeautifulSoup, Tag

import vars
from add_media_files import create_tags


def helper(html_file: Path, media_dir: Path) -> str:
    """Add media files in `media_dir` to diary entry."""
    logging.info("Args: html_file = %s, media_dir = %s", html_file, media_dir)
    tags: list[Tag] = create_tags(html_file, media_dir)
    logging.info("Insert created tags after '<pre>'")
    html_content = Path(html_file).read_text(encoding='utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')
    if (pre_tag := soup.find('pre')):
        pre_tag.insert_after(*tags)
    with tempfile.NamedTemporaryFile(delete=False) as html_tmp_file:
        html_tmp_file.write(bytes(soup.prettify(encoding='utf-8')))
        html_tmp_file.flush()
        return html_tmp_file.name


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format=vars.LOG_FORMAT,
                        datefmt=vars.LOG_DATEFMT,
                        filename=vars.LOG_FILE,
                        filemode='a')
    logging.info('%s %s %s', vars.HLINE, 'open_diary_entry.py', vars.HLINE)
    import sys
    import urllib.parse
    html_file = urllib.parse.unquote(sys.argv[1])
    prefix = 'file://'
    html_file = Path(html_file[len(prefix):])
    if (dir_path := read_base_href(html_file)):
        html_file = helper(html_file, dir_path)
    subprocess.run(['/usr/bin/firefox', html_file], check=False)
