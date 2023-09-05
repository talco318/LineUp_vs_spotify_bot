from telebot import types
import spotify_funcs
import telebot
import json
from artist import Artist
import requests
import random
import APIs

bot = telebot.TeleBot(APIs.telegram_Bot_API)

my_relevant = []
tomorrowland_lineup_weekend_json_files = ['tml2023w1.json', 'tml2023w2.json']


def get_lineup_artists_from_playlist(link):
    """
    Get relevant artists from a Spotify playlist based on the extracted data from a festival lineup.

    Arguments:
        link (str): The link to the Spotify playlist.

    Returns:
        list: A list of 'Artist' objects representing relevant artists found both in the Spotify playlist and the festival lineup.
    """
    playlist_artists = spotify_funcs.get_artists_from_spotify_playlist(link)
    lineup_data = extract_artists_from_tomorrowland_lineup()
    matching_artists = []

    artist_map = {artist.name: artist for artist in lineup_data}
    for artist in playlist_artists:
        if artist.name in artist_map:
            artist_obj = artist_map[artist.name]
            artist_obj.songs_num = artist.songs_num
            matching_artists.append(artist_obj)

    return matching_artists


def find_artist_and_update_new_data(artists, artist_name, songs_num, new_date, weekend, host_name_and_stage):
    """
    This function searches for the artist with the given 'artist_name' in the list of 'artists'.
    If the artist is found, it updates the 'songs_num' attribute with the provided 'songs_num'.
    It also calls the 'add_show' method of the artist to add a new show with the provided 'new_date',
    'weekend', and 'host_name_and_stage' information.

    Arguments:
        artists (list): A list of 'Artist' objects.
        artist_name (str): The name of the artist to find.
        songs_num (int): The number of songs attributed to the artist.
        new_date (str): The date of the new show to add.
        weekend (str): The weekend information for the new show.
        host_name_and_stage (str): The name of the host and the stage for the new show.

    Returns:
        None: The function does not return anything; it updates the attributes of the matching artist in the list.
    """
    for artist in artists:
        if artist.name == artist_name:
            artist.songs_num = songs_num
            artist.add_new_show(weekend, host_name_and_stage, new_date)
            break


def fatch_json_data(url):
    """
    Read and parse JSON data from the specified URL.

    Arguments:
        url (str): The URL from which to read the JSON data.

    Returns:
        dict: A dictionary representing the parsed JSON data.
    """
    user_agents_list = [
        'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
    ]
    response = requests.get(url, headers={'User-Agent': random.choice(user_agents_list)})
    data = response.json()
    return data


def filtered_list(artists, weekend_number):
    """
    Filter the list of artists based on the provided weekend number.

    Arguments:
        artists (list): A list of 'Artist' objects.
        weekend_number (int): The weekend number to filter by.

    Returns:
        list: A new list containing the 'Artist' objects with shows scheduled for the provided weekend number.
    """
    filtered_artists = []
    for art in artists:
        if art.show.weekend_number == weekend_number or (art.show2 is not None and art.show2.weekend_number == weekend_number):
            filtered_artists.append(art)
    return filtered_artists


import json


def extract_artists_from_tomorrowland_lineup():
    """
    Extract artists' data from Tomorrowland (TML) festival JSON tomorrowland_lineup_weekend_json_files.

    Returns:
        list: A list of 'Artist' objects containing the extracted data for the artists.
    """
    artists = []

    for file in tomorrowland_lineup_weekend_json_files:
        try:
            url = f'https://clashfinder.com/data/event/{file}'

            # Try to open and read the JSON file, handle exceptions if it fails
            try:
                with open(file, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)
            except FileNotFoundError:
                print(f"Error: JSON file {file} not found.")
                continue
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in {file}: {str(e)}")
                continue

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

                    try:
                        if any(a.name == name for a in artists):
                            find_artist_and_update_new_data(artists, artist.name, 0, time, weekend, host_name_and_stage)
                        else:
                            artists.append(artist)
                    except Exception as e:
                        print(f"Error updating artist data: {str(e)}")

        except Exception as e:
            print(f"Error fetching data for {file}: {str(e)}")

    return artists


def messege_artists_to_user(call, artists):
    """
    Print and send messages for each item in the 'arr' list.

    Arguments:
        call (object): An object containing information about the chat and the message.
        artists (list): A list of items to be printed and sent as messages.

    Returns:
        None: The function does not return anything; it sends messages using the 'bot.send_message' function.
    """
    for art in artists:
        bot.send_message(call.message.chat.id, str(art), parse_mode='Markdown')
        print(art, "\n")


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
    username = message.from_user.username
    print(f'Username is: {username}, wrote:\n{str(message.text)}')
    if not spotify_funcs.is_link_valid(str(message.text)):
        bot.send_message(message.chat.id, "Invalid link!", parse_mode='Markdown')
        print("Invalid link!")
        return

    new_link = spotify_funcs.cut_content_after_question_mark(message.text)
    global my_relevant
    my_relevant = get_lineup_artists_from_playlist(new_link)
    keyboard = types.InlineKeyboardMarkup()
    weekend1_button = types.InlineKeyboardButton(text='Weekend 1', callback_data='weekend1')
    weekend2_button = types.InlineKeyboardButton(text='Weekend 2', callback_data='weekend2')
    all_button = types.InlineKeyboardButton(text='All', callback_data='weekend_all')

    keyboard.add(weekend1_button, weekend2_button, all_button)

    bot.send_message(message.chat.id, 'Select a weekend:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data)
def handle_callback(call):
    if call.data == 'weekend1':
        filtered_artists = filtered_list(my_relevant, weekend_number='weekend 1')
        bot.send_message(call.message.chat.id, "*Weekend 1 artists*\n", parse_mode='Markdown')
        bot.send_message(call.message.chat.id, f"Number of artists that have been found: {len(filtered_artists)}",
                         parse_mode='Markdown')
        messege_artists_to_user(call, filtered_artists)

    elif call.data == 'weekend2':
        filtered_artists = filtered_list(my_relevant, weekend_number='weekend 2')
        bot.send_message(call.message.chat.id, "*Weekend 2 artists:*\n", parse_mode='Markdown')
        bot.send_message(call.message.chat.id, f"Number of artists that have been found: {len(filtered_artists)}",
                         parse_mode='Markdown')
        messege_artists_to_user(call, filtered_artists)

    elif call.data == 'weekend_all':
        bot.send_message(call.message.chat.id, "*All artists:*\n", parse_mode='Markdown')
        bot.send_message(call.message.chat.id, f"Number of artists that have been found: {len(my_relevant)}",
                         parse_mode='Markdown')
        messege_artists_to_user(call, my_relevant)
    else:
        bot.send_message(call.message.chat.id, 'Invalid option selected!')
        print("--------------------------------------------------------------")


bot.infinity_polling()
