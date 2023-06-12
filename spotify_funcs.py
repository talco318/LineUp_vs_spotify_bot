import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from artist import Artist
import APIs

# Replace with your own Spotify API credentials
client_id = APIs.spotify_client_id_API
client_secret = APIs.spotify_client_secret_API


def cut_content_after_question_mark(link):
    # Use regular expression to match the question mark and the content after it
    match = re.search(r"(.*?)(\?.*)", link)

    # If the match is found, return the content before the question mark
    if match:
        return match.group(1)

    # Otherwise, return the original link
    else:
        return link


def get_artists_from_spotify(playlist_link):
    # Authenticate with Spotify API
    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    playlist_id = playlist_link.split('/')[-1]

    # Get the playlist tracks
    results = sp.playlist_items(playlist_id)
    tracks = results['items']

    # Retrieve all tracks in the playlist
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    artists = []
    for track in tracks:
        for artist in track['track']['artists']:
            artist_name = artist['name']
            if is_artist_in_array(artist_name, artists):
                find_artist_and_update_songs_num(artist_name, artists)
            else:
                new_artist = Artist(artist_name, 'none', 'none', 'none')
                artists.append(new_artist)

    return artists


def find_artist_and_update_songs_num(artist_name, artists):
    for artist in artists:
        if artist.name == artist_name:
            artist.songs_num += 1
            break


def is_artist_in_array(artist_name, array):
    return any(artist.name == artist_name for artist in array)


def is_link_good(link):
    """
    This function checks if a link is valid.

    Args:
      link: The link that you want to check.

    Returns:
      `True` if the link is valid, `False` if not.
    """

    # Check if the link is empty.
    if not link:
        return False

    try:
        response = requests.get(link)
        # Check if the request was successful.
        return response.status_code == 200
    except requests.exceptions.HTTPError:
        # The link is not valid.
        return False
