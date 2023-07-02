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
    """
    Cuts the content after the question mark in a given link.

    This function uses regular expression to find the question mark in the 'link' string
    and extracts the content before it. If no question mark is found, the original link
    is returned.

    Arguments:
        link (str): A string representing a link with or without a question mark.

    Returns:
        str: The content before the question mark, if it exists, otherwise the original link.
    """
    # Use regular expression to match the question mark and the content after it
    match = re.search(r"(.*?)(\?.*)", link)

    # If the match is found, return the content before the question mark
    if match:
        return match.group(1)

    # Otherwise, return the original link
    else:
        return link


def get_artists_from_spotify(playlist_link):
    """
    Retrieves a list of artists from a Spotify playlist.

    This function uses the Spotify API to fetch the playlist tracks from the given 'playlist_link'.
    It then processes the tracks and extracts the unique artists' names along with the number of songs by each artist.

    Arguments:
        playlist_link (str): The link to the Spotify playlist.

    Returns:
        list: A list of 'Artist' objects representing each unique artist in the playlist.
    """
    # Authenticate with Spotify API
    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Extract the playlist ID from the link
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
    """
     Find an artist in the list and update the number of songs attributed to the artist.

     This function searches for the artist with the given 'artist_name' in the list of 'artists'.
     If the artist is found, the 'songs_num' attribute of the artist object is incremented by 1.

     Arguments:
         artist_name (str): The name of the artist to find.
         artists (list): A list of 'Artist' objects.

     Returns:
         None: The function does not return anything; it updates the 'songs_num' attribute of the matching artist in the list.
     """
    for artist in artists:
        if artist.name == artist_name:
            artist.songs_num += 1
            break


def is_artist_in_array(artist_name, array):
    """
    This function checks if an artist with the specified 'artist_name' exists in the list of 'Artist' objects,
    which is represented by the 'array'.

    Arguments:
        artist_name (str): The name of the artist to check for.
        array (list): A list of 'Artist' objects representing various artists.

    Returns:
        bool: True if an artist with the specified name exists in the array, False otherwise.
    """
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
