import logging
import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import vars
from add_media_files import create_tags
from entry import Entry

if TYPE_CHECKING:
    from bs4 import Tag


def helper(entry: Entry) -> str:
    """Add media files in `media_dir` to diary entry."""
    logging.info("Args: html_file = %s, media_dir = %s", entry, entry.base_href)
    assert entry.base_href is not None  # Alawys True because function isn't called when entry.base_href == False
    tags: list[Tag] = create_tags(entry, entry.base_href)
    logging.info("Insert created tags after '<pre>'")
    if (pre_tag := entry.soup.find('pre')):
        pre_tag.insert_after(*tags)
    with tempfile.NamedTemporaryFile(delete=False) as html_tmp_file:
        html_tmp_file.write(bytes(entry.soup.prettify(encoding='utf-8')))
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
    file = urllib.parse.unquote(sys.argv[1])
    prefix = 'file://'
    file = Path(file[len(prefix):])
    entry = Entry(path_to_parent_dir=file.parent)
    if entry.base_href is not None:
        file = helper(entry)
    subprocess.run(['/usr/bin/firefox', file], check=False)
