from audioconvert import *
from sys import argv


dir = '/path/to/unconverted'
auto_folder = '/path/to/auto'
cues = get_cues(dir)
split_cues(cues)
convert_all_alac(dir)
move_to_auto(dir, auto_folder)

