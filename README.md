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

3. Open `convert_dir.py` and replace `dir` and `auto_folder` with your path to Automatically Add to Music.localized.

   <img src="demo/demo1.png" style="zoom:25%;" />

4. Now you can run

   ```bash
   python3 ~/audioconvert/convert_dir.py
   ```

   to convert and move all the tracks.

5. Now the program will split cue files, convert everything to ALAC and sort it out in the Music app!



## Using `cueparser.py`

This is the machinery behind processing .cue files. It assumes there is artwork in the parent directory and loads it.

```python
from cueparser import Cue
my_cue = Cue('/path/to/cue/file.cue')

# to change attributes, use like a dict
my_cue['artist'] = 'New Artist'
my_cue['tracklist'][0]['name'] = 'The first track'

# this will split the large files and tag them
# it converts to ALAC by default
my_cue.split()
```

