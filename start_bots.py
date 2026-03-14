import asyncio
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import logging
from pyrogram import compose
from bots.finder.bot import finder_app
from bots.store.bot import store_app
from core.database import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("SystemRunner")

async def main():
    logger.info("Starting up both Telegram Bots...")
    # Ensure dependencies are connected and initialized
    await db.ensure_indexes()

    print("\n" + "="*50)
    print("🚀 Dual-Bot Scalable Movie System Started!")
    print(f"1. 🎬 AutoMovieFinderBot is running")
    print(f"2. 🗄 PhiloStoreBot is running")
    print("Background tasks are running natively via Pyrogram asyncio.")
    print("="*50 + "\n")

    # Run Pyrogram apps simultaneously
    # Run Pyrogram apps simultaneously
    await compose([finder_app, store_app])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
