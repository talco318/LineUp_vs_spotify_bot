# ./playlists_managment/spotify_funcs.py
import re
from typing import List
from urllib.parse import parse_qs

import spotipy
from httpx._urlparse import urlparse
from spotipy import SpotifyException
from spotipy.oauth2 import SpotifyClientCredentials, logger
from app.artist import Artist


class SpotifyManager:
    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize the SpotifyManager with client credentials.

        Args:
            client_id (str): Spotify API client ID.
            client_secret (str): Spotify API client secret.
        """
        self.client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)

    def get_artists_from_spotify_playlist(self, playlist_link: str) -> List[Artist]:
        """
        Retrieves a list of artists from a Spotify playlist.

        This function uses the Spotify API to fetch the playlist tracks from the given 'playlist_link'.
        It then processes the tracks and extracts the unique artists' names along with the number of songs by each artist.

        Args:
            playlist_link (str): The link to the Spotify playlist.

        Returns:
            List[Artist]: A list of 'Artist' objects representing each unique artist in the playlist.

        Raises:
            ValueError: If the playlist link is invalid.
            SpotifyException: If there's an error communicating with the Spotify API.
        """
        try:
            playlist_id = self._extract_playlist_id(playlist_link)
            tracks = self._fetch_all_playlist_tracks(playlist_id)
            artist_song_count = self._count_artist_songs(tracks)
            return self._create_artists(artist_song_count)
        except SpotifyException as e:
            logger.error(f"Spotify API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    @staticmethod
    def _extract_playlist_id(playlist_link: str) -> str:
        """
        Extract the playlist ID from the given link.

        Args:
            playlist_link (str): The Spotify playlist link.

        Returns:
            str: The extracted playlist ID.

        Raises:
            ValueError: If the playlist link format is invalid.
        """
        parsed_url = urlparse(playlist_link)
        if parsed_url.netloc not in ['open.spotify.com', 'spotify.com']:
            raise ValueError("Invalid Spotify playlist link")

        path_parts = parsed_url.path.split('/')
        if len(path_parts) < 3 or path_parts[-2] != 'playlist':
            raise ValueError("Invalid Spotify playlist link format")

        playlist_id = path_parts[-1]
        query_params = parse_qs(parsed_url.query)
        if 'si' in query_params:
            playlist_id = playlist_id.split('?')[0]

        return playlist_id

    def _fetch_all_playlist_tracks(self, playlist_id: str) -> List[dict]:
        """
        Fetch all tracks from a playlist, handling pagination.

        Args:
            playlist_id (str): The Spotify playlist ID.

        Returns:
            List[Dict]: A list of track dictionaries.

        Raises:
            SpotifyException: If there's an error fetching the playlist tracks.
        """
        tracks = []
        results = self.sp.playlist_items(playlist_id)
        tracks.extend(results['items'])

        while results['next']:
            results = self.sp.next(results)
            tracks.extend(results['items'])

        return tracks

    @staticmethod
    def _count_artist_songs(tracks: List[dict]) -> dict[str, int]:
        """
        Count the number of songs for each artist in the playlist.

        Args:
            tracks (List[Dict]): A list of track dictionaries.

        Returns:
            Dict[str, int]: A dictionary with artist names as keys and song counts as values.
        """
        artist_song_count = {}
        for track in tracks:
            try:
                for artist in track['track']['artists']:
                    artist_name = artist['name']
                    artist_song_count[artist_name] = artist_song_count.get(artist_name, 0) + 1
            except KeyError:
                logger.warning(f"Unexpected track format: {track}")
        return artist_song_count

    @staticmethod
    def _create_artists(artist_song_count: dict[str, int]) -> List[Artist]:
        """
        Create Artist objects from the artist song count dictionary.

        Args:
            artist_song_count (Dict[str, int]): A dictionary with artist names as keys and song counts as values.

        Returns:
            List[Artist]: A list of Artist objects.
        """
        return [
            Artist(
                name=artist_name,
                host_name_and_stage='none',
                weekend='none',
                date='none',
                songs_num=songs_num
            )
            for artist_name, songs_num in artist_song_count.items()
        ]


def get_artists_from_spotify_playlist(playlist_link: str) -> List[Artist]:
    """
    Wrapper function to get artists from a Spotify playlist.

    Args:
        playlist_link (str): The link to the Spotify playlist.

    Returns:
        List[Artist]: A list of Artist objects.

    Raises:
        ValueError: If the playlist link is invalid.
        SpotifyException: If there's an error communicating with the Spotify API.
    """
    return get_artists_from_spotify_playlist(playlist_link)
