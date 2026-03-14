"""
Native asyncio tasks to replace the Arq Redis worker.
Runs inside the same Pyrogram event loop.
"""
import asyncio
import logging
from pyrogram import Client
from pyrogram.errors import FloodWait

from core.database import db

logger = logging.getLogger(__name__)

async def broadcast_message(app: Client, message_id: int, from_chat_id: int):
    """Broadcasts a forwarded message to all users slowly to avoid FloodWait."""
    users = await db.get_all_users()
    success = 0
    failed = 0
    
    for u in users:
        try:
            await app.forward_messages(
                chat_id=u["user_id"],
                from_chat_id=from_chat_id,
                message_ids=message_id
            )
            success += 1
            await asyncio.sleep(0.05)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await app.forward_messages(chat_id=u["user_id"], from_chat_id=from_chat_id, message_ids=message_id)
                success += 1
            except:
                failed += 1
        except Exception:
            failed += 1

    logger.info(f"Broadcast complete. Success: {success}, Failed: {failed}")

async def process_new_movie_upload(
    app: Client, file_id: str, file_name: str, file_size: int, message_id: int, caption: str, title: str, year: str, genre: str
):
    """Saves to MongoDB and notifies users who requested the movie."""
    
    # 1. Save to MongoDB natively
    success_db = await db.index_file(
        file_id=file_id,
        file_name=file_name,
        file_size=file_size,
        message_id=message_id,
        caption=caption
    )
    
    if not success_db:
        return
        
    logger.info(f"Indexed movie {title} ({year}) to MongoDB!")

    # 2. Notify pending requests using the Finder Bot instance
    users_to_notify = await db.get_pending_requests(title)
    if users_to_notify:
        for uid in users_to_notify:
            try:
                await app.send_message(
                    chat_id=uid,
                    text=f"🎬 **Good News!**\n\nThe movie you requested: **{title}** has been uploaded!\nSearch it now in the group."
                )
                await asyncio.sleep(0.05)
            except Exception:
                pass
        
        # Mark fulfilled
        await db.mark_request_fulfilled(title)
