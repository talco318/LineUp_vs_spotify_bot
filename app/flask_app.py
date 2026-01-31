"""
Flask Web App for Tomorrowland LineUp Finder
=============================================
A web-based alternative to the Telegram bot.
Users can paste playlist URLs and get matching Tomorrowland artists.
"""
from flask import Flask, request, jsonify, abort, render_template, redirect, session, url_for
from urllib.parse import urlencode
import os
import sys
import json
import logging
import secrets
import requests
from pathlib import Path

# Setup paths FIRST
project_root = Path(__file__).resolve().parents[1]
app_dir = Path(__file__).resolve().parent
template_dir = app_dir / 'templates'
static_dir = app_dir / 'static'

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import project modules
from telebot.types import Update
from app.telegram_bot import bot, user_sessions, telegram_bot_api
from app.utils.spotify_funcs import SpotifyManager, get_spotify_artist_link
import app.utils.youtube_funcs as youtube_funcs
from tomorrowland_lineup_managment.public_funcs import extract_artists_from_tomorrowland_lineup
from AI import AI_funcs_gemini as Gemini

# Create Flask app with explicit template and static folders
app = Flask(__name__, template_folder=str(template_dir), static_folder=str(static_dir))
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
WEBHOOK_BASE_URL = os.getenv("TELEGRAM_WEBHOOK_BASE_URL", "").rstrip("/")
WEBHOOK_PATH = telegram_bot_api if telegram_bot_api else "webhook"

# Spotify OAuth Configuration
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
# Note: Make sure to add this redirect URI in your Spotify Developer Dashboard:
# http://localhost:5000/spotify/callback
# AND/OR http://127.0.0.1:5000/spotify/callback
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:5000/spotify/callback")
SPOTIFY_SCOPES = "playlist-read-private playlist-read-collaborative user-library-read"

# Initialize Spotify Manager
spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID_API")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET_API")
spotify_manager = SpotifyManager(spotify_client_id, spotify_client_secret)

# Stage locations for festival map (relative coordinates)
STAGE_LOCATIONS = {
    "Mainstage": {"x": 50, "y": 20, "color": "#FF6B6B", "size": "large"},
    "Freedom Stage": {"x": 20, "y": 35, "color": "#4ECDC4", "size": "large"},
    "Atmosphere": {"x": 80, "y": 35, "color": "#45B7D1", "size": "medium"},
    "Core": {"x": 30, "y": 55, "color": "#96CEB4", "size": "medium"},
    "KARA SAVI": {"x": 70, "y": 55, "color": "#FFEAA7", "size": "medium"},
    "Cage": {"x": 15, "y": 75, "color": "#DDA0DD", "size": "small"},
    "Rose Garden": {"x": 85, "y": 75, "color": "#98D8C8", "size": "small"},
    "Crystal Garden": {"x": 40, "y": 80, "color": "#F7DC6F", "size": "small"},
    "Tulip": {"x": 60, "y": 80, "color": "#BB8FCE", "size": "small"},
    "The Library": {"x": 50, "y": 65, "color": "#85C1E9", "size": "small"},
    "Elixir": {"x": 25, "y": 90, "color": "#F1948A", "size": "small"},
    "Youphoria": {"x": 75, "y": 90, "color": "#82E0AA", "size": "small"},
}

# Log startup info
logger.info(f"Template folder: {template_dir}")
logger.info(f"Template folder exists: {template_dir.exists()}")


# ============== HELPER FUNCTIONS ==============

def get_matching_artists(playlist_artists, lineup_data):
    """Get matching artists between playlist and lineup"""
    matching_artists = []
    for playlist_artist in playlist_artists:
        for lineup_artist in lineup_data:
            if lineup_artist.name.lower() == playlist_artist.name.lower():
                lineup_artist.songs_num = playlist_artist.songs_num
                matching_artists.append(lineup_artist)
                break
    return matching_artists


