from app.models.artist_model import Artist

def display_artist_info(artist: Artist, selected_weekend: str = "") -> str:
    return str(artist.__str__(selected_weekend))
