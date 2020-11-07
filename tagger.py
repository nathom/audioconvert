from requests import get
from bs4 import BeautifulSoup
from re import findall
import json
import music_tag
from os import listdir, rename, system
from sys import argv
from string import ascii_uppercase
from html import unescape
from progress.bar import IncrementalBar

# param: query
# return: dict tags
# searches discogs releases for query
# returns first result by default
def searchTags(query, result_item=0):
        query_formatted = query.replace(' ', '+')
        base_url = 'https://www.discogs.com'
        url = f'https://www.discogs.com/search/?q={query_formatted}&type=release'
        r = get(url)
        try:
            soup = BeautifulSoup(r.content, features='lxml')
            links = soup.findAll("a", {"class": "search_result_title"})
            result = str(links[result_item])
            page = base_url + findall('href="[^"]+"', result)[0][6:-1]
            r = get(page)
            r.encoding = 'utf-8'
            #print(r.content)

            # gets the included json on the top of discogs page source
            start = '<script type="application\/ld\+json" id="release_schema">'
            end = '<\/script>'
            matches = findall(f'{start}[^<]+{end}', r.text)
            plain_text = matches[0][len(start):-len(end)]
            soup = BeautifulSoup(r.text, features='lxml')

            artists = []
            artists_found = soup.find_all('td', {'class': 'tracklist_track_artists'})
            for artist in artists_found:
                a = [s[2:-4] for s in findall('">[^<]+</a>', str(artist))]
                artists.append(a)


            info = json.loads(plain_text)
            for track in info['tracks']:
                track['name'] = unescape(track['name'])
            #print(info)
        except:
            # if there are no results
            return 0

        #print(info)
        release = info['releaseOf']
        tracks = info['tracks']
        labels = [label['name'] for label in info['recordLabel']]
        alph = list(ascii_uppercase)
        track_pos = [(alph.index(pos[1:-1][0]) + 1, int(pos[1:-1][1:])) for pos in findall('"[A-Z]\d\d?"', r.text)]
        #print(track_pos)

        format = lambda strTime: (int(strTime[2]) * 3600 + int(strTime[4:6].replace('0', '', 1)) * 60 + int(strTime[7:9].replace('0', '', 1)))

        if len(track_pos) == len(tracks) and len(artists) == len(tracks):
            tracklist = [{'name': tracks[i]['name'].replace('&amp;', '&'), 'duration': format(tracks[i]['duration']), 'pos':track_pos[i], 'artists': artists[i]} for i in range(len(tracks))]
        elif len(track_pos) == len(tracks):
            tracklist = [{'name': tracks[i]['name'].replace('&amp;', '&'), 'duration': format(tracks[i]['duration']), 'pos':track_pos[i]} for i in range(len(tracks))]
        else:
            tracklist = [{'name': tracks[i]['name'].replace('&amp;', '&'), 'duration': format(tracks[i]['duration'])} for i in range(len(tracks))]
        if len(info['genre']) > 3:
            genres = info['genre'][:3]
        else:
            genres = info['genre']

        tags = {
            'album' : release['name'], # String
            'artist': [artist['name'] for artist in release['byArtist']], # list
            'numtracks': release['numTracks'], # int
            'tracklist' : tracklist, #list of dicts -> {name:String, duration:int secs, (optional)pos: (int disc, track)}
            'image' : info['image'], #url
            'genre' : genres, #list of genres
            'year' : str(release['datePublished']), #int
            'label': labels
        }
        return tags

# sets the tags
# param: tag dict with filepath
# return: None
def setTags(tags, no_disc):
    nd = no_disc
    if not nd:
        try:
            tags['tracklist'][-1]['pos']
        except KeyError:
            nd = True

    genre_str = ''
    for g in tags['genre']:
        genre_str += (g + ', ' * ( len(tags['genre']) > 1 and g != tags['genre'][-1] ))

    # system('clear')
    bar = IncrementalBar('Setting tags...', max = len(tags['tracklist']))

    for track in tags['tracklist']:
        system('clear')
        bar.next()
        index = tags['tracklist'].index(track)
        try:
            f = music_tag.load_file(track['path'])
            f['album'] = tags['album']
            try:
                f['artist'] = track['artists']
            except KeyError:
                f['artist'] = tags['artist']
            f['totaltracks'] = tags['numtracks']
            f['tracktitle'] = track['name']
            f['year'] = tags['year']

            if nd:
                f['tracknumber'] = index + 1

            else:
                f['discnumber'] = track['pos'][0]
                f['tracknumber'] = track['pos'][1]

            f['genre'] = genre_str
            album = tags['album']
            title = track['name']

            art = get(tags['image'])
            img_path = f'/Volumes/nathanbackup/Music/Artwork/{album}.jpg'
            open(img_path, 'wb').write(art.content)

            with open(img_path, 'rb') as img_in:
                f['artwork'] = img_in.read()

            f.save()

        except KeyError:
            pass
    bar.finish()


