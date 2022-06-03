import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import src.tidalfy_common as tidalfy_common


class SpotifyWrapper:
    def __init__(self):
        scope = 'playlist-read-private,playlist-modify-public'
        self._client = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(), auth_manager=SpotifyOAuth(scope=scope))
        self._user_id = self._client.me()['id']

    def get_playlist(self, url: str) -> tidalfy_common.Playlist:
        spotify_playlist = self._client.playlist(url)
        #print(spotify_playlist)
        track_list = []
        for item in spotify_playlist['tracks']['items']:
            track = item['track']
            album = track['album']['name']
            artist = track['artists'][0]['name']  # TODO: address multiple artists
            title = track['name']
            new_track = tidalfy_common.Track(album, artist, title)
            new_track.spotify_id = track['id']
            track_list.append(new_track)

        common_playlist = tidalfy_common.Playlist(spotify_playlist['name'], track_list, spotify_id=spotify_playlist['id'])

        return common_playlist

    def create_playlist(self, name: str, track_list: list) -> str:
        playlist = self._client.user_playlist_create(self._user_id, name)
        print(playlist)
        uri_list = [x.spotify_id for x in track_list]
        self._client.playlist_add_items(playlist['id'], uri_list)

        return playlist['id'] #TODO: return URL
