#!/usr/bin/env python3
"""
Highrise Music Bot - KingRadio Edition
Maintained and updated for KingRadio (Icecast) streaming.
"""

import asyncio
import os
import logging
import json
import traceback
from typing import Any, Dict, Union

from highrise import BaseBot, User, Position, AnchorPosition
from highrise.models import (
    SessionMetadata, 
    ChatEvent, 
    RoomPermissions, 
    GetMessagesRequest,
    Item,
)

# Config aur Manager se settings load karna
from config import HighriseSettings, StreamSettings, LogSettings
from continuous_playlist_manager import ContinuousPlaylistManager

# Logging setup - KingRadio branding
logging.basicConfig(
    level=getattr(logging, LogSettings.LOG_LEVEL, logging.WARNING),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('KingRadioBot')

class KingRadioBot(BaseBot):
    """Highrise Bot class optimized for KingRadio streaming"""
    
    def __init__(self):
        super().__init__()
        self.playlist_manager = ContinuousPlaylistManager()
        self.bot_id = None
        self.owner_id = None
        self.is_streaming = False
        
        # KingRadio stream details from config
        self.stream_url = StreamSettings.STREAM_URL
        self.mount_point = StreamSettings.RADIO_MOUNT_POINT

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        """Bot start hone par call hota hai"""
        self.bot_id = session_metadata.user_id
        print(f"🚀 KingRadio Bot is ONLINE!")
        print(f"📡 Radio Server: {StreamSettings.RADIO_SERVER}")
        print(f"🎵 Mount Point: {self.mount_point}")
        
        # Highrise room mein bot ki position set karna
        await self.highrise.teleport(self.bot_id, Position(15.5, 0.0, 15.5, "FacingFront"))
        
        # Playback loop shuru karein
        asyncio.create_task(self.run_radio_engine())

    async def run_radio_engine(self):
        """KingRadio playback loop jo queue aur default playlist handle karta hai"""
        while True:
            try:
                # Agla gana check karein
                next_song = self.playlist_manager.get_next_song()
                
                if next_song:
                    logger.info(f"📻 Now Streaming on KingRadio: {next_song}")
                    # Actual streaming command ya FFmpeg trigger yahan hota hai
                    # Hum manager ko notify karte hain ki gane ki koshish shuru hui
                    self.playlist_manager.mark_song_started_successfully(next_song)
                    
                    # Gane ki duration tak wait karein (simulated)
                    # Asal mein FFmpeg process ka wait kiya jata hai
                    await asyncio.sleep(StreamSettings.MIN_SONG_DURATION)
                    
                    self.playlist_manager.mark_song_finished(next_song)
                else:
                    await asyncio.sleep(5)
                    
            except Exception as e:
                logger.error(f"❌ Radio Engine Error: {e}")
                print(traceback.format_exc())
                await asyncio.sleep(10)

    async def on_chat(self, user: User, message: str) -> None:
        """Chat commands handle karne ke liye"""
        # User request handler
        if message.lower().startswith("!play "):
            song_query = message[6:].strip()
            if song_query:
                # Queue file mein request add karna (Username|||Query format)
                with open("queue.txt", "a", encoding="utf-8") as f:
                    f.write(f"{user.username}|||{song_query}|||{song_query}\n")
                
                await self.highrise.chat(f"✅ @{user.username}, aapka gana KingRadio queue mein add ho gaya hai!")
                logger.info(f"📩 New Request: {song_query} by {user.username}")

        # Status command
        elif message.lower() == "!status":
            status = self.playlist_manager.get_queue_status()
            current = status.get('current_song', 'Khali')
            pending = status.get('user_requests_pending', 0)
            await self.highrise.chat(f"📻 Radio Status: Playing {current} | Requests in Queue: {pending}")

    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:
        """User join welcome message"""
        await self.highrise.chat(f"Welcome to the room @{user.username}! Powered by KingRadio 🎶")

    async def on_error(self, error: Exception) -> None:
        """Bot error handling"""
        logger.error(f"⚠️ Bot Error: {error}")

if __name__ == "__main__":
    # Bot ko Highrise settings ke saath run karein
    from highrise.__main__ import main
    
    # Ye ensure karein ki variables config se aa rahe hain
    os.environ["BOT_TOKEN"] = HighriseSettings.BOT_TOKEN
    os.environ["ROOM_ID"] = HighriseSettings.ROOM_ID
    
    # Bot instance trigger
    bot = KingRadioBot()