def artist_to_dict(artist):
    """Convert Artist object to dictionary for JSON response"""
    result = {
        "name": artist.name,
        "songs_num": getattr(artist, 'songs_num', 0),
        "spotify_link": getattr(artist, 'spotify_link', None),
    }

    if artist.show:
        result["show"] = {
            "weekend_number": getattr(artist.show, 'weekend_number', ''),
            "host_name_and_stage": getattr(artist.show, 'host_name_and_stage', ''),
            "date": getattr(artist.show, 'date', ''),
        }

    if artist.show2:
        result["show2"] = {
            "weekend_number": getattr(artist.show2, 'weekend_number', ''),
            "host_name_and_stage": getattr(artist.show2, 'host_name_and_stage', ''),
            "date": getattr(artist.show2, 'date', ''),
        }

    return result


# ============== WEB ROUTES ==============

@app.route("/")
def index():
    """Main page - Web UI for playlist analysis"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        return f"<h1>Error loading page</h1><p>{str(e)}</p>", 500


@app.route("/analyze", methods=["POST"])
def analyze_playlist():
    """Analyze a playlist and return matching Tomorrowland artists"""
    try:
        data = request.get_json()
        playlist_url = data.get('playlist_url', '').strip()
        platform = data.get('platform', 'spotify')

        if not playlist_url:
            return jsonify({"ok": False, "error": "לא סופק קישור לפלייליסט"}), 400

        logger.info(f"Analyzing playlist: {playlist_url} (platform: {platform})")

        # Get artists from playlist
        if platform == 'spotify' or 'spotify.com' in playlist_url:
            playlist_artists = spotify_manager.get_artists_from_spotify_playlist(playlist_url)
        else:
            playlist_artists = youtube_funcs.get_artists_from_youtube_playlist(playlist_url)

        # Get Tomorrowland lineup
        lineup_data = extract_artists_from_tomorrowland_lineup()

        # Find matching artists
        matching_artists = get_matching_artists(playlist_artists, lineup_data)

        # Add Spotify links
        for artist in matching_artists:
            if not getattr(artist, 'spotify_link', None):
                artist.spotify_link = get_spotify_artist_link(spotify_manager, artist.name)

        # Convert to JSON-serializable format
        artists_data = [artist_to_dict(artist) for artist in matching_artists]

        logger.info(f"Found {len(artists_data)} matching artists")

        return jsonify({
            "ok": True,
            "artists": artists_data,
            "total": len(artists_data)
        })

    except Exception as e:
        logger.exception(f"Error analyzing playlist: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/generate_lineup", methods=["POST"])
def generate_lineup():
    """Generate AI lineup recommendation - returns structured JSON"""
    try:
        data = request.get_json()
        artists = data.get('artists', [])
        weekend = data.get('weekend', 'both')

        if not artists:
            return jsonify({"ok": False, "error": "לא סופקו אמנים"}), 400

        logger.info(f"Generating AI lineup for {len(artists)} artists, weekend: {weekend}")

        artists_str = ", ".join(artists)

        # Generate AI response (returns JSON string)
        response = Gemini.generate_response(artists_str, weekend)

        # Parse the JSON response
        try:
            lineup_data = json.loads(response)
            return jsonify({
                "ok": True,
                "lineup": lineup_data
            })
        except json.JSONDecodeError:
            # Fallback: return raw text if JSON parsing fails
            logger.warning("Could not parse Gemini response as JSON, returning raw")
            return jsonify({
                "ok": True,
                "lineup": {
                    "days": [],
                    "tips": [],
                    "raw_text": response,
                    "parse_error": True
                }
            })

    except Exception as e:
        logger.exception(f"Error generating lineup: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


# ============== API ROUTES ==============

@app.route("/api")
def api_info():
    """API endpoint - returns JSON"""
    return jsonify({
        "ok": True,
        "message": "Tomorrowland LineUp Finder API",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Web UI"},
            {"path": "/analyze", "method": "POST", "description": "Analyze playlist"},
            {"path": "/generate_lineup", "method": "POST", "description": "Generate AI lineup"},
            {"path": "/status", "method": "GET", "description": "Server status"},
        ],
    })


@app.route("/status")
def status():
    """Status endpoint - returns JSON with server status"""
    try:
        webhook_info = bot.get_webhook_info()
        webhook_url = getattr(webhook_info, 'url', None) if webhook_info else None
    except Exception:
        webhook_url = None

    return jsonify({
        "ok": True,
        "sessions_count": len(user_sessions),
        "webhook_set": bool(webhook_url),
        "webhook_url": webhook_url,
        "webhook_base_env_set": bool(WEBHOOK_BASE_URL)
    })


# ============== TELEGRAM WEBHOOK ROUTES ==============

@app.route("/set_webhook", methods=["GET", "POST"])
def set_webhook():
    """Set Telegram webhook"""
    if not WEBHOOK_BASE_URL:
        return jsonify({"ok": False, "error": "TELEGRAM_WEBHOOK_BASE_URL not set"}), 400

    webhook_url = f"{WEBHOOK_BASE_URL}/{WEBHOOK_PATH}"
    try:
        success = bot.set_webhook(webhook_url)
        logger.info("Set webhook to %s: %s", webhook_url, success)
        return jsonify({"ok": True, "webhook_url": webhook_url})
    except Exception as e:
        logger.exception("Failed to set webhook: %s", e)
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/delete_webhook", methods=["GET", "POST"])
def delete_webhook():
    """Delete Telegram webhook"""
    try:
        success = bot.remove_webhook()
        logger.info("Deleted webhook: %s", success)
        return jsonify({"ok": success})
    except Exception as e:
        logger.exception("Failed to delete webhook: %s", e)
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route(f"/{WEBHOOK_PATH}", methods=["POST"])
def telegram_webhook():
    """Receive Telegram updates via webhook"""
    content_type = request.headers.get("Content-Type", "")
    if not content_type.lower().startswith("application/json"):
        abort(400)

    try:
        json_string = request.get_data().decode("utf-8")
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
    except Exception as e:
        logger.exception("Failed to process incoming update: %s", e)

    return "OK", 200


# ============== SPOTIFY OAUTH ROUTES ==============

@app.route("/spotify/login")
def spotify_login():
    """Redirect to Spotify OAuth authorization"""
    state = secrets.token_urlsafe(16)
    session['spotify_state'] = state

    params = {
        'client_id': spotify_client_id,
        'response_type': 'code',
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'scope': SPOTIFY_SCOPES,
        'state': state,
        'show_dialog': 'true'
    }
    auth_url = f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"
    return redirect(auth_url)


@app.route("/spotify/callback")
def spotify_callback():
    """Handle Spotify OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')

    if error:
        logger.error(f"Spotify OAuth error: {error}")
        return redirect('/?spotify_error=' + error)

    if state != session.get('spotify_state'):
        logger.error("Spotify OAuth state mismatch")
        return redirect('/?spotify_error=state_mismatch')

    # Exchange code for token
    try:
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': SPOTIFY_REDIRECT_URI,
            'client_id': spotify_client_id,
            'client_secret': spotify_client_secret
        }
        response = requests.post(SPOTIFY_TOKEN_URL, data=token_data)

        if response.ok:
            tokens = response.json()
            session['spotify_token'] = tokens['access_token']
            session['spotify_refresh'] = tokens.get('refresh_token')
            session['spotify_expires'] = tokens.get('expires_in', 3600)
            logger.info("Spotify OAuth successful")
            return redirect('/?spotify=connected')
        else:
            logger.error(f"Spotify token exchange failed: {response.text}")
            return redirect('/?spotify_error=token_failed')

    except Exception as e:
        logger.exception(f"Spotify OAuth exception: {e}")
        return redirect('/?spotify_error=exception')


