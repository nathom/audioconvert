from pathlib import Path

# finds files with specified extension(s)
def find(*args, dir):
    files = []
    for ext in args:
        pathlist = Path(dir).rglob(f'*.{ext}')
        for path in pathlist:
            path = str(path)
            files.append(path)
    return files

def splitjoin(s, delim, start=None, end=None):
    return delim.join(s.split(delim)[start:end])

