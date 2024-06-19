import logging
from typing import List, Union

import telebot

import sys

# setting path
sys.path.append('../LineUp_vs_spotify_bot')

import APIs
from AI import AI_funcs_gemini as Gemini
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

finish_keyboard = telebot.types.InlineKeyboardMarkup()
start_again_button = telebot.types.InlineKeyboardButton("Start again!", callback_data='start_again')
finish_keyboard.add(start_again_button)


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
        lineup_artist_names = set(artist.name for artist in lineup_data)

        matching_artists = [
            lineup_artist for playlist_artist in playlist_artists
            for lineup_artist in [
                artist for artist in lineup_data
                if artist.name == playlist_artist.name
            ]
            if lineup_artist
        ]

        for matching_artist in matching_artists:
            matching_artist.songs_num = next(
                artist.songs_num for artist in playlist_artists
                if artist.name == matching_artist.name
            )

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
        if isinstance(playlist, str):
            if "spotify.com" in playlist:
                playlist_artists = spotify_funcs.get_artists_from_spotify_playlist(playlist)
            else:
                playlist_artists = youtube_funcs.get_artists_from_youtube_playlist(playlist)
        else:
            playlist_artists = (
                spotify_funcs.get_artists_from_spotify_playlist(playlist.link)
                if "spotify.com" in playlist.link
                else youtube_funcs.get_artists_from_youtube_playlist(playlist.link)
            )

        lineup_data = extract_artists_from_tomorrowland_lineup()
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
        return [
            artist for artist in user_session.my_relevant
            if (artist.show.weekend_number.lower() == weekend_name.lower()) or
               (artist.show2 is not None and artist.show2.weekend_number.lower() == weekend_name.lower())
        ]
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
        artists_chunks = [user_session.artists_by_weekend[i:i + 12] for i in
                          range(0, len(user_session.artists_by_weekend), 12)]
        typing_action(bot, call.message.chat.id)
        for chunk in artists_chunks:
            chunk_str = "\n\n--------------------------------\n\n".join(
                str(artist.__str__(user_session.selected_weekend)) for artist in chunk)
            bot.send_message(call.message.chat.id, chunk_str, parse_mode='Markdown')

        user_session.artists_str = ", ".join(str(art.__str__(user_session.selected_weekend)) for art in user_session.artists_by_weekend)
    except Exception as e:
        logging.error(f"Error messaging artists to user: {str(e)}")
        bot.send_message(call.message.chat.id,
                         "An error occurred while processing the artist list. Please try again later.")


def process_weekend_data(call, user_session: UserSession):
    """
    Process the artist data for the specified weekend and send it to the Telegram chat.

    Args:
        call: The Telegram callback query object.
        user_session (UserSession): The user session object.
    """
    user_session.artists_by_weekend = filter_artists_by_weekend(user_session,
                                                                weekend_name=user_session.selected_weekend.lower())
    typing_action(bot, call.message.chat.id)
    bot.send_message(call.message.chat.id,
                     f"*{user_session.selected_weekend} artists:*\n"
                     f"*{len(user_session.artists_by_weekend)}* artists that have been found in {user_session.selected_weekend}:",
                     parse_mode='Markdown')

    message_artists_to_user(call, user_session)


def add_artists_from_new_playlist(current_artists, new_artists):
    return current_artists + [artist for artist in new_artists if all(
        artist.name != existing_artist.name or artist.show.date != existing_artist.show.date for existing_artist in
        current_artists)]


def check_sessions(chat_id):
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
    check_sessions(chat_id)
    user_sessions[chat_id].clear_all()
    first_message = "Hello! I am the Telegram bot.\nTo get started, send a playlist link:\n" \
                    "Notes:\n" \
                    "If you want to use your liked songs playlist, you have to copy it to a new playlist " \
                    "(as mentioned <a href='https://community.spotify.com/t5/Your-Library/Create-a-Playlist-from-Liked-Songs/td-p/4998474'>here</a>)."
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
    bot.send_message(message.chat.id, "Please send a valid Spotify or YouTube music link!")
    username = message.from_user.username
    logging.info(f'Username is: {username}, wrote:\n{str(message.text)}')


