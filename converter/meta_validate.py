import re
from pathlib import Path
import os

import music_tag

def artwork(path1, path2):
    f1 = music_tag.load_file(path1)
    f2 = music_tag.load_file(path2)

    try:
        f2['artwork']
    except KeyError:
        f2['artwork'] = f1['artwork']

    f2.save()

def find(*args, dir):
    files = []
    for ext in args:
        pathlist = Path(dir).rglob(f'*.{ext}')
        for path in pathlist:
            path = str(path)
            files.append(path)
    return files

def validate_dir(downloads_path):
    tracks = find('m4a', 'flac', dir=downloads_path)
    tracks = [re.sub('\.m4a|\.flac', '', t) for t in tracks]

    for track in tracks:
        artwork(f'{track}.flac', f'{track}.m4a')



