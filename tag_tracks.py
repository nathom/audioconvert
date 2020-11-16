import spotify
import tagger
from re import findall, sub
from os import listdir
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('path' , help='path to playlist directory')
parser.add_argument('pattern', help='e.g. "Ric Flair Drip - Offset.m4a" would have the pattern "$track - $artist.m4a"')
args = parser.parse_args()

ext = lambda path: path.split('.')[-1]
path = args.path
parent_dir = '/'.join(path.split('/')[:-1])
files = listdir(path)
pattern = args.pattern

info_list = []
for file in files:
    if ext(file) == 'jpg':
        continue

    info = tagger.parse_filenames(pattern, file)
    r = spotify.search_track(tagger.format(info['track'] + ' ' + info['artist']))
    if r:
        r['path'] = f'{parent_dir}/{file}'
        tagger.set_track_tags(r)
    else:
        print(file, ' not found.')
