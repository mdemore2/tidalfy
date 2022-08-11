import pytest
from src.tidal_wrapper import TidalWrapper
from src.tidalfy_common import Track, Playlist


def test_get_playlist():
    pass


if __name__ == '__main__':
    wrapper = TidalWrapper()
    url = 'https://listen.tidal.com/playlist/8192bcd8-b97e-431f-aa5f-36b72f9123dc'
    wrapper.get_playlist(url)
    wrapper._search_for_track(Track(title='Fables', artist='Interpol', album='The Other Side Of Make-Believe'))
