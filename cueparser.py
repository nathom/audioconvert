
'''
parses .cue files and splits audio
'''
from re import findall
from pydub import AudioSegment
from os import system
import audioconvert
import music_tag
from pathlib import Path

# takes cue filepath as input
# returns data in dict
def parse(cue):
    parent_dir = '/'.join(cue.split('/')[:-1])
    f = open(cue, 'r').read()

    in_quotes = [item[1:-1] for item in findall('"[^"]+"', f)]
    timestamps = findall('\d\d:\d\d:\d\d', f)
    artist, album = in_quotes[0], in_quotes[1]
    in_quotes.pop(0)
    in_quotes.pop(0)

    filepaths = []
    for item in in_quotes:
        if '.flac' in item or '.dsf' in item or '.ape' in item:
            filepaths.append(item)

    files = []
    indices = [in_quotes.index(file) for file in filepaths]

    indices.append(len(in_quotes))

    start = 0
    for i in range(len(filepaths)):
        titles = in_quotes[indices[i] + 1:indices[i+1]]
        curr_file = {
            'artist': artist,
            'album': album,
            'filepath': parent_dir + '/' + filepaths[i],
            'tracklist': titles,
            'timestamps': [format_time(stamp) for stamp in timestamps[start:start + len(titles)]]
        }
        start += len(titles)
        files.append(curr_file)
    return files


# takes time in hh:mm:ss and converts to seconds
def format_time(stamp):
    sl = stamp.split(':')
    mins = int(sl[0][0]) * 10 + int(sl[0][1])
    sec = int(sl[1][0]) * 10 + int(sl[1][1])
    ms = int(sl[2][0]) * 10 + int(sl[2][1])
    time = 60*mins + sec + ms / 100
    return time


def split(cuesheet):
    for file in cuesheet:
        path = file['filepath']
        # replace extension with .flac
        new_path = '.'.join(path.split('.')[:-1]) + '.flac'
        # convert the large file into a flac
        system(f"ffmpeg -i \"{path}\" \"{new_path}\"")
        parent_dir = '/'.join(path.split('/')[:-1])
        ext = 'flac'
        path = new_path

        # loops through titles, splits audio based on timestamp
        # adds metadata for album based on cue
        song = AudioSegment.from_file(path, ext)
        for i in range(len(file['tracklist'])):
            title = file['tracklist'][i]
            start = file['timestamps'][i] * 1000

            if i is len(file['tracklist']) - 1:
                end = None
            else:
                end = file['timestamps'][i + 1] * 1000

            track = song[start:end]
            form_title = title.replace('/', '|')
            track_path = f'{parent_dir}/{form_title}.{ext}'
            track.export(track_path, format=ext)

            # tags new flac files
            f = music_tag.load_file(track_path)
            f['album'] = file['album']
            f['artist'] = file['artist']
            f['tracknumber'] = i + 1
            f['tracktitle'] = title

            # adds artwork if there is a file named Front.*
            files = []
            pathlist = Path('/users/nathan/audioconvert').rglob(f'Front*')
            [files.append(f) for f in pathlist]
            if len(files) > 0:
                art = files[0]
                with open(art, 'rb') as img_in:
                        f['artwork'] = img_in.read()
            else:
                pass

            f.save()

        # removes initial large file
        system(f"rm \"path\"")


