from src.spotify_wrapper import SpotifyWrapper


def test_spotify():
    client = SpotifyWrapper()
    playlist = client.get_playlist('https://open.spotify.com/playlist/6SFy8Nb6EbFFhLZENxRli0?si=e11a6860a4094c01')
    print(playlist)
    print(playlist.name)
    print(playlist.spotify_id)
    print(playlist.track_list)
    print(playlist.track_list[0].title)
    client._search_for_track(playlist.track_list[0])
    #new_playlist = client.create_playlist(playlist
    # track = tidalfy_common.Track(track['al'])



if __name__ == '__main__':
    test_spotify()

