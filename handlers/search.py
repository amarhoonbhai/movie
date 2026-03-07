from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.ext import ContextTypes
from api.tmdb import tmdb
from database import db
from utils.formatters import get_post_text
from config import TMDB_IMAGE_BASE_URL, BANNER_URL
import uuid


# ---------------------------------------------------------------------------
# /search
# ---------------------------------------------------------------------------

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        if update.message:
            await update.message.set_reaction(reactions=["🔥"])
    except Exception:
        pass

    query_text = " ".join(context.args) if context.args else ""
    if not query_text:
        await update.message.reply_text(
            "Please provide a movie or series name.\nExample: /search Outlander"
        )
        return

    await db.add_search_query(query_text)
    results = await tmdb.search(query_text)

    if not results:
        await update.message.reply_text("No results found on TMDb.")
        return

    keyboard = []
    for res in results:
        title = res.get("title", res.get("name", "Unknown"))
        date = res.get("release_date") or res.get("first_air_date") or ""
        year = date.split("-")[0] if date else "N/A"
        media_type = res.get("media_type")
        media_id = res.get("id")
        keyboard.append([
            InlineKeyboardButton(
                f"🎬 {title} ({year})",
                callback_data=f"details_{media_type}_{media_id}",
            )
        ])

    await update.message.reply_text(
        "<b>Top Results found:</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )


# ---------------------------------------------------------------------------
# Details callback (Portrait / Landscape switcher)
# ---------------------------------------------------------------------------

async def search_details_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    media_type = data[1]
    media_id = data[2]
    layout = data[3] if len(data) > 3 else "portrait"

    try:
        details = await tmdb.get_details(media_type, media_id)
    except Exception:
        await query.message.reply_text("⚠️ Could not fetch details. Try again later.")
        return

    poster_path = details.get("poster_path")
    backdrop_path = details.get("backdrop_path")

    if layout == "landscape" and backdrop_path:
        media_url = f"{TMDB_IMAGE_BASE_URL}{backdrop_path}"
    elif poster_path:
        media_url = f"{TMDB_IMAGE_BASE_URL}{poster_path}"
    else:
        media_url = None

    post_text = get_post_text(details, media_type, layout)

    # Build layout-switch buttons
    keyboard = []
    layout_row = []
    if poster_path:
        layout_row.append(InlineKeyboardButton("📱 Portrait", callback_data=f"details_{media_type}_{media_id}_portrait"))
    if backdrop_path:
        layout_row.append(InlineKeyboardButton("🖼️ Landscape", callback_data=f"details_{media_type}_{media_id}_landscape"))
    if layout_row:
        keyboard.append(layout_row)

    keyboard.append([InlineKeyboardButton("➕ Custom Thumbnail", callback_data=f"custom_thumb_{media_type}_{media_id}")])
    keyboard.append([InlineKeyboardButton("❌ Close", callback_data="close_post")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query.message.photo:
        from telegram import InputMediaPhoto
        try:
            await query.edit_message_media(
                media=InputMediaPhoto(
                    media=media_url or BANNER_URL,
                    caption=post_text,
                    parse_mode="HTML",
                ),
                reply_markup=reply_markup,
            )
        except Exception:
            await query.message.reply_text(post_text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        title = details.get("title") or details.get("name") or "Unknown"
        await query.message.reply_text(
            f"<b>{title}</b>\n\nChoose your preferred layout or upload a custom thumbnail.",
            reply_markup=reply_markup,
            parse_mode="HTML",
        )
        context.user_data["pending_post"] = {
            "text": post_text,
            "poster_url": media_url,
            "media_type": media_type,
            "media_id": media_id,
        }


# ---------------------------------------------------------------------------
# Inline Search
# ---------------------------------------------------------------------------

async def inline_search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = update.inline_query.query
    if not query_text:
        return

    results = await tmdb.search(query_text)
    inline_results = []

    for res in results:
        title = res.get("title", res.get("name", "Unknown"))
        media_type = res.get("media_type")
        media_id = res.get("id")
        date = res.get("release_date") or res.get("first_air_date") or ""
        year = date.split("-")[0] if date else "N/A"
        poster_path = res.get("poster_path")
        thumb_url = f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None

        bot_username = context.bot.username
        share_link = f"https://t.me/{bot_username}?start=info_{media_type}_{media_id}"

        inline_results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"{title} ({year})",
                input_message_content=InputTextMessageContent(
                    f"🎬 <b>{title} ({year})</b>\n\nClick below to view full details!",
                    parse_mode="HTML",
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("👀 VIEW DETAILS", url=share_link)]
                ]),
                thumbnail_url=thumb_url,
                description=f"{media_type.capitalize()} • {(res.get('overview') or '')[:50]}...",
            )
        )

    await update.inline_query.answer(inline_results, cache_time=300)


# ---------------------------------------------------------------------------
# Most Searched
# ---------------------------------------------------------------------------

async def most_searched_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    most_searched = await db.get_most_searched(10)
    message = update.effective_message
    if not most_searched:
        await message.reply_text("No search history found.")
        return

    keyboard = []
    for item in most_searched:
        q = item["query"]
        keyboard.append([InlineKeyboardButton(q.title(), callback_data=f"search_again_{q[:50]}")])

    await message.reply_text(
        "<b>📊 Most Searched:</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )


# ---------------------------------------------------------------------------
# Search-again callback
# ---------------------------------------------------------------------------

async def search_again_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    search_query = query.data.replace("search_again_", "")
    results = await tmdb.search(search_query)

    if not results:
        await query.message.reply_text("No results found.")
        return

    keyboard = []
    for res in results:
        title = res.get("title", res.get("name", "Unknown"))
        date = res.get("release_date") or res.get("first_air_date") or ""
        year = date.split("-")[0] if date else "N/A"
        media_type = res.get("media_type")
        media_id = res.get("id")
        keyboard.append([InlineKeyboardButton(f"🎬 {title} ({year})", callback_data=f"details_{media_type}_{media_id}")])

    await query.message.reply_text(
        f"<b>Results for '{search_query}':</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )


# ---------------------------------------------------------------------------
# Skip Thumbnail
# ---------------------------------------------------------------------------

async def skip_thumbnail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pending = context.user_data.get("pending_post")
    if not pending:
        await query.message.reply_text("Error: Pending post context lost.")
        return

    if pending["poster_url"]:
        await query.message.reply_photo(
            photo=pending["poster_url"],
            caption=pending["text"],
            parse_mode="HTML",
        )
    else:
        await query.message.reply_text(pending["text"], parse_mode="HTML")

    context.user_data.pop("pending_post", None)