def handle_music_link(message, platform_name, link_checker, extract_artists_func):
    """
    Handle incoming music playlist links.

    Args:
        message: The Telegram message object.
        platform_name: Name of the music platform (e.g., 'Spotify', 'YouTube Music').
        link_checker: Function to check if the link is valid.
        extract_artists_func: Function to extract artists from the playlist.
    """
    chat_id = message.chat.id
    check_sessions(chat_id)
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

    if curr_playlist.link not in [playlist.link for playlist in user_session.playlist_links_list]:
        user_session.playlist_links_list.append(curr_playlist)
        user_session.my_relevant = add_artists_from_new_playlist(user_session.my_relevant,
                                                                 extract_artists_func(user_session, curr_playlist))

    if not link_checker(curr_playlist.link):
        bot.send_message(chat_id, "Invalid link!", parse_mode='Markdown')
        logging.warning(f'Invalid {platform_name} link received')
        return

    typing_action(bot, chat_id)
    bot.send_message(chat_id,
                     'If you want to add one more playlist, just send the link.\nIf not - select your weekend:',
                     reply_markup=weekend_keyboard)


@bot.message_handler(func=lambda message: message.text.startswith("https://open.spotify.com/playlist/"))
def handle_spotify_link(message):
    handle_music_link(
        message,
        platform_name="Spotify",
        link_checker=playlists_managment.public_funcs.is_link_valid,
        extract_artists_func=get_lineup_artists_from_playlist
    )


def handle_youtube_music_link(message):
    bot.send_message(message.chat.id, "YouTube music isn't supported yet.", parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data)
def handle_callback(call):
    """
    Handle callback queries from inline keyboard buttons.

    Args:
        call: The Telegram callback query object.
    """
    chat_id = call.message.chat.id
    check_sessions(chat_id)
    user_session = user_sessions[chat_id]

    if call.data in ['weekend_all', 'weekend 1', 'weekend 2']:
        if call.data == 'weekend_all':
            bot.send_message(call.message.chat.id, "*All artists:*\n", parse_mode='Markdown')
            bot.send_message(call.message.chat.id,
                             f" *{len(user_session.my_relevant)}* artists that have been found in both weekends:",
                             parse_mode='Markdown')
            message_artists_to_user(call, user_session)
        else:
            user_session.selected_weekend = call.data.capitalize()
            logging.info(f"{user_session.selected_weekend} selected")
            process_weekend_data(call, user_session)
            if len(user_session.artists_by_weekend) > 5:
                bot.send_message(call.message.chat.id, "If you want to add one more playlist, just send the link.",
                                 parse_mode='Markdown')
                bot.send_message(call.message.chat.id,
                                 "Or would you like to generate an AI lineup? Let me do it for you! It's highly recommended!",
                                 reply_markup=generate_lineup_keyboard)
                logging.info(f"The call.data is: {call.data}")

    elif call.data == 'generate_ai_lineup':
        logging.info(f"{call.data} clicked")
        if len(user_session.my_relevant) == 0:
            bot.send_message(call.message.chat.id, "No artists found for the selected weekend! Please try again.")
            logging.warning("No artists found for the selected weekend, he can't generate an AI lineup.")
            return
        generate_and_print_ai_lineup(user_session, call.message.chat.id)
        bot.send_message(call.message.chat.id,
                         "Would you like to start again or generate a lineup for a different playlist?",
                         reply_markup=finish_keyboard)
    elif call.data == 'start_again':
        user_session.clear_all()
        bot.send_message(call.message.chat.id, "No problem!\nSend a playlist link to get started!")
        logging.info(f"{call.data} clicked")

    elif call.data == 'done':
        user_session.clear_all()
        logging.info(f"{call.data} clicked")
        bot.send_message(call.message.chat.id,
                         'You have chosen not to generate an AI lineup. \nIf you want to generate an AI lineup, '
                         'you can click the button again.\nIf you want to generate a lineup for a different playlist, '
                         'send the playlist link again.\nGoodbye for now!')

    else:
        bot.send_message(call.message.chat.id, 'Invalid option selected!')
        logging.warning("Invalid option selected")


# Start the bot and keep it running
if __name__ == "__main__":
    bot.infinity_polling()
