"""
plugins/indexer.py — Auto-index files posted in the STORAGE_CHANNEL.
Also notifies users who had requested a movie that's now available.
"""
import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from config import STORAGE_CHANNEL, ALLOWED_GROUP
from database import db
from utils.helpers import normalize_query

logger = logging.getLogger(__name__)


def _get_file_info(message: Message):
    """
    Extract (file_id, file_name, file_size) from any media type.
    Returns (None, None, None) if the message has no indexable file.
    """
    if message.document:
        return (
            message.document.file_id,
            message.document.file_name or "document",
            message.document.file_size or 0,
        )
    if message.video:
        return (
            message.video.file_id,
            message.video.file_name or f"video_{message.id}",
            message.video.file_size or 0,
        )
    if message.audio:
        return (
            message.audio.file_id,
            message.audio.file_name or f"audio_{message.id}",
            message.audio.file_size or 0,
        )
    return None, None, None


@Client.on_message(filters.channel & filters.chat(STORAGE_CHANNEL))
async def indexer_handler(client: Client, message: Message):
    """
    Triggered every time the owner posts a file in the STORAGE_CHANNEL.
    Indexes it in MongoDB and notifies users who requested that movie.
    """
    file_id, file_name, file_size = _get_file_info(message)
    if not file_id:
        return   # text-only or unsupported media — skip

    caption = message.caption or message.text or file_name

    # ── Store in MongoDB ──────────────────────────────────────────────────────
    ok = await db.index_file(
        file_id    = file_id,
        file_name  = file_name,
        file_size  = file_size,
        message_id = message.id,
        caption    = caption,
        upload_time= message.date,
    )

    if ok:
        logger.info(f"[Indexer] Indexed: {file_name} (msg_id={message.id})")
    else:
        logger.warning(f"[Indexer] Skipped duplicate: msg_id={message.id}")
        return

    # ── Notify pending requestors ─────────────────────────────────────────────
    normalized = normalize_query(file_name)
    # Search by the base name (first 2-3 meaningful words)
    words       = normalized.split()
    search_term = " ".join(words[:3]) if len(words) >= 3 else normalized

    requestors = await db.get_pending_requests(search_term)
    if not requestors:
        return

    # Get a jump link to the group where the file will appear
    group_id_str = str(ALLOWED_GROUP).replace("-100", "")

    notify_text = (
        f"🎉 <b>Good news!</b>\n\n"
        f"The movie you requested (<b>{file_name}</b>) is now available!\n\n"
        f"📢 Head to our group and search for it:\n"
        f"<code>/search {search_term}</code>\n\n"
        f"━━━━━━━━━━━━━━\n"
        f"📢 Powered by: @PhiloBots\n"
        f"━━━━━━━━━━━━━━"
    )

    notified = 0
    for uid in requestors:
        try:
            await client.send_message(uid, notify_text, parse_mode="html")
            notified += 1
        except Exception as e:
            logger.debug(f"Notify failed for user {uid}: {e}")

    if notified:
        logger.info(f"[Indexer] Notified {notified} users about: {file_name}")

    # Mark request as fulfilled
    await db.mark_request_fulfilled(search_term)