# matches tags with filepaths
# param tags: dict tags
# param dir_path: path of directory to search
# return: dict tags with 'path' key
# return: list of files not matched
def matchTags(mod_tags, dir_path):
    getFilename = lambda path: path.split('/')[-1]
    files = listdir(dir_path)
    ext = lambda path: path.split('.')[-1]
    for f in files:
        if ext(f) != 'flac' and ext(f) != 'm4a':
            files.remove(f)

    files.sort()
    sorted_paths = []
    #print(files)
    for track in mod_tags['tracklist']:
        for filename in files:
            keywords = findall("(?i)\w+[']?\w", track['name'])
            is_match = True
            for word in keywords:
                if matches(word, filename):
                    pass
                else:
                    is_match = False
                    break
            if is_match:
                try:
                    mod_tags['tracklist'][mod_tags['tracklist'].index(track)]['path']
                except KeyError:
                    mod_tags['tracklist'][mod_tags['tracklist'].index(track)]['path'] = f'{dir_path}/{filename}'
                    pass

    for track in mod_tags['tracklist']:
        try:
            files.remove(getFilename(track['path']))
        except KeyError:
            pass

    return mod_tags, files

# Utilities

# makes text red or green
# param color: 0 for red, 1 for green
# return colored text
def colorize(text, color):
    if color != '':
        COLOR = {
        "GREEN": "\033[92m",
        "RED": "\033[91m",
        "ENDC": "\033[0m",
        }
        return color * COLOR['GREEN'] + (1 - color) * COLOR['RED'] + text + COLOR['ENDC']
    else:
        return text

# checks if word is in name
# every word in the discogs track name must be in each file name
# case insensitive
# ignores single quotes
def matches(word, name):
    adj_word, adj_name = word.replace("'", ''), name.replace("'", '')
    r = findall(f'(?i){adj_word}', adj_name)
    if r != []:
        return True
    else:
        return False

# displays which items have been matched, which have not
def tryMatch(tags, path):
    getFilename = lambda path: path.split('/')[-1]
    matched_tags, not_matched = matchTags(tags, path)
    not_found = 0
    album = matched_tags['album']
    artist = ''
    for g in matched_tags['artist']:
        artist += (g + ', ' * ( len(matched_tags['artist']) > 1 and g != matched_tags['artist'][-1] ))

    print(f'{artist} - {album}', end='\n\n')
    for track in matched_tags['tracklist']:
        try:
            name = colorize(track['name'], 1) + ' \u2192 '
            path = getFilename(track['path'])
            print(name, end='')
            print(path)
        except KeyError:
            name = colorize(track['name'], 1) + ' \u2192 '
            print(name, end='')
            print(colorize('Not found', 0))
            not_found += 1
            pass

    print(f'{len(not_matched)} not matched.')


# arg: path of directory
# searches directory name as query
# asks for manual search
# sets tags

if __name__ == "__main__":
    path = argv[1]
    try:
        no_disc = (argv[2] == '-n')
    except:
        no_disc = False

    getFilename = lambda path: path.split('/')[-1]

    filename = getFilename(path)
    query = ' '.join(findall('\w+', filename))
    history = query
    tags = searchTags(query)
    if tags != 0:
        tryMatch(tags, path)
    else:
        print('Matches could not automatically be found.')
        pass
    item = 0
    unsatisfied = True
    while unsatisfied:
        query = input('Press enter to continue. Type \'n\' to get next result. Type anything else to manual search.\n')
        if query == 'n':
            item += 1
            tags = searchTags(history, result_item=item)
            if tags != 0:
                tryMatch(tags, path)
            else:
                print('Matches could not automatically be found.')
                pass
        elif query != '':
            tags = searchTags(query)

            if tags != 0:
                tryMatch(tags, path)
            else:
                print('Matches could not automatically be found.')
                pass
        else:
            matched_tags, not_matched = matchTags(tags, path)
            unsatisfied = False

    input('Press enter to confirm tags.')
    setTags(matched_tags, no_disc)
    print('Finished.')












