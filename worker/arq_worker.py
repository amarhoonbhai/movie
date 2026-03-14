import asyncio
import logging
from arq import create_pool
from arq.connections import RedisSettings
from pyrogram import Client
from pyrogram.errors import FloodWait

from core.config import REDIS_URL, BOT_TOKEN, API_ID, API_HASH
from core.database import db
from search.meili import meili

logger = logging.getLogger(__name__)

# Pyrogram client instance for the worker to use (Finder Bot)
worker_app = Client(
    "worker_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

async def startup(ctx):
    """Run on worker startup."""
    logger.info("Starting up Arq Worker...")
    await db.ensure_indexes()
    await meili.ensure_index()
    await worker_app.start()
    ctx['app'] = worker_app

async def shutdown(ctx):
    """Run on worker shutdown."""
    logger.info("Shutting down Arq Worker...")
    await worker_app.stop()

# ──────────────────────────────────────────────────────────────────────────
# Tasks
# ──────────────────────────────────────────────────────────────────────────

async def schedule_auto_delete(ctx, chat_id: int, message_id: int):
    """Deletes a message after a delay."""
    app = ctx['app']
    try:
        await app.delete_messages(chat_id=chat_id, message_ids=message_id)
        logger.info(f"Auto-deleted message {message_id} in {chat_id}")
    except Exception as e:
        logger.error(f"Failed to auto-delete message {message_id}: {e}")

async def broadcast_message(ctx, message_id: int, from_chat_id: int):
    """Broadcasts a forwarded message to all users."""
    app = ctx['app']
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
            await asyncio.sleep(0.05)  # Throttle to avoid FloodWait
        except FloodWait as e:
            await asyncio.sleep(e.value)
            # Retry
            try:
                await app.forward_messages(chat_id=u["user_id"], from_chat_id=from_chat_id, message_ids=message_id)
                success += 1
            except:
                failed += 1
        except Exception:
            failed += 1

    logger.info(f"Broadcast complete. Success: {success}, Failed: {failed}")

async def process_new_movie_upload(ctx, file_id: str, file_name: str, file_size: int, message_id: int, caption: str, title: str, year: str, genre: str):
    """Saves to MongoDB, Meilisearch, and checks requests."""
    
    # 1. Save to MongoDB
    doc_id = f"msg_{message_id}"
    success_db = await db.index_file(
        file_id=file_id,
        file_name=file_name,
        file_size=file_size,
        message_id=message_id,
        caption=caption
    )
    
    # 2. Save to Meilisearch
    if success_db:
        await meili.index_movie(
            movie_id=doc_id,
            title=title,
            year=year,
            genre=genre,
            caption=caption
        )
        logger.info(f"Indexed movie {title} ({year})")
        
    # 3. Notify pending requests for this movie title
    users_to_notify = await db.get_pending_requests(title)
    if users_to_notify:
        app = ctx['app']
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

# Worker configuration class for ARQ
class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(REDIS_URL)
    functions = [
        schedule_auto_delete,
        broadcast_message,
        process_new_movie_upload
    ]
    on_startup = startup
    on_shutdown = shutdown

# Helper to enqueue tasks
async def get_redis_pool():
    return await create_pool(RedisSettings.from_dsn(REDIS_URL))
