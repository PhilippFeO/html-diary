import logging
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup, Tag

import vars
from add_media_files import create_tags
from date import Date
from entry import Entry
from utils import create_stump

# Use different Log file when executed as test


def check(date: Date) -> bool:
    """If date of today is equal to the last date for which a summery was generated return `False`, ie. don't create a new summery. (The summery was alread red).

    If they differ, ie. no summery for today has been created, create one.
    """
    # TODO: This function is currently not tested <23-06-2024>
    create_summery = True
    last_date_file = vars.DIARY_DIR/'.last_look_into_the_past.txt'
    last_date = Date(last_date_file.read_text()[:-1],
                     sep='.')
    create_summery = last_date != date
    if create_summery:
        last_date_file.write_text(str(date), encoding='utf-8')
    return create_summery


def look_into_the_past(date: Date) -> tuple[bool, str]:
    """Collect past entries of the current date.

    - `date`: `str` in the format `dd.mm.yyyy`. No consistency checks are performed.
    """
    create_summery = check(date)
    if not create_summery:
        logging.info('The summery was already created and red.')
        return False, ''

    title = f'Heute, {date}, am...'
    # Contents of past days will be inserted after h1
    # TODO: Check if body or h1 is better for appending <22-05-2024>
    overview = create_stump(title, '')
    if isinstance(pre := overview.find('pre'), Tag):
        pre.decompose()
    else:
        logging.error("'<pre>' in 'html_skeleton' is not of Type 'Tag'. Date: {date}.")

    # In case there are no past entries for a date, the returned is basically empty. Further processing is not necessary, then.
    past_entries_exists = False

    # for past_year in range(1996, int(this_year) + 1):
    for past_year in range(int(date.year), 1995, -1):
        try:
            entry = Entry(
                date=Date(
                    f'{date.day}.{date.month}.{past_year}',
                    sep='.',
                ))
        # Probably no file for the day in the year 'past_year'
        except AssertionError:
            continue
        past_entries_exists = True
        assert overview.h1 is not None
        logging.info('%d: File exists: "%s". Extract media files.', past_year, entry.file)
        # If entry already has a 'base.href' attribute
        # Read it and add the media files within this dir to the overview
        if entry.base_href:
            tags = create_tags(entry.file, entry.base_href)
            new_h2 = f'<h2>{entry.past_heading(past_year)}</h2>'
            past_entry = BeautifulSoup(new_h2, 'html.parser')
            if (h2 := past_entry.h2):
                h2.insert_after(*tags)
            # Merge past day into overview
            overview.h1.append(past_entry)
        # No 'base.href' => Reuse whole body, because it already contains the correct <img> and <video> tags. Create a new h2 tag with the same content as the h1 tag
        else:
            assert entry.soup.body is not None
            h1_entry = entry.soup.body.h1
            assert h1_entry is not None
            h2 = entry.soup.new_tag('h2')
            h2.string = entry.past_heading(past_year)
            h1_entry.replace_with(h2)
            # Merge past day into overview
            overview.h1.append(entry.soup.body)
    return past_entries_exists, overview.prettify()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format=vars.LOG_FORMAT,
                        datefmt=vars.LOG_DATEFMT,
                        filename=vars.LOG_FILE,
                        filemode='a')
    logging.info('%s %s %s', vars.HLINE, 'look_into_the_past.py', vars.HLINE)
    # date = Date(datetime.datetime.today().strftime('%d.%m.%Y'), sep='.')
    date = Date('20.06.2024', sep='.')
    past_entries, html = look_into_the_past(date)
    if past_entries:
        html_file = Path('/tmp/look_into_the_past.html')
        logging.info("Write collected past entried to '%s'.", html_file)
        html_file.write_text(html, encoding='utf-8')
        subprocess.run(['/usr/bin/firefox', html_file], check=True)
    else:
        logging.info("There aren't any past entries for '%s' or a summery has already been created and red.", date)
    logging.shutdown()
