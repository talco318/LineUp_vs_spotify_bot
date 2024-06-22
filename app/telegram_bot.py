import logging
from typing import List, Union, Callable
import sys
from pathlib import Path
import APIs
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from AI import AI_funcs_gemini as Gemini
from app.models.artist_model import Artist
from app.utils.spotify_funcs import SpotifyManager
from app.utils.spotify_funcs import get_spotify_artist_link
import app.utils.youtube_funcs as youtube_funcs
import app.utils.public_funcs as public_funcs
from tomorrowland_lineup_managment.public_funcs import extract_artists_from_tomorrowland_lineup
from UserSession import UserSession
from app.models.playlist_model import Playlist

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
        bot.send_message(chat_id=chat_id, text="Your lineup is in process, please wait a while.. ",
                         parse_mode='Markdown')
        bot.send_animation(chat_id=chat_id, animation=GIF_URL)
        typing_action(chat_id)
        response = Gemini.generate_response(user_session.artists_str, user_session.selected_weekend)
        logger.info(f"Username is: {user_session.username}, AI response: {str(response)}")
        typing_action(chat_id)
        bot.send_message(chat_id=chat_id, text=str(response))
    except Exception as e:
        logger.error(f"Username is: {user_session.username}, Error generating and printing AI lineup: {str(e)}")
        typing_action(chat_id)
        bot.send_message(chat_id=chat_id,
                         text="An error occurred while generating the AI lineup. Please try again later.")


def message_artists_to_user(chat_id: int, user_session: UserSession) -> None:
    try:
        if len(user_session.artists_by_weekend) == 0:
            # It means that the user chose 'both' weekends
            artists_chunks = [user_session.my_relevant[i:i + 12] for i in range(0, len(user_session.my_relevant), 12)]
        else:
            artists_chunks = [user_session.artists_by_weekend[i:i + 12] for i in
                              range(0, len(user_session.artists_by_weekend), 12)]
        typing_action(chat_id)
        for chunk in artists_chunks:
            chunk_str = "\n\n--------------------------------\n\n".join(
                str(artist.__str__(user_session.selected_weekend)) for artist in chunk)
            bot.send_message(chat_id, chunk_str, parse_mode='HTML', disable_web_page_preview=True)

        user_session.artists_str = ", ".join(
            str(art.__str__(user_session.selected_weekend))
            for art in
            (user_session.my_relevant if user_session.selected_weekend == 'both' else user_session.artists_by_weekend)
        )
    except Exception as e:
        logger.error(f"Username is: {user_session.username}, Error messaging artists to user: {str(e)}")
        bot.send_message(chat_id, "An error occurred while processing the artist list. Please try again later.")


def process_weekend_data(chat_id: int, user_session: UserSession) -> None:
    user_session.artists_by_weekend = filter_artists_by_weekend(user_session.my_relevant,
                                                                user_session.selected_weekend.lower())
    typing_action(chat_id)
    list_len = len(user_session.artists_by_weekend if user_session.selected_weekend != 'both' else user_session.my_relevant)
    bot.send_message(chat_id,
                     f"*{user_session.selected_weekend} artists:*\n"
                     f"*{list_len}* artists that have been found in {user_session.selected_weekend}:",
                     parse_mode='Markdown')

    message_artists_to_user(chat_id, user_session)


def add_artists_from_new_playlist(current_artists: List[Artist], new_artists: List[Artist]) -> List[Artist]:
    artist_dict = {artist.name: artist for artist in current_artists}

    for new_artist in new_artists:
        if new_artist.name in artist_dict:
            artist_dict[new_artist.name].songs_num += new_artist.songs_num
        else:
            artist_dict[new_artist.name] = new_artist

    return list(artist_dict.values())


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


@bot.message_handler(func=lambda message: not message.text.startswith(
    "https://open.spotify.com/playlist/") and not message.text.startswith("https://music.youtube.com"))
def handle_invalid_link(message: telebot.types.Message) -> None:
    typing_action(message.chat.id)
    bot.send_message(message.chat.id, "Please send a valid Spotify or YouTube music link!")


