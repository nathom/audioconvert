from audioconvert import *
from sys import argv


if len(argv) > 1:
    dir = argv[1]
else:
    dir = input('What folder do you want to convert?\n')
    auto_folder = input('What is the path of "Automatically Add to Music"?\n')

auto_folder = '/Volumes/nathanbackup/Library/Automatically Add to Music.localized'

cues = get_cues(dir)
split_cues(cues)
convert_all_alac(dir)
move_to_auto(dir, auto_folder)

