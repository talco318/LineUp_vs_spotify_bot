# ./app/telegram_bot.py
import json
import logging
import requests
import telebot

import APIs
from AI import AI_funcs_gemini as Gemini

from app.artist import Artist
from playlists_managment import spotify_funcs
import playlists_managment.public_funcs

bot = telebot.TeleBot(APIs.telegram_Bot_API)

my_relevant = []
tomorrowland_lineup_weekend_json_files = ['tml2024w1.json', 'tml2024w2.json']
weekend_names = ["weekend 1", "weekend 2"]
selected_weekend = "none"
artists_str = ""
artists_to_print_list = []
playlist_links_list = []

# keyboards (buttons):
weekend_keyboard = telebot.types.InlineKeyboardMarkup()
weekend1_button = telebot.types.InlineKeyboardButton(text=weekend_names[0], callback_data=weekend_names[0])
weekend2_button = telebot.types.InlineKeyboardButton(text=weekend_names[1], callback_data=weekend_names[1])
all_button = telebot.types.InlineKeyboardButton(text='All', callback_data='weekend_all')
weekend_keyboard.add(weekend1_button, weekend2_button, all_button)

generate_lineup_keyboard = telebot.types.InlineKeyboardMarkup()
generate_lineup_button = telebot.types.InlineKeyboardButton("Generate AI Lineup", callback_data='generate_ai_lineup')
no_lineup_button = telebot.types.InlineKeyboardButton("No, I'm done", callback_data='done')
generate_lineup_keyboard.add(generate_lineup_button, no_lineup_button)


gif = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExNW45bTBnaGRxbmF0a2wxbnJ0ajR6aDV6MHJ6eTltMnphY2xqZmdpeCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5zoxhCaYbdVHoJkmpf/giphy.gif"

def get_matching_artists(playlist_artists, lineup_data):
    """
    Finds and returns artists that appear in both the playlist and the festival lineup.

    Args:
        playlist_artists (list): 'Artist' objects from the Spotify playlist.
        lineup_data (list): 'Artist' objects from the festival lineup.

    Returns:
        list: Matching 'Artist' objects with updated 'songs_num' values.
    """
    # Create a dictionary to map artist names to their corresponding objects in the lineup data
    lineup_artist_map = {artist.name: artist for artist in lineup_data}

    # Iterate through the playlist artists and update the songs_num attribute for matching artists
    matching_artists = []
    for playlist_artist in playlist_artists:
        if playlist_artist.name in lineup_artist_map:
            lineup_artist = lineup_artist_map[playlist_artist.name]
            lineup_artist.songs_num = playlist_artist.songs_num
            matching_artists.append(lineup_artist)

    return matching_artists


def get_lineup_artists_from_playlist(link) -> list[Artist]:
    """
    Retrieve relevant artists from a Spotify playlist that match artists in a festival lineup.

    Args:
        link (str): The link to the Spotify playlist.

    Returns:
        list: A list of 'Artist' objects representing relevant artists found in both the Spotify playlist and the
        festival lineup.
    """
    try:
        # Retrieve artists from the Spotify playlist
        playlist_artists = spotify_funcs.get_artists_from_spotify_playlist(link)

        # Retrieve artists from the festival lineup
        lineup_data = extract_artists_from_tomorrowland_lineup()

        # Find the matching artists between the playlist and the lineup
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
            break  # Exit the loop once the artist is found and updated


def filter_artists_by_weekend(artists_list, weekend_name):
    """
    Filter the list of artists based on the provided weekend name.

    Args:
        artists_list (list): A list of 'Artist' objects.
        weekend_name (str): The weekend number to filter by.

    Returns:
        list: A new list containing the 'Artist' objects with shows scheduled for the provided weekend number.
    """
    filtered_artists = []

    for artist in artists_list:
        # Check if the artist's primary show is scheduled for the given weekend
        if artist.show.weekend_number == weekend_name:
            filtered_artists.append(artist)
        # Check if the artist has a secondary show scheduled for the given weekend
        elif artist.show2 is not None and artist.show2.weekend_number == weekend_name:
            filtered_artists.append(artist)

    return filtered_artists


def extract_artists_from_tomorrowland_lineup():
    """
    Extract artist data from the Tomorrowland (TML) festival JSON lineup files.

    This function retrieves the artist data from the Tomorrowland festival lineup
    JSON files, creates 'Artist' objects for each artist, and returns a list of
    these objects.

    Returns:
        list: A list of 'Artist' objects containing the extracted data for the artists.
    """
    artists = []

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
            print(f"Error fetching data for {file}: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in {file}: {str(e)}")

    return artists


# def generate_and_print_ai_lineup(chat_id, artists_str: str, selected_weekend: str):
def generate_and_print_ai_lineup(chat_id):

    # claude:
    # response = claude.generate_response(artists_str, selected_weekend)
    # print(response[0].text)

    # Gemini:
    bot.send_message(chat_id=chat_id, text="Your lineup is in process, please wait a while.. ", parse_mode='Markdown')
    bot.send_animation(chat_id=chat_id, animation=gif)
    response = Gemini.generate_response(artists_str, selected_weekend)
    print(str(response))

    bot.send_message(chat_id=chat_id, text=str(response))


