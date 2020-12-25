from os import listdir
from shutil import rmtree, move
import converter
from tqdm import tqdm
from converter.util import find

# moves all .m4a files to Automatically Add to Music Folder
# input: str path to find .m4a files in
# output: None
def move_to_auto(search_path, auto_path):
    pathlist = find('m4a', dir=search_path)
    for path in tqdm(pathlist, unit='files'):
        filename = path.split('/')[-1]
        move(path, f"{auto_path}/{filename}")

def convert_all(dir, auto_folder):
    cues = converter.get_cues(dir)
    if len(cues) > 0:
        converter.split_cues(cues)

    converter.convert_dir(dir)
    converter.validate_dir(dir)
    print(f'\nMoving files to {auto_folder}...\n')
    move_to_auto(dir, auto_folder)

    # deletes the flac files
    remaining_dirs = listdir(dir)
    remaining_dirs.remove('.DS_Store')
    if remaining_dirs:
        for file in remaining_dirs:
            rmtree(dir + '/' + file)


if __name__ == '__main__':
    dir = '/Volumes/nathanbackup/Downloads'
    auto_folder = '/Volumes/nathanbackup/Library/Automatically Add to Music.localized'
    convert_all(dir, auto_folder)

