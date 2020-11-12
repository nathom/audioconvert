from os import system
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

system("export SPOTIPY_CLIENT_ID='b69d1047383b485aa4c18906b036fb16'")
system("export SPOTIPY_CLIENT_SECRET='01fc99ce735c4ddb8ca509eed50f0e80'")
def search_album(query, n=0):
    s = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    r = s.search(q=f"album:{query}", type='album')
    result = r['albums']['items']
    uri = result[n]['uri']
    album_info = s.album(uri)

    tracklist = [{
        'name': track['name'],
        'artist': [artist['name'] for artist in track['artists']],
        'pos': (track['disc_number'], track['track_number'])
    } for track in album_info['tracks']['items']]

    album = {
        'title': album_info['name'],
        'artist': [artist['name'] for artist in album_info['artists']],
        'tracklist': tracklist,
        'numtracks': album_info['total_tracks'],
        'image': album_info['images'][0]['url'],
        'genre': album_info['genres'],
        'year': album_info['release_date'][:4],
        'label': album_info['label'],
        'copyright': [c['text'] for c in album_info['copyrights']]
    }

    return album


def search_track(query, n=0):
    s = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    r = s.search(q=f"track:{query}", type='track')
    result = r['tracks']['items'][n]
    album = result['album']
    track = {
        'name': result['name'],
        'artist': [artist['name'] for artist in result['artists']],
        'image': album['images'][0]['url']
    }
    return track

