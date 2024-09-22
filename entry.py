import glob
import logging
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, PageElement, Tag

import vars
from date import Date
from extract_html_body import past_heading


class Entry:

    def __init__(self, year: int, month: str, day: str):
        self.date = Date(f'{day}.{month}.{year}', sep='.')
        self.matching_files = glob.glob(f"{vars.DIARY_DIR}/{year}/{month}-*/{day}-*/*.html")
        self.num_files = len(self.matching_files)
        if self.num_files > 1:
            msg = f'Es gibt zu viele Dateien für den {day}.{month}.{year}.'
            raise Exception(msg)
        self.base_href_path = self.__read_base_href()
        self.soup = BeautifulSoup(self.file.read_text(encoding='utf-8'), 'html.parser')
        self.past_heading = past_heading(self.date)

    # TODO: Turn into cached_property <21-09-2024>
    @property
    def file(self) -> Path:
        if self.num_files == 1:
            return Path(self.matching_files[0])
        msg = f'Es gibt keine Datei für den {self.date}'
        raise Exception(msg)

    def __read_base_href(self) -> Path | None:
        """Retrieve the value of `head.base.href` from the HTML entry."""
        logging.info('Arg: self.file = %s', self.file)
        if '.tagebuch' in self.file.parts:
            html_content = Path(self.file).read_text(encoding='utf-8')
            soup = BeautifulSoup(html_content, 'html.parser')
            logging.info('Parsed: %s', self.file)
            if soup.head and soup.head.base and (href := soup.head.base.get('href')):
                if isinstance(href, str):
                    # Remove prefix 'file://' from base.href
                    # Replace '~' by 'Path.home()'
                    dir_path = Path(href[len('file://'):].replace('~', str(Path.home())))
                    logging.info('dir_path = %s', dir_path)
                    return dir_path
                logging.warning("'href' is not of type 'str' but 'list[str] | None'.")
            else:
                logging.info("Either no 'head', 'head.base' or 'href' attribute within 'head.base'. Maybe media files reside next to to %s", self.file)
        return None

    def __repr__(self) -> str:
        return self.file.name
