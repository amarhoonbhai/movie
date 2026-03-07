from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from api.tmdb import tmdb

async def trending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Animations & Reactions
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        if update.message:
            await update.message.set_reaction(reactions=["📈"])
    except:
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
        callback_data = f"details_{media_type}_{media_id}"
        keyboard.append([InlineKeyboardButton(title, callback_data=callback_data)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("Top Trending Today:", reply_markup=reply_markup)

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
        callback_data = f"details_{media_type}_{media_id}"
        keyboard.append([InlineKeyboardButton(title, callback_data=callback_data)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Top Trending Today:", reply_markup=reply_markup)
