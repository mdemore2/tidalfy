import logging
from src.spotify_wrapper import SpotifyWrapper
from src.tidal_wrapper import TidalWrapper
from flask import Flask, render_template, redirect, url_for, request, session
import webbrowser

app = Flask(__name__)
app.secret_key = 'secret'


def copy_to_tidal(tidal: TidalWrapper, spotify: SpotifyWrapper, url: str) -> str:
    playlist = spotify.get_playlist(url)
    playlist = tidal.create_playlist(playlist)
    return playlist.get_tidal_url()


def copy_to_spotify(tidal: TidalWrapper, spotify: SpotifyWrapper, url: str) -> str:
    playlist = tidal.get_playlist(url)
    playlist = spotify.create_playlist(playlist)
    return playlist.get_spotify_url()


@app.route('/', methods=('GET', 'POST'))
def index():
    """
    get playlist url from user
    :return:
    """
    if request.method == 'POST':
        session['playlist_url'] = request.form['playlist_url']
        return redirect(url_for('copy'))
    return render_template('index.html')


@app.route('/copy')
def copy():
    """
    initialize wrappers and link accounts
    :return:
    """
    tidal = TidalWrapper()
    spotify = SpotifyWrapper()
    print(tidal.login_url)
    webbrowser.open(f'https://{tidal.login_url}')
    try:
        tidal.login_future.result()
    except Exception as e:
        # unable to complete login
        return redirect(url_for('index'))
    if 'spotify' in session['playlist_url']:
        new_playlist_url = copy_to_tidal(tidal, spotify, session['playlist_url'])
    else:
        new_playlist_url = copy_to_spotify(tidal, spotify, session['playlist_url'])
    webbrowser.open(new_playlist_url)
    # return redirect(url_for('/work'))
    return render_template('copy.html', new_playlist_url=new_playlist_url)


@app.route('/status')
def status():
    """
    log progress and eventually display new url
    :return:
    """
    return


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
    app.run()
