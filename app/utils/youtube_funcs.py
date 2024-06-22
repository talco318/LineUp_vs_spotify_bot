import logging
import re
from app.models.artist_model import Artist
from googleapiclient.discovery import build

# Replace with your own YouTube Data API key
import APIs

API_KEY = APIs.YOUTUBE_API


def get_artists_from_youtube_playlist(playlist_link):
    """
    Retrieves a list of artists from a YouTube/YouTube Music playlist.

    Args:
        playlist_id (str): The ID of the YouTube/YouTube Music playlist.

    Returns:
        list: A list of unique artist names in the playlist.
    """

    playlist_id = cut_content_after_equal_mark(playlist_link)
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    artists_list = []
    next_page_token = None

    while True:
        # Call the YouTube Data API to retrieve the playlist items
        response = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        artist_song_count = {}

        # Extract the artist names from the video titles
        for item in response['items']:
            video_title = item['snippet']['title']
            artist_name = extract_artist_from_title(video_title)
            # TODO: (fix) Add the artist to the 'artists' set if it is not already present
            #  and update songs_num for existing artists
            if artist_name in artist_song_count:
                artist_song_count[artist_name] += 1
            else:
                artist_song_count[artist_name] = 1

        # Check if there are more pages of results
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    for artist_name, songs_num in artist_song_count.items():
        new_artist = Artist(name=artist_name, host_name_and_stage='none', weekend='none', date='none')
        new_artist.songs_num = songs_num
        artists_list.append(new_artist)

    return artists_list


def cut_content_after_equal_mark(link):
    """
    Cuts the content after the equal sign in a given link.

    Arguments:
        link (str): A string representing a link with or without an equal sign.

    Returns:
        str: The content before the equal sign, if it exists, otherwise the original link.
    """
    # Use regular expression to match the equal sign and the content after it
    match = re.search(r"=(.*)$", link)

    # If the match is found, return the content before the equal sign
    if match:
        return match.group(1)

    # Otherwise, return the original link
    return link


def extract_artist_from_title(title):
    """
    Extracts the artist name from a video title.
    This is a simple implementation that assumes the artist name is followed by a hyphen or a pipe symbol.
    You may need to modify this function based on your specific use case.

    Args:
        title (str): The title of the video.

    Returns:
        str: The artist name extracted from the title, or None if not found.
    """
    separators = [' - ', ' | ']
    for separator in separators:
        if separator in title:
            artist, _ = title.split(separator, 1)
            return artist.strip()
    return None

# playlist_id = 'PLnKVD11LThZQL-r7h1vQ1bDJ-QFkGwbJe'
# artists = get_artists_from_youtube_playlist(playlist_id)
# print(artists)
