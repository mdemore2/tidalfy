import pytest
from src.tidalfy_common import Playlist, Track
from src.tidal_wrapper import TidalWrapper
from src.spotify_wrapper import SpotifyWrapper


def test_get_spotify_url():
    playlist = Playlist()
    playlist.spotify_id = '3W5zFozDB2hK7bpCDTOAPl'
    assert playlist.get_spotify_url() == 'https://open.spotify.com/playlist/3W5zFozDB2hK7bpCDTOAPl'


def test_get_tidal_url():
    playlist = Playlist()
    playlist.tidal_id = '95a31215-c081-4a8c-8111-7950716e5c7f'
    assert playlist.get_tidal_url() == 'https://listen.tidal.com/playlist/95a31215-c081-4a8c-8111-7950716e5c7f'


def test_spotify_2_tidal():
    url = 'https://open.spotify.com/playlist/5LFlju2pmUImpwcRRrk41K?si=79DuR83RTf6VMdHrDnomqg&nd=1'
    spotify = SpotifyWrapper()
    tidal = TidalWrapper()
    playlist = spotify.get_playlist(url)
    playlist = tidal.create_playlist(playlist)
    print(playlist.get_tidal_url())
    assert isinstance(playlist.get_tidal_url(), str)


def test_tidal_2_spotify():
    url = 'https://listen.tidal.com/playlist/062cb536-6c5b-4584-99dc-21cb1d069374'
    spotify = SpotifyWrapper()
    tidal = TidalWrapper()
    playlist = tidal.get_playlist(url)
    playlist = spotify.create_playlist(playlist)
    print(playlist.get_spotify_url())
    assert isinstance(playlist.get_spotify_url(), str)



