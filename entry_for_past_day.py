import datetime
import glob
import os
import logging
import sys

from bs4 import BeautifulSoup, Tag

from vars import tagebuch_dir

# TODO: in ifmain <26-05-2024>
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


def entry_for_past_day(date: str):
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    weekday = date_obj.strftime('%A')
    month_name = date_obj.strftime('%B')
    # split 'dd.mm.yyyy'
    year, month, day = date.split('-', 2)

    # Find matching directories
    day_dir_pattern = f'{tagebuch_dir}/{year}/{month}-{month_name}/{day}-{month}-{year}-{weekday}-*'
    day_dirs = glob.glob(day_dir_pattern)

    match len(day_dirs):
        case 0:  # No day-dir exists yet
            x = input("Überschrift: ")
            title = f'{weekday}, {date}: {x}'
            x = x.replace(' ', '-')
            day_dir = day_dir_pattern.replace('*', x)
            os.makedirs(day_dir)
            html_skeleton = "<!DOCTYPE html>" + \
                '<html>' + \
                '  <head>' + \
                f'	<title>{title}</title>' + \
                '	<!-- weitere Kopfinformationen -->' + \
                '	<!-- Styles für <pre> -->' + \
                '	<link rel="stylesheet" href="/home/philipp/.tagebuch/style.css">' + \
                '  </head>' + \
                '  <body>' + \
                f'	<h1>{title}</h1>' + \
                '  <pre></pre>' + \
                '  </body>' + \
                '</html>'
            entry_soup = BeautifulSoup(html_skeleton, 'html.parser')
            pre_tag = entry_soup.find('pre')
            if not isinstance(pre_tag, Tag):
                raise Exception('The found pre-tag is not of type Tag')
            description = input(f'Enter description for {date}:\n')
            pre_tag.string = description
            with open(f'{day_dir}/{day}-{month}-{year}-{weekday}-{x}.html', 'w') as f:
                f.write(entry_soup.prettify())
        # day-dir already exists and hence an entry file
        # transfer_files() can create no-description entries which contain media files only
        case 1:
            html_files = glob.glob(f'{day_dir_pattern}/*.html')
            match len(html_files):
                case 0:  # There is a day-dir but no HTML entry -> Can't happen currently
                    raise Exception(f'"{day_dirs[0]} doesn\'t contain a HTML file')
                case 1:
                    html_file = html_files[0]
                    logging.info(f'HTML file in "{day_dirs[0]}" present: {html_file}')
                    with open(html_file, 'r') as f:
                        html = f.read()
                    if not html:
                        raise Exception(f'"{html_file}" could not be red')
                    entry_soup = BeautifulSoup(html, 'html.parser')
                    pre = entry_soup.find_all('pre')
                    match len(pre):
                        case 0:
                            raise Exception(f'File "{html_file}" doesn\'t contain a <pre> tag')
                        case 1:
                            # Query user for input
                            description = input(f'Enter description for {date}:\n')
                            pre_tag = pre[0]
                            pre_tag.string = description
                            with open(html_file, 'w') as f:
                                f.write(entry_soup.prettify())
                        # Too many pre-tags in HTML file
                        case _:
                            raise Exception(f'"{len(pre)} instead of 1 pre-tags in "{html_file}"')
                # Too many HTML files in day_dir
                case _:
                    html_files_str = ',\n\t'.join(html_files)
                    raise Exception(f'There are too many HTML files in "{day_dirs}":\n{html_files_str}')
        # To many day_dirs
        case _:
            logging.warning(
                f"Found {len(day_dirs)} matching Directories obeying '{day_dir_pattern}'. There should be exactly 1. The Directories are:\n{', '.join(day_dirs)}")


if __name__ == "__main__":
    import locale
    locale.setlocale(locale.LC_ALL, '')
    entry_for_past_day(sys.argv[1])
