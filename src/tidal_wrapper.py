import logging
import requests
import tidalapi
from typing import Union
from src.tidalfy_common import Playlist, Track


class TidalWrapper:
    def __init__(self):
        self._session = tidalapi.Session()
        # is there a way to do some of this without logging into tidal?
        self._session.login_oauth_simple()  # TODO: auto redirect/open new window

    def get_playlist(self, url: str) -> Playlist:
        tidal_playlist_id = url.split('/')[-1]
        tidal_playlist = self._session.get_playlist_tracks(tidal_playlist_id)

        track_list = []
        for track in tidal_playlist:
            album = track.album.name
            artist = track.artist.name
            title = track.name
            new_track = Track(album, artist, title)
            new_track.tidal_id = track.id
            track_list.append(new_track)

        playlist_name = self._session.get_playlist(tidal_playlist_id).name
        common_playlist = Playlist(playlist_name, track_list, tidal_id=tidal_playlist_id)

        return common_playlist

    def create_playlist(self, playlist: Playlist) -> Playlist:
        playlist.tidal_id = self._create_playlist(playlist.name)
        playlist = self._get_tracks(playlist)
        self._add_tracks(playlist)
        return playlist  # maybe return url here?

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
        results = self._session.search(field="track", value=track.title).tracks
        track, match = self._check_results(results, track)

        return track

    def _add_tracks(self, playlist: Playlist) -> None:
        #r = requests.get(f'https://listen.tidal.com/v1/playlists/{playlist.tidal_id}')
        #etag = r.headers['etag']
        for track in playlist.track_list:
            tidal_add_track_url = (
                    "https://listen.tidal.com/v1/playlists/"
                    + str(playlist.tidal_id)
                    + "/items"
            )
            print(f'Tidal Track_id:{track.tidal_id}')
            r = requests.post(
                tidal_add_track_url,
                headers={'authorization': self._session.token_type + ' ' + self._session.access_token,
                    'If-None-Match': '*'},
                data={
                    'onArtifactNotFound': 'SKIP',
                    'onDupes': 'SKIP',
                    "trackIds": track.tidal_id}
            )
            r.raise_for_status()
            logging.getLogger(__name__).info("Added: %s - %s", track.artist, track.title)

    def _create_playlist(self, playlist_name):  # func courtesy spotify2tidal
        """Create a tidal playlist and return its ID.
        Parameters
        ----------
        playlist_name: str
            Name of the playlist to create
        """

        tidal_create_playlist_url = (
                "https://listen.tidal.com/v1/users/"
                + str(self._session.user.id)
                + "/playlists"
        )

        r = requests.post(
            tidal_create_playlist_url,
            data={"title": playlist_name, "description": ""},
            #headers={"x-tidal-sessionid": self._session.session_id}
            headers={'authorization': self._session.token_type + ' ' + self._session.access_token}
        )
        print(r.raise_for_status())

        logging.getLogger(__name__).debug(
            "Created playlist: %s", playlist_name
        )

        return r.json()["uuid"]

    def _check_results(self, results: list, track: Track) -> tuple:
        max_score = 0
        max_id = None
        for result in results:
            score = 0
            if result.name == track.title:
                score += 1
            if result.artist.name == track.artist:
                score += 3
            if result.album.name == track.album:
                score += 5
            if score > 8:
                track.tidal_id = result.id
                return track, True
            else:
                if score > max_score:
                    max_score = score
                    max_id = result.id
        if max_score > 0:
            track.tidal_id = max_id
            return track, True
        else:
            return track, False
