import logging
import json
import requests
import types
from app.artist import Artist

tomorrowland_lineup_weekend_json_files = ['tml2024w1.json', 'tml2024w2.json']
weekend_names = ["weekend 1", "weekend 2"]


def find_artist_and_update_new_data(artists_list: list[Artist], artist_name: str, songs_num: int, new_date: str,
                                    other_weekend: str, host_name_and_stage: str):
    """
    Search for an artist by name in the list of 'artists_list'.
    If this artists already exist, update their data of the other show.

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
    Extract artist data from the Tomorrowland (TML) festival JSON lineup files.

    Returns:
        List[Artist]: A list of 'Artist' objects containing the extracted data for the artists.
    """
    artists: list[Artist] = []

    for file in tomorrowland_lineup_weekend_json_files:
        try:
            # Construct the URL for the JSON data
            url = f'https://clashfinder.com/data/event/{file}'
            headers = {'User-Agent': 'My App 1.0'}

            # Fetch the JSON data and parse it
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Extract artist information from the JSON data
            locations = data.get("locations")
            for location in locations:
                events = location.get("events")
                for event in events:
                    name = event.get("name")
                    start = event.get("start")
                    end = event.get("end")
                    weekend = weekend_names[0] if file == 'tml2024w1.json' else weekend_names[1]
                    host_name_and_stage = location.get("name")
                    time = f'{start} to {end}'

                    # Create an 'Artist' object and update or add it to the artists list
                    artist = Artist(name=name, host_name_and_stage=host_name_and_stage, weekend=weekend, date=time)
                    matching_artists = [a for a in artists if a.name == artist.name]
                    if matching_artists:
                        find_artist_and_update_new_data(artists, artist.name, 0, time, weekend, host_name_and_stage)
                    else:
                        artists.append(artist)

        except requests.RequestException as e:
            logging.error(f"Error fetching data for {file}: {str(e)}")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON in {file}: {str(e)}")

    return artists



#for python anywhere:
# import json
# import os
#
# def extract_artists_from_tomorrowland_lineup() -> list[Artist]:
#     """
#     Extract artist data from local Tomorrowland (TML) festival JSON files in the parent directory.
#
#     Returns:
#         List[Artist]: A list of 'Artist' objects containing the extracted data for the artists.
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
#                 locations = data.get("locations")
#                 for location in locations:
#                     events = location.get("events")
#                     for event in events:
#                         name = event.get("name")
#                         start = event.get("start")
#                         end = event.get("end")
#                         weekend = weekend_names[0] if filename == "tml2024w1.json" else weekend_names[1]
#                         host_name_and_stage = location.get("name")
#                         time = f"{start} to {end}"
#
#                         # Create an 'Artist' object and update or add it to the artists list
#                         artist = Artist(name=name, host_name_and_stage=host_name_and_stage, weekend=weekend, date=time)
#                         matching_artists = [a for a in artists if a.name == artist.name]
#                         if matching_artists:
#                             find_artist_and_update_new_data(artists, artist.name, 0, time, weekend, host_name_and_stage)
#                         else:
#                             artists.append(artist)
#
#         except FileNotFoundError as e:
#             logging.error(f"Error: File not found - {filepath}")
#         except json.JSONDecodeError as e:
#             logging.error(f"Error decoding JSON in {filepath}: {str(e)}")
#
#     return artists
