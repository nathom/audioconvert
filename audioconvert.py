from os import system, listdir
from pathlib import Path

import cueparser


# converts flac to alac
# input: str path of flac, str path of output directory
# output: None
def convert_alac(path, delete_original=True):
    ext = path.split('.')[-1]
    outfile = path.replace('.' + ext, '.m4a')
    command = f'ffmpeg -i "{path}" -vn -c:v copy -c:a alac -y "{outfile}"'
    if delete_original:
        command += f' && rm "{path}"'
    system(command)


# moves all .m4a files to Automatically Add to Music Folder
# input: str path to find .m4a files in
# output: None
def move_to_auto(search_path, auto_path):
    pathlist = find('m4a', dir=search_path)
    for path in pathlist:
        filename = path.split('/')[-1]
        system(f'mv "{path}" "{auto_path}/{filename}"')


# finds files with specified extension(s)
def find(*args, dir):
    files = []
    for ext in args:
        pathlist = Path(dir).rglob(f'*.{ext}')
        for path in pathlist:
            path = str(path)
            files.append(path)
    return files

# finds and parses all cue files in a dir
# input str: path to directory
# output dict: dict of cue info
def get_cues(dir):
    cues = [cueparser.parse_cue(c) for c in find('cue', dir=dir)]
    return cues

def split_cues(cues):
    for cue in cues:
        cueparser.split_cue(cue)

def convert_all_alac(dir):
    paths = find('flac', 'wav', 'wv', 'dsf', dir=dir)
    for path in paths:
        convert_alac(path)





