from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes
from api.tmdb import tmdb
from database import db
from utils.formatters import get_post_text
from config import TMDB_IMAGE_BASE_URL
import uuid

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = " ".join(context.args)
    if not query_text:
        await update.message.reply_text("Please provide a movie or series name to search.\nExample: /search Outlander")
        return

    await db.add_search_query(query_text)
    results = await tmdb.search(query_text)

    if not results:
        await update.message.reply_text("No results found on TMDb.")
        return

    keyboard = []
    for res in results:
        title = res.get("title", res.get("name", "Unknown"))
        date = res.get("release_date", res.get("first_air_date", "N/A"))
        year = date.split("-")[0] if date != "N/A" else "N/A"
        media_type = res.get("media_type")
        media_id = res.get("id")
        
        callback_data = f"details_{media_type}_{media_id}"
        keyboard.append([InlineKeyboardButton(f"🎬 {title} ({year})", callback_data=callback_data)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("<b>Top Results found:</b>", reply_markup=reply_markup, parse_mode="HTML")

async def search_details_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    media_type = data[1]
    media_id = data[2]
    layout = data[3] if len(data) > 3 else "portrait"

    details = await tmdb.get_details(media_type, media_id)
    
    poster_path = details.get("poster_path")
    backdrop_path = details.get("backdrop_path")
    
    media_url = f"{TMDB_IMAGE_BASE_URL}{backdrop_path if layout == 'landscape' else poster_path}"
    if not poster_path and not backdrop_path:
        media_url = None

    post_text = get_post_text(details, media_type, layout)

    keyboard = []
    layout_row = []
    if poster_path:
        layout_row.append(InlineKeyboardButton("📱 Portrait", callback_data=f"details_{media_type}_{media_id}_portrait"))
    if backdrop_path:
        layout_row.append(InlineKeyboardButton("🖼️ Landscape", callback_data=f"details_{media_type}_{media_id}_landscape"))
    
    if layout_row:
        keyboard.append(layout_row)
        
    keyboard.append([InlineKeyboardButton("➕ Set Custom Thumbnail", callback_data=f"custom_thumb_{media_type}_{media_id}")])
    keyboard.append([InlineKeyboardButton("❌ Skip", callback_data="close_post")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query.message.photo:
        # Edit existing photo and caption if possible
        from telegram import InputMediaPhoto
        await query.edit_message_media(
            media=InputMediaPhoto(media=media_url or BANNER_URL, caption=post_text, parse_mode="HTML"),
            reply_markup=reply_markup
        )
    else:
        await query.message.reply_text(
            f"<b>{details.get('title', details.get('name'))}</b>\n\n"
            "Choose your preferred layout below or upload a custom thumbnail.",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        # Store for custom thumbnail logic
        context.user_data["pending_post"] = {
            "text": post_text,
            "poster_url": media_url,
            "media_type": media_type,
            "media_id": media_id
        }

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
        year = res.get("release_date", res.get("first_air_date", "N/A")).split("-")[0]
        poster_path = res.get("poster_path")
        thumb_url = f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None
        
        # In results, we just show basic info. Selection triggers the details callback via a link or similar
        # For simplicity, we'll send the details directly as a result for now
        # Ideally we'd use a deep link to the bot
        bot_username = context.bot.username
        share_link = f"https://t.me/{bot_username}?start=info_{media_type}_{media_id}"
        
        inline_results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"{title} ({year})",
                input_message_content=InputTextMessageContent(
                    f"🎬 <b>{title} ({year})</b>\n\nClick below to view full details and high-quality posters!",
                    parse_mode="HTML"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("👀 VIEW DETAILS", url=share_link)]
                ]),
                thumbnail_url=thumb_url,
                description=f"{media_type.capitalize()} • {res.get('overview', '')[:50]}..."
            )
        )

    await update.inline_query.answer(inline_results, cache_time=300)

async def most_searched_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    most_searched = await db.get_most_searched(10)
    message = update.effective_message
    if not most_searched:
        await message.reply_text("No search history found.")
        return

    keyboard = []
    for item in most_searched:
        keyboard.append([InlineKeyboardButton(item["query"].title(), callback_data=f"search_again_{item['query']}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("Most Searched Queries:", reply_markup=reply_markup)

async def search_again_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Extract query and trigger search
    search_query = query.data.replace("search_again_", "")
    # Add to database done inside search_command logic effectively or just here
    results = await tmdb.search(search_query)
    
    if not results:
        await query.message.reply_text("No results found.")
        return

    keyboard = []
    for res in results:
        title = res.get("title", res.get("name", "Unknown"))
        year = res.get("release_date", res.get("first_air_date", "N/A")).split("-")[0]
        media_type = res.get("media_type")
        media_id = res.get("id")
        callback_data = f"details_{media_type}_{media_id}"
        keyboard.append([InlineKeyboardButton(f"{title} ({year})", callback_data=callback_data)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(f"Search results for '{search_query}':", reply_markup=reply_markup)

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
            parse_mode="HTML"
        )
    else:
        await query.message.reply_text(pending["text"], parse_mode="HTML")
    
    context.user_data.pop("pending_post", None)
