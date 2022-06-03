import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from src.tidalfy_common import Track, Playlist
import src.tidalfy_common as tidalfy_common
from typing import Union
import urllib.parse


class SpotifyWrapper:
    def __init__(self):
        scope = 'playlist-read-private,playlist-modify-public'
        self._client = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(), auth_manager=SpotifyOAuth(scope=scope))
        self._user_id = self._client.me()['id']

    def get_playlist(self, url: str) -> Playlist: #spotify login needed to get playlist IFF private playlist
        spotify_playlist = self._client.playlist(url)
        #print(spotify_playlist)
        track_list = []
        for item in spotify_playlist['tracks']['items']:
            track = item['track']
            album = track['album']['name']
            artist = track['artists'][0]['name']  # TODO: address multiple artists
            title = track['name']
            new_track = Track(album, artist, title)
            new_track.spotify_id = track['id']
            track_list.append(new_track)

        common_playlist = Playlist(spotify_playlist['name'], track_list, spotify_id=spotify_playlist['id'])

        return common_playlist

    def create_playlist(self, name: str, track_list: list) -> str: #spotify login needed to create playlist
        playlist = self._client.user_playlist_create(self._user_id, name)
        print(playlist)
        uri_list = [x.spotify_id for x in track_list]
        self._client.playlist_add_items(playlist['id'], uri_list)

        return playlist['id'] #TODO: return URL

    def _search_for_track(self, track: Track) -> Union[Track, None]:
        q = 'artist:' + track.artist + '+album:' + track.album + '+track:' + track.title
        results = self._client.search(q, type='track') #TODO: add similarity func to compare results w/ track data
        track.spotify_id = results['tracks']['items'][0]['id']
        #print(results['tracks']['items'][0].keys())
        print(f'TRACK ID: {track.spotify_id}')
        print(f"SEARCHED_ID: {results['tracks']['items'][0]['id']}")
        return