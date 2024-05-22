import glob
import logging
from datetime import datetime

from bs4 import BeautifulSoup

from extract_html_body import extract_html_body

date = datetime.today().strftime('%d.%m.%Y')
day, month, this_year = date.split(".", 2)

title = f'Heute, {date}, vor...'
# Contents of past days will be inserted after h1
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
    '  </body>' + \
    '</html>'

overview = BeautifulSoup(html_skeleton, 'html.parser')

# TODO: Szenario abdecken, dass es zu einem Tag keine vergangenen Einträge geben kann <22-05-2024>

# for past_year in range(1996, int(this_year) + 1):
for past_year in range(int(this_year), 1995, -1):
    matching_files = glob.glob(f"{past_year}/{month}-*/{day}-*/*.html")
    match (nmb_entries := len(matching_files)):
        case 0:
            print(f'No entry for year {past_year}.')
        case 1:
            # if len(matching_files) == 1:
            past_entry: 'BeautifulSoup' = extract_html_body(matching_files[0], f'{day}.{month}.{past_year}')
            # Merge past day into overview
            if overview.body:
                overview.body.append(past_entry)
        case _:
            files = ',\n\t'.join(matching_files)
            logging.error(f'There are {nmb_entries} files whereas there should be 1 or 0. The files are:\n\t{files}')

with open('/tmp/kombiniert.html', 'w') as f:
    f.write(overview.prettify())
print(overview.prettify())
