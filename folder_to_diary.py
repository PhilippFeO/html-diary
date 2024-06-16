#!/home/philipp/.tagebuch/.venv/tagebuch/bin/python3
from glob import glob
from pathlib import Path

from bs4 import BeautifulSoup

from utils import count_directories, get_date_created


def collect_dates_paths(directory: Path) -> set[tuple[str, Path]]:
    dates_paths: set[tuple[str, Path]] = set()  # dates are in format 'yyyy:mm:dd'
    for file in directory.iterdir():
        if Path.is_dir(file):
            # TODO: Welches Verzeichnis, wenn Foto in Unterordner? <16-06-2024>
            folder_to_diary(file)
        elif Path.is_file(file):
            # Read Metadata to retrieve creation date
            if date_created := get_date_created(file):
                dates_paths.add((date_created, file.parent))
            else:
                continue
    return dates_paths


def folder_to_diary(directory: Path):
    dates_paths: set[tuple[str, Path]] = collect_dates_paths(directory)
    assert len(dates_paths) > 0, f'No dates collected. "dates" is empty: {dates_paths}.'
    for date, path in dates_paths:
        # Schauen, ob Datei für Datum existiert
        year, month, day = date.split(':')
        matching_dirs = count_directories(day, month, year)
        match len(matching_dirs):
            # Ja, base-Pfad hinzufügen
            case 1:
                day_dir = matching_dirs[0]
                html_files = glob(f'{day_dir}/*.html')
                assert len(html_files) == 1, f'"{day_dir}" contains {len(html_files)} HTML files. There should be exactly 1.'
                entry_file = html_files[0]
                entry = BeautifulSoup(Path(entry_file).read_text(encoding='utf-8'), 'html.parser')
                # No base tag (=> base.href attribute)
                # Add base.href
                if entry.head and not entry.head.base:
                    base_tag = entry.new_tag('base', href=f'file://{path}')
                    entry.head.append(base_tag)
                    Path(entry_file).write_text(entry.prettify())
                # Was, wenn schon einer existiert?
                else:
                    pass
        #   Nein, Datei mit base-Pfad anlegen


if __name__ == "__main__":
    CWD = Path.cwd()
    assert 'Bilder' in CWD.parents, 'Not in ~/Bilder.'
    folder_to_diary(CWD)
