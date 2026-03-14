import logging
from pyrogram import Client
from core.config import STORE_BOT_TOKEN, API_ID, API_HASH

logger = logging.getLogger(__name__)

store_app = Client(
    "store_bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=STORE_BOT_TOKEN,
    plugins=dict(root="bots.store")
)
