"""
Main Bot Configuration File - KingRadio Version
"""
import os
from dataclasses import dataclass

@dataclass
class SystemFiles:
    """System File Paths"""
    QUEUE = "queue.txt"
    DEFAULT_PLAYLIST = "default_playlist.txt"
    PLAYLIST_STATE = "playlist_state.json"
    HISTORY = "play_history.txt"
    FAILED_REQUESTS = "failed_requests.txt"
    SONG_NOTIFICATIONS = "song_notifications.json"

@dataclass
class StreamSettings:
    """Stream Settings - KingRadio (Icecast) Configuration"""
    # KingRadio ke liye updated details
    STREAM_URL = "https://play.radioking.io/alex9" # Apna KingRadio URL yahan dalein
    RADIO_SERVER = "live.radioking.com"
    RADIO_PORT = 80 # KingRadio usually uses 8000 or 8010
    RADIO_USERNAME = "Alex_YT" # Icecast default username
    RADIO_MOUNT_POINT = "/alex9" # KingRadio ka mount point (e.g., /live ya /radio)
    
    # Password environment variable se ya phir direct yahan change karein
    RADIO_PASSWORD = os.environ.get("RADIO_PASSWORD", "Ayush111")
    
    RADIO_ENCODING = "MP3"
    MIN_SONG_DURATION = 30
    MAX_RETRY_ATTEMPTS = 3
    STREAM_BITRATE = "128k" # KingRadio supports 128k for better quality
    CACHE_DIR = "song_cache"
    
    AUTO_CLEAN_ENABLED = True
    MAX_CACHE_SIZE_MB = 64
    MAX_CACHED_SONGS = 40
    KEEP_USER_CACHE = False
    KEEP_DEFAULT_CACHE = False
    CACHE_CLEAN_INTERVAL_SEC = 120
    PREDOWNLOAD_ENABLED = False
    NO_CACHE = True

@dataclass
class LogSettings:
    """Logging Settings"""
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

@dataclass
class HighriseSettings:
    """Highrise Settings"""
    BOT_TOKEN = os.environ.get("HIGHRISE_BOT_TOKEN", "c4ba100bbcea7e901f955ee997faa2846f4e030170245207a9155e2f1ff8264f")
    ROOM_ID = os.environ.get("HIGHRISE_ROOM_ID", "663da7935f9d75c3f42bf455")
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "Ayysun")
    
    MODERATORS = []
    VIP_PRICE = 500 

# Default Songs List
DEFAULT_SONGS = [
    "JadaL - I'm in Love with a Wali",
    "JadaL - Yumain o Leila",
    "JadaL - Ana Bakhaf Min El Commit",
    "JadaL - Malyoun",
    "JadaL - El Makina",
    "Massar Egbari - Nehayat El Hakawy",
    "Massar Egbari - Cherrophobia",
    "Massar Egbari - Toaa we Teoum",
    "Massar Egbari - Matloub Habib",
    "Massar Egbari - Ana Hweit",
    "Tamer Hosny - Nasseny Leh",
    "Tamer Hosny - 180 Daraga",
    "Tamer Hosny - Kifayak Aazar",
    "Tamer Hosny - Eish Besho2ak",
    "Tamer Hosny - Helw El Makan",
    "Cairokee - Kan Lak Ma'aya",
    "Cairokee - Marbout Be Astek",
    "Cairokee - El Sekka Shemal",
    "The Weeknd - Blinding Lights",
    "The Weeknd - Save Your Tears",
    "Arctic Monkeys - Do I Wanna Know",
    "Arctic Monkeys - I Wanna Be Yours",
    "Coldplay - Yellow",
    "Coldplay - Viva La Vida",
    "Imagine Dragons - Believer",
    "Imagine Dragons - Demons",
    "Twenty One Pilots - Stressed Out",
    "Billie Eilish - bad guy",
    "Glass Animals - Heat Waves",
    "Harry Styles - As It Was",
    "Adele - Easy On Me",
    "Ed Sheeran - Shape of You",
    "Dua Lipa - Levitating",
    "Post Malone - Circles",
    "The Neighbourhood - Sweater Weather",
    "Tame Impala - The Less I Know The Better",
    "Foster The People - Pumped Up Kicks",
    "Hozier - Take Me To Church",
    "CKay - Love Nwantiti",
    "Rema - Calm Down",
    "Tom Odell - Another Love",
    "Ruth B. - Dandelions",
    "Stephen Sanchez - Until I Found You",
    "JVKE - Golden Hour",
    "d4vd - Here With Me",
    "Sia - Unstoppable",
    "Sia - Chandelier",
    "ZAYN - Dusk Till Dawn",
    "Maroon 5 - Memories",
    "OneRepublic - Counting Stars",
]
