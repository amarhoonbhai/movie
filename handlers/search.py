from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from api.tmdb import tmdb
from database import db
from utils.formatters import format_movie_post, format_series_post
from config import TMDB_IMAGE_BASE_URL

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Please provide a movie or series name to search.\nExample: /search Outlander")
        return

    await db.add_search_query(query)
    results = await tmdb.search(query)

    if not results:
        await update.message.reply_text("No results found on TMDb.")
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
    await update.message.reply_text("Select a result:", reply_markup=reply_markup)

async def search_details_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    media_type = data[1]
    media_id = data[2]

    details = await tmdb.get_details(media_type, media_id)
    
    poster_path = details.get("poster_path") or details.get("backdrop_path")
    poster_url = f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None
    
    if media_type == "movie":
        post_text = format_movie_post(details)
    else:
        post_text = format_series_post(details)

    keyboard = [[InlineKeyboardButton("Skip", callback_data=f"skip_thumb_{media_type}_{media_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(
        f"Generated info for: {details.get('title', details.get('name'))}\n\n"
        "Send a custom thumbnail or click Skip to use default poster.",
        reply_markup=reply_markup
    )
    
    # Store temporary state to handle thumbnail upload
    context.user_data["pending_post"] = {
        "text": post_text,
        "poster_url": poster_url,
        "media_type": media_type,
        "media_id": media_id
    }

async def most_searched_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    most_searched = await db.get_most_searched(10)
    if not most_searched:
        await update.message.reply_text("No search history found.")
        return

    keyboard = []
    for item in most_searched:
        keyboard.append([InlineKeyboardButton(item["query"].title(), callback_data=f"search_again_{item['query']}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Most Searched Queries:", reply_markup=reply_markup)

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
