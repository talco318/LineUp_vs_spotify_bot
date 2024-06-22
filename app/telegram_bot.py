import logging
from typing import List, Union, Callable
import sys
from pathlib import Path
import APIs
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from config import Config
from AI import AI_funcs_gemini as Gemini
from app.artist import Artist
from playlists_managment.spotify_funcs import SpotifyManager
from playlists_managment.spotify_funcs import get_spotify_artist_link
import playlists_managment.youtube_funcs as youtube_funcs
import playlists_managment.public_funcs as public_funcs
from TML_lineup_managment.public_funcs import extract_artists_from_tomorrowland_lineup
from UserSession import UserSession
from playlist import Playlist

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Telegram bot
bot = telebot.TeleBot(APIs.TELEGRAM_BOT_API)

# Constants
WEEKEND_NAMES = ["Weekend 1", "Weekend 2"]
GIF_URL = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExNW45bTBnaGRxbmF0a2wxbnJ0ajR6aDV6MHJ6eTltMnphY2xqZmdpeCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5zoxhCaYbdVHoJkmpf/giphy.gif"

# Initialize SpotifyManager
spotify_manager = SpotifyManager(APIs.SPOTIFY_CLIENT_ID_API, APIs.SPOTIFY_CLIENT_SECRET_API)

# Store user sessions
user_sessions: dict[int, UserSession] = {}

# Keyboard layouts
def create_weekend_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(text=WEEKEND_NAMES[0], callback_data=WEEKEND_NAMES[0]),
        InlineKeyboardButton(text=WEEKEND_NAMES[1], callback_data=WEEKEND_NAMES[1])
    )
    keyboard.row(InlineKeyboardButton(text='All', callback_data='weekend_all'))
    return keyboard

def create_generate_lineup_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("Generate AI Lineup", callback_data='generate_ai_lineup'),
        InlineKeyboardButton("No, I'm done", callback_data='done')
    )
    return keyboard

def create_finish_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Start again!", callback_data='start_again'))
    return keyboard

# Helper functions
def typing_action(chat_id: int) -> None:
    bot.send_chat_action(chat_id=chat_id, action='typing')

def get_matching_artists(playlist_artists: List[Artist], lineup_data: List[Artist]) -> List[Artist]:
    matching_artists = [
        lineup_artist for playlist_artist in playlist_artists
        for lineup_artist in lineup_data
        if lineup_artist.name.lower() == playlist_artist.name.lower()
    ]

    for matching_artist in matching_artists:
        matching_artist.songs_num = next(
            artist.songs_num for artist in playlist_artists
            if artist.name.lower() == matching_artist.name.lower()
        )

    return matching_artists

def get_lineup_artists_from_playlist(playlist: Union[Playlist, str]) -> List[Artist]:
    try:
        if isinstance(playlist, str):
            playlist_link = playlist
        else:
            playlist_link = playlist.link

        if "spotify.com" in playlist_link:
            playlist_artists = spotify_manager.get_artists_from_spotify_playlist(playlist_link)
        else:
            playlist_artists = youtube_funcs.get_artists_from_youtube_playlist(playlist_link)

        lineup_data = extract_artists_from_tomorrowland_lineup()
        return get_matching_artists(playlist_artists, lineup_data)
    except Exception as e:
        logger.error(f"An error occurred in get_lineup_artists_from_playlist: {str(e)}")
        raise

def update_spotify_link(user_session: UserSession) -> None:
    for artist in user_session.my_relevant:
        if not artist.spotify_link:
            artist.spotify_link = get_spotify_artist_link(spotify_manager=spotify_manager, artist_name=artist.name)

def filter_artists_by_weekend(artists: List[Artist], weekend_name: str) -> List[Artist]:
    return [
        artist for artist in artists
        if (artist.show.weekend_number.lower() == weekend_name.lower()) or
           (artist.show2 is not None and artist.show2.weekend_number.lower() == weekend_name.lower())
    ]

