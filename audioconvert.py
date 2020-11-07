from os import system, listdir
import audio_metadata
from pathlib import Path

import tagger
import cueparser


# converts flac to alac
# input: str path of flac, str path of output directory
# output: None
def convert_alac(path, out_dir):
    ext = path.split('.')[-1]
    filename = path.split('/')[-1]
    outfile = filename.replace('.' + ext, '.m4a')

    # system(f'ffmpeg -i "{path}" -map_metadata -1 -vn -acodec alac -ar {samplerate} -sample_fmt {bitdepth} -map 0:0 -y "{outfile}"')
    system(f'ffmpeg -i "{path}" -c:v copy -c:a alac -y "{out_dir}/{outfile}"')


# moves all .m4a files to Automatically Add to Music Folder
# input: str path to find .m4a files in
# output: None
def move_to_auto(search_path, auto_path):
    pathlist = find('m4a', search_path)
    for path in pathlist:
        filename = path.split('/')[-1]
        system(f'mv "{path}" "{auto_path}/{filename}"')


# WORK IN PROGRESS
# converts dsf files into alac
# input dict: cue info
# output None
def convert_dsf(cue):
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


def convert_wav(dir, out_dir):
    wav_list = find('wav', dir) + find('wv', dir)
    for path in wav_list:
        filename = path.split('/')[-1].replace('.wav', '.m4a').replace('.wv', '.m4a')
        system(f'ffmpeg -i "{path}" -c:v copy -c:a alac -y "{out_dir}/{filename}"')

# finds files with a specified extension
# input str: extension to search for, directory to search in
# output list: files with specified extension
def find(ext, dir):
    pathlist = Path(dir).rglob(f'*.{ext}')
    files = []
    for path in pathlist:
        path = str(path)
        files.append(path)
    return files

# finds and parses all cue files in a dir
# input str: path to directory
# output dict: dict of cue info
def get_cues(dir):
    cues = [cueparser.parse(c) for c in find('cue', dir)]
    return cues

def split_cues(cues):
    for cue in cues:
        cueparser.split(cue)

def convert_all_alac(dir, out_dir):
    paths = find('flac', dir)
    for path in paths:
        convert_alac(path, out_dir)




if __name__ == '__main__':
    dir = '/Volumes/nathanbackup/Downloads'
    out_dir = '/Volumes/nathanbackup/Music/Converted'
    auto_folder = '/Volumes/nathanbackup/Library/Automatically Add to Music.localized'
    music_dir = '/Volumes/nathanbackup/Music'
    convert_wav(dir, out_dir)

    cues = get_cues(dir)
    split_cues(cues)

    move_to_auto(out_dir, auto_folder)

    for d in listdir(dir):
        system(f'mv "{dir}/{d}" "{music_dir}/{d}"')



