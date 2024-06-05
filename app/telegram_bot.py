import json
import logging
from typing import List
from typing import Union

import requests
import telebot

import APIs
import AI.AI_funcs_gemini as Gemini
from app.artist import Artist
import playlists_managment.spotify_funcs as spotify_funcs
import playlists_managment.youtube_funcs as youtube_funcs
import playlists_managment.public_funcs
from TML_lineup_managment.public_funcs import extract_artists_from_tomorrowland_lineup
from UserSession import UserSession
from playlist import Playlist

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Telegram bot
bot = telebot.TeleBot(APIs.telegram_Bot_API)

# Global variables
tomorrowland_lineup_weekend_json_files = ['tml2024w1.json', 'tml2024w2.json']
weekend_names = ["weekend 1", "weekend 2"]
gif = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExNW45bTBnaGRxbmF0a2wxbnJ0ajR6aDV6MHJ6eTltMnphY2xqZmdpeCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5zoxhCaYbdVHoJkmpf/giphy.gif"

# Store user sessions
user_sessions = {}

# Keyboards (buttons)
weekend_keyboard = telebot.types.InlineKeyboardMarkup()
weekend1_button = telebot.types.InlineKeyboardButton(text=weekend_names[0], callback_data=weekend_names[0])
weekend2_button = telebot.types.InlineKeyboardButton(text=weekend_names[1], callback_data=weekend_names[1])
all_button = telebot.types.InlineKeyboardButton(text='All', callback_data='weekend_all')
weekend_keyboard.add(weekend1_button, weekend2_button, all_button)

generate_lineup_keyboard = telebot.types.InlineKeyboardMarkup()
generate_lineup_button = telebot.types.InlineKeyboardButton("Generate AI Lineup", callback_data='generate_ai_lineup')
no_lineup_button = telebot.types.InlineKeyboardButton("No, I'm done", callback_data='done')
generate_lineup_keyboard.add(generate_lineup_button, no_lineup_button)


def typing_action(bot, chat_id):
    bot.send_chat_action(chat_id=chat_id, action='typing')


def get_matching_artists(user_session: UserSession, playlist_artists: List[Artist], lineup_data: List[Artist]) -> List[
    Artist]:
    """
    Find and return a list of artists that appear in both the provided Spotify playlist and festival lineup.

    Args:
        user_session (UserSession): The user session object.
        playlist_artists (List[Artist]): A list of 'Artist' objects from the Spotify playlist.
        lineup_data (List[Artist]): A list of 'Artist' objects from the festival lineup.

    Returns:
        List[Artist]: A list of 'Artist' objects that match between the playlist and lineup, with updated 'songs_num' values.
    """
    try:
        # Create a set of artist names from the lineup data for faster lookup
        lineup_artist_names = set(artist.name for artist in lineup_data)

        matching_artists = []
        for playlist_artist in playlist_artists:
            try:
                if playlist_artist.name in lineup_artist_names:
                    # Find the matching artist object from the lineup data
                    lineup_artist = next((artist for artist in lineup_data if artist.name == playlist_artist.name),
                                         None)
                    if lineup_artist:
                        lineup_artist.songs_num = playlist_artist.songs_num
                        matching_artists.append(lineup_artist)
            except Exception as e:
                logging.error(f"Error processing artist {playlist_artist.name}: {str(e)}")
                continue

        return matching_artists
    except Exception as e:
        logging.error(f"Error in get_matching_artists: {str(e)}")
        return []


def get_lineup_artists_from_playlist(user_session: UserSession, playlist: Union[Playlist, str]) -> List[Artist]:
    """
    Retrieve relevant artists from a Spotify playlist and the Tomorrowland lineup, and find the matching artists between them.

    Args:
        user_session (UserSession): The user session object.
        playlist (Union[Playlist, str]): The Playlist object or the link to the playlist.

    Returns:
        List[Artist]: A list of 'Artist' objects representing relevant artists found in both the Spotify playlist and the festival lineup.
    """
    try:
        playlist_artists = []
        if isinstance(playlist, str):
            if "spotify.com" in playlist:
                playlist_artists = spotify_funcs.get_artists_from_spotify_playlist(playlist)
            else:
                playlist_artists = youtube_funcs.get_artists_from_youtube_playlist(playlist)
        else:
            if playlist.link.find("spotify.com") != -1:
                playlist_artists = spotify_funcs.get_artists_from_spotify_playlist(playlist.link)
            else:
                playlist_artists = youtube_funcs.get_artists_from_youtube_playlist(playlist.link)

        # Retrieve relevant artists from the Tomorrowland lineup
        lineup_data = extract_artists_from_tomorrowland_lineup()

        # Find the matching artists between the playlist and the lineup
        matching_artists = get_matching_artists(user_session, playlist_artists, lineup_data)

        return matching_artists
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise e


