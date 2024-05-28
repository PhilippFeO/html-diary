from pathlib import Path
from vars import tagebuch_dir


tests_dir = tagebuch_dir / 'tests'
test_diary_dir: Path = tests_dir / 'test_tagebuch'
test_tmp_dir: Path = test_diary_dir / '.tmp'
test_transfered_dir: Path = test_tmp_dir / 'transfered'

foto_1_name: Path = Path('transfer_files_foto_1.jpg')
foto_2_name: Path = Path('transfer_files_foto_2.jpg')
tf_foto_no_day_dir: Path = Path('transfer_files_no_day_dir.jpg')
tf_foto_two_day_dir: Path = Path('transfer_files_two_day_dir.jpg')

video_1_name: Path = Path('transfer_files_video_1.mp4')
