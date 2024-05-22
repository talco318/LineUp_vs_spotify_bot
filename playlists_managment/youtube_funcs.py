from googleapiclient.discovery import build

# Replace with your own YouTube Data API key
import APIs
API_KEY = APIs.youtube_API

def get_artists_from_youtube_playlist(playlist_id):
    """
    Retrieves a list of artists from a YouTube/YouTube Music playlist.

    Args:
        playlist_id (str): The ID of the YouTube/YouTube Music playlist.

    Returns:
        list: A list of unique artist names in the playlist.
    """
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    artists = set()
    next_page_token = None

    while True:
        # Call the YouTube Data API to retrieve the playlist items
        response = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        # Extract the artist names from the video titles
        for item in response['items']:
            video_title = item['snippet']['title']
            artist = extract_artist_from_title(video_title)
            if artist:
                artists.add(artist)

        # Check if there are more pages of results
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return list(artists)

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