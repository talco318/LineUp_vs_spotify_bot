"""
Flask Web App for Tomorrowland LineUp Finder
=============================================
A web-based alternative to the Telegram bot.
Users can paste playlist URLs and get matching Tomorrowland artists.
"""
from flask import Flask, request, jsonify, abort, render_template
import os
import sys
import json
import logging
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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
WEBHOOK_BASE_URL = os.getenv("TELEGRAM_WEBHOOK_BASE_URL", "").rstrip("/")
WEBHOOK_PATH = telegram_bot_api if telegram_bot_api else "webhook"

# Initialize Spotify Manager
spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID_API")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET_API")
spotify_manager = SpotifyManager(spotify_client_id, spotify_client_secret)

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


# ============== MAIN ==============

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🎵 Tomorrowland LineUp Finder - Web App")
    print("="*50)
    print(f"📁 Template folder: {template_dir}")
    print(f"✅ Template exists: {template_dir.exists()}")
    print(f"🌐 Open in browser: http://127.0.0.1:5000/")
    print("="*50 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=True)
