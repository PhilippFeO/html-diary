import glob
import logging
import os
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from date import Date
from num2words import num2words
from utils import create_stump

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

    def __init__(self, **kwargs):
        key_new_entry = 'new_entry'
        key_date = 'date'
        key_path_to_parent_dir = 'path_to_parent_dir'
        # Create new diary entry
        if key_new_entry in kwargs:
            # Disassemble tuple
            new_entry_path_value = kwargs[key_new_entry]
            date: Date = new_entry_path_value[0]
            location: str = new_entry_path_value[1]
            href: str = new_entry_path_value[2]
            # Media files were added if there was an entry fitting the created date.
            # Some media files have no according entry for their created date. In this block,
            # the (empty) entry is created to avoid remaining media files in .tmp/.
            title = f"{date.weekday}, {date.title_fmt}{f': {location}' if location != '' else ''}"
            self.soup = create_stump(title, location)
            assert self.soup.head, "No 'head' in the HTML skeleton."  # Should not happen
            if href is not None:
                base_tag = self.soup.new_tag('base', href=href)
                self.soup.head.append(base_tag)
            parent_dir: Path = vars.DIARY_DIR/date.year / \
                f"{date.month}-{date.monthname}/{date.day}-{date.month}-{date.year}-{date.weekday}{f'-{location}' if location != '' else ''}"
            # TODO: These lines were originally tested in tests/utils_test.py::test_create_dir_and_file() <27-09-2024>
            Path.mkdir(parent_dir, parents=True)
            self.file = Path(parent_dir/f'{parent_dir.name}.html')
            # Write the HTML (media files are added later as usual)
            self.file.write_text(self.soup.prettify())
            self.date = date
            logging.info('Created empty Entry: %s', self.file)
        else:
            # Create entry from provided date
            if key_date in kwargs:
                self.date = kwargs[key_date]
                glob_pattern = f"{vars.DIARY_DIR}/{self.date.year}/{self.date.month}-*/{self.date.day}-*/*.html"
            # Create entry instance from path of parent directory
            elif key_path_to_parent_dir in kwargs:
                glob_pattern = os.path.join(kwargs[key_path_to_parent_dir], '*.html')
            else:
                msg = f'Wrong kwarg(s). See Entry.__init__() for valid kwargs. Provided kwargs: {kwargs}'
                raise Exception(msg)
            self.matching_files = glob.glob(glob_pattern)
            self.num_files = len(self.matching_files)
            assert len(self.matching_files) == 1, f'There are {self.num_files} != 1 files: {self.matching_files}'
            self.file = Path(self.matching_files[0])
            self.soup = BeautifulSoup(self.file.read_text(encoding='utf-8'), 'html.parser')
            # Every instance needs a working date and file attribute
            if key_path_to_parent_dir in kwargs:
                self.date = self.get_date_from_html()

    def __eq__(self, other, /) -> bool:
        return self.date == other.date and self.file == other.file

    def __hash__(self) -> int:
        # There should always be a date but without the LSP complains
        assert self.date
        return int(f'{self.date.year}{self.date.month}{self.date.day}')

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
        assert self.date is not None
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
