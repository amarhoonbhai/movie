import logging
from pyrogram import Client
from config import BOT_TOKEN, API_ID, API_HASH

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Initialize Pyrogram Client ---
app = Client(
    "movie_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    plugins=dict(root="plugins")
)

if __name__ == "__main__":
    logger.info("Bot started...")
    app.run()
