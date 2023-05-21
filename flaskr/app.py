import logging
from src.spotify_wrapper import SpotifyWrapper
from src.tidal_wrapper import TidalWrapper
from flask import Flask, render_template, redirect, url_for, request, session, flash, get_flashed_messages, jsonify
from celery import Celery
import webbrowser

def make_app():
    app = Flask(__name__)
    app.secret_key = 'secret'
    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost"))
    
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    return app, celery

app, celery = make_app()

@celery.task(bind=True)
def copy_to_tidal(self, tidal: TidalWrapper, spotify: SpotifyWrapper, url: str) -> tuple:
    playlist = spotify.get_playlist(url)
    playlist = tidal.create_playlist(playlist, task=self)
    return playlist.get_tidal_url(), playlist.name

@celery.task(bind=True)
def copy_to_spotify(self, tidal: TidalWrapper, spotify: SpotifyWrapper, url: str) -> tuple:
    playlist = tidal.get_playlist(url)
    playlist = spotify.create_playlist(playlist, task=self)
    return playlist.get_spotify_url(), playlist.name


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
        new_playlist_url, playlist_title = copy_to_tidal(tidal, spotify, session['playlist_url'])
    else:
        new_playlist_url, playlist_title = copy_to_spotify(tidal, spotify, session['playlist_url'])
    webbrowser.open(new_playlist_url)
    # return redirect(url_for('/work'))
    return render_template('copy.html', new_playlist_url=new_playlist_url, playlist_title=playlist_title)


@app.route('/status/<dest>/<task_id>')
def status(dest, task_id):
    """
    log progress and eventually display new url
    :return:
    """
    if dest == 'spotify':
        task = copy_to_spotify.AsyncResult(task_id)
    elif dest == 'tidal':
        task = copy_to_tidal.AsyncResult(task_id)
    else:
        return jsonify({
            'state': 'ERROR',
            'current': 0,
            'total': 0,
            'status': 'Err'
        })
    response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 0),
            'status': task.info.get('status', 'Err')
        }
    return jsonify(response)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
    app.run()
