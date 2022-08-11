import logging

import requests
import tidalapi
import spotify2tidal.tidal as tidalhelper
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

        pass

    def _search_for_track(self, track: Track) -> Track:
        results = self._session.search(field="track", value=track.title).tracks
        track, match = self._check_results(results, track)

        pass

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
            headers={"x-tidal-sessionid": self._session.session_id},
        )
        r.raise_for_status()

        logging.getLogger(__name__).debug(
            "Created playlist: %s", playlist_name
        )

        return r.json()["uuid"]

    def _check_results(self, results: list, track: Track) -> tuple:
        max_score = 0
        max_id = None
        for result in results:
            score = 0
            if result.name == track.title: #todo fix
                score += 1
            if result.artist.name == track.artist:
                score += 3
            if result.album.name == track.album: #todo fix
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