@app.route("/spotify/playlists")
def get_spotify_playlists():
    """Get user's Spotify playlists"""
    token = session.get('spotify_token')
    if not token:
        return jsonify({"ok": False, "error": "Not connected to Spotify"}), 401

    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get('https://api.spotify.com/v1/me/playlists?limit=50', headers=headers)

        if response.ok:
            data = response.json()
            playlists = [{
                'id': p['id'],
                'name': p['name'],
                'image': p['images'][0]['url'] if p.get('images') else None,
                'tracks': p['tracks']['total'],
                'uri': p['uri']
            } for p in data.get('items', [])]

            return jsonify({"ok": True, "playlists": playlists})
        elif response.status_code == 401:
            # Token expired, clear session
            session.pop('spotify_token', None)
            return jsonify({"ok": False, "error": "Token expired"}), 401
        else:
            return jsonify({"ok": False, "error": "Failed to fetch playlists"}), 500

    except Exception as e:
        logger.exception(f"Error fetching Spotify playlists: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/spotify/playlist/<playlist_id>/analyze")
def analyze_spotify_playlist_direct(playlist_id):
    """Analyze a Spotify playlist directly using OAuth token"""
    token = session.get('spotify_token')
    if not token:
        return jsonify({"ok": False, "error": "Not connected to Spotify"}), 401

    try:
        # Get playlist tracks using user's token
        headers = {'Authorization': f'Bearer {token}'}
        tracks_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=100'

        all_artists = {}
        while tracks_url:
            response = requests.get(tracks_url, headers=headers)
            if not response.ok:
                return jsonify({"ok": False, "error": "Failed to fetch playlist"}), 500

            data = response.json()
            for item in data.get('items', []):
                track = item.get('track')
                if track and track.get('artists'):
                    for artist in track['artists']:
                        artist_name = artist['name']
                        if artist_name in all_artists:
                            all_artists[artist_name]['count'] += 1
                        else:
                            all_artists[artist_name] = {
                                'name': artist_name,
                                'count': 1,
                                'spotify_id': artist.get('id')
                            }

            tracks_url = data.get('next')

        # Get Tomorrowland lineup
        lineup_data = extract_artists_from_tomorrowland_lineup()

        # Find matching artists
        matching = []
        for lineup_artist in lineup_data:
            artist_key = lineup_artist.name
            # Check for exact or close match
            for playlist_artist_name, playlist_data in all_artists.items():
                if lineup_artist.name.lower() == playlist_artist_name.lower():
                    lineup_artist.songs_num = playlist_data['count']
                    lineup_artist.spotify_link = f"https://open.spotify.com/artist/{playlist_data['spotify_id']}" if playlist_data.get('spotify_id') else None
                    matching.append(lineup_artist)
                    break

        artists_data = [artist_to_dict(artist) for artist in matching]

        return jsonify({
            "ok": True,
            "artists": artists_data,
            "total": len(artists_data)
        })

    except Exception as e:
        logger.exception(f"Error analyzing Spotify playlist: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/spotify/status")
