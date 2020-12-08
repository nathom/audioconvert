
'''
parses .cue files and splits audio
'''
import re
import os
import music_tag
import subprocess
from pathlib import Path

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
    def __init__(self, path):
        self.filepath = path
        self.parent_dir = '/'.join(self.filepath.split('/')[:-1])

        self.files = []
        self.tracklist = []

        self.album = None
        self.albumartist = None
        self.genre = None
        self.composer = None
        self.url = None
        self.date = None
        self.label = None
        self.comment = None
        self.year = None

        lines = open(self.filepath).readlines()

        for l in lines:
            l = l.strip()
            if l.startswith('REM'):
                m = re.match(r'REM (\w+) "?([\w\d-]+)"?', l).groups()
                self.set(m[0].lower(), m[1])
                continue
            elif l.startswith('PERFORMER'):
                self.albumartist = self._get_in_quotes(l)
                continue
            elif l.startswith('TITLE') and self.album is None:
                self.album = self._get_in_quotes(l)
                continue

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
                continue
        self._get_stamps()

    def split(self):
        i = 0
        print(zip(self.tracklist))
        for track in self.tracklist:
            self.tracklist[i].filepath_converted = f'{self.parent_dir}/{i+1}. {track.name}.m4a'
            self._split_file(track.filepath, self.tracklist[i].filepath_converted, track.start, track.length)
            i += 1


    def __getitem__(self, key):
        return self.get(self._format_query(key))

    def __setitem__(self, key, val):
        self.set(self._format_query(key), val)

    def __str__(self):
        tracks =  '\n'.join(list(map(str, self.tracklist)))
        return f'{self.albumartist} - {self.album}\n{tracks}'


    def get(self, key):
        if key == 'tracklist':
            tracklist = []
            stamps = []
            for file in self.files:
                tracklist.extend(file['tracklist'])
                stamps.extend(file['timestamps'])
            return list(zip(tracklist, stamps))
        elif key in ['artist', 'albumartist']:
            return self.albumartist
        elif key in ['filepath', 'filepaths']:
            return [file['filepath for file in self.files']]
        else:
            return self._info[key]

    def set(self, key, val):
        if key in ['path', 'filepath']:
            self.filepath = val
        elif key == 'album':
            self.album = val
        elif key == 'genre':
            self.genre = val
        elif key == 'albumartist':
            self.albumartist = val
        elif key == 'date':
            self.date = val
        elif key == 'year':
            self.year = val
        elif key == 'label':
            self.label = val
        elif key == 'comment':
            self.comment = val
        else:
            raise AttributeError('Invalid key')

    # TODO: add remove function
    def _split_file(self, in_file, out_file, start, length):
        print(in_file, out_file, start, length)
        command = ['ffmpeg', '-i', in_file, '-map_metadata', '-1', '-ss', str(start), '-vn', '-acodec', 'alac', '-map', '0:0', '-y', out_file]

        if length:
            command.insert(7, '-t')
            command.insert(8, str(length))

        print(command)
        with open(os.devnull, 'rb') as devnull:
            p = subprocess.Popen(command, stdin=devnull, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p_out, p_err = p.communicate()



    # input: str timestamp in format hh:mm:ss
    # output: int timestamp in seconds
    def _format_time(self, stamp):
        sl = stamp.split(':')
        mins = int(sl[0][0]) * 10 + int(sl[0][1])
        sec = int(sl[1][0]) * 10 + int(sl[1][1])
        ms = int(sl[2][0]) * 10 + int(sl[2][1])
        time = 60*mins + sec + ms / 100
        return time

    def _toint(self, s):
        return int(s[0])*10 + int(s[1])


    def _format_query(self, q):
        return ''.join(re.findall('\w', q)).lower()



    def _get_in_quotes(self, s):
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
        if self.end:
            return self.end - self.start
        else:
            return None


    def __str__(self):
        return f'{self.pos}. {self.name} ({self.timestamp}) {self.length}'
    def __len__(self):
        return self.length






# converts audio file to flac, splits into tracks
# renames and tags the new files
# input: cue dict
# output: None
"""def split_cue(cuesheet):
    for file in cuesheet:
        tracklist = file['tracklist']
        path = file['filepath']
        stamps = file['timestamps']
        ext = path.split('.')[-1]
        parent_dir = '/'.join(path.split('/')[:-1])

        # loops through titles, splits audio based on timestamp
        # adds metadata for album based on cue
        for i in range(len(tracklist)):
            start = stamps[i]

            if i is len(tracklist) - 1:
                end = None
            else:
                end = stamps[i + 1]

            title = tracklist[i]
            form_title = title.replace('/', '|')
            track_path = f'{parent_dir}/{form_title}.m4a'
            split_file(path, track_path, start, end)

            # tags new flac files
            f = music_tag.load_file(track_path)
            f.album = file['album']
            f.artist = file['artist']
            f['tracknumber = i + 1
            f['tracktitle = title

            files = []
            pathlist = Path(parent_dir).rglob(f'*front*')
            [files.append(f) for f in pathlist]
            if len(files) > 0:
                art = files[0]
                with open(art, 'rb') as img_in:
                        f['artwork'] = img_in.read()
            else:
                pass

            f.save()

        system(f'rm "{path}"')



def split_file(in_file, out_file, start, end):
    if end is None:
        length = None
        length_str = ''
    else:
        length = end - start
        length_str = f'-t {length}'

    command = f'ffmpeg -i "{in_file}" -map_metadata -1 -ss {start} {length_str} -vn -acodec alac -map 0:0 -y "{out_file}"'
    system(command)
"""

c = Cue('/Volumes/nathanbackup/Downloads/Santa Esmeralda - Another Cha-Cha 1979/Santa Esmeralda - Another Cha-Cha.cue')
print(c)
c.split()
