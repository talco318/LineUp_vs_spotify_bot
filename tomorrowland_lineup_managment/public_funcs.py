import logging
import json
from urllib import response

import requests
import types
from app.models.artist_model import Artist
import csv
import os

tomorrowland_lineup_weekend_json_files = ['tml2024w1.json', 'tml2024w2.json']
weekend_names = ["weekend 1", "weekend 2"]


def find_artist_and_update_new_data(artists_list: list[Artist], artist_name: str, songs_num: int, new_date: str,
                                    other_weekend: str, host_name_and_stage: str):
    """
    Search for an artist by name in the list of 'artists_list'.
    If artists already exist, update their data of the other show.

    Args:
        artists_list (List[Artist]): The list of artists to search in.
        artist_name (str): The name of the artist to find.
        songs_num (int): The number of songs for the artist.
        new_date (str): The new date for the other show.
        other_weekend (str): The weekend number for the other show.
        host_name_and_stage (str): The host name and stage for the other show.
    """
    for artist in artists_list:
        if artist.name == artist_name:
            artist.songs_num = songs_num
            artist.add_new_show(other_weekend, host_name_and_stage, new_date)
            break


def extract_artists_from_tomorrowland_lineup() -> list[Artist]:
    """
    Extract artist data from the Tomorrowland (TML) festival JSON lineup file.

    Returns:
    List[Artist]: A list of 'Artist' objects containing the extracted data for the artists.
    """
    artists: list[Artist] = []
    url_w1 = 'https://artist-lineup-cdn.tomorrowland.com/TLBE24-W1-211903bb-da4c-445d-a1b3-6b17479a9fab.json'
    url_w2 = 'https://artist-lineup-cdn.tomorrowland.com/TLBE24-W2-211903bb-da4c-445d-a1b3-6b17479a9fab.json'

    headers = {'User-Agent': 'My App 1.0'}
    for url in [url_w1, url_w2]:
        try:
            # Fetch the JSON data and parse it
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Extract artist information from the JSON data
            performances = data.get("performances", [])
            for performance in performances:
                name = performance.get("name")

                stage = performance.get("stage", {}).get("name")
                start_time = performance.get("startTime").split('+')[0]
                end_time = performance.get("endTime").split('+')[0]
                day = performance.get("day")
                time = f"{day} {start_time} - {end_time}"
                # Extract additional artist information if available
                artist_info = performance.get("artists", [{}])[0]
                spotify_link = artist_info.get("spotify", "")

                weekend = weekend_names[0] if url == url_w1 else weekend_names[1]
                artist = Artist(
                    name=name,
                    host_name_and_stage=stage,
                    weekend=weekend,
                    date=time,
                    spotify_link=spotify_link if spotify_link else "",

                )
                matching_artists = [a for a in artists if a.name == artist.name]

                if matching_artists:
                    find_artist_and_update_new_data(artists, artist.name, 0, time, weekend, stage)
                else:
                    artists.append(artist)

        except requests.RequestException as e:
            logging.error(f"Error fetching data: {str(e)}")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {str(e)}")

    return artists

# For local file lineup:
# def extract_artists_from_tomorrowland_lineup() -> list[Artist]:
#     """
#     Extract artist data from the Tomorrowland (TML) festival local JSON lineup file.
#
#     Returns:
#     List[Artist]: A list of 'Artist' objects containing the extracted data for the artists.
#     """
#     artists: list[Artist] = []
#     weekend_names = ["Weekend 1", "Weekend 2"]  # Assuming weekend names are the same
#
#     parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))  # Get parent directory path
#
#     for filename in ["tml2024w1.json", "tml2024w2.json"]:  # Assuming specific filenames
#         filepath = os.path.join(parent_dir, filename)
#         try:
#             # Open the JSON file
#             with open(filepath, "r", encoding="utf-8") as jsonfile:
#                 data = json.load(jsonfile)
#
#                 # Extract artist information from the JSON data
#                 performances = data.get("performances", [])
#                 for performance in performances:
#                     name = performance.get("name")
#                     stage = performance.get("stage", {}).get("name")
#                     date = performance.get("date")
#                     start_time = performance.get("startTime").split('+')[0]
#                     end_time = performance.get("endTime").split('+')[0]
#                     day = performance.get("day")
#
#                     # Extract additional artist information if available
#                     artist_info = performance.get("artists", [{}])[0]
#                     image = artist_info.get("image", "")
#                     date = f"{day} {start_time} - {end_time}"
#                     weekend = weekend_names[0] if filename == "tml2024w1.json" else weekend_names[1]
#
#                     # Create an 'Artist' object and add it to the artists list
#                     artist = Artist(
#                         name=name,
#                         host_name_and_stage=stage,
#                         weekend=weekend,
#                         date=date
#                     )
#                     matching_artists = [a for a in artists if a.name == artist.name]
#
#                     if matching_artists:
#                         find_artist_and_update_new_data(artists, artist.name, 0, date, weekend, stage)
#                     else:
#                         artists.append(artist)
#
#         except FileNotFoundError as e:
#             logging.error(f"Error: File not found - {filepath}")
#
#         except json.JSONDecodeError as e:
#             logging.error(f"Error decoding JSON in {filepath}: {str(e)}")
#     return artists
