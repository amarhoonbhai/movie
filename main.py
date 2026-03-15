import asyncio
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import logging
from pyrogram import Client
from core.database import db
from core.config import BOT_TOKEN, API_ID, API_HASH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("MovieBot")

app = Client(
    "movie_bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="bots.finder.plugins")
)

async def main():
    logger.info("Starting up Movie Bot...")
    # Ensure dependencies are connected and initialized
    await db.ensure_indexes()

    print("\n" + "="*50)
    print("🚀 Movie Bot System Started!")
    print("Background tasks are running natively via Pyrogram asyncio.")
    print("="*50 + "\n")

    await app.start()
    from pyrogram import idle
    await idle()
    await app.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
