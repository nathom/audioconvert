import os
from time import sleep
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
def convert_alac(path):
    ext = path.split('.')[-1]
    outfile = path.replace('.' + ext, '.m4a')

    with open(os.devnull, 'rb') as devnull:
        command = get_conversion_command(path, outfile)
        p = subprocess.Popen(command, stdin=devnull, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    p_out, p_err = p.communicate()


def get_conversion_command(in_path, out_path) -> list:
    conversion_command = [
        'ffmpeg',
        '-loglevel',
        'panic',
        '-i',
        in_path,
        '-vn',
        '-c:v',
        'copy',
        '-c:a',
        'alac',
        '-y',
        out_path
    ]
    return conversion_command



# finds and parses all cue files in a dir
# input str: path to directory
# output dict: dict of cue info
def get_cues(dir):
    cues = [cueparser.Cue(c) for c in util.find('cue', dir=dir)]
    return cues

def splitjoin(s, delim, start=None, end=None):
    return delim.join(s.split(delim)[start:end])

def split_cues(cues, remove_flac=False):
    for cue in cues:
        cue.split(remove_flac=remove_flac)

def convert_all_alac(dir, threads=1):
    paths = util.find('flac', 'wav', 'wv', 'dsf', dir=dir)
    if len(paths) == 0:
        print(f'{dir} is empty.')
        sys.exit()

    if threads == 1:
        print(f'\nConverting files in {dir}...\n')
        for path in tqdm(paths, unit='track'):
            convert_alac(path)
    else:
        # add 30 processes
        # while there are paths left
        # if a process is done, add another

        def _get_finished_proc(processes):
            counter = 0
            for p in processes:
                if p.poll() is not None:
                    p.kill()
                    counter += 1
            return counter

        def _get_open_proc(processes):
            counter = 0
            for p in processes:
                if p.poll() is None:
                    counter += 1
            return counter

        with open(os.devnull, 'rb') as devnull:
            processes = []
            total_paths = len(paths)
            # while processes are not finished
            bar = tqdm(total=total_paths, unit='track')
            # p_count = 0
            prev = 0
            while len(paths) > 0:
                # keep a maximum of `thread` processes active at once
                while (o := _get_open_proc(processes)) >= threads:
                    # print(f'sleeping, {o} open proc.')
                    sleep(0.5)


                # add process
                path = paths.pop()
                command = get_conversion_command(path,
                                                 fmt_alac_path(path))
                p = subprocess.Popen(command, stdin=devnull,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
                processes.append(p)
                # p_count += 1
                # print(f'open files: {p_count=}')

                finished = _get_finished_proc(processes)
                bar.update(finished - prev)
                prev = finished
                # print(f'open: {_get_open_proc(processes)}, closed: {_get_finished_proc(processes)}')

            for p in processes:
                p.wait()
                finished = _get_finished_proc(processes)
                bar.update(prev - finished)
                prev = finished

            bar.close()








def fmt_alac_path(path):
    ext = path.split('.')[-1]
    outfile = path.replace('.' + ext, '.m4a')
    return outfile









