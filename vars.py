import datetime
from pathlib import Path

DIARY_DIR: Path = Path.home()/'.tagebuch'
TMP_DIR: Path = DIARY_DIR/'.tmp'

LENGTH: int = 20
HLINE: str = '-' * LENGTH
TODAY = datetime.datetime.today()
LOG_STRING: str = f'{HLINE} {TODAY} {HLINE}'
