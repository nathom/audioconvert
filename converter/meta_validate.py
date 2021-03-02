from pathlib import Path
import os
from tqdm import tqdm

import music_tag


def artwork(path1, path2):
    if not (os.path.exists(path1) and os.path.exists(path2)):
        return

    f1 = music_tag.load_file(path1)
    f2 = music_tag.load_file(path2)

    try:
        f2["artwork"]
    except KeyError:
        f2["artwork"] = f1["artwork"]

    f2.save()


def find(*args, dir):
    files = []
    for ext in args:
        pathlist = Path(dir).rglob(f"*.{ext}")
        for path in pathlist:
            path = str(path)
            files.append(path)
    return files


def validate_dir(downloads_path):
    tracks = find("m4a", dir=downloads_path)
    tracks = [s.replace(".m4a", "") for s in tracks]

    for track in tqdm(tracks, unit="files"):
        artwork(f"{track}.flac", f"{track}.m4a")
