import logging
import requests
import tidalapi
import concurrent.futures
from typing import Union
from src.tidalfy_common import Playlist, Track
from celery import Task


class TidalWrapper:
    def __init__(self):
        self._session = tidalapi.Session()
        # is there a way to do some of this without logging into tidal?
        login, future = self._session.login_oauth()  # TODO: auto redirect/open new window
        self.login_url = login.verification_uri_complete
        self.login_future = future

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

    def create_playlist(self, playlist: Playlist, task: Task) -> Playlist:
        playlist.tidal_id = self._create_playlist(playlist.name)
        task.update_state(state='SEARCHING',
                          meta={'current': 0, 'total': 0,
                                'status': 'Searching for matching tracks...'})
        playlist = self._get_tracks(playlist)
        self._add_tracks(playlist, task)
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

    def _search_for_track(self, track: Track) -> Union[Track, None]: #TODO: address multiple artists
        results = self._session.search(field="track", value=track.title).tracks
        track, match = self._check_results(results, track)

        return track

    def _add_tracks(self, playlist: Playlist, task:Task) -> None:
        task.update_state(state='ADDING',
                          meta={'current': 0, 'total': len(playlist.track_list),
                                'status': 'Adding tracks to playlist...'})
        count = 0
        for track in playlist.track_list:
            count += 1
            if count % 5 == 0:
                task.update_state(state='ADDING',
                          meta={'current': count, 'total':  len(playlist.track_list),
                                'status': 'Adding tracks to playlist...'})
            if track.tidal_id:
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
            # TODO: add logging for partial match
            track.tidal_id = max_id
            return track, True
        else:
            # TODO: add logging for song not found
            return track, False
