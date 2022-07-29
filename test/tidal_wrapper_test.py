from src.tidal_wrapper import TidalWrapper

if __name__ == '__main__':
    wrapper = TidalWrapper()
    url = 'https://listen.tidal.com/playlist/8192bcd8-b97e-431f-aa5f-36b72f9123dc'
    wrapper.get_playlist(url)
