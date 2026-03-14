import asyncio
import logging
from pyrogram import compose
from bots.finder.bot import finder_app
from bots.store.bot import store_app
from core.database import db
from search.meili import meili

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
    await meili.ensure_index()

    print("\n" + "="*50)
    print("🚀 Dual-Bot Scalable Movie System Started!")
    print(f"1. 🎬 AutoMovieFinderBot is running")
    print(f"2. 🗄 PhiloStoreBot is running")
    print("Ensure Redis & Arq Worker are also running (arq worker.arq_worker.WorkerSettings)!")
    print("="*50 + "\n")

    # Run Pyrogram apps simultaneously
    await compose([finder_app, store_app])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