def generate_and_print_ai_lineup(user_session: UserSession, chat_id: int) -> None:
    try:
        typing_action(chat_id)
        bot.send_message(chat_id=chat_id, text="Your lineup is in process, please wait a while.. ", parse_mode='Markdown')
        bot.send_animation(chat_id=chat_id, animation=GIF_URL)
        typing_action(chat_id)
        response = Gemini.generate_response(user_session.artists_str, user_session.selected_weekend)
        logger.info(f"Username is: {user_session.username}, AI response: {str(response)}")
        typing_action(chat_id)
        bot.send_message(chat_id=chat_id, text=str(response), parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Username is: {user_session.username}, Error generating and printing AI lineup: {str(e)}")
        typing_action(chat_id)
        bot.send_message(chat_id=chat_id, text="An error occurred while generating the AI lineup. Please try again later.")

def message_artists_to_user(chat_id: int, user_session: UserSession) -> None:
    try:
        if len(user_session.artists_by_weekend) == 0:
            artists_chunks = [user_session.my_relevant[i:i + 12] for i in range(0, len(user_session.my_relevant), 12)]
        else:
            artists_chunks = [user_session.artists_by_weekend[i:i + 12] for i in range(0, len(user_session.artists_by_weekend), 12)]
        typing_action(chat_id)
        for chunk in artists_chunks:
            chunk_str = "\n\n--------------------------------\n\n".join(
                str(artist.__str__(user_session.selected_weekend)) for artist in chunk)
            bot.send_message(chat_id, chunk_str, parse_mode='HTML', disable_web_page_preview=True)

        user_session.artists_str = ", ".join(str(art.__str__(user_session.selected_weekend)) for art in user_session.artists_by_weekend)
    except Exception as e:
        logger.error(f"Username is: {user_session.username}, Error messaging artists to user: {str(e)}")
        bot.send_message(chat_id, "An error occurred while processing the artist list. Please try again later.")

def process_weekend_data(chat_id: int, user_session: UserSession) -> None:
    user_session.artists_by_weekend = filter_artists_by_weekend(user_session.my_relevant, user_session.selected_weekend.lower())
    typing_action(chat_id)
    bot.send_message(chat_id,
                     f"*{user_session.selected_weekend} artists:*\n"
                     f"*{len(user_session.artists_by_weekend)}* artists that have been found in {user_session.selected_weekend}:",
                     parse_mode='Markdown')

    message_artists_to_user(chat_id, user_session)

def add_artists_from_new_playlist(current_artists: List[Artist], new_artists: List[Artist]) -> List[Artist]:
    return current_artists + [
        artist for artist in new_artists
        if all(artist.name != existing_artist.name or artist.show.date != existing_artist.show.date
               for existing_artist in current_artists)
    ]

def get_or_create_session(chat_id: int) -> UserSession:
    if chat_id not in user_sessions:
        user_sessions[chat_id] = UserSession()
    return user_sessions[chat_id]

# Message handlers
@bot.message_handler(commands=["start"])
def start(message: telebot.types.Message) -> None:
    chat_id = message.chat.id
    user_session = get_or_create_session(chat_id)
    user_session.clear_all()
    first_message = (
        "Hello! I am the Telegram bot.\nTo get started, send a playlist link:\n"
        "Notes:\n"
        "If you want to use your liked songs playlist, you have to copy it to a new playlist "
        "(as mentioned <a href='https://community.spotify.com/t5/Your-Library/Create-a-Playlist-from-Liked-Songs/td-p/4998474'>here</a>)."
    )
    typing_action(chat_id)
    bot.send_message(chat_id, first_message, parse_mode='HTML', disable_web_page_preview=True)
    logger.info(f'Username is: {user_session.username}, wrote:\n{str(message.text)}')

@bot.message_handler(func=lambda message: not message.text.startswith("https://open.spotify.com/playlist/") and not message.text.startswith("https://music.youtube.com"))
def handle_invalid_link(message: telebot.types.Message) -> None:
    typing_action(message.chat.id)
    bot.send_message(message.chat.id, "Please send a valid Spotify or YouTube music link!")
    logger.info(f'Username is: {user_session.username}, wrote:\n{str(message.text)}')

def handle_music_link(message: telebot.types.Message, platform_name: str, link_checker: Callable[[str], bool]) -> None:
    chat_id = message.chat.id
    user_session = get_or_create_session(chat_id)
    user_session.username = message.from_user.username
    bot.send_message(chat_id, f"Great! Next step:", parse_mode='Markdown')
    typing_action(chat_id)
    logger.info(f'User {user_session.username} sent {platform_name} link: {message.text}')
    curr_playlist = Playlist(platform=platform_name, link=message.text)
    if curr_playlist.platform == "Unknown":
        bot.send_message(chat_id, "Invalid link!", parse_mode='Markdown')
        logger.warning(f'Username is: {user_session.username} Invalid {platform_name} link received')
        return

    if curr_playlist.link not in [playlist.link for playlist in user_session.playlist_links_list]:
        user_session.playlist_links_list.append(curr_playlist)
        try:
            new_artists = get_lineup_artists_from_playlist(curr_playlist)
            user_session.my_relevant = add_artists_from_new_playlist(user_session.my_relevant, new_artists)
        except Exception as e:
            logger.error(f"Username is: {user_session.username} Error processing playlist: {str(e)}")
            bot.send_message(chat_id, "An error occurred while processing the playlist. Please try again.")
            return

    if not link_checker(curr_playlist.link):
        bot.send_message(chat_id, "Invalid link!", parse_mode='Markdown')
        logger.warning(f'Username is: {user_session.username}, Invalid {platform_name} link received')
        return

    typing_action(chat_id)
    bot.send_message(chat_id,
                     'If you want to add one more playlist, just send the link.\nIf not - select your weekend:',
                     reply_markup=create_weekend_keyboard())

@bot.message_handler(func=lambda message: message.text.startswith("https://open.spotify.com/playlist/"))
def handle_spotify_link(message: telebot.types.Message) -> None:
    handle_music_link(
        message,
        platform_name="Spotify",
        link_checker=public_funcs.is_link_valid
    )

@bot.message_handler(func=lambda message: message.text.startswith("https://music.youtube.com"))
def handle_youtube_music_link(message: telebot.types.Message) -> None:
    bot.send_message(message.chat.id, "YouTube music isn't supported yet.", parse_mode='Markdown')

# Callback query handler
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call: telebot.types.CallbackQuery) -> None:
    chat_id = call.message.chat.id
    user_session = get_or_create_session(chat_id)
    bot.send_message(chat_id,
                     " No problem, working on it! Please wait a moment..",
                     parse_mode='Markdown')
    typing_action(chat_id)
    update_spotify_link(user_session)
    if call.data in ['weekend_all'] + WEEKEND_NAMES:
        if call.data == 'weekend_all':
            user_session.selected_weekend = "both"
            bot.send_message(chat_id, "*All artists:*\n", parse_mode='Markdown')
            bot.send_message(chat_id,
                             f" *{len(user_session.my_relevant)}* artists that have been found in both weekends:",
                             parse_mode='Markdown')
            logger.info(f"Username is: {user_session.username}, The call.data is: {call.data}")
            message_artists_to_user(chat_id, user_session)
        else:
            user_session.selected_weekend = call.data
            logger.info(f"Username is: {user_session.username}, {user_session.selected_weekend} selected")
            process_weekend_data(chat_id, user_session)
            if len(user_session.artists_by_weekend) > 5:
                bot.send_message(chat_id, "If you want to add one more playlist, just send the link.",
                                 parse_mode='Markdown')
                bot.send_message(chat_id,
                                 "Or would you like to generate an AI lineup? Let me do it for you! It's highly recommended!",
                                 reply_markup=create_generate_lineup_keyboard())
                logger.info(f"Username is: {user_session.username}, The call.data is: {call.data}")

    elif call.data == 'generate_ai_lineup':
        logger.info(f"Username is: {user_session.username}, {call.data} clicked")
        if len(user_session.my_relevant) == 0:
            bot.send_message(chat_id, "No artists found for the selected weekend! Please try again.")
            logger.warning(f"Username is: {user_session.username}, No artists found for the selected weekend, he can't generate an AI lineup.")
            return
        generate_and_print_ai_lineup(user_session, chat_id)
        bot.send_message(chat_id,
                         "Would you like to start again or generate a lineup for a different playlist?",
                         reply_markup=create_finish_keyboard())
    elif call.data == 'start_again':
        user_session.clear_all()
        bot.send_message(chat_id, "No problem!\nSend a playlist link to get started!")
        logger.info(f"Username is: {user_session.username}, {call.data} clicked")

    elif call.data == 'done':
        user_session.clear_all()
        logger.info(f"Username is: {user_session.username}, {call.data} clicked")
        bot.send_message(chat_id,
                         'You have chosen not to generate an AI lineup. \nIf you want to generate an AI lineup, '
                         'you can click the button again.\nIf you want to generate a lineup for a different playlist, '
                         'send the playlist link again.\nGoodbye for now!')

    else:
        bot.send_message(chat_id, 'Invalid option selected!')
        logger.warning(f"Username is: {user_session.username}, Invalid option selected")

if __name__ == "__main__":
    bot.infinity_polling()