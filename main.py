from telebot import types
import spotify_funcs
import telebot
import json
from artist import Artist
import requests
import random
import APIs
import logging

bot = telebot.TeleBot(APIs.telegram_Bot_API)

my_relevant = []
tomorrowland_lineup_weekend_json_files = ['tml2023w1.json', 'tml2023w2.json']


def get_matching_artists(playlist_artists, lineup_data):
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
                with open('json_lineup_files/' + file, 'r', encoding='utf-8') as json_file:
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


def process_weekend_data(call, weekend_name):
    filtered_artists = filtered_list(my_relevant, weekend_number=weekend_name)
    bot.send_message(call.message.chat.id, f"*{weekend_name} artists:*\n", parse_mode='Markdown')
    bot.send_message(call.message.chat.id,
                    f"*{len(filtered_artists)}* artists that have been found in {weekend_name}:",
                    parse_mode='Markdown')
    messege_artists_to_user(call, filtered_artists)


# def process_weekend_data(call, weekend_name, artist_list):
#         filtered_artists = filtered_list(my_relevant, weekend_number=call.data)
#         bot.send_message(call.message.chat.id, f"*{weekend_name} artists:*\n", parse_mode='Markdown')
#         bot.send_message(call.message.chat.id, f"*{len(filtered_artists)}* artists that have been found in {weekend_name}:", parse_mode='Markdown')
#         messege_artists_to_user(call, filtered_artists)

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
        process_weekend_data(call, 'weekend 1')
    elif call.data == 'weekend2':
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



