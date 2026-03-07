from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from api.tmdb import tmdb


async def trending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        if update.message:
            await update.message.set_reaction(reactions=["📈"])
    except Exception:
        pass

    results = await tmdb.get_trending("all", "day")
    message = update.effective_message

    if not results:
        await message.reply_text("No trending results found.")
        return

    keyboard = []
    for res in results:
        title = res.get("title", res.get("name", "Unknown"))
        media_type = res.get("media_type")
        media_id = res.get("id")
        keyboard.append([InlineKeyboardButton(f"🔥 {title}", callback_data=f"details_{media_type}_{media_id}")])

    await message.reply_text(
        "<b>🔥 Top Trending Today:</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )


async def trending_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    results = await tmdb.get_trending("all", "day")
    if not results:
        await query.message.reply_text("No trending results found.")
        return

    keyboard = []
    for res in results:
        title = res.get("title", res.get("name", "Unknown"))
        media_type = res.get("media_type")
        media_id = res.get("id")
        keyboard.append([InlineKeyboardButton(f"🔥 {title}", callback_data=f"details_{media_type}_{media_id}")])

    try:
        await query.edit_message_text(
            "<b>🔥 Top Trending Today:</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )
    except Exception:
        await query.message.reply_text(
            "<b>🔥 Top Trending Today:</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )
