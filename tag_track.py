import spotify
import tagger
from re import findall, sub
from os import listdir

# formats the file name for searching
def format(track):
    track = track.replace('.m4a', '')
    track = track.replace(' - ', ' ')
    track = sub('\([^\(|^\)]+\)', '', track)
    track = sub('\[[^\[|^\]]+\]', '', track)
    track = sub('[fF]eat[\s\S]+', '', track)
    track = sub('·\ ([\w]+\ )+', '', track)

    return track

