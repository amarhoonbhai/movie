"""
main.py — Pyrogram bot entry point.
Run with: python main.py
"""
import asyncio
import logging
from pyrogram import Client
from config import BOT_TOKEN, API_ID, API_HASH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def main():
    # Ensure MongoDB indexes before starting
    from database import db
    await db.ensure_indexes()

    app = Client(
        "movie_bot_session",
        bot_token=BOT_TOKEN,
        api_id=API_ID,
        api_hash=API_HASH,
        plugins=dict(root="plugins"),
    )

    logger.info("🎬 Movie Search Bot starting...")
    async with app:
        logger.info("✅ Bot is online and listening.")
        await asyncio.Event().wait()          # run forever


if __name__ == "__main__":
    asyncio.run(main())