def handle_music_link(message: telebot.types.Message, platform_name: str) -> None:
    chat_id = message.chat.id
    user_session = get_or_create_session(chat_id)
    # if len(user_session.my_relevant) != 0:
    #     typing_action(chat_id)
    #     bot.send_message(chat_id, "Would you like to start? Select your weekend. If you want to add a new playlist, just send it now. ",
    #                      reply_markup=create_weekend_keyboard())

    try:
        bot.send_message(chat_id,
                         "Great! Please wait a moment while I process the playlist...")
        typing_action(chat_id)
        curr_playlist = Playlist(platform=platform_name, link=message.text)
        typing_action(chat_id)
        if curr_playlist.platform == "Unknown":
            bot.send_message(chat_id, "Invalid link!", parse_mode='Markdown')
            logger.warning(f'Username is: {user_session.username} Invalid {platform_name} link received')
            return
        if curr_playlist.link not in [playlist.link for playlist in user_session.playlist_links_list]:
            user_session.playlist_links_list.append(curr_playlist)

        new_artists = get_lineup_artists_from_playlist(curr_playlist)
        user_session.my_relevant = add_artists_from_new_playlist(user_session.my_relevant, new_artists)

        typing_action(chat_id)

        if len(user_session.my_relevant) == 0:
            bot.send_message(chat_id,
                             "No matching artists found in the playlist. Please try a different playlist link.")
        else:
            update_spotify_link(user_session)
            typing_action(chat_id)
            bot.send_message(chat_id,
                             f"Playlist contains {len(user_session.my_relevant)} relevant artists. "
                             f"If you want to add a new playlist, just send it now. "
                             f"If not - please select your weekend:",
                             reply_markup=create_weekend_keyboard())
    except Exception as e:
        logger.error(f"Username is: {user_session.username}, Error in handle_music_link: {str(e)}")
        bot.send_message(chat_id, "An error occurred while processing the playlist. Please try again later.")


@bot.message_handler(func=lambda message: message.text.startswith("https://open.spotify.com/playlist/"))
def handle_spotify_link(message: telebot.types.Message) -> None:
    handle_music_link(message, "Spotify")


@bot.message_handler(func=lambda message: message.text.startswith("https://music.youtube.com"))
def handle_youtube_link(message: telebot.types.Message) -> None:
    handle_music_link(message, "YouTube")


@bot.callback_query_handler(func=lambda call: call.data in WEEKEND_NAMES)
def handle_weekend_selection(call: telebot.types.CallbackQuery) -> None:
    chat_id = call.message.chat.id
    user_session = get_or_create_session(chat_id)
    user_session.selected_weekend = call.data
    bot.answer_callback_query(call.id)
    process_weekend_data(chat_id, user_session)
    typing_action(chat_id)
    bot.send_message(chat_id, "Would you like to generate an AI lineup?",
                     reply_markup=create_generate_lineup_keyboard())


@bot.callback_query_handler(func=lambda call: call.data == 'weekend_all')
def handle_all_weekends(call: telebot.types.CallbackQuery) -> None:
    chat_id = call.message.chat.id
    user_session = get_or_create_session(chat_id)
    bot.answer_callback_query(call.id)
    user_session.selected_weekend = 'both'
    process_weekend_data(chat_id, user_session)
    typing_action(chat_id)
    bot.send_message(chat_id, "Would you like to generate an AI lineup?",
                     reply_markup=create_generate_lineup_keyboard())


@bot.callback_query_handler(func=lambda call: call.data == 'generate_ai_lineup')
def handle_generate_ai_lineup(call: telebot.types.CallbackQuery) -> None:
    chat_id = call.message.chat.id
    user_session = get_or_create_session(chat_id)
    bot.answer_callback_query(call.id)
    generate_and_print_ai_lineup(user_session, chat_id)
    typing_action(chat_id)
    bot.send_message(chat_id, "Would you like to start over?",
                     reply_markup=create_finish_keyboard())


@bot.callback_query_handler(func=lambda call: call.data == 'done')
def handle_done(call: telebot.types.CallbackQuery) -> None:
    chat_id = call.message.chat.id
    user_session = get_or_create_session(chat_id)
    user_session.clear_all()
    bot.answer_callback_query(call.id)
    typing_action(chat_id)
    bot.send_message(chat_id, "Thank you for using the bot!")


@bot.callback_query_handler(func=lambda call: call.data == 'start_again')
def handle_start_again(call: telebot.types.CallbackQuery) -> None:
    chat_id = call.message.chat.id
    user_session = get_or_create_session(chat_id)
    user_session.clear_all()
    typing_action(chat_id)
    bot.send_message(chat_id, "Starting over! Please send a playlist link to get started:")
    logger.info(f'Username is: {user_session.username}, clicked start again')


# Error handler
@bot.message_handler(func=lambda message: True)
def fallback_handler(message: telebot.types.Message) -> None:
    chat_id = message.chat.id
    typing_action(chat_id)
    bot.send_message(chat_id, "Unrecognized command. Please send a valid Spotify or YouTube music link.")


# Start the bot
if __name__ == "__main__":
    bot.polling(none_stop=True)
