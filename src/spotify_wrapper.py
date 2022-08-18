import urllib.parse

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from src.tidalfy_common import Track, Playlist
from typing import Union
import time


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
        uri_list = []
        for track in playlist.track_list:
            if track.spotify_id:
                uri_list.append(track.spotify_id)
        print(uri_list)
        self._client.playlist_add_items(playlist.spotify_id, uri_list)

        return playlist

    def _get_tracks(self, playlist: Playlist) -> Playlist:
        """
        add spotify id's to tracks in Playlist obj
        :param playlist:
        :return:
        """
        updated_track_list = []
        for track in playlist.track_list:
            updated_track_list.append(self._search_for_track(track))
        playlist.track_list = updated_track_list
        return playlist

    def _search_for_track(self, track: Track) -> Union[Track, None]:
        q = 'artist:' + track.artist + ' album:' + track.album + ' track:' + track.title
        q_url = 'https://api.spotify.com/v1/search?q=' + q
        q_url = urllib.parse.quote_plus(q)
        if len(q_url) > 100:
            q = 'artist:' + track.artist + ' track:' + track.title
            q_url = 'https://api.spotify.com/v1/search?q=' + q
            q_url = urllib.parse.quote_plus(q)
            if len(q_url) > 100:
                q = 'track:' + track.title

        print(q)
        results = self._client.search(q, type='track')
        track, match = self._check_results(results, track)
        # TODO: failing on Courtney Barnett Write A List of THings to Look Forward To
        # spotify returning 404 not found on search
        return track

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
            # todo: add logging for partial match
            track.spotify_id = max_id
            return track, True
        else:
            # TODO: add logging for song not found
            return track, False
