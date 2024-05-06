# ./playlists_managment/spotify_funcs.py

import re
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


def cut_content_after_question_mark(link):
    """
    Cuts the content after the question mark in a given link.

    Arguments:
        link (str): A string representing a link with or without a question mark.

    Returns:
        str: The content before the question mark, if it exists, otherwise the original link.
    """
    # Use regular expression to match the question mark and the content after it
    match = re.search(r"^(.*?)(\?.*)$", link)

    # If the match is found, return the content before the question mark
    if match:
        return match.group(1)

    # Otherwise, return the original link
    return link


def get_artists_from_spotify_playlist(playlist_link):
    """
    Retrieves a list of artists_list from a Spotify playlist.

    This function uses the Spotify API to fetch the playlist tracks from the given 'playlist_link'.
    It then processes the tracks and extracts the unique artists_list' names along with the number of songs by each artist.

    Arguments:
        playlist_link (str): The link to the Spotify playlist.

    Returns:
        list: A list of 'Artist' objects representing each unique artist in the playlist.
    """

    # Extract the playlist ID from the link
    playlist_id = playlist_link.split('/')[-1]

    # Get the playlist tracks
    results = sp.playlist_items(playlist_id)
    tracks = results.get('items')

    # Get all tracks in the playlist
    while results.get('next'):
        results = sp.next(results)
        tracks.extend(results.get('items'))

    artists_list = []
    artist_song_count = {}

    for track in tracks:
        for artist in track.get('track').get('artists'):
            artist_name = artist.get('name')

            if artist_name in artist_song_count:
                artist_song_count[artist_name] += 1
            else:
                artist_song_count[artist_name] = 1

    # Create Artist objects with the collected data
    for artist_name, songs_num in artist_song_count.items():
        new_artist = Artist(name=artist_name, host_name_and_stage='none', weekend='none', date='none')
        new_artist.songs_num = songs_num
        artists_list.append(new_artist)

    return artists_list
