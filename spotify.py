import requests

def search_album(query, n=0):
    headers = {
        'Authorization': 'Bearer BQCMHpTQDpjK81AK5s6NxXTAtB_KSd5lM-rza1ZQUVoJTinrYzFMGSXJlb0lwC9GYxigFmNefHf7_r-qJ3N4bObb3VeqVyetnhGCM7r_dVf9cZiWYrkcwmjDkUlhH3MZv6F45kJDeQ50bjaRMJEj513zHX52Olo_qeX1Ohpk2rRciTk97aRn9TJyfDvOutGyKyc'
    }
    formatted_query = query.replace(' ', '%20')
    url = f'https://api.spotify.com/v1/search?q={formatted_query}&type=album'
    r = requests.get(url, headers=headers).json()
    result = r['albums']['items']
    api_url = result[n]['href']

    r_album = requests.get(api_url, headers=headers).json()
    album = r_album['name']
    artist = [artist['name'] for artist in r_album['artists']]
    label = r_album['label']
    art = r_album['images'][0]['url']
    total_tracks = r_album['total_tracks']
    genre = r_album['genres']
    release_date = r_album['release_date']
    tracks = [{'title': track['name'], 'pos': (track['disc_number'], track['track_number'])} for track in r_album['tracks']['items']]

    album_info = {
        'name': album,
        'artist': artist,
        'tracklist': tracks,
        'art': art,
        'genre': genre,
        'release_date': release_date,
        'label': label
    }
    return album_info



