# audioconvert

Very scrappy code that converts .flac files to ALAC .m4a files and tags music. Made for myself, use at your own discretion.

### Usage of batchConvert

```python
from audioconvert import Convert
c = Convert('/path/to/flacs', '/path/to/move/converted/files')

# converts everything automatically
c.batchConvert()
```

### Usage of tagger

**Interactive mode**

Type in terminal

```
python3 tagger.py /path/to/album
```

**As module**

```python
import tagger

album_path = '/path/to/album'

# returns dict with results from discogs.com
tags = tagger.searchTags('abbey road', result_item=0)
# you can optionally check if the file names match the names from discogs
tryMatch(tags, album_path)

# if you're satisfied with the tags
# this will return a dict with tags containing the matched path
# and the number of files not matched
matched_tags, not_matched = matchTags(tags, album_path)

# if you don't want disc numbers (A1, A2.. D3, D4) and just track numbers (1, 2, 3...)
no_disc = True

# this sets the tags
# it will only work with matched tags
setTags(matched_tags, no_disc)
```