def filter_artists_by_weekend(user_session: UserSession, weekend_name: str) -> List[Artist]:
    """
    Filter the list of artists based on the provided weekend name.

    Args:
        user_session (UserSession): The user session object.
        weekend_name (str): The weekend number to filter by.

    Returns:
        List[Artist]: A new list containing the 'Artist' objects with shows scheduled for the provided weekend number.
    """
    try:
        filtered_artists = []

        for artist in user_session.my_relevant:
            try:
                # Check if the artist's primary show is scheduled for the given weekend
                if artist.show.weekend_number == weekend_name:
                    filtered_artists.append(artist)
                # Check if the artist has a secondary show scheduled for the given weekend
                elif artist.show2 is not None and artist.show2.weekend_number == weekend_name:
                    filtered_artists.append(artist)
            except Exception as e:
                logging.error(f"Error processing artist {artist.name}: {str(e)}")
                continue

        return filtered_artists
    except Exception as e:
        logging.error(f"Error in filter_artists_by_weekend: {str(e)}")
        return []


def generate_and_print_ai_lineup(user_session: UserSession, chat_id: str):
    """
    Generate an AI lineup based on the user's input and send it to the specified chat.

    Args:
        user_session (UserSession): The user session object.
        chat_id (str): The chat ID of the Telegram user.
    """
    try:
        typing_action(bot, chat_id)
        bot.send_message(chat_id=chat_id, text="Your lineup is in process, please wait a while.. ",
                         parse_mode='Markdown')
        bot.send_animation(chat_id=chat_id, animation=gif)
        bot.send_chat_action(chat_id=chat_id, action='typing')
        typing_action(bot, chat_id)
        response = Gemini.generate_response(user_session.artists_str, user_session.selected_weekend)
        logging.info(f"AI response: {str(response)}")
        typing_action(bot, chat_id)
        bot.send_message(chat_id=chat_id, text=str(response))
    except Exception as e:
        logging.error(f"Error generating and printing AI lineup: {str(e)}")
        typing_action(bot, chat_id)
        bot.send_message(chat_id=chat_id,
                         text="An error occurred while generating the AI lineup. Please try again later.")


def message_artists_to_user(call, user_session: UserSession):
    """
    Send messages to the user containing information about the artists in the 'artists_list'.

    Args:
        call: The Telegram callback query object.
        user_session (UserSession): The user session object.
    """
    try:
        artists_list = user_session.my_relevant

        # Split the artists list into chunks of 12 artists
        artists_chunks = [artists_list[i:i + 12] for i in range(0, len(artists_list), 12)]
        typing_action(bot, call.message.chat.id)
        for chunk in artists_chunks:
            chunk_str = ""
            for artist in chunk:
                chunk_str += str(artist) + "\n\n--------------------------------\n\n"
            bot.send_message(call.message.chat.id, chunk_str, parse_mode='Markdown')

        user_session.artists_to_print_list = artists_list
        user_session.artists_str = ", ".join(str(art) for art in user_session.artists_to_print_list)
    except Exception as e:
        logging.error(f"Error messaging artists to user: {str(e)}")
        bot.send_message(call.message.chat.id,
                         "An error occurred while processing the artist list. Please try again later.")


def process_weekend_data(call, user_session: UserSession, weekend_name: str):
    """
    Process the artist data for the specified weekend and send it to the Telegram chat.

    Args:
        call: The Telegram callback query object.
        user_session (UserSession): The user session object.
        weekend_name (str): The name of the weekend to filter the artist data by.
    """
    # Filter the artists based on the specified weekend
    output_artists = filter_artists_by_weekend(user_session, weekend_name=weekend_name)
    # Send a message with the number of artists found for the weekend
    typing_action(bot, call.message.chat.id)
    bot.send_message(
        call.message.chat.id,
        f"*{weekend_name} artists:*\n*{len(output_artists)}* artists that have been found in {weekend_name}:",
        parse_mode='Markdown')

    message_artists_to_user(call, user_session)


def check_sessions(chat_id):
    global user_sessions
    if chat_id not in user_sessions:
        user_sessions[chat_id] = UserSession()


@bot.message_handler(commands=["start"])
def start(message):
    """
    Handle the /start command.

    Args:
        message: The Telegram message object.
    """
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        user_sessions[chat_id] = UserSession()

    first_message = "Hello! I am the Telegram bot.\nTo get started, send a playlist link:\nNotes:\nIf you want to use " \
                    "your liked songs playlist, you have to copy it to a new playlist (as mentioned " \
                    "<a href='https://community.spotify.com/t5/Your-Library/Create-a-Playlist-from-Liked-Songs/td-p/4998474'>here</a>)."
    typing_action(bot, message.chat.id)

    bot.send_message(message.chat.id, first_message, parse_mode='HTML', disable_web_page_preview=True)
    username = message.from_user.username
    logging.info(f'Username is: {username}, wrote:\n{str(message.text)}')


@bot.message_handler(func=lambda message: not message.text.startswith(
    "https://open.spotify.com/playlist/") and not message.text.startswith("https://music.youtube.com"))
def handle_invalid_link(message):
    """
    Handle invalid Spotify links.

    Args:
        message: The Telegram message object.
    """
    typing_action(bot, message.chat.id)
    bot.send_message(message.chat.id, "Please send a valid Spotify or Youtube music link!")
    username = message.from_user.username
    logging.info(f'Username is: {username}, wrote:\n{str(message.text)}')


