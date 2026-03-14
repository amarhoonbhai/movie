import logging
from pyrogram import Client
from core.config import BOT_TOKEN, API_ID, API_HASH

logger = logging.getLogger(__name__)

import asyncio
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

finder_app = Client(
    "finder_bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="bots.finder.plugins")
)
