import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

#spotify api:
your_client_id = '47b7fe5aad594079b5c0d9d4c62819c2'
your_client_secret = '9979cf4e8f524bcdb1702816b79d2988'




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
    # Replace with your own Spotify API credentials
    client_id = your_client_id
    client_secret = your_client_secret

    # Authenticate with Spotify API
    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    playlist_id = playlist_link.split('/')[-1]

    # Get the playlist tracks
    results = sp.playlist_items(playlist_id)
    tracks = results['items']

    # Iterate over the tracks and extract artists' names
    artists = []
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    for track in tracks:
        for artist in track['track']['artists']:
            if artist['name'] not in artists:
                artists.append(artist['name'])
                # print(artist['name'])
    return artists



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

    # Try to access the link.
    try:
        response = requests.get(link)
    except requests.exceptions.HTTPError as e:
        # The link is not valid.
        return False

    # Check if the request was successful.
    if response.status_code == 200:
        # The link is valid.
        return True
    else:
        # The link is not valid.
        return False