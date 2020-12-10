
'''
parses .cue files and splits audio
'''
from collections import namedtuple
import hashlib
import io
import shutil
import PIL
from PIL import Image
_HAS_PIL = True
BICUBIC = PIL.Image.BICUBIC
import re
import os
import subprocess
import json
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover
from mutagen.id3 import PictureType

from util import find
# input: str path of .cue file
# output: dict of cue info
'''
{
'artist': str
'album': str
'filepath': str
'tracklist': list of titles
'timestamps': list of stamps in seconds; starts at 0, ends at start of last track
}
'''
# TODO: add tagging capabilities

class Cue(object):
    _mp4_keys = {
        'title': r'©nam',
        'artist': r'©ART',
        'album': r'©alb',
        'albumartist': r'aART',
        'composer': r'©day',
        'year': r'©day',
        'comment': r'©cmt',
        'description': 'desc',
        'purchase_date': 'purd',
        'grouping': r'©grp',
        'genre': r'©gen',
        'lyrics': r'©lyr',
        'encoder': r'©too',
        'copyright': 'cprt',
        'compilation': 'cpil',
        'cover': 'covr',
        'tracknumber': 'trkn',
        'discnumber': 'disk'
    }
    def __init__(self, path):
        self.filepath = path
        self.parent_dir = '/'.join(self.filepath.split('/')[:-1])

        self.tracklist = []

        self.images = []
        for path in find('png', 'jpg', 'jpeg', dir=self.parent_dir):
            self._add_image(path)

        self.album = None
        self.albumartist = None
        self.comment = None
        self.composer = None
        self.copyright = None
        self.disctotal = None
        self.date = None
        self.genre = None
        self.isrc = None
        self.label = None
        self.performer = None
        self.url = None
        self.upc = None
        self.year = None
        self.discid = None


        lines = open(self.filepath).readlines()

        for l in lines:
            l = l.strip()
            if l.startswith('REM'):
                m = re.match(r'REM (\w+) "?([\w\d-]+)"?', l).groups()
                self.set(m[0].lower(), m[1])
            elif l.startswith('PERFORMER') and self.albumartist is None:
                self.albumartist = self._get_in_quotes(l)
            elif l.startswith('TITLE') and self.album is None:
                self.album = self._get_in_quotes(l)

            elif l.startswith('FILE'):
                curr_file = self.parent_dir + '/' + self._get_in_quotes(l)

            elif l.startswith('TRACK'):
                tracknum = self._toint(re.findall('\d\d', l)[0])
                self.tracklist.append(Track(pos=(1, tracknum)))
            elif l.startswith('TITLE'):
                self.tracklist[-1].name = self._get_in_quotes(l)
                self.tracklist[-1].album = self.album
                self.tracklist[-1].filepath = curr_file
            elif l.startswith('INDEX'):
                stamp = re.findall('\d\d:\d\d:\d\d', l)[0]
                self.tracklist[-1].timestamp = self._format_time(stamp)

            elif l.startswith('PERFORMER'):
                artist = re.match(f'PERFORMER "([^"]+)"', l).groups()
                self.tracklist[-1].artist = artist[0]
            else:
                raise NotImplementedError(f'"{l.split(" ")[0]}" tag not implemented')
        self._get_stamps()

    def split(self):
        i = 0
        for track in self.tracklist:
            conv_path = self.tracklist[i].filepath_converted = f'{self.parent_dir}/{i+1}. {track.name}.m4a'
            if not os.path.exists(conv_path):
                print(f'Splitting {track.name}')
                self._split_file(track.filepath, conv_path, track.start, track.length)
            else:
                print(f'{track.name} already converted.')
            i += 1
        self.tag_files()

    @property
    def totaltracks(self):
        return len(self.tracklist)

    @property
    def totaldiscs(self):
        discs = [track.pos[0] for track in self.tracklist]
        return max(discs)

    @property
    def artwork(self):
        return self.images

    @artwork.setter
    def artwork(self, val):
        self.images = []
        self._add_image(val)



    @property
    def copyright(self):
        if self.label is not None and '©' not in self.label:
            return f'© {self.label}'
        elif self.label is not None:
            return self.label

    @copyright.setter
    def copyright(self, val):
        self.label = val




    def tag_files(self):
        info = {}
        for k, v in self.__dict__.items():
            if k in ['genre', 'albumartist', 'tracktotal', 'disctotal', 'album', 'copyright', 'url', 'year'] and v is not None:
                info[k] = v
            if k == 'label':
                info['copyright'] = self.copyright

        # TODO: properly implement disc numbers
        tags = [{
            'title': track.name,
            'artist': track.artist,
            'tracknumber': [(track.pos[1], self.totaltracks)],
            'discnumber': [(track.pos[0], self.totaldiscs)],
            **info
        } for track in self.tracklist]

        i = 0
        for track in self.tracklist:
            audio = MP4(track.filepath_converted)
            for k, v in tags[i].items():
                audio[Cue._mp4_keys[k]] = v
            i += 1
            audio['covr'] = self.images
            audio.save()


    def get(self, key):
        if key in possible_keys:
            return self.__dict__[key]
        else:
            raise AttributeError('Invalid key')


    def set(self, key, val):
        possible_keys = [k for k,v in self.__dict__.items()]
        if key in possible_keys:
            self.__dict__[key] = val
        else:
            raise AttributeError('Invalid key')

    def _add_image(self, path):
        ext = lambda p: p.split('.')[-1]
        if ext(path) in ['jpeg', 'jpg']:
            fmt = MP4Cover.FORMAT_JPEG
        else:
            fmt = MP4Cover.FORMAT_PNG

        f = open(path, 'rb')
        self.images.append(MP4Cover(f.read(), imageformat=fmt))


    def _split_file(self, in_file: str, out_file: str, start: float, length: float) -> None:
        command = ['ffmpeg', '-i', in_file, '-map_metadata', '-1', '-ss', str(start), '-vn', '-acodec', 'alac', '-map', '0:0', '-y', out_file]

        if length:
            command.insert(7, '-t')
            command.insert(8, str(length))

        with open(os.devnull, 'rb') as devnull:
            p = subprocess.Popen(command, stdin=devnull, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p_out, p_err = p.communicate()



    # input: str timestamp in format hh:mm:ss
    # output: int timestamp in seconds
    def _format_time(self, stamp: str) -> int:
        sl = stamp.split(':')
        mins = int(sl[0][0]) * 10 + int(sl[0][1])
        sec = int(sl[1][0]) * 10 + int(sl[1][1])
        ms = int(sl[2][0]) * 10 + int(sl[2][1])
        time = 60*mins + sec + ms / 100
        return time

    def _toint(self, s: str) -> int:
        return int(s[0])*10 + int(s[1])


    def _format_query(self, q: str) -> str:
        return ''.join(re.findall('\w', q)).lower()



    def _get_in_quotes(self, s: str) -> str:
        match = re.findall('"([^"]+)"', s)[0]
        return match

    def _get_stamps(self):
        stamps = [track.timestamp for track in self.tracklist]
        stamps_shifted = stamps.copy()
        stamps_shifted.pop(0)
        stamps_shifted.append(None)
        pairs = list(zip(stamps, stamps_shifted))
        pars = [(0.0, None) if t == (0.0, 0.0) else t for t in pairs]
        i = 0
        for track in self.tracklist:
            track.start = pairs[i][0]
            track.end = pairs[i][1]
            i += 1

    def __getitem__(self, key):
        return self.get(self._format_query(key))

    def __setitem__(self, key, val):
        self.set(self._format_query(key), val)

    def __str__(self):
        d = self.__dict__.copy()
        d['tracklist'] = list(map(str, d['tracklist']))
        j = json.dumps(d, indent=3)
        return j





class Track(object):
    def __init__(self, **kwargs):
        self.filepath = kwargs['filepath'] if 'filepath' in kwargs else None
        self.filepath_converted = kwargs['filepath_converted'] if 'filepath_converted' in kwargs else None

        self.name = kwargs['name'] if 'name' in kwargs else None
        self.artist = kwargs['artist'] if 'artist' in kwargs else None
        self.album = kwargs['album'] if 'album' in kwargs else None
        self.pos = kwargs['pos'] if 'pos' in kwargs else None

        self.start = kwargs['start'] if 'start' in kwargs else None
        self.end = kwargs['end'] if 'end' in kwargs else None

    @property
    def length(self):
        if self.end is not None and self.start is not None:
            return self.end - self.start
        else:
            return None


    def __str__(self):
        return f'{self.pos}. {self.name} ({self.start}:{self.end} = {self.length})'
    def __len__(self):
        return self.length


c = Cue('/Volumes/nathanbackup/Santa Esmeralda - Another Cha-Cha 1979/Santa Esmeralda - Another Cha-Cha.cue')
c.split()
