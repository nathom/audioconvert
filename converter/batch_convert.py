import os
import sys
import subprocess
from shutil import move
from pathlib import Path
from tqdm import tqdm

from . import cueparser
from . import util
# converts flac to alac
# input: str path of flac, str path of output directory
# output: None
def convert_alac(path, delete_original=True):
    ext = path.split('.')[-1]
    outfile = path.replace('.' + ext, '.m4a')
    conversion_command = [
        'ffmpeg',
        '-loglevel',
        'panic',
        '-i',
        path,
        '-vn',
        '-c:v',
        'copy',
        '-c:a',
        'alac',
        '-y',
        outfile
    ]

    with open(os.devnull, 'rb') as devnull:
        p = subprocess.Popen(conversion_command, stdin=devnull, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    p_out, p_err = p.communicate()




# finds and parses all cue files in a dir
# input str: path to directory
# output dict: dict of cue info
def get_cues(dir):
    cues = [cueparser.Cue(c) for c in util.find('cue', dir=dir)]
    return cues

def splitjoin(s, delim, start=None, end=None):
    return delim.join(s.split(delim)[start:end])

def split_cues(cues):
    for cue in cues:
        cue.split()

def convert_all_alac(dir):
    paths = util.find('flac', 'wav', 'wv', 'dsf', dir=dir)
    if len(paths) == 0:
        print(f'{dir} is empty.')
        sys.exit()

    print(f'\nConverting files in {dir}...\n')
    for path in tqdm(paths, unit='track'):
        convert_alac(path)





