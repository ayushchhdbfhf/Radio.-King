#!/usr/bin/env python3
"""
Continuous Playlist Manager System - KingRadio Version
Maintains uninterrupted streaming and plays requests immediately
"""

import os
import time
import json
import logging
import threading
from pathlib import Path
import random
import re
from typing import List, Optional, Dict
from datetime import datetime

# Import settings from config.py (Jahan humne KingRadio set kiya hai)
from config import SystemFiles, StreamSettings, DEFAULT_SONGS, LogSettings

logging.basicConfig(
    level=getattr(logging, LogSettings.LOG_LEVEL, logging.WARNING),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('kingradio_playlist')

class ContinuousPlaylistManager:
    """Continuous Playlist Manager for KingRadio"""

    def __init__(self):
        # System files from config
        self.QUEUE_FILE = SystemFiles.QUEUE
        self.DEFAULT_PLAYLIST_FILE = SystemFiles.DEFAULT_PLAYLIST
        self.CURRENT_STATE_FILE = SystemFiles.PLAYLIST_STATE
        self.HISTORY_FILE = SystemFiles.HISTORY
        self.FAILED_REQUESTS_FILE = SystemFiles.FAILED_REQUESTS

        # System state
        self.current_song = None
        self.is_playing_user_request = False
        self.default_playlist = []
        self.current_default_index = 0
        self.last_played_time = None
        self.disable_default_playlist = False

        # Settings from config (Now using KingRadio bitrates/settings)
        self.min_song_duration = StreamSettings.MIN_SONG_DURATION
        self.shuffle_default_playlist = True
        self.max_retry_attempts = StreamSettings.MAX_RETRY_ATTEMPTS

        # Track failed attempts
        self.failed_requests = {}  # {song: attempts_count}

        # Load saved data
        self.load_default_playlist()
        self.load_state()

        logger.info("🎵 KingRadio Continuous Playlist Manager started")

    def load_default_playlist(self):
        """Load default playlist from file or config"""
        try:
            if Path(self.DEFAULT_PLAYLIST_FILE).exists():
                with open(self.DEFAULT_PLAYLIST_FILE, 'r', encoding='utf-8') as f:
                    self.default_playlist = [
                        line.strip() for line in f.readlines() 
                        if line.strip() and not line.strip().startswith('#')
                    ]
                if self.default_playlist:
                    logger.info(f"✅ Loaded {len(self.default_playlist)} default songs")
                else:
                    logger.warning("⚠️ Playlist empty, using default list from config")
                    self.create_default_playlist()
            else:
                self.create_default_playlist()
        except Exception as e:
            logger.error(f"❌ Error loading default playlist: {e}")
            self.create_default_playlist()

    def create_default_playlist(self):
        """Create default playlist using songs from config.py"""
        default_songs = DEFAULT_SONGS

        try:
            with open(self.DEFAULT_PLAYLIST_FILE, 'w', encoding='utf-8') as f:
                for song in default_songs:
                    f.write(f"{song}\n")
            self.default_playlist = default_songs
            logger.info(f"✅ Created KingRadio playlist with {len(default_songs)} songs")
        except Exception as e:
            logger.error(f"❌ Error creating default playlist: {e}")

    def load_state(self):
        """Load saved playback state"""
        try:
            if Path(self.CURRENT_STATE_FILE).exists():
                with open(self.CURRENT_STATE_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.current_default_index = state.get('current_default_index', 0)
                    self.current_song = state.get('current_song')
                    self.is_playing_user_request = state.get('is_playing_user_request', False)
                    self.disable_default_playlist = state.get('disable_default_playlist', False)

                if self.current_default_index >= len(self.default_playlist):
                    self.current_default_index = 0

                logger.info("✅ KingRadio playback state loaded")
        except Exception as e:
            logger.error(f"❌ Error loading state: {e}")

    def save_state(self):
        """Save current playback state"""
        try:
            state = {
                'current_default_index': self.current_default_index,
                'current_song': self.current_song,
                'is_playing_user_request': self.is_playing_user_request,
                'disable_default_playlist': self.disable_default_playlist,
                'last_saved': datetime.now().isoformat()
            }
            with open(self.CURRENT_STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving state: {e}")

    def get_next_song(self) -> Optional[str]:
        """Get next song to play (Priority: User Requests > Default Playlist)"""
        user_request = self.peek_user_request()
        if user_request:
            self.current_song = user_request
            self.is_playing_user_request = True
            self.save_state()
            logger.info(f"🎵 User request playing on KingRadio: {user_request}")
            return user_request
        
        try:
            has_queue = False
            if Path(self.QUEUE_FILE).exists():
                with open(self.QUEUE_FILE, 'r', encoding='utf-8') as f:
                    has_queue = any(line.strip() for line in f.readlines())
            self.disable_default_playlist = bool(has_queue)
            self.save_state()
        except Exception as e:
            logger.debug(f"Could not update status: {e}")

        if self.default_playlist and not self.disable_default_playlist:
            if self.current_default_index >= len(self.default_playlist):
                self.current_default_index = 0

            song = self.default_playlist[self.current_default_index]
            self.current_song = song
            self.is_playing_user_request = False
            self.save_state()
            logger.info(f"🎶 KingRadio Default: {song}")
            return song

        logger.warning("⚠️ No songs available for KingRadio")
        return None

    def mark_song_started_successfully(self, song: str):
        """Record song start success"""
        if self.is_playing_user_request and song == self.current_song:
            if song in self.failed_requests:
                del self.failed_requests[song]
            
            if self.consume_user_request():
                logger.info(f"✅ User request started on KingRadio: {song}")
                self.advance_default_index()
        else:
            logger.info(f"✅ Default song started on KingRadio: {song}")
            self.advance_default_index()

    def peek_user_request(self) -> Optional[str]:
        """Check the queue file for next user request"""
        try:
            if not Path(self.QUEUE_FILE).exists():
                return None
            with open(self.QUEUE_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines: return None

            next_request = lines[0].strip()
            if not next_request: return None
            
            parts = next_request.split('|||')
            if len(parts) >= 2:
                return parts[1] # query for streamer
            return next_request
        except Exception as e:
            logger.error(f"❌ Error peeking requests: {e}")
            return None

    def consume_user_request(self) -> bool:
        """Remove request from queue after successful play"""
        try:
            if not Path(self.QUEUE_FILE).exists(): return False
            with open(self.QUEUE_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if not lines: return False

            with open(self.QUEUE_FILE, 'w', encoding='utf-8') as f:
                f.writelines(lines[1:])
            return True
        except Exception as e:
            logger.error(f"❌ Error removing request: {e}")
            return False

    def mark_song_finished(self, song: str):
        """Clean up after song finishes"""
        logger.info(f"✅ KingRadio song finished: {song}")
        self.save_state()

    def advance_default_index(self):
        """Move to the next song in rotation"""
        if self.default_playlist:
            self.current_default_index = (self.current_default_index + 1) % len(self.default_playlist)

    def mark_request_failed(self, song: str):
        """Handle stream/song playback failure"""
        self.failed_requests[song] = self.failed_requests.get(song, 0) + 1
        attempts = self.failed_requests[song]
        
        logger.error(f"❌ KingRadio play failed: {song} (Attempt {attempts}/{self.max_retry_attempts})")

        if attempts >= self.max_retry_attempts:
            if self.is_playing_user_request:
                self.consume_user_request() # Remove if keeps failing
            if song in self.failed_requests:
                del self.failed_requests[song]

# Logic remains same for rest of the helper functions...
