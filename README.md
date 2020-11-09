# audioconvert

**A scrappy library that tags and converts audio files to ALAC m4a. Written for those that use the macOS music app.**

### Quick start

1. Clone the repository

   ```bash
   git clone https://github.com/pynathanthomas/audioconvert.git
   ```

2. Install dependencies

   ```bash
   cd audioconvert; pip3 install -r requirements.txt
   ```

3. Open `convert_dir.py` and replace the highlighted line with your path to Automatically Add to Music.localized.

   <img src="demo/demo3.png" style="zoom:25%;" />

4. Now you can either run

   ```bash
   python3 ~/audioconvert/convert_dir.py /directory/to/convert
   ```

   or just

   ```bash
   python3 ~/audioconvert/convert_dir.py
   ```

   for the interactive mode.

5. Now the program will split cue files, convert everything to ALAC and sort it out in the Music app!

### Usage of converter

```python
import audioconvert as a

dir = '/path/to/unconverted'

# finds cue files and parses them
cues = a.get_cues(in_dir)
# splits files based on cue
a.split_cues(cues)

# this will convert all .flac, .wav, and .wv files to ALAC
a.convert_all_alac(dir)

auto_folder = '/path/to/Automatically Add to Music.localized'
a.move_to_auto(out_dir, auto_folder)
```

This does not delete any files, so you may have to use `os.remove` on all the flacs after you're done.

### Usage of tagger

This scrapes [discogs](https://www.discogs.com/) for data and tags the files automatically.

**Interactive mode** in terminal

```bash
python3 tagger.py '/path/to/album/directory'
```

This will:

1. Search the name of the directory in discogs and get the release
2. Check if the names of the tracks match the names of the files

<img src="demo/demo1.png" style="zoom: 25%;" />

3. Hit enter to set the tags, type in the album name to search again, or type "n" to get the next result

**As a module**

```python
import tagger

path = '/path/to/abbey_road'
query = 'abbey road'
# searches query on discogs
tags = tagger.search_tags(query)

# check if the file names match, display the arrows and stuff
# optional
tagger.try_match(tags, path)

# associates a filepath with each track in tag dict
matched_tags, not_matched = tagger.match_tags(tags, path)

# set to True if you don't want disc numbers (A1, A2...) and just track numbers (1, 2...)
no_disc = False

# sets the tags
# will only work with matched_tags
tagger.set_tags(matched_tags, no_disc)
```
