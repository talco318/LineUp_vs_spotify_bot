# ./playlists_managment/spotify_funcs.py
import re
from typing import List
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import APIs
from app.artist import Artist

# Replace with your own Spotify API credentials
client_id = APIs.spotify_client_id_API
client_secret = APIs.spotify_client_secret_API

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def cut_content_after_question_mark(link: str) -> str:
    """
    Cuts the content after the question mark in a given link.

    Args:
        link (str): A string representing a link with or without a question mark.

    Returns:
        str: The content before the question mark, if it exists, otherwise the original link.
    """
    match = re.search(r"^(.*?)(\?.*)$", link)
    # If the match is found, return the content before the question mark
    if match:
        return match.group(1)
    # Otherwise, return the original link
    return link


def get_artists_from_spotify_playlist(playlist_link: str) -> List[Artist]:
    """
    Retrieves a list of artists from a Spotify playlist.

    This function uses the Spotify API to fetch the playlist tracks from the given 'playlist_link'.
    It then processes the tracks and extracts the unique artists' names along with the number of songs by each artist.

    Args:
        playlist_link (str): The link to the Spotify playlist.

    Returns:
        list: A list of 'Artist' objects representing each unique artist in the playlist.
    """
    playlist_id = cut_content_after_question_mark(playlist_link).split('/')[-1]

    # Get the playlist tracks
    results = sp.playlist_items(playlist_id)
    tracks = results.get('items')

    # Get all tracks in the playlist
    while results.get('next'):
        results = sp.next(results)
        tracks.extend(results.get('items'))

    # Create a dictionary to store artist song counts
    artist_song_count = {}
    for track in tracks:
        for artist in track["track"]["artists"]:
            artist_name = artist["name"]
            artist_song_count[artist_name] = artist_song_count.get(artist_name, 0) + 1

    # Create Artist objects with the collected data
    artists_list = create_artists(artist_song_count)

    return artists_list


def create_artists(artist_song_count: dict) -> List[Artist]:
    """
    Creates a list of Artist objects from a dictionary of artist song counts.

    Args:
        artist_song_count (dict): A dictionary where the keys are artist names and the values are song counts.

    Returns:
        list: A list of 'Artist' objects with the corresponding song counts.
    """
    artists_list = []
    for artist_name, songs_num in artist_song_count.items():
        new_artist = Artist(name=artist_name, host_name_and_stage='none', weekend='none', date='none')
        new_artist.songs_num = songs_num
        artists_list.append(new_artist)
    return artists_list