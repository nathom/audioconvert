from pathlib import Path
import os


# finds files with specified extension(s)
def find(*args, dir):
    files = []
    for ext in args:
        pathlist = Path(dir).rglob(f'*.{ext}')
        files.extend(list(map(str, pathlist)))
    return files


def splitjoin(s, delim, start=None, end=None):
    return delim.join(s.split(delim)[start:end])


def move_to_auto(dir, auto_dir):
    files = find('m4a', dir=dir)

    def filename(f):
        return f.split('/')[-1]

    for file in files:
        os.move(dir + '/' + filename(file), auto_dir + '/' + filename(file))
