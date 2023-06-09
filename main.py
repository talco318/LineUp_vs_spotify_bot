import spotify_funcs
import telebot
import json
from artist import Artist



#telegram bot api:
YOUR_API_TOKEN = '6184179776:AAGaWgK7BB3Vv7_APE8YJgRvYQ81fxx_s6w'


def get_relevant(link):
    playlist_artists = spotify_funcs.get_artists_from_spotify(link)
    lineup_data = extract_artists_from_tml()
    my_relavant = []

    for artist_name in playlist_artists:
        for artist_obj in lineup_data:
            if artist_name == artist_obj.name:
                my_relavant.append(artist_obj)
                break
    return my_relavant


def find_artist_and_update(artists, artist_name, new_date, weekend, host_name_and_stage):
    for artist in artists:
        if artist.name == artist_name:
            artist.host_name_and_stage = artist.host_name_and_stage + '\n' + host_name_and_stage
            artist.date = artist.date + '\n' + new_date
            artist.weekend = artist.weekend + '\n' + weekend
            break  # Exit the loop after updating the first matching


def is_artist_in_array(artist_name, array):
    for artist in array:
        if artist.name == artist_name:
            return True, artist
    return False


def extract_artists_from_tml():
    artists = []
    files = ['tml2023w1.json', 'tml2023w2.json']
    for file in files:
        with open(file) as file:
            data = json.load(file)
            locations = data["locations"]
            for location in locations:
                events = location["events"]
                for event in events:
                    name = event["name"]
                    start = event["start"]
                    end = event["end"]
                    # datetime_obj = datetime.strptime(start, "%Y-%m-%d %H:%M")
                    weekend = 'weekend 1' if file.name == 'tml2023w1.json' else 'weekend 2'
                    host_name_and_stage = location["name"]
                    time = start + " to " + end
                    artist = Artist(name, host_name_and_stage, weekend, time)
                    if is_artist_in_array(name, artists):
                        find_artist_and_update(artists, artist.name, time, weekend, host_name_and_stage)
                    else:
                        artists.append(artist)
    return artists





if __name__ == '__main__':
    # link = input("Please enter playlist link\n")
    # lineup_data = extract_artists_from_tml()
    # my_relavant = get_relevant(link)
    # print("Number of artists that has been found: ", len(my_relavant))
    # for art in my_relavant:
    #     print(art, "\n")
    # print("Number of artists that has been found: ", len(my_relavant))

    bot = telebot.TeleBot(YOUR_API_TOKEN)


    @bot.message_handler(commands=["start"])
    def start(message):
        bot.send_message(message.chat.id, "Hello! I am the telegram bot. \nTo get started - send a playlist link:")
        username = message.from_user.username
        print('username is: ' + username + ' wrote:\n' + str(message.text))

        @bot.message_handler(func=lambda message: not message.text.startswith("https://open.spotify.com/playlist/"))
        def greet(message):
            bot.send_message(message.chat.id, "Send spotify link only!")
            username = message.from_user.username
            print('username is: ' + username + ' wrote:\n' + str(message.text))


    @bot.message_handler(func=lambda message: message.text.startswith("https://open.spotify.com/playlist/"))
    def greet(message):
        username = message.from_user.username
        print('username is: ' + username + ' wrote:\n' + str(message.text))
        if (not spotify_funcs.is_link_good(str(message.text))):
            bot.send_message(message.chat.id, "link not valid!", parse_mode='Markdown')
            return
        newlink = spotify_funcs.cut_content_after_question_mark(message.text)
        my_relavant = get_relevant(newlink)

        mess = "Number of artists that has been found: " + str(len(my_relavant))
        bot.send_message(message.chat.id, mess, parse_mode='Markdown')

        for art in my_relavant:
            # bot.send_message("Artist: ", art.name, " Stage: ", art.stage)
            bot.send_message(message.chat.id, art, parse_mode='Markdown')
            print(art, "\n")

        print("--------------------------------------------------------------")


    bot.polling()
