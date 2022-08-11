import pytest
from src.tidal_wrapper import TidalWrapper
from src.tidalfy_common import Track, Playlist


def test_get_playlist():
    client = TidalWrapper()
    playlist = client.get_playlist('https://listen.tidal.com/playlist/062cb536-6c5b-4584-99dc-21cb1d069374')
    assert playlist.track_list is not None


def test_create_playlist():
    client = TidalWrapper()
    playlist = client.get_playlist('https://listen.tidal.com/playlist/062cb536-6c5b-4584-99dc-21cb1d069374')
    playlist = client.create_playlist(playlist)
    assert isinstance(playlist.get_spotify_url(), str)


def test_tidal():
    client = TidalWrapper()
    assert client is not None
