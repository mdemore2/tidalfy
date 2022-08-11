class Track:
    def __init__(self, album: str, artist: str, title: str, spotify_id: str = None, tidal_id: str = None):
        self.album = album
        self.artist = artist
        self.title = title
        self.spotify_id = spotify_id
        self.tidal_id = tidal_id


class Playlist:
    def __init__(self, name: str, track_list: list, spotify_id: str = None, tidal_id: str = None):
        self.name = name
        self.track_list = track_list
        self.spotify_id = spotify_id
        self.tidal_id = tidal_id

    def get_spotify_url(self) -> str:
        if self.spotify_id:
            return f'https://open.spotify.com/playlist/{self.spotify_id}'

    def get_tidal_url(self) -> str:
        if self.tidal_id:
            return f'https://listen.tidal.com/playlist/{self.tidal_id}'
