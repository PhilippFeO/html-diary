from datetime import datetime


class Date:
    def __init__(self, date_str: str, sep: str = ':', maxsplit: int = -1):
        self.year, self.month, self.day = date_str.split(sep, maxsplit)
        # date_str has to be either 'dd.mm.yyyy' or 'yyyy.mm.dd'
        # swap day and year if date_str has scheme 'dd.mm.yyyy'
        assert (len(self.year) == 4) ^ (len(self.day) == 4), \
            f'{len(self.year) = } ({self.year = }), {len(self.day) = } ({self.day = }), but only one shold have length 4.'
        if len(self.year) != 4:
            self.day, self.year = self.year, self.day

        date_obj = datetime.strptime(f'{self.year}{sep}{self.month}{sep}{self.day}', f'%Y{sep}%m{sep}%d').date()
        self.weekday = date_obj.strftime('%A')
        self.monthname = date_obj.strftime('%B')
        self.title_fmt = date_obj.strftime('%d. %B %Y')

    def __eq__(self, other):
        return (self.year == other.year and
                self.month == other.month and
                self.day == other.day)

    def __hash__(self):
        return int(f'{self.year}{self.month}{self.day}')

    def __str__(self) -> str:
        return f'{self.day}.{self.month}.{self.year}'

    def __repr__(self) -> str:
        return f'{self.__str__()}, {self.weekday}, {self.monthname}, {self.title_fmt}'


if __name__ == "__main__":
    d = Date('28.07.2024', sep='.')
