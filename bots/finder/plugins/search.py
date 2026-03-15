"""
/search command using Meilisearch, metadata, and auto-delete.
"""
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from core.config import STORAGE_CHANNEL, ALLOWED_GROUP, AUTO_DELETE_TIMER
from core.database import db

from utils.force_join import force_join_check
from utils.helpers import normalize_query, extract_quality, extract_audio, human_size, schedule_delete
from utils.tmdb import tmdb
from utils.formatter import format_movie_caption, format_series_caption

logger = logging.getLogger(__name__)

# Key: cache_key string, Value: list of file dicts from MongoDB
_result_cache: dict[str, list] = {}

# Strong references for fire-and-forget tasks
_bg_tasks = set()

def _is_allowed(message: Message) -> bool:
    return message.chat.id == ALLOWED_GROUP or message.chat.type.value == "private"

@Client.on_message(filters.command("search"))
async def search_cmd(client: Client, message: Message):
    if not _is_allowed(message):
        return

    if not await force_join_check(client, message):
        return

    if len(message.command) < 2:
        await message.reply_text(
            "❌ <b>Please provide a movie name!</b>\n\nExample: <code>/search kgf 2</code>",
            parse_mode="html",
        )
        return

    query = " ".join(message.command[1:]).strip()
    normalized = normalize_query(query)

    await db.add_search_stat(query)

    wait_msg = await message.reply_text(f"🔍 Searching for <b>{query}</b>…", parse_mode="html")

    # 1. Search MongoDB directly
    results = await db.search_files(normalized)
    
    if not results:
        await db.add_request(message.from_user.id, query)
        await wait_msg.edit_text(
            f"❌ <b>{query}</b> is not available yet.\n\n"
            "📥 Your request has been saved. We'll notify you when it's uploaded!\n\n"
            "━━━━━━━━━━━━━━\n📢 Powered by: @PhiloBots\n━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📢 Request Support", url="https://t.me/PhiloBots")]]),
            parse_mode="html",
        )
        return

    tmdb_info = await tmdb.get_movie_info(query)

    if len(results) == 1:
        await wait_msg.delete()
        await _send_file(client, message, results[0], tmdb_info)
        return

    cache_key = f"search_{message.from_user.id}_{normalized[:20].replace(' ', '_')}"
    _result_cache[cache_key] = results

    buttons = []
    for i, r in enumerate(results):
        fn      = r.get("file_name", "Unknown")
        quality = extract_quality(fn)
        size    = human_size(r.get("file_size", 0))
        label   = f"📥 {quality}  •  {size}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"dl_{cache_key}_{i}")])

    header = f"🎬 <b>{tmdb_info['title']} ({tmdb_info['year']})</b>\n\n<b>Available Qualities:</b>" if tmdb_info else f"🎬 <b>{query.title()}</b>\n\n<b>Available Qualities:</b>"
    
    title_line = ""
    if tmdb_info:
        genres = tmdb_info.get("genres", "")
        rating = tmdb_info.get("rating", "")
        title_line = f"\n🎭 Genres: {genres}  |  ⭐ Rating: {rating}"

    await wait_msg.edit_text(header + title_line, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="html")

@Client.on_callback_query(filters.regex(r"^dl_"))
async def quality_selection_callback(client: Client, callback: CallbackQuery):
    await callback.answer("⏳ Fetching your file…")

    parts = callback.data.split("_")
    index = int(parts[-1])
    cache_key = "_".join(parts[1:-1])

    results = _result_cache.get(cache_key)
    if not results or index >= len(results):
        await callback.message.reply_text("⚠️ Session expired. Please search again.")
        return

    file_doc  = results[index]
    query     = callback.message.text.split("\n")[0].replace("🎬 ", "").strip()
    tmdb_info = await tmdb.get_movie_info(query)

    try:
        await callback.message.delete()
    except Exception:
        pass

    await _send_file(client, callback.message, file_doc, tmdb_info)

async def _send_file(client: Client, message: Message, file_doc: dict, tmdb_info: dict | None):
    chat_id    = message.chat.id
    message_id = file_doc.get("message_id")
    file_name  = file_doc.get("file_name", "")
    quality    = extract_quality(file_name)
    audio      = extract_audio(file_name)

    if tmdb_info:
        if tmdb_info.get("type") == "series":
            caption = format_series_caption(tmdb_info, quality, audio)
        else:
            caption = format_movie_caption(tmdb_info, quality, audio)
    else:
        size    = human_size(file_doc.get("file_size", 0))
        caption = (
            f"📂 <b>{file_name}</b>\n\n"
            f"➪ Quality: <code>{quality}</code>\n"
            f"➪ Audio: <code>{audio}</code>\n"
            f"➪ Size: <code>{size}</code>\n\n"
            "━━━━━━━━━━━━━━\n📢 Powered by: @PhiloBots\n━━━━━━━━━━━━━━"
        )

    try:
        sent_file = await client.copy_message(
            chat_id=chat_id,
            from_chat_id=STORAGE_CHANNEL,
            message_id=message_id,
            caption=caption,
            parse_mode="html",
        )
    except Exception as e:
        logger.error(f"copy_message failed: {e}")
        await message.reply_text("⚠️ Could not retrieve the file. Please contact admin.", parse_mode="html")
        return

    minutes = AUTO_DELETE_TIMER // 60
    notice_msg = await message.reply_text(
        f"⚠️ <b>Please save or download the movie.</b>\n\n"
        f"🗑 This file will be automatically deleted in <b>{minutes} minutes</b>.",
        parse_mode="html",
    )

    # Native asyncio auto-delete task (keep strong reference to avoid GC)
    task = asyncio.create_task(schedule_delete(client, chat_id, AUTO_DELETE_TIMER, sent_file.id, notice_msg.id))
    _bg_tasks.add(task)
    task.add_done_callback(_bg_tasks.discard)
