import datetime
import glob
import locale
import logging
import sys
from pathlib import Path

from bs4 import BeautifulSoup

import vars
from entry import Entry
from utils import create_stump

locale.setlocale(locale.LC_ALL, '')


def entry_for_past_day(date: str, heading: str):
    """Print the path to the html entry to start nvim with this file in the calling bash script."""
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    weekday = date_obj.strftime('%A')
    month_name = date_obj.strftime('%B')
    # split 'yyyy-mm-dd'
    year, month, day = date.split('-', 2)

    # Find matching directories
    day_dir_pattern = f'{vars.DIARY_DIR}/{year}/{month}-{month_name}/{day}-{month}-{year}-{weekday}-*'
    day_dirs = glob.glob(day_dir_pattern)

    match len(day_dirs):
        case 0:  # No day-dir exists yet
            logging.info("No directory for '%s' exists.", date)
            title = f'{weekday}, {day}. {month_name} {year}: {heading}'
            heading = heading.replace(' ', '-')
            day_dir = Path(day_dir_pattern.replace('*', heading))
            Path.mkdir(day_dir, parents=True)
            logging.info("Directory for '%s' created: %s", {date}, {day_dir})
            stump = create_stump(title, '')
            entry_file = Path(f'{day_dir}/{day}-{month}-{year}-{weekday}-{heading}.html')
            entry_file.write_text(stump.prettify(), encoding='utf-8')
            logging.info('New Entry created: %s', {entry_file})
            return str(entry_file)
        # day-dir already exists and hence an entry file
        # transfer_files() can create no-description entries which contain media files only
        case 1:
            logging.info("Directory for '%s' already exists: %s", {date}, {day_dirs[0]})
            entry = Entry(path_to_parent_dir=Path(day_dirs[0]))
            pre = entry.soup.find_all('pre')
            assert len(pre) == 1, f'Number of pre-tags: {len(pre)}. There should be exactly 1 in "{entry.file}".'
            pre_tag = pre[0]
            if pre_tag.string is not None or pre_tag.string != '':
                msg = f'Description for {date} exists: "{entry.file}".'
                raise Exception(msg)
            # Query user for input
            pre_tag.string = input(f'Enter description for {date}:\n')
            entry.file.write_text(entry.soup.prettify())
            logging.info("Description for Date '%s' added to File '%s'", date, entry.file)
            return str(entry.file)
        # To many day_dirs
        case _:
            msg = f"Found {len(day_dirs)} matching Directories obeying '{day_dir_pattern}'. There should be exactly 1. The Directories are:\n{', '.join(day_dirs)}"
            raise Exception(msg)


if __name__ == "__main__":
    # TODO: No logs are written during Test. Do I want this? <28-05-2024>
    # Define the path to the directory containing the files
    logging.basicConfig(level=logging.INFO,
                        format=vars.LOG_FORMAT,
                        datefmt=vars.LOG_DATEFMT,
                        filename=vars.LOG_FILE,
                        filemode='a')
    logging.info('%s %s %s', vars.HLINE, 'entry_for_past_day.py', vars.HLINE)

    # sys.argv[1]: yyyy-mm-dd, str
    # sys.argv[2]: heading, str
    print(entry_for_past_day(sys.argv[1], sys.argv[2]))
