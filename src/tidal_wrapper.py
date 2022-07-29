import tidalapi
from src.tidalfy_common import Playlist, Track


class TidalWrapper():
    def __init__(self, username, password):
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

    def create_playlist(self):
        pass

    def _search_for_track(self):
        pass
