import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ALLOWED_GROUP, STORAGE_CHANNEL, FSUB_CHANNEL
from database import db
from utils.middlewares import is_subscribed, is_allowed_chat

logger = logging.getLogger(__name__)

async def index_storage_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Listens to channel posts in STORAGE_CHANNEL and indexes them in the database.
    """
    if update.channel_post and update.channel_post.chat.id == STORAGE_CHANNEL:
        msg = update.channel_post
        caption = msg.caption or msg.text
        if caption:
            await db.index_file(caption, msg.message_id)
            logger.info(f"Indexed file: {caption} (ID: {msg.message_id})")

async def group_search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Main handler for searching movies in the allowed group.
    """
    if not await is_allowed_chat(update):
        return

    user_id = update.effective_user.id
    query_text = update.message.text.strip()
    
    # Ignore commands
    if query_text.startswith("/"):
        return

    # Force Join Check
    if not await is_subscribed(context.bot, user_id):
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FSUB_CHANNEL.replace('@', '')}")],
            [InlineKeyboardButton("🔄 Verify", url=f"https://t.me/{context.bot.username}?start=verify")]
        ]
        await update.message.reply_text(
            f"<b>You must join {FSUB_CHANNEL} to use this bot.</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        return

    # Search in Indexed Files
    results = await db.search_files(query_text)

    if not results:
        await db.add_movie_request(query_text)
        await update.message.reply_text(
            "❌ <b>Movie not found.</b>\n"
            "📥 Your request has been added.",
            parse_mode="HTML"
        )
        return

    if len(results) == 1:
        # Forward single result directly
        await context.bot.forward_message(
            chat_id=ALLOWED_GROUP,
            from_chat_id=STORAGE_CHANNEL,
            message_id=results[0]["message_id"]
        )
    else:
        # Multiple results (Qualities)
        keyboard = []
        for res in results:
            caption = res["caption"]
            msg_id = res["message_id"]
            # Extract quality if possible for cleaner buttons, but user asked for caption buttons if multiple
            keyboard.append([InlineKeyboardButton(caption, callback_data=f"fwd_{msg_id}")])
            
        await update.message.reply_text(
            "📍 <b>Multiple Qualities Found:</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

async def file_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles button clicks for selecting a specific quality to forward.
    """
    query = update.callback_query
    await query.answer()
    
    # Pattern: fwd_message_id
    msg_id = int(query.data.split("_")[1])
    
    await context.bot.forward_message(
        chat_id=ALLOWED_GROUP,
        from_chat_id=STORAGE_CHANNEL,
        message_id=msg_id
    )
