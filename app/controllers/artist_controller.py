from app.models.artist_model import Artist
from app.views.artist_view import display_artist_info

def get_artist_info(name, host_name_and_stage, weekend, date, songs_num=0, spotify_link="", selected_weekend=""):
    artist = Artist(name, host_name_and_stage, weekend, date, songs_num, spotify_link)
    return display_artist_info(artist, selected_weekend)
