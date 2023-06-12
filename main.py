import spotify_funcs
import telebot
import json
from artist import Artist
import requests
import random
import APIs

bot = telebot.TeleBot(APIs.telegram_Bot_API)


def get_relevant(link):
    playlist_artists = spotify_funcs.get_artists_from_spotify(link)
    lineup_data = extract_artists_from_tml()

    artist_map = {artist.name: artist for artist in lineup_data}
    my_relevant = [artist_map[artist.name] for artist in playlist_artists if artist.name in artist_map]

    return my_relevant


def find_artist_and_update(artists, artist_name, songs_num, new_date, weekend, host_name_and_stage):
    for artist in artists:
        if artist.name == artist_name:
            artist.songs_num = songs_num
            artist.add_show(weekend, host_name_and_stage, new_date)
            break


def read_json_data(url):
    user_agents_list = [
        'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
    ]
    response = requests.get(url, headers={'User-Agent': random.choice(user_agents_list)})
    data = response.json()
    return data


def extract_artists_from_tml():
    artists = []
    files = ['tml2023w1.json', 'tml2023w2.json']
    for file in files:
        url = f'https://clashfinder.com/data/event/{file}'
        data = read_json_data(url)
        locations = data["locations"]
        for location in locations:
            events = location["events"]
            for event in events:
                name = event["name"]
                start = event["start"]
                end = event["end"]
                weekend = 'weekend 1' if file == 'tml2023w1.json' else 'weekend 2'
                host_name_and_stage = location["name"]
                time = f'{start} to {end}'
                artist = Artist(name, host_name_and_stage, weekend, time)
                existing_artist = next((a for a in artists if a.name == name), None)
                if existing_artist:
                    find_artist_and_update(artists, name, 0, time, weekend, host_name_and_stage)
                else:
                    artists.append(artist)
    return artists


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
    if not spotify_funcs.is_link_good(str(message.text)):
        bot.send_message(message.chat.id, "Invalid link!", parse_mode='Markdown')
        return

    new_link = spotify_funcs.cut_content_after_question_mark(message.text)
    my_relevant = get_relevant(new_link)

    num_artists = len(my_relevant)
    bot.send_message(message.chat.id, f"Number of artists found: {num_artists}", parse_mode='Markdown')

    for art in my_relevant:
        bot.send_message(message.chat.id, str(art), parse_mode='Markdown')
        print(art, "\n")

    print("--------------------------------------------------------------")


bot.infinity_polling()
