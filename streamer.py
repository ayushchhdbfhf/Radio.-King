#!/usr/bin/env python3
"""
Live streaming service to KingRadio (Icecast)
"""

import os
import subprocess
import time
import json
import logging
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from continuous_playlist_manager import ContinuousPlaylistManager
from config import SystemFiles, StreamSettings, LogSettings
import hashlib
import random
import re
import sys
import tempfile
import gc

# Logging setup - Completely migrated to KingRadio
logging.basicConfig(
    level=getattr(logging, LogSettings.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('KingRadioStreamer')

def clean_search_query(query: str) -> str:
    """Clean search query from emojis and problematic symbols"""
    if query.strip().startswith(('http://', 'https://')):
        return query.strip()
    return re.sub(r'[^\w\s\-.,]', '', query).strip()

class KingRadioStreamer:
    """Streaming service for KingRadio.net (Icecast Protocol)"""
    
    def __init__(self):
        self.playlist_manager = ContinuousPlaylistManager()
        self.is_running = True
        
        # KingRadio variables from updated config.py
        self.radio_server = StreamSettings.RADIO_SERVER 
        self.radio_port = StreamSettings.RADIO_PORT
        self.radio_password = StreamSettings.RADIO_PASSWORD
        self.radio_mount = StreamSettings.RADIO_MOUNT_POINT
        self.bitrate = StreamSettings.STREAM_BITRATE
        self.cache_dir = StreamSettings.CACHE_DIR

    def stream_song(self, file_path: str, song_name: str, is_request: bool, requester: str):
        """Streams audio to KingRadio using FFmpeg Icecast protocol"""
        logger.info(f"📡 KingRadio Streaming: {song_name} | Requested by: {requester}")
        
        # Icecast format: icecast://source:password@host:port/mount
        kingradio_url = f"icecast://source:{self.radio_password}@{self.radio_server}:{self.radio_port}/{self.radio_mount}"
        
        # Metadata update for the stream
        metadata = f"title={song_name}:artist=KingRadioBot"
        
        command = [
            'ffmpeg', '-re', '-i', file_path,
            '-metadata', metadata,
            '-c:a', 'libmp3lame', '-b:a', self.bitrate,
            '-content_type', 'audio/mpeg',
            '-f', 'mp3', kingradio_url
        ]
        
        try:
            # Security: Don't show password in logs
            safe_url = kingradio_url.replace(self.radio_password, "********")
            logger.debug(f"Executing: ffmpeg -> {safe_url}")
            
            process = subprocess.Popen(
                command, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Monitor process
            _, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"❌ FFmpeg Error: {stderr}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"❌ Critical Streaming Error: {e}")
            return False

    def get_audio_file(self, song_query: str) -> Optional[str]:
        """Check if song exists in KingRadio cache"""
        clean_name = hashlib.md5(song_query.encode()).hexdigest()
        file_path = os.path.join(self.cache_dir, f"{clean_name}.mp3")
        
        if os.path.exists(file_path):
            return file_path
        return None

    def run(self):
        """Main KingRadio streaming loop"""
        logger.info("🚀 KingRadio Streamer Service is now ONLINE")
        
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        while self.is_running:
            try:
                # 1. Get next song from manager
                next_song = self.playlist_manager.get_next_song()
                
                if not next_song:
                    logger.info("💤 No songs in queue, waiting...")
                    time.sleep(5)
                    continue

                # 2. Locate file
                audio_file = self.get_audio_file(next_song)
                
                if not audio_file:
                    logger.warning(f"⚠️ Cache miss for: {next_song}")
                    self.playlist_manager.mark_request_failed(next_song)
                    time.sleep(2)
                    continue

                # 3. Stream to KingRadio
                is_request = self.playlist_manager.is_playing_user_request
                requester = "User" if is_request else "System"
                
                success = self.stream_song(audio_file, next_song, is_request, requester)

                if success:
                    logger.info(f"✅ Finished playing on KingRadio: {next_song}")
                    self.playlist_manager.mark_song_finished(next_song)
                else:
                    logger.error(f"❌ Playback failed for: {next_song}")
                    self.playlist_manager.mark_request_failed(next_song)
                
                # Force cleanup
                gc.collect()

            except Exception as e:
                logger.error(f"❌ Loop Error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    streamer = KingRadioStreamer()
    streamer.run()
