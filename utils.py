from glob import glob
from vars import tagebuch_dir


def count_directories(day: str, month: str, year: str) -> list[str]:
    return glob(f"{tagebuch_dir}/{year}/{month}-*/{day}-{month}-{year}-*")
