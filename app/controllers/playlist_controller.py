from app.models.playlist_model import Playlist
from app.views.playlist_view import display_playlist_info

def get_playlist_info(platform, link):
    playlist = Playlist(platform, link)
    return display_playlist_info(playlist)
