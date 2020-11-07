from os import system, listdir
import audio_metadata
from pathlib import Path
from re import findall
from pydub import AudioSegment
from glob import glob
from time import sleep
from pyunpack import Archive
from requests import get
from bs4 import BeautifulSoup

import tagger
import cueparser



# input - flac
# creates alac in autoAdd
def convertAlac(path, out_dir, tags=0):
    filename = path.split('/')[-1].replace('.flac', '.m4a')
    try:
        artist, album = tags['artist'][0], tags['album'][0]
        outfile = f'{out_dir}/{artist}/{album}'
        system(f'mkdir -p "{outfile}"')
        outfile = f'{outfile}/{filename}'
    except:
        outfile = f'{out_dir}/{filename}'

    # system(f'ffmpeg -i "{path}" -map_metadata -1 -vn -acodec alac -ar {samplerate} -sample_fmt {bitdepth} -map 0:0 -y "{outfile}"')
    system(f'ffmpeg -i "{path}" -c:v copy -c:a alac -y "{outfile}"')


def moveToAuto(search_path):
    pathlist = find('m4a', search_path)
    for path in pathlist:
        filename = path.split('/')[-1]
        system(f'mv "{path}" "/Volumes/nathanbackup/Library/Automatically Add to Music.localized/{filename}"')


# takes cue dict as input
# moves converted alac to out_dir
def convertdsf(cue):
    for f in cue:
        artist = f['artist']
        album = f['album']
        dsf_in = f['filepath']
        parent_dir = '/'.join(f['filepath'].split('/')[:-1])
        for i in range(len(f['tracklist'])):
            start_time = f['timestamps'][i]
            title = f['tracklist'][i]
            m4a_out = f'{parent_dir}/{title}.m4a'
            try:
                duration_from_start_time = '-t ' + str(f['timestamps'][i + 1] - f['timestamps'][i])
            except IndexError:
                duration_from_start_time = ''


            command = f'ffmpeg -i "{dsf_in}" -map_metadata -1 -ss {start_time} {duration_from_start_time} -vn -acodec alac -ar 192000 -sample_fmt s32p -map 0:0 -y "{m4a_out}"'
            #print(command)
            #system(command)

    path = '/'.join(cue[0]['filepath'].split('/')[:-1])
    filename = path.split('/')[-1]
    query = ' '.join(findall('\w+', filename))
    tags = tagger.searchTags(query)
    tagger.tryMatch(tags, path)
    matched_tags = tagger.matchTags(tags, path)
    tagger.setTags(matched_tags)


def convertWav(dir):
    wav_list = find('wav', dir) + find('wv', dir)
    for path in wav_list:
        newpath = path.replace('.wav', '.m4a')
        system(f'ffmpeg -i "{path}" -c:v copy -c:a alac -y "{newpath}"')

def find(ext, dir):
    pathlist = Path(dir).rglob(f'*.{ext}')
    files = []
    for path in pathlist:
        path = str(path)
        files.append(path)
    return files

# converts all flacs in dir to alac
# moves to music

if __name__ == '__main__':

    dir = '/Volumes/nathanbackup/Downloads'
    out_dir = '/Volumes/nathanbackup/Music/Converted'
    autoAdd = '/Volumes/nathanbackup/Library/Automatically Add to Music.localized'
    musicDir = '/Volumes/nathanbackup/Music'
    '''
    # find wav files and convert to m4a
    convertWav(dir)
    cues = [cueparser.parse(c) for c in find('cue', dir)]
    for cue in cues:
        cueparser.split(cue)

    moveToAuto(dir)
    flaclist = [audio_metadata.load(path) for path in find('flac')]
    for flac in flaclist:
        path, tags = flac['filepath'], flac['tags']
        convertAlac(path, tags)
    '''
    moveToAuto(out_dir)

    for d in listdir(dir):
        system(f'mv "{dir}/{d}" "{musicDir}/{d}"')



