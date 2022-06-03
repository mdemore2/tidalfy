from src.spotify_wrapper import SpotifyWrapper


# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def test_spotify():
    client = SpotifyWrapper()
    playlist = client.get_playlist('https://open.spotify.com/playlist/6SFy8Nb6EbFFhLZENxRli0?si=e11a6860a4094c01')
    print(playlist)
    print(playlist.name)
    print(playlist.spotify_id)
    print(playlist.track_list)
    print(playlist.track_list[0].title)
    #new_playlist = client.create_playlist(playlist
    # track = tidalfy_common.Track(track['al'])


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    test_spotify()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
