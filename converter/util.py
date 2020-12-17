from pathlib import Path

# finds files with specified extension(s)
def find(*args, dir, organize=False):
    files = []
    for ext in args:
        pathlist = Path(dir).rglob(f'*.{ext}')
        for path in pathlist:
            path = str(path)
            files.append(path)

    if organize:
        files.sort()
        files_dict = {}
        new_files = []
        for file in files:
            parent = '/'.join(file.split('/')[:-1])
            if parent not in files_dict:
                files_dict[parent] = []
            files_dict[parent].append(file)
        key = lambda p: int(p.split('/')[-1][:2] if p.split('/')[-1][1] != '.' else p.split('/')[-1][0])
        for k, v in files_dict.items():
            print(f'{k, v=}')
            v.sort(key=key)
            new_files.extend(v)

        return new_files
    else:
        return files


def splitjoin(s, delim, start=None, end=None):
    return delim.join(s.split(delim)[start:end])

def move_to_auto(dir, auto_dir):
    files = find('m4a', dir=dir)
    filename = lambda f: f.split('/')[-1]
    for file in files:
        move(dir + '/' + filename(file), auto_dir + '/' + filename(file))
