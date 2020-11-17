from audioconvert import *

dir = '/Volumes/nathanbackup/Downloads'
auto_folder = '/Volumes/nathanbackup/Library/Automatically Add to Music.localized'
music_dir = '/Volumes/nathanbackup/Music'

cues = get_cues(dir)
split_cues(cues)
convert_all_alac(dir)
move_to_auto(dir, auto_folder)

for d in listdir(dir):
    system(f'mv "{dir}/{d}" "{music_dir}/{d}"')

