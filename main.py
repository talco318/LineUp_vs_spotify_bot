import telebot
import requests
import json
import logging

import spotify_funcs
from artist import Artist
import APIs

bot = telebot.TeleBot(APIs.telegram_Bot_API)

my_relevant = []
tomorrowland_lineup_weekend_json_files = ['tml2023w1.json', 'tml2023w2.json']


def get_matching_artists(playlist_artists, lineup_data):
    """
       Finds and returns artists that appear in both the playlist and the festival lineup.

       Args:
           playlist_artists (list): 'Artist' objects from the Spotify playlist.
           lineup_data (list): 'Artist' objects from the festival lineup.

       Returns:
           list: Matching 'Artist' objects with updated 'songs_num' values.
    """
    matching_artists = []
    artist_map = {artist.name: artist for artist in lineup_data}
    for artist in playlist_artists:
        if artist.name in artist_map:
            artist_obj = artist_map[artist.name]
            artist_obj.songs_num = artist.songs_num
            matching_artists.append(artist_obj)
    return matching_artists

def get_lineup_artists_from_playlist(link):
    """
    Retrieve relevant artists from a Spotify playlist that match artists in a festival lineup.

    Arguments:
        link (str): The link to the Spotify playlist.

    Returns:
        list: A list of 'Artist' objects representing relevant artists found in both the Spotify playlist and the festival lineup.
    """
    try:
        playlist_artists = spotify_funcs.get_artists_from_spotify_playlist(link)
        lineup_data = extract_artists_from_tomorrowland_lineup()
        matching_artists = get_matching_artists(playlist_artists, lineup_data)
        return matching_artists
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise



def find_artist_and_update_new_data(artists_list, artist_name, songs_num, new_date, other_weekend, host_name_and_stage):
    """
    Search for an artist by name in the list of 'artists_list' and update their data of other show.

    Returns:
        None: The function does not return anything; it updates the attributes of the matching artist in the list.
    """
    for artist in artists_list:
        if artist.name == artist_name:
            artist.songs_num = songs_num
            artist.add_new_show(other_weekend, host_name_and_stage, new_date)
            break


def filter_artists_by_weekend(artists_list, weekend_number):
    """
    Filter the list of artists based on the provided weekend number.

    Args:
        artists_list (list): A list of 'Artist' objects.
        weekend_number (int): The weekend number to filter by.

    Returns:
        list: A new list containing the 'Artist' objects with shows scheduled for the provided weekend number.
    """
    filtered_artists = []

    for artist in artists_list:
        # Check if the artist's primary show matches the provided weekend number
        if artist.show.weekend_number == weekend_number:
            filtered_artists.append(artist)
        # Check if the artist's secondary show matches the provided weekend number (if available)
        elif artist.show2 is not None and artist.show2.weekend_number == weekend_number:
            filtered_artists.append(artist)

    return filtered_artists


def extract_artists_from_tomorrowland_lineup():
    """
    Extract artist data from Tomorrowland (TML) festival JSON lineup files.

    Returns:
        list: A list of 'Artist' objects containing the extracted data for the artists.
    """
    artists = []

    for file in tomorrowland_lineup_weekend_json_files:
        try:
            # Starting URL of the JSON data
            url = f'https://clashfinder.com/data/event/{file}'
            # Try to fetch JSON data from the URL
            headers = {'User-Agent': 'My App 1.0'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            locations = data.get("locations")

            for location in locations:
                events = location.get("events")

                for event in events:
                    name = event.get("name")
                    start = event.get("start")
                    end = event.get("end")
                    weekend = 'weekend 1' if file == 'tml2023w1.json' else 'weekend 2'
                    host_name_and_stage = location.get("name")
                    time = f'{start} to {end}'
                    artist = Artist(name=name, host_name_and_stage=host_name_and_stage, weekend=weekend, date=time)

                    # Check if the artist already exists in the list and update data
                    matching_artists = [a for a in artists if a.name == artist.name]
                    if matching_artists:
                        find_artist_and_update_new_data(artists, artist.name, 0, time, weekend, host_name_and_stage)
                    else:
                        artists.append(artist)

        except requests.RequestException as e:
            print(f"Error fetching data for {file}: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in {file}: {str(e)}")

    return artists



def messege_artists_to_user(call, artists_list):
    """
    Print and send messages for each item in the 'artists_list' list.
    """
    for art in artists_list:
        bot.send_message(call.message.chat.id, str(art), parse_mode='Markdown')
        print(art, "\n")


def process_weekend_data(call, weekend_name):
    filtered_artists = filter_artists_by_weekend(my_relevant, weekend_number=weekend_name)
    bot.send_message(call.message.chat.id, f"*{weekend_name} artists:*\n", parse_mode='Markdown')
    bot.send_message(call.message.chat.id,
                    f"*{len(filtered_artists)}* artists that have been found in {weekend_name}:",
                    parse_mode='Markdown')
    messege_artists_to_user(call, filtered_artists)


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Hello! I am the Telegram bot.\nTo get started, send a playlist link:")
    username = message.from_user.username
    print(f'Username is: {username}, wrote:\n{str(message.text)}')


@bot.message_handler(func=lambda message: not message.text.startswith("https://open.spotify.com/playlist/"))
def handle_invalid_link(message):
    bot.send_message(message.chat.id, "Please send a valid Spotify link!")
    username = message.from_user.username
    print(f'Username is: {username}, wrote:\n{str(message.text)}')


@bot.message_handler(func=lambda message: message.text.startswith("https://open.spotify.com/playlist/"))
def handle_spotify_link(message):
    """Handles incoming Spotify playlist links"""

    username = message.from_user.username
    logging.info(f'User {username} sent Spotify link: {message.text}')

    if not spotify_funcs.is_link_valid(message.text):
        bot.send_message(message.chat.id, "Invalid link!", parse_mode='Markdown')
        logging.warning('Invalid Spotify link received')
        return

    print(f'Username is: {username}, wrote:\n{str(message.text)}')
    new_link = spotify_funcs.cut_content_after_question_mark(message.text)
    global my_relevant
    my_relevant = get_lineup_artists_from_playlist(new_link)
    keyboard = telebot.types.InlineKeyboardMarkup()
    weekend1_button = telebot.types.InlineKeyboardButton(text='Weekend 1', callback_data='weekend1')
    weekend2_button = telebot.types.InlineKeyboardButton(text='Weekend 2', callback_data='weekend2')
    all_button = telebot.types.InlineKeyboardButton(text='All', callback_data='weekend_all')

    keyboard.add(weekend1_button, weekend2_button, all_button)

    bot.send_message(message.chat.id, 'Select a weekend:', reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: call.data)
def handle_callback(call):
    if call.data == 'weekend1':
        print('weekend 1 selected\n')
        process_weekend_data(call, 'weekend 1')
    elif call.data == 'weekend2':
        print('weekend 2 selected\n')
        process_weekend_data(call, 'weekend 2')


    elif call.data == 'weekend_all':
        bot.send_message(call.message.chat.id, "*All artists:*\n", parse_mode='Markdown')
        bot.send_message(call.message.chat.id, f" *{len(my_relevant)}* artists that have been found in both weekends: ",
                         parse_mode='Markdown')
        messege_artists_to_user(call, my_relevant)
    else:
        bot.send_message(call.message.chat.id, 'Invalid option selected!')
        print("--------------------------------------------------------------")


bot.infinity_polling()




