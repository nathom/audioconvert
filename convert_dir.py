from os import listdir, move
from shutil import rmtree
from converter import convert_dir, split_cues, validate_dir
from converter.util import find

# moves all .m4a files to Automatically Add to Music Folder
# input: str path to find .m4a files in
# output: None
def move_to_auto(search_path, auto_path):
    pathlist = find('m4a', dir=search_path)
    for path in pathlist:
        filename = path.split('/')[-1]
        move(path, f"{auto_path}/{filename}")


dir = '/Volumes/nathanbackup/Downloads'
auto_folder = '/Volumes/nathanbackup/Library/Automatically Add to Music.localized'

cues = get_cues(dir)
if len(cues) > 0:
    split_cues(cues)

convert_dir(dir)
validate_dir(dir)
move_to_auto(dir, auto_folder)

# deletes the flac files
remaining_dirs = listdir(dir)
remaining_dirs.remove('.DS_Store')
if remaining_dirs:
    for file in remaining_dirs:
        rmtree(dir + '/' + file)


