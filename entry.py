import glob
import logging
import os
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from date import Date
from num2words import num2words

import vars

# {Januar: 01, Februar: 02, ..., Dezember: 12}
MONTH_NUM: dict[str, str] = {month: str(num + 1).zfill(2) for num, month in enumerate((
    'Januar',
    'Februar',
    'März',
    'April',
    'Mai',
    'Juni',
    'Juli',
    'August',
    'September',
    'Oktober',
    'November',
    'Dezember',
))}


class Entry:

    def __init__(self, date: Date | None = None, path_to_parent_dir: Path | None = None):
        if date is not None:
            self.date = date
            glob_pattern = f"{vars.DIARY_DIR}/{self.date.year}/{self.date.month}-*/{self.date.day}-*/*.html"
        elif path_to_parent_dir is not None:
            glob_pattern = os.path.join(path_to_parent_dir, '*.html')
        else:
            msg = 'date and path are None'
            raise Exception(msg)
        self.matching_files = glob.glob(glob_pattern)
        self.num_files = len(self.matching_files)
        assert len(self.matching_files) == 1, f'There are {self.num_files} != 1 files: {self.matching_files}'
        self.file = Path(self.matching_files[0])
        self.soup = BeautifulSoup(self.file.read_text(encoding='utf-8'), 'html.parser')
        if path_to_parent_dir is not None:
            self.date = self.get_date_from_html()

    def __repr__(self) -> str:
        return self.file.name

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

    def get_date_from_html(self) -> Date | None:
        """Retrieve the date of the entry from it's HTML, ie. from the `<title>` tag.

        `<title>` has the following scheme: `[d]d. Monthname yyyy: …`
        """
        logging.info("Argument: html = <SKIP>")
        if self.soup.head and self.soup.head.title:
            # title = Weekday, [d]d. Monthname yyyy: Lorem Ipsum
            title = self.soup.head.title.text
            logging.info("Title to retrieve the date from: %s", title)
            # 1. split(): [d]d. Monthname yyyy: Lorem Ipsum
            # 2. split(): [d]d. Monthname yyyy
            date_month_name = title.split(',')[1] \
                .split(':')[0] \
                .strip()
            day, monthname, year = date_month_name.split()
            # handle [d]d.
            day = str(day[:-1]).zfill(2)
            month_num = MONTH_NUM[monthname]
            return Date(f'{year}:{month_num}:{day}')
        msg = f'Impossible to retrieve the date from HTML:\n{self.soup.prettify()}'
        raise Exception(msg)
