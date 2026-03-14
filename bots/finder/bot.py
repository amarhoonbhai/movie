import logging
from pyrogram import Client
from core.config import BOT_TOKEN, API_ID, API_HASH

logger = logging.getLogger(__name__)

finder_app = Client(
    "finder_bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="bots.finder.plugins")
)
