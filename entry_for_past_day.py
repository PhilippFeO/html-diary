import datetime
import glob
import locale
import logging
import sys
from pathlib import Path

from bs4 import BeautifulSoup

from utils import create_stump
from vars import DIARY_DIR

locale.setlocale(locale.LC_ALL, '')


def entry_for_past_day(date: str):
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    weekday = date_obj.strftime('%A')
    month_name = date_obj.strftime('%B')
    # split 'yyyy-mm-dd'
    year, month, day = date.split('-', 2)

    # Find matching directories
    day_dir_pattern = f'{DIARY_DIR}/{year}/{month}-{month_name}/{day}-{month}-{year}-{weekday}-*'
    day_dirs = glob.glob(day_dir_pattern)

    match len(day_dirs):
        case 0:  # No day-dir exists yet
            logging.info("No directory for '%s' exists.", date)
            activity = input("Überschrift: ")
            title = f'{weekday}, {day}. {month_name} {year}: {activity}'
            activity = activity.replace(' ', '-')
            day_dir = Path(day_dir_pattern.replace('*', activity))
            Path.mkdir(day_dir, parents=True)
            logging.info("Directory for '%s' created: %s", {date}, {day_dir})
            html_skeleton = create_stump(title)
            entry_soup = BeautifulSoup(html_skeleton, 'html.parser')
            pre_tag = entry_soup.new_tag('pre')
            description = input(f'Enter description for {date}:\n')
            pre_tag.string = description
            html_entry = Path(f'{day_dir}/{day}-{month}-{year}-{weekday}-{activity}.html')
            html_entry.write_text(entry_soup.prettify(), encoding='utf-8')
            logging.info('New Entry created: %s', {html_entry})
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
            entry_soup = BeautifulSoup(html, 'html.parser')
            pre = entry_soup.find_all('pre')
            assert len(pre) == 1, f'Number of pre-tags: {len(pre)}. There should be exactly 1 in "{html_file}".'
            pre_tag = pre[0]
            if pre_tag.string:
                msg = f'Description for {date} exists: "{html_file}".'
                raise Exception(msg)
            # Query user for input
            description = input(f'Enter description for {date}:\n')
            pre_tag.string = description
            html_file.write_text(entry_soup.prettify())
            logging.info("Description for Date '%s' added to File '%s'", date, html_file)
        # To many day_dirs
        case _:
            raise Exception(
                f"Found {len(day_dirs)} matching Directories obeying '{day_dir_pattern}'. There should be exactly 1. The Directories are:\n{', '.join(day_dirs)}")


if __name__ == "__main__":
    # TODO: No logs are written during Test. Do I want this? <28-05-2024>
    # Define the path to the directory containing the files
    tmp_dir = DIARY_DIR/'.tmp'

    logging.basicConfig(level=logging.INFO,
                        format='[%(levelname)s: %(asctime)s] %(message)s',
                        # Mit Datum: %d.%m.%Y
                        datefmt=' %Y.%m.%d  %H:%M:%S',
                        filename=DIARY_DIR/'.logs/entry_for_past_day.log.txt',
                        filemode='a')
    length = 20
    logging.info(f'{"-" * length} {datetime.datetime.today()} {"-" * length}')

    entry_for_past_day(sys.argv[1])
