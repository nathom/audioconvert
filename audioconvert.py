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

class Convert():
    def __init__(self, in_dir='/Volumes/nathanbackup/Downloads', out_dir='/Volumes/nathanbackup/Music/Converted'):
        self.dir = in_dir
        self.outDir = out_dir
        self.autoAdd = '/Volumes/nathanbackup/Library/Automatically Add to Music.localized'
        self.musicDir = '/Volumes/nathanbackup/Music'


    # converts all flacs in self.dir to alac
    # moves to music
    def batchConvert(self):

        self.convertWav()
        self.moveToMusic()
        flaclist = self.findFlacs()
        for flac in flaclist:
            path, tags = flac['filepath'], flac['tags']
            print(f'Converting {path}...')
            self.convertAlac(path, tags)

        #self.convertdsf()
        self.moveToAuto(self.outDir)

        for d in listdir(self.dir):
            system(f'mv "{self.dir}/{d}" "{self.musicDir}/{d}"')


    # input - flac
    # creates alac in self.autoAdd
    def convertAlac(self, path, tags=0):
        filename = path.split('/')[-1].replace('.flac', '.m4a')
        try:
            artist, album = tags['artist'][0], tags['album'][0]
            outfile = f'{self.outDir}/{artist}/{album}'
            system(f'mkdir -p "{outfile}"')
            outfile = f'{outfile}/{filename}'
        except:
            outfile = f'{self.outDir}/{filename}'
        #system(f'ffmpeg -i "{path}" -map_metadata -1 -vn -acodec alac -ar {samplerate} -sample_fmt {bitdepth} -map 0:0 -y "{outfile}"')
        system(f'ffmpeg -i "{path}" -c:v copy -c:a alac -y "{outfile}"')
        '''
        if not isCue(path):
            system(f'mv "{outfile}" "{self.autoAdd}/{filename}"')
        '''


    # finds flacs, returns their metadata
    def findFlacs(self):
        pathlist = Path(self.dir).rglob('*.flac')
        flaclist = []
        for path in pathlist:
            path_in_str = str(path)
            meta = audio_metadata.load(path)
            flaclist.append(meta)
        return flaclist


    # takes \d\d:\d\d:\d\d and converts to seconds
    def formatTime(self, stamp):
        sl = stamp.split(':')
        mins = int(sl[0][0]) * 10 + int(sl[0][1])
        sec = int(sl[1][0]) * 10 + int(sl[1][1])
        ms = int(sl[2][0]) * 10 + int(sl[2][1])
        time = 60*mins + sec + ms / 100
        return time


    # takes cue file as input
    # returns data in dict
    def getInfoFromCue(self, cue):
        parent_dir = '/'.join(cue.split('/')[:-1])
        f = open(cue, 'r').read()

        in_quotes = [item[1:-1] for item in findall('"[^"]+"', f)]
        timestamps = findall('\d\d:\d\d:\d\d', f)
        artist, album = in_quotes[0], in_quotes[1]
        in_quotes.pop(0)
        in_quotes.pop(0)
        filepaths = []
        for item in in_quotes:
            if '.flac' in item or '.dsf' in item:
                filepaths.append(item)
        #print(filepaths)
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
                'timestamps': [self.formatTime(stamp) for stamp in timestamps[start:start + len(titles)]]
            }
            start += len(titles)
            files.append(curr_file)
        return files


    # opens all compressed files in self.dir
    def openZips(self):
        extensions = ('zip', '7z', 'rar', 'tar')
        all_files = []
        for ext in extensions:
            pathlist = Path(self.dir).rglob(f'*.{ext}')
            for path in pathlist:
                path_in_str = str(path)
                all_files.append(path_in_str)

        for file in all_files:
            system(f'open "{file}"')


    # moves m4a files in self.dir to music
    def moveToMusic(self):
        ext = 'm4a'
        pathlist = Path(self.dir).rglob(f'*.{ext}')
        for path in pathlist:
            path_in_str = str(path)
            system(f'osascript -e \'tell application \"Music\" to add \"{path_in_str}\"\'')
            system(f'rm "{path_in_str}"')


    def moveToAuto(self, search_path):
        ext = 'm4a'
        pathlist = Path(search_path).rglob(f'*.{ext}')
        for path in pathlist:
            path = str(path)
            filename = path.split('/')[-1]
            system(f'mv "{path}" "/Volumes/nathanbackup/Library/Automatically Add to Music.localized/{filename}"')


    # takes dsf as input
    # moves converted alac to self.outDir
    def convertdsf(self, cue):
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


    def findCues(self):
        pathlist = Path(self.dir).rglob('*.cue')
        cues = []
        for path in pathlist:
            path = str(path)
            cues.extend(self.getInfoFromCue(path))
        return cues

    def findWav(self):
        pathlist = Path(self.dir).rglob('*.wav')
        wavs = []
        for path in pathlist:
            path = str(path)
            wavs.append(path)

        pathlist = Path(self.dir).rglob('*.wv')
        for path in pathlist:
            path = str(path)
            wavs.append(path)
        return wavs

    def convertWav(self):
        flaclist = self.findWav()
        for path in flaclist:
            newpath = path.replace('.wav', '.m4a')
            system(f'ffmpeg -i "{path}" -c:v copy -c:a alac -y "{newpath}"')

