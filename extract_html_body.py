import logging
from datetime import datetime
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from num2words import num2words

if TYPE_CHECKING:
    from date import Date


def past_heading(past_date: 'Date') -> BeautifulSoup:
    # Configure heading for entry depending on the number of years it lays in the past
    this_year = int(datetime.today().strftime('%Y'))
    diff = this_year - (past_date_year := int(past_date.year))
    # Just to be sure
    # TODO: Reformulieren, ich finde es besser, wenn Text mit "vor einem Jahr, DATUM" startet <09-06-2024>
    assert diff >= 0, f'Difference between {this_year} and {past_date_year} is {diff}<0. Should be >=0.'
    match diff:
        case 0:
            h2 = f"<h2>... {past_date}</h2>"
        case 1:
            h2 = f"<h2>... {past_date}, vor einem Jahr</h2>"
        case _:
            h2 = f"<h2>... {past_date}, vor {num2words(diff, lang='de')} Jahren</h2>"
    return BeautifulSoup(h2, 'html.parser')
