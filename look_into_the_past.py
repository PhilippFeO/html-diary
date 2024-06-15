import datetime
import glob
import logging
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup

import vars
from add_media_files import add_media_files_dir_file
from extract_html_body import extract_html_body, past_heading
from my_html_handler import read_base_href
from utils import create_stump

# Use different Log file when executed as test
logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s: %(asctime)s] %(message)s',
                    # Mit Datum: %d.%m.%Y
                    datefmt=' %Y.%m.%d  %H:%M:%S',
                    filename=vars.DIARY_DIR/'.logs/look_into_the_past.log.txt',
                    filemode='a')
length = 20
logging.info(f'{"-" * length} {datetime.datetime.today()} {"-" * length}')


def check(date: str) -> bool:
    """If date of today is equal to the last date for which a summery was generated return `False`, ie. don't create a new summery. (The summery was alread red).
    If they differ, ie. no summery for today has been created, create one."""
    create_summery = True
    # TODO: tagebuch-Dir as parameter for testing <26-05-2024>
    #   This function is currently not tested
    with open((last := vars.DIARY_DIR/'.last_look_into_the_past.txt'), 'r') as f:
        last_date = f.read()
        create_summery = last_date != date
    if create_summery:
        with open(last, 'w') as f:
            f.write(date)
    return create_summery


def look_into_the_past(date: str) -> tuple[bool, str]:
    """Collects past entries of the current date.

    - `date`: `str` in the format `dd.mm.yyyy`. No consistency checks are performed.
    - `tagebuch_dir`: `Path` of the diary."""
    create_summery = check(date)
    if not create_summery:
        logging.info('The summery was already created and red.')
        return False, ''

    day, month, this_year = date.split(".", 2)

    title = f'Heute, {date}, am...'
    # Contents of past days will be inserted after h1
    # TODO: Check if body or h1 is better for appending <22-05-2024>
    html_skeleton = create_stump(title)
    overview = BeautifulSoup(html_skeleton, 'html.parser')

    # In case there are no past entries for a date, the returned is basically empty. Further processing is not necessary, then.
    past_entries = False

    # for past_year in range(1996, int(this_year) + 1):
    for past_year in range(int(this_year), 1995, -1):
        matching_files = glob.glob(f"{vars.DIARY_DIR}/{past_year}/{month}-*/{day}-*/*.html")
        match (nmb_entries := len(matching_files)):
            case 0:
                logging.info(f'No entry for year {past_year}.')
            case 1:
                past_entries = True
                h1 = overview.h1
                past_entry: 'BeautifulSoup'
                logging.info(f'{past_year}: File exists: "{(html_entry := matching_files[0])}". Extract media files.')
                if (dir_path := read_base_href(html_entry)):
                    tags = add_media_files_dir_file(html_entry, dir_path)
                    past_entry = past_heading(f'{day}.{month}.{past_year}')
                    if (h2 := past_entry.h2):
                        h2.insert_after(*tags)
                else:
                    past_entry = extract_html_body(html_entry, f'{day}.{month}.{past_year}')
                # Merge past day into overview
                if h1:
                    h1.append(past_entry)
            case _:
                files = ',\n\t'.join(matching_files)
                logging.error(f'There are {nmb_entries} files whereas there should be 1 or 0. The files are:\n\t{files}')

    return past_entries, overview.prettify()


if __name__ == "__main__":
    date = datetime.datetime.today().strftime('%d.%m.%Y')
    past_entries, html = look_into_the_past(date)
    if past_entries:
        html_path = Path('/tmp/look_into_the_past.html')
        logging.info(f"Write collected past entried to '{html_path}'.")
        # TODO: Use File Descriptors <24-05-2024>
        with open(html_path, 'w') as html_file:
            html_file.write(html)
        subprocess.run(['firefox', html_path])
    else:
        logging.info(f"There aren't any past entries for {date} or a summery has already been created and red.")
