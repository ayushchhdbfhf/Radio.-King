#!/usr/bin/env python3
"""
Main Entry Point - KingRadio Music Bot
Handles bot initialization and service coordination.
"""

import asyncio
import logging
import sys
from highrise import BaseBot
from highrise.__main__ import main as highrise_main

# Import KingRadio configurations
from config import HighriseSettings, StreamSettings, LogSettings
from highrise_music_bot import MusicBot

# Setup Logging for KingRadio Bot
logging.basicConfig(
    level=getattr(logging, LogSettings.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('KingRadioMain')

def run_bot():
    """
    KingRadio Bot Runner
    Initializes the Highrise connection using KingRadio stream settings.
    """
    try:
        # Check if KingRadio settings are present
        if not StreamSettings.RADIO_SERVER or "zeno" in StreamSettings.RADIO_SERVER.lower():
            logger.error("❌ Invalid Radio Server! Please check config.py for KingRadio details.")
            return

        print("--- KingRadio Music Bot Initializing ---")
        print(f"📡 Radio Host: {StreamSettings.RADIO_SERVER}")
        print(f"🔊 Stream Port: {StreamSettings.RADIO_PORT}")
        print(f"🏠 Highrise Room ID: {HighriseSettings.ROOM_ID}")
        print("-----------------------------------------")

        # Define bot credentials for the Highrise runner
        definitions = [
            f"highrise_music_bot:MusicBot",
            HighriseSettings.ROOM_ID,
            HighriseSettings.BOT_TOKEN
        ]

        # Start Highrise process
        sys.argv = ["highrise", "highrise_music_bot:MusicBot", HighriseSettings.ROOM_ID, HighriseSettings.BOT_TOKEN]
        highrise_main()

    except Exception as e:
        logger.critical(f"💥 Failed to start KingRadio Bot: {e}")

if __name__ == "__main__":
    run_bot()
