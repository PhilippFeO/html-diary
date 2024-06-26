import datetime
from pathlib import Path

DIARY_DIR: Path = Path.home()/'.tagebuch'
TMP_DIR: Path = DIARY_DIR/'.tmp'

LENGTH: int = 20
HLINE: str = '-' * LENGTH
TODAY = datetime.datetime.today()
LOG_STRING: str = f'{HLINE} {TODAY} {HLINE}'
LOG_FORMAT: str = '[%(levelname)s:  %(asctime)s  %(funcName)s]  %(message)s'
LOG_DATEFMT: str = '%d.%m.%Y  %H:%M:%S'
LOG_FILE: Path = DIARY_DIR/'.logs/log.txt'
