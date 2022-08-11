import pytest
from src.tidal_wrapper import TidalWrapper
from src.spotify_wrapper import SpotifyWrapper


def test_spotify_2_tidal():
    url = 'https://open.spotify.com/playlist/5LFlju2pmUImpwcRRrk41K?si=79DuR83RTf6VMdHrDnomqg&nd=1'
    spotify = SpotifyWrapper()
    tidal = TidalWrapper()
    playlist = spotify.get_playlist(url)
    playlist = tidal.create_playlist(playlist)
    print(playlist.get_tidal_url())
    return


def test_tidal_2_spotify():
    url = 'https://listen.tidal.com/playlist/062cb536-6c5b-4584-99dc-21cb1d069374'
    spotify = SpotifyWrapper()
    tidal = TidalWrapper()
    playlist = tidal.get_playlist(url)
    playlist = spotify.create_playlist(playlist)
    print(playlist.get_spotify_url())
    return


if __name__ == "__main__":
    exit()
    # test_tidal_2_spotify()
    # test_spotify_2_tidal()