def spotify_status():
    """Check Spotify connection status"""
    connected = 'spotify_token' in session
    return jsonify({
        "ok": True,
        "connected": connected
    })


@app.route("/spotify/logout")
def spotify_logout():
    """Disconnect from Spotify"""
    session.pop('spotify_token', None)
    session.pop('spotify_refresh', None)
    session.pop('spotify_state', None)
    return jsonify({"ok": True, "message": "Disconnected from Spotify"})


# ============== MAP ROUTES ==============

@app.route("/api/map/stages")
def get_stages():
    """Get all stage locations for the festival map"""
    return jsonify({
        "ok": True,
        "stages": STAGE_LOCATIONS
    })


@app.route("/api/map/walking-times")
def get_walking_times():
    """Get walking times between stages from CSV"""
    try:
        walking_times = {}
        csv_path = project_root / 'walking_time.csv'

        if csv_path.exists():
            import csv
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                headers = next(reader)
                for row in reader:
                    if row:
                        stage_from = row[0]
                        walking_times[stage_from] = {}
                        for i, time in enumerate(row[1:], 1):
                            if i < len(headers):
                                walking_times[stage_from][headers[i]] = int(time) if time.isdigit() else 0

        return jsonify({
            "ok": True,
            "walking_times": walking_times
        })
    except Exception as e:
        logger.exception(f"Error loading walking times: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


# ============== CALENDAR ROUTES ==============

@app.route("/api/calendar/generate")
def generate_calendar_event():
    """Generate calendar event data for an artist show"""
    artist = request.args.get('artist')
    stage = request.args.get('stage')
    date = request.args.get('date')
    start_time = request.args.get('start')
    end_time = request.args.get('end')

    if not all([artist, stage, date]):
        return jsonify({"ok": False, "error": "Missing parameters"}), 400

    # Parse date and time - expected format: "FRIDAY 2025-07-18 14:00:00 - 2025-07-18 15:00:00"
    try:
        import re
        from datetime import datetime

        # Extract start and end datetime
        time_match = re.search(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})', date)
        if time_match:
            date_str = time_match.group(1)
            time_str = time_match.group(2)
            start_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

            # Try to find end time
            end_match = re.search(r'-\s*\d{4}-\d{2}-\d{2}\s+(\d{2}:\d{2})', date)
            if end_match:
                end_time_str = end_match.group(1)
                end_dt = datetime.strptime(f"{date_str} {end_time_str}", "%Y-%m-%d %H:%M")
            else:
                # Default 1 hour duration
                from datetime import timedelta
                end_dt = start_dt + timedelta(hours=1)
        else:
            # Fallback
            start_dt = datetime.now()
            from datetime import timedelta
            end_dt = start_dt + timedelta(hours=1)

        # Format for calendar URLs
        def format_google(dt):
            return dt.strftime("%Y%m%dT%H%M%S")

        def format_ics(dt):
            return dt.strftime("%Y%m%dT%H%M%S")

        event_title = f"🎵 {artist} @ Tomorrowland"
        event_location = f"Tomorrowland - {stage}"
        event_description = f"Performance by {artist} at {stage}"

        # Google Calendar URL
        google_params = {
            'action': 'TEMPLATE',
            'text': event_title,
            'dates': f"{format_google(start_dt)}/{format_google(end_dt)}",
            'location': event_location,
            'details': event_description
        }
        google_url = f"https://calendar.google.com/calendar/render?{urlencode(google_params)}"

        # ICS content for Apple/Outlook
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//TML LineUp//EN
BEGIN:VEVENT
DTSTART:{format_ics(start_dt)}
DTEND:{format_ics(end_dt)}
SUMMARY:{event_title}
LOCATION:{event_location}
DESCRIPTION:{event_description}
BEGIN:VALARM
TRIGGER:-PT30M
ACTION:DISPLAY
DESCRIPTION:Reminder: {artist} in 30 minutes!
END:VALARM
END:VEVENT
END:VCALENDAR"""

        return jsonify({
            "ok": True,
            "google_url": google_url,
            "ics_content": ics_content,
            "event": {
                "title": event_title,
                "location": event_location,
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat()
            }
        })

    except Exception as e:
        logger.exception(f"Error generating calendar event: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


# ============== MAIN ==============

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎵 Tomorrowland LineUp Finder - Web App")
    print("="*60)
    print(f"📁 Template folder: {template_dir}")
    print(f"✅ Template exists: {template_dir.exists()}")
    print(f"🌐 Open in browser: http://localhost:5000/")
    print("-"*60)
    print("🎧 SPOTIFY SETUP:")
    print(f"   Redirect URI: {SPOTIFY_REDIRECT_URI}")
    print("   ⚠️  Add this URI to your Spotify Developer Dashboard:")
    print("      https://developer.spotify.com/dashboard")
    print("      Go to your app → Settings → Redirect URIs")
    print("="*60 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=True)
