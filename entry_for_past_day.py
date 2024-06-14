import datetime
import glob
import locale
import logging
import os
import sys

from bs4 import BeautifulSoup, Tag
from utils import create_stump

from vars import tagebuch_dir

locale.setlocale(locale.LC_ALL, '')


def entry_for_past_day(date: str):
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    weekday = date_obj.strftime('%A')
    month_name = date_obj.strftime('%B')
    # split 'yyyy-mm-dd'
    year, month, day = date.split('-', 2)

    # Find matching directories
    day_dir_pattern = f'{tagebuch_dir}/{year}/{month}-{month_name}/{day}-{month}-{year}-{weekday}-*'
    day_dirs = glob.glob(day_dir_pattern)

    match len(day_dirs):
        case 0:  # No day-dir exists yet
            logging.info(f'No directory for {date} exists.')
            x = input("Überschrift: ")
            title = f'{weekday}, {date}: {x}'
            x = x.replace(' ', '-')
            day_dir = day_dir_pattern.replace('*', x)
            os.makedirs(day_dir)
            logging.info(f'Directory for {date} created: {day_dir}')
            html_skeleton = create_stump(title)
            entry_soup = BeautifulSoup(html_skeleton, 'html.parser')
            pre_tag = entry_soup.find('pre')
            if not isinstance(pre_tag, Tag):
                raise Exception('The found pre-tag is not of type Tag')
            description = input(f'Enter description for {date}:\n')
            pre_tag.string = description
            with open((html_entry := f'{day_dir}/{day}-{month}-{year}-{weekday}-{x}.html'), 'w') as f:
                f.write(entry_soup.prettify())
            logging.info(f'New Entry created: {html_entry}')
        # day-dir already exists and hence an entry file
        # transfer_files() can create no-description entries which contain media files only
        case 1:
            logging.info(f'Directory for {date} already exists: {day_dirs[0]}')
            html_files = glob.glob(f'{day_dir_pattern}/*.html')
            assert len(html_files) == 1, f'"{day_dirs[0]}" contains {len(html_files)} HTML files. There should be exactly 1.'
            html_file = html_files[0]
            logging.info(f'Entry for {date} exists: {html_file}')
            with open(html_file, 'r') as f:
                html = f.read()
            if not html:
                raise Exception(f'"{html_file}" could not be red')
            entry_soup = BeautifulSoup(html, 'html.parser')
            pre = entry_soup.find_all('pre')
            assert len(pre) == 1, f'Number of pre-tags: {len(pre)}. There should be exactly 1 in "{html_file}".'
            pre_tag = pre[0]
            if pre_tag.string:
                raise Exception(f'Description for {date} exists: "{html_file}"')
            else:
                # Query user for input
                description = input(f'Enter description for {date}:\n')
                pre_tag.string = description
                with open(html_file, 'w') as f:
                    f.write(entry_soup.prettify())
                logging.info(f'Description for Date {date} added to File "{html_file}"')
        # To many day_dirs
        case _:
            raise Exception(
                f"Found {len(day_dirs)} matching Directories obeying '{day_dir_pattern}'. There should be exactly 1. The Directories are:\n{', '.join(day_dirs)}")


if __name__ == "__main__":
    # TODO: No logs are written during Test. Do I want this? <28-05-2024>
    # Define the path to the directory containing the files
    tmp_dir = tagebuch_dir/'.tmp'

    logging.basicConfig(level=logging.INFO,
                        format='[%(levelname)s: %(asctime)s] %(message)s',
                        # Mit Datum: %d.%m.%Y
                        datefmt=' %Y.%m.%d  %H:%M:%S',
                        filename=tagebuch_dir/'.logs/entry_for_past_day.log.txt',
                        filemode='a')
    length = 20
    logging.info(f'{"-" * length} {datetime.datetime.today()} {"-" * length}')

    entry_for_past_day(sys.argv[1])
