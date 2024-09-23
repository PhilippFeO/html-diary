import glob
import logging
import os
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from num2words import num2words

import vars
from date import Date


class Entry:

    def __init__(self, date: Date | None = None, path: Path | None = None):
        if date is not None:
            self.date = date
            self.matching_files = glob.glob(f"{vars.DIARY_DIR}/{self.date.year}/{self.date.month}-*/{self.date.day}-*/*.html")
            self.num_files = len(self.matching_files)
            assert self.num_files == 1, f'There are {self.num_files} != 1 files for {self.date}: {self.matching_files}'
            self.file = Path(self.matching_files[0])
        elif path is not None:
            html_files = glob.glob(os.path.join(path, '*.html'))
            assert len(html_files) == 1, f'There are {self.num_files} != 1 files for {self.date}: {self.matching_files}'
            self.file = Path(html_files[0])
        self.soup = BeautifulSoup(self.file.read_text(encoding='utf-8'), 'html.parser')

    @property
    def base_href(self) -> Path | None:
        """Retrieve the value of `head.base.href` from the HTML entry."""
        logging.info('Arg: self.file = %s', self.file)
        if '.tagebuch' in self.file.parts:
            logging.info('Parsed: %s', self.file)
            assert self.soup is not None
            if self.soup.head and self.soup.head.base and (href := self.soup.head.base.get('href')):
                assert isinstance(href, str)
                # Remove prefix 'file://' from base.href
                # Replace '~' by 'Path.home()'
                dir_path = Path(href[len('file://'):].replace('~', str(Path.home())))
                logging.info('dir_path = %s', dir_path)
                return dir_path
            logging.info("Either no 'head', 'head.base' or 'href' attribute within 'head.base'. Maybe media files reside next to to %s", self.file)
        return None

    def past_heading(self, past_year: int) -> str:
        # Configure heading for entry depending on the number of years it lays in the past
        this_year = int(datetime.today().strftime('%Y'))
        diff = this_year - past_year
        # Just to be sure
        # TODO: Reformulieren, ich finde es besser, wenn Text mit "vor einem Jahr, DATUM" startet <09-06-2024>
        assert diff >= 0, f'Difference between {this_year} and {past_year} is {diff}<0. Should be >=0.'
        past_date = Date(f'{self.date.day}.{self.date.month}.{past_year}', sep='.')
        match diff:
            case 0:
                h2 = f"... {past_date}"
            case 1:
                h2 = f"... {past_date}, vor einem Jahr"
            case _:
                h2 = f"... {past_date}, vor {num2words(diff, lang='de')} Jahren"
        return h2

    def __repr__(self) -> str:
        return self.file.name