def message_artists_to_user(call, artists_list):
    """
    Print and send messages for each item in the 'artists_list' list.
    """
    global artists_to_print_list
    global selected_weekend
    global artists_str
    for artist in artists_list:
        bot.send_message(call.message.chat.id, str(artist), parse_mode='Markdown')
        # print(artist, "\n")
    artists_str = ", ".join(str(art) for art in artists_to_print_list)
    # print(artists_str)
    # generate_and_print_ai_lineup(call.message.chat.id, artists_str, selected_weekend)


def process_weekend_data(call, weekend_name):
    """
    Process the artist data for the specified weekend.

    This function takes a Telegram `call` object and a weekend name, filters the
    list of relevant artists based on the weekend, and sends messages to the user
    with the filtered artist information.

    Args:
        call (telegram.CallbackQuery): The Telegram callback query object.
        weekend_name (str): The name of the weekend to filter the artist data by.
    """
    # Filter the artists based on the specified weekend
    output_artists = filter_artists_by_weekend(my_relevant, weekend_name=weekend_name)
    global artists_to_print_list
    artists_to_print_list = output_artists
    # Send a message with the number of artists found for the weekend
    bot.send_message(
        call.message.chat.id,
        f"*{weekend_name} artists:*\n*{len(output_artists)}* artists that have been found in {weekend_name}:",
        parse_mode='Markdown'
    )

    message_artists_to_user(call, output_artists)


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Hello! I am the Telegram bot.\nTo get started, send a playlist link:")
    username = message.from_user.username
    print(f'Username is: {username}, wrote:\n{str(message.text)}')


# TODO: Add an option for apple music links.
@bot.message_handler(func=lambda message: not message.text.startswith("https://open.spotify.com/playlist/"))
def handle_invalid_link(message):
    bot.send_message(message.chat.id, "Please send a valid Spotify link!")
    username = message.from_user.username
    print(f'Username is: {username}, wrote:\n{str(message.text)}')


# @bot.message_handler(func=lambda message: message.text.startswith("https://open.spotify.com/playlist/"))
# def handle_spotify_link(message):
#     """Handles incoming Spotify playlist links"""
#     global my_relevant
#
#     username = message.from_user.username
#     logging.info(f'User {username} sent Spotify link: {message.text}')
#
#     playlist_links_list = playlists_managment.public_funcs.split_links(message.text)
#     for i, link in enumerate(playlist_links_list):
#         playlist_links_list[i] = spotify_funcs.cut_content_after_question_mark(message.text)
#         my_relevant.extend(get_lineup_artists_from_playlist(playlist_links_list[i]))
#
#     if not playlists_managment.public_funcs.is_link_valid(message.text):
#         bot.send_message(message.chat.id, "Invalid link!", parse_mode='Markdown')
#         logging.warning('Invalid Spotify link received')
#         return
#
#     print(f'Username is: {username}, wrote:\n{str(message.text)}')
#
#
#     bot.send_message(message.chat.id, 'Select a weekend:', reply_markup=weekend_keyboard)



@bot.message_handler(func=lambda message: message.text.startswith("https://open.spotify.com/playlist/"))
def handle_spotify_link(message):
    """Handles incoming Spotify playlist links"""

    username = message.from_user.username
    logging.info(f'User {username} sent Spotify link: {message.text}')

    if not playlists_managment.public_funcs.is_link_valid(message.text):
        bot.send_message(message.chat.id, "Invalid link!", parse_mode='Markdown')
        logging.warning('Invalid Spotify link received')
        return

    print(f'Username is: {username}, wrote:\n{str(message.text)}')
    new_link = spotify_funcs.cut_content_after_question_mark(message.text)
    global my_relevant
    my_relevant = get_lineup_artists_from_playlist(new_link)

    bot.send_message(message.chat.id, 'Select a weekend:', reply_markup=weekend_keyboard)


@bot.callback_query_handler(func=lambda call: call.data)
def handle_callback(call):
    if call.data != 'weekend_all' or call.data != weekend_names[0] or call.data != weekend_names[1]:
        # its valid input
        if call.data == 'weekend_all':
            bot.send_message(call.message.chat.id, "*All artists:*\n", parse_mode='Markdown')
            bot.send_message(call.message.chat.id,
                             f" *{len(my_relevant)}* artists that have been found in both weekends: ",
                             parse_mode='Markdown')
            message_artists_to_user(call, my_relevant)

        elif call.data == weekend_names[0] or call.data == weekend_names[1]:
            # its a regular week
            global selected_weekend
            selected_weekend = call.data
            print(selected_weekend + " selected\n")
            process_weekend_data(call, selected_weekend)

            # ask the user if they want to generate an AI lineup
            bot.send_message(call.message.chat.id, "Would you like to generate an AI lineup?",
                             reply_markup=generate_lineup_keyboard)
            print("--------------------------------------------------------------")
            print("the call.data is: ", call.data, "\n")
            print("--------------------------------------------------------------")
        elif call.data == 'generate_ai_lineup':
            # generate_and_print_ai_lineup(call.message.chat.id, artists_str, selected_weekend)
            generate_and_print_ai_lineup(call.message.chat.id)

        elif call.data == 'done':
            bot.send_message(call.message.chat.id,
                             'You have chosen not to generate an AI lineup. \nIf you want to generate an AI lineup,'
                             ' you can click the button again.\nIf you want to generate a lineup for a different '
                             'playlist, send the playlist link again.\nGoodbye for now!')

    #
    #
    # else:
    #     bot.send_message(call.message.chat.id, 'Invalid option selected!')
    #     print("--------------------------------------------------------------")


bot.infinity_polling()
