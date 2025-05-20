from flask import Flask, request, jsonify
from flask_cors import CORS
from telegram_bot import (
    get_lineup_artists_from_playlist,
    filter_artists_by_weekend
)
import AI.AI_funcs_gemini as Gemini
from tomorrowland_lineup_managment.public_funcs import extract_artists_from_tomorrowland_lineup  # Your existing function

app = Flask(__name__)
CORS(app)  # This allows the React frontend to call the API


@app.route('/api/process-playlist', methods=['POST'])
def process_playlist():
    data = request.json
    playlist_url = data['url']
    try:
        # This function already uses spotify_manager internally
        artists = get_lineup_artists_from_playlist(playlist_url)

        # Convert artists to a serializable format
        serialized_artists = []
        for artist in artists:
            artist_dict = {
                'name': artist.name,
                'spotify_link': artist.spotify_link,
                'songs_num': artist.songs_num,
                'show': artist.show.__dict__ if artist.show else None,
                'show2': artist.show2.__dict__ if artist.show2 else None
            }
            serialized_artists.append(artist_dict)

        return jsonify({
            'success': True,
            'artists': serialized_artists
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/generate-lineup', methods=['POST'])
def generate_ai_lineup():
    data = request.json
    artists_str = data['artists_str']
    selected_weekend = data['weekend']

    try:
        # Use the Gemini function exactly as it's used in your Telegram bot
        response = Gemini.generate_response(artists_str, selected_weekend)

        return jsonify({
            'success': True,
            'lineup': response
        })
    except Exception as e:
        print(f"Error generating AI lineup: {str(e)}")  # For debugging
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/artists-by-weekend', methods=['POST'])
def get_artists_by_weekend():
    data = request.json
    artists_data = data['artists']
    weekend = data['weekend']

    try:
        # Convert the JSON data back to Artist objects
        from app.models.artist_model import Artist  # Import your Artist model

        artists = []
        for artist_data in artists_data:
            artist = Artist(name=artist_data['name'])
            artist.spotify_link = artist_data.get('spotify_link')
            artist.songs_num = artist_data.get('songs_num', 0)

            # Reconstruct show objects
            if artist_data.get('show'):
                from collections import namedtuple
                Show = namedtuple('Show', ['weekend_number'])
                artist.show = Show(weekend_number=artist_data['show']['weekend_number'])

            if artist_data.get('show2'):
                Show = namedtuple('Show', ['weekend_number'])
                artist.show2 = Show(weekend_number=artist_data['show2']['weekend_number'])

            artists.append(artist)

        # Now use the filter_artists_by_weekend function
        filtered_artists = filter_artists_by_weekend(artists, weekend)

        # Convert back to serializable format
        serialized_artists = []
        for artist in filtered_artists:
            artist_dict = {
                'name': artist.name,
                'spotify_link': artist.spotify_link,
                'songs_num': artist.songs_num,
                'show': {'weekend_number': artist.show.weekend_number} if artist.show else None,
                'show2': {'weekend_number': artist.show2.weekend_number} if artist.show2 else None
            }
            serialized_artists.append(artist_dict)

        return jsonify({
            'success': True,
            'filtered_artists': serialized_artists
        })
    except Exception as e:
        print(f"Error in get_artists_by_weekend: {str(e)}")  # For debugging
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/get-artist-by-name', methods=['POST'])
def get_artist_by_name():
    data = request.json
    artist_name = data.get('artist_name', '')

    if not artist_name:
        return jsonify({'success': False, 'error': 'Artist name is required'}), 400

    try:
        artists = extract_artists_from_tomorrowland_lineup()
        for artist in artists:
            if artist.name.lower() == artist_name.lower():
                artist_dict = {
                    'name': artist.name,
                    'spotify_link': artist.spotify_link,
                    'songs_num': artist.songs_num,
                    'show': artist.show.__dict__ if artist.show else None,
                    'show2': artist.show2.__dict__ if artist.show2 else None
                }
                return jsonify({'success': True, 'artist': artist_dict})
        return jsonify({'success': False, 'error': 'Artist not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True, port=5000)