import datetime
import glob
import locale
import logging
import sys
from pathlib import Path

from bs4 import BeautifulSoup

import vars
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
            entry = create_stump(title, '')
            html_entry = Path(f'{day_dir}/{day}-{month}-{year}-{weekday}-{heading}.html')
            html_entry.write_text(entry.prettify(), encoding='utf-8')
            logging.info('New Entry created: %s', {html_entry})
            return str(html_entry)
        # day-dir already exists and hence an entry file
        # transfer_files() can create no-description entries which contain media files only
        case 1:
            logging.info("Directory for '%s' already exists: %s", {date}, {day_dirs[0]})
            html_files = glob.glob(f'{day_dir_pattern}/*.html')
            assert len(html_files) == 1, f'"{day_dirs[0]}" contains {len(html_files)} HTML files. There should be exactly 1.'
            html_file = Path(html_files[0])
            logging.info("Entry for '%s' exists: %s", date, html_file)
            html = html_file.read_text(encoding='utf-8')
            if not html:
                msg = f"{html_file} could not be red."
                raise Exception(msg)
            entry = BeautifulSoup(html, 'html.parser')
            pre = entry.find_all('pre')
            assert len(pre) == 1, f'Number of pre-tags: {len(pre)}. There should be exactly 1 in "{html_file}".'
            pre_tag = pre[0]
            if pre_tag.string:
                msg = f'Description for {date} exists: "{html_file}".'
                raise Exception(msg)
            # Query user for input
            # description = input(f'Enter description for {date}:\n')
            # pre_tag.string = description
            # html_file.write_text(entry.prettify())
            # logging.info("Description for Date '%s' added to File '%s'", date, html_file)
            return str(html_file)
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
