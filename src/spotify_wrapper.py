import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from src.tidalfy_common import Track, Playlist
import src.tidalfy_common as tidalfy_common
from typing import Union
import urllib.parse


class SpotifyWrapper:
    def __init__(self):
        scope = 'playlist-read-private,playlist-modify-public'
        self._client = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(),
                                       auth_manager=SpotifyOAuth(scope=scope))
        self._user_id = self._client.me()['id']

    def get_playlist(self, url: str) -> Playlist:  # spotify login needed to get playlist IFF private playlist
        spotify_playlist = self._client.playlist(url)
        # print(spotify_playlist)
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

    def create_playlist(self, playlist: Playlist) -> Playlist:  # spotify login needed to create playlist
        """
        create spotify playlist and populate with tracks
        :param playlist: playlist object w/ name and track list
        :return: playlist object w/ spotify_id for created playlist
        """
        playlist.spotify_id = self._client.user_playlist_create(self._user_id, playlist.name)['id']
        print(playlist.spotify_id)
        playlist = self._get_tracks(playlist)
        uri_list = [x.spotify_id for x in playlist.track_list]
        print(uri_list)
        self._client.playlist_add_items(playlist.spotify_id, uri_list)

        return playlist

    def _get_tracks(self, playlist: Playlist) -> Playlist:
        """
        add spotify id's to tracks in Playlist obj
        :param Playlist:
        :return:
        """
        updated_track_list = []
        for track in playlist.track_list:
            updated_track_list.append(self._search_for_track(track))
        playlist.track_list = updated_track_list
        return playlist

    def _search_for_track(self, track: Track) -> Union[Track, None]:
        q = 'artist:' + track.artist + ' album:' + track.album + ' track:' + track.title
        print(q)
        results = self._client.search(q, type='track')
        track, match = self._check_results(results, track)

        return track
        # track.spotify_id = results['tracks']['items'][0]['id']
        # print(results['tracks']['items'][0].keys())
        # if match:
        #    print(f'TRACK ID: {track.spotify_id}')
        #    print(f"SEARCHED_ID: {results['tracks']['items'][0]['id']}")
        # else:
        #    print(f"Unable to find track: {track.title}\nFirst result:{results['tracks']['items'][0]['name']} by {results['tracks']['items'][0]['artists'][0]}")
        # return

    def _check_results(self, results, track: Track) -> tuple:
        max_score = 0
        max_id = None
        print('IN CHECK RESULTS')
        print(results)
        for result in results['tracks']['items']:
            print(result)
            score = 0
            if result['name'] == track.title:
                print(result['name'])
                score += 1
            if result['artists'][0] == track.artist:
                score += 3
            if result['album']['name'] == track.album:
                score += 5
            if score > 8:
                track.spotify_id = result['id']
                return track, True
            else:
                if score > max_score:
                    max_score = score
                    max_id = result['id']
        if max_score > 0:
            track.spotify_id = max_id
            return track, True
        else:
            return track, False