def handle_music_link(message, platform_name, link_checker, playlist_class, extract_artists_func):
    """
    Handle incoming music playlist links.

    Args:
        message: The Telegram message object.
        platform_name: Name of the music platform (e.g., 'Spotify', 'YouTube Music').
        link_checker: Function to check if the link is valid.
        playlist_class: Class to instantiate a playlist object.
        extract_artists_func: Function to extract artists from the playlist.
    """
    global user_sessions
    chat_id = message.chat.id

    if chat_id not in user_sessions:
        user_sessions[chat_id] = UserSession()

    user_session = user_sessions[chat_id]

    bot.send_message(chat_id, f"Great! Next step:", parse_mode='Markdown')
    typing_action(bot, chat_id)
    username = message.from_user.username
    logging.info(f'User {username} sent {platform_name} link: {message.text}')
    curr_playlist = Playlist(platform=platform_name, link=message.text)
    if curr_playlist.platform == "Unknown":
        bot.send_message(chat_id, "Invalid link!", parse_mode='Markdown')
        logging.warning(f'Invalid {platform_name} link received')
        return

    if curr_playlist.link not in user_session.playlist_links_list:

        user_session.playlist_links_list.append(curr_playlist)
        for i, curr_playlist in enumerate(user_session.playlist_links_list):
            user_session.my_relevant.extend(extract_artists_func(user_session, user_session.playlist_links_list[i]))

    if not link_checker(curr_playlist.link):
        bot.send_message(chat_id, "Invalid link!", parse_mode='Markdown')
        logging.warning(f'Invalid {platform_name} link received')
        return

    typing_action(bot, chat_id)
    bot.send_message(chat_id, 'If you want to add one more weekend, just send the link.\n'
                              'If not - select your weekend:', reply_markup=weekend_keyboard)


@bot.message_handler(func=lambda message: message.text.startswith("https://open.spotify.com/playlist/"))
def handle_spotify_link(message):
    handle_music_link(
        message,
        platform_name="Spotify",
        link_checker=playlists_managment.public_funcs.is_link_valid,
        playlist_class=Playlist,
        extract_artists_func=get_lineup_artists_from_playlist
    )


@bot.message_handler(func=lambda message: message.text.startswith("https://music.youtube.com/"))
def handle_youtube_music_link(message):
    # handle_music_link(
    #     message,
    #     platform_name="YouTube",
    #     link_checker=playlists_managment.public_funcs.is_link_valid,
    #     playlist_class=Playlist,
    #     extract_artists_func=get_lineup_artists_from_playlist
    # )
    bot.send_message(message.chat.id, "Youtube music isnt supporting yet. ", parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data)
def handle_callback(call):
    """
    Handle callback queries from inline keyboard buttons.

    Args:
        call: The Telegram callback query object.
    """
    chat_id = call.message.chat.id
    if chat_id not in user_sessions:
        user_sessions[chat_id] = UserSession()
    user_session = user_sessions[chat_id]

    if call.data in ['weekend_all', weekend_names[0], weekend_names[1]]:
        if call.data == 'weekend_all':
            bot.send_message(call.message.chat.id, "*All artists:*\n", parse_mode='Markdown')
            bot.send_message(call.message.chat.id,
                             f" *{len(user_session.my_relevant)}* artists that have been found in both weekends: ",
                             parse_mode='Markdown')
            message_artists_to_user(call, user_session)

        elif call.data in [weekend_names[0], weekend_names[1]]:
            user_session.selected_weekend = call.data
            logging.info(f"{user_session.selected_weekend} selected")
            process_weekend_data(call, user_session, user_session.selected_weekend)

            # Ask the user if they want to generate an AI lineup
            if len(user_session.my_relevant) > 0:
                bot.send_message(call.message.chat.id, "Would you like to generate an AI lineup?",
                                 reply_markup=generate_lineup_keyboard)
                logging.info(f"The call.data is: {call.data}")

    elif call.data == 'generate_ai_lineup':
        logging.info(f"{call.data} clicked ")
        if len(user_session.my_relevant) == 0:
            bot.send_message(call.message.chat.id, "No artists found for the selected weekend! Please try again.")
            logging.warning("No artists found for the selected weekend, he cant generate an AI lineup.")
            return
        generate_and_print_ai_lineup(user_session, call.message.chat.id)

    elif call.data == 'done':
        user_session.clear_all()
        logging.info(f"{call.data} clicked ")
        bot.send_message(call.message.chat.id,
                         'You have chosen not to generate an AI lineup. \n'
                         'If you want to generate an AI lineup, you can click the button again.\n'
                         'If you want to generate a lineup for a different playlist, send the playlist link again.\n'
                         'Goodbye for now!')

    else:
        bot.send_message(call.message.chat.id, 'Invalid option selected!')
        logging.warning("Invalid option selected")


# Start the bot and keep it running
if __name__ == "__main__":
    bot.infinity_polling()
