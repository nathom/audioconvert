from audioconvert import *
from os import listdir, remove
from shutil import rmtree
import argparse

dir = '/Volumes/nathanbackup/Downloads'
auto_folder = '/Volumes/nathanbackup/Library/Automatically Add to Music.localized'

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--split-cues', help='split large audio files based on cue', action='store_true')
args = parser.parse_args()

if args.split_cues:
    cues = get_cues(dir)
    split_cues(cues)

convert_all_alac(dir)
move_to_auto(dir, auto_folder)


