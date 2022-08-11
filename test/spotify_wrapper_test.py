import pytest
from src.spotify_wrapper import SpotifyWrapper
from src.tidalfy_common import Track, Playlist


def test_get_playlist():
    client = SpotifyWrapper()
    playlist = client.get_playlist('https://open.spotify.com/playlist/6SFy8Nb6EbFFhLZENxRli0?si=e11a6860a4094c01')
    assert playlist.track_list is not None


def test_create_playlist():
    client = SpotifyWrapper()
    playlist = client.get_playlist('https://open.spotify.com/playlist/6SFy8Nb6EbFFhLZENxRli0?si=e11a6860a4094c01')
    playlist = client.create_playlist(playlist)
    assert isinstance(playlist.get_spotify_url(), str)


def test_spotify():
    client = SpotifyWrapper()
    assert client is not None
