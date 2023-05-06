import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from bs4 import BeautifulSoup
import telebot
import artist as artists_class
import re


your_client_id = '47b7fe5aad594079b5c0d9d4c62819c2'
your_client_secret = '9979cf4e8f524bcdb1702816b79d2988'
YOUR_API_TOKEN = '6117611777:AAG7B5P8aLOWYyxh2T3l5pfYmCqcKUhb_6s'



def cut_content_after_question_mark(link):
  # Use regular expression to match the question mark and the content after it
  match = re.search(r"(.*?)(\?.*)", link)

  # If the match is found, return the content before the question mark
  if match:
    return match.group(1)

  # Otherwise, return the original link
  else:
    return link


def get_artists_from_spotify(playlist_link):
    # Replace with your own Spotify API credentials
    client_id = your_client_id
    client_secret = your_client_secret

    # Authenticate with Spotify API
    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Retrieve the playlist ID from the link
    playlist_id = playlist_link.split('/')[-1]

    # Retrieve the track objects from the playlist
    results = sp.playlist_items(playlist_id, fields='items(track(name, artists(name)))')

    # Extract the artists' names from the track objects
    artists = []
    for track in results['items']:
        for artist in track['track']['artists']:
            if artist['name'] not in artists:
                artists.append(artist['name'])
    return artists


def get_relevant(link):
    playlist_artists = get_artists_from_spotify(link)
    lineup_data = extract_artists_from_tml()
    my_relavant = []
    for art in lineup_data:
        if art.name in playlist_artists:
            if art not in my_relavant:
                my_relavant.append(art)
    return my_relavant


def get_weekend(date):
    # Use regular expression to match the day and the number
    match = re.search(r"(\w+) (\d+)", date)

    # If the match is found, print the number
    if match:
        number = match.group(2)
    if number in ['21','22','23']:
        return 1
    else:
        return 2

def extract_artists_from_tml():
    response = requests.get('https://www.tomorrowland.com/en/festival/line-up/stages')
    artists = []
    soup = BeautifulSoup(response.content, "html.parser")
    weekends = soup.find_all('div', class_="weekend-switch")
    days = soup.find_all('div', class_="eventday")
    for day in days:
        data_eventday = day.attrs['data-eventday']
        stages = day.find_all('div', class_="stage")
        for stage_div in stages:
            host_name = stage_div.find('div', class_="stage__heading").text
            host_name = host_name.lstrip()
            host_name = host_name.rstrip()
            stage_contents = stage_div.find_all('div', class_='stage__content')

            for stage in stage_contents:
                stage_location = stage.find('p')
                if (stage_location):
                    stage_location= stage_location.text

                for li_element in stage.find_all("li"):
                    # Get the text content of the `<li>` element
                    artist_name = li_element.text
                    artist_name = artist_name.lstrip()
                    artist_name = artist_name.rstrip()
                    if(stage_location):
                        host_name_and_stage = str(stage_location) + ", " + str(host_name)
                    else:
                        host_name_and_stage = host_name


                    new_art = artists_class.Artist(artist_name, host_name_and_stage, "Weekend "+ str(get_weekend(data_eventday)), data_eventday)
                    # new_art = artists_class.Artist(artist_name, host_name_and_stage, "Weekend ", data_eventday)

                    artists.append(new_art)
    return artists


if __name__ == '__main__':
    # link = input("Please enter playlist link\n")
    # my_relavant = get_relevant(link)
    # print("Number of artists that has been found: ", len(my_relavant))
    # for art in my_relavant:
    #     print(art, "\n")
    # print("Number of artists that has been found: ", len(my_relavant))

    bot = telebot.TeleBot(YOUR_API_TOKEN)
    @bot.message_handler(commands=["start"])
    def start(message):
        bot.send_message(message.chat.id, "Hello! I am the telegram bot. \nTo get started - send a playlist link:")
        @bot.message_handler(func=lambda message: not message.text.startswith("https://open.spotify.com/playlist/"))
        def greet(message):
            bot.send_message(message.chat.id, "Send spotify link only!")

        @bot.message_handler(func=lambda message: message.text.startswith("https://open.spotify.com/playlist/"))
        def greet(message):
            newlink = cut_content_after_question_mark(message.text)
            my_relavant = get_relevant(newlink)

            mess = "Number of artists that has been found: "+ str(len(my_relavant))
            bot.send_message(message.chat.id, mess)

            for art in my_relavant:
                #bot.send_message("Artist: ", art.name, " Stage: ", art.stage)
                bot.send_message(message.chat.id, art)

                print(art,"\n")
    bot.polling()