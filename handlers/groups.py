import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ALLOWED_GROUP, STORAGE_CHANNEL, FSUB_CHANNEL
from database import db
from utils.middlewares import is_subscribed, is_allowed_chat

logger = logging.getLogger(__name__)


async def index_storage_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Index files posted in STORAGE_CHANNEL by their caption."""
    if update.channel_post and update.channel_post.chat.id == STORAGE_CHANNEL:
        msg = update.channel_post
        caption = msg.caption or msg.text
        if caption:
            await db.index_file(caption, msg.message_id)


async def group_search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-filter: search for movies when users type in the allowed group."""
    if not update.message or not update.message.text:
        return

    if not await is_allowed_chat(update):
        return

    user_id = update.effective_user.id
    query_text = update.message.text.strip()

    if query_text.startswith("/"):
        return

    # Force Join Check
    if not await is_subscribed(context.bot, user_id):
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FSUB_CHANNEL.replace('@', '')}")],
            [InlineKeyboardButton("🔄 Verify", url=f"https://t.me/{context.bot.username}?start=verify")],
        ]
        await update.message.reply_text(
            f"<b>You must join {FSUB_CHANNEL} to use this bot.</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )
        return

    # Typing animation
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    results = await db.search_files(query_text)

    if not results:
        await db.add_movie_request(query_text)
        await update.message.reply_text(
            "❌ <b>Movie not found.</b>\n📥 Your request has been added.",
            parse_mode="HTML",
        )
        return

    if len(results) == 1:
        try:
            await context.bot.forward_message(
                chat_id=ALLOWED_GROUP,
                from_chat_id=STORAGE_CHANNEL,
                message_id=results[0]["message_id"],
            )
        except Exception as e:
            logger.error(f"Forward failed: {e}")
            await update.message.reply_text("⚠️ Could not forward file. Contact admin.")
    else:
        keyboard = []
        for res in results:
            caption = res["caption"]
            msg_id = res["message_id"]
            # Truncate caption for button text (Telegram 64-byte callback_data limit)
            label = caption[:40].title()
            keyboard.append([InlineKeyboardButton(label, callback_data=f"fwd_{msg_id}")])

        await update.message.reply_text(
            "📍 <b>Multiple Qualities Found:</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )


async def file_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward the selected file from storage channel."""
    query = update.callback_query
    await query.answer()

    msg_id = int(query.data.split("_")[1])

    try:
        await context.bot.forward_message(
            chat_id=ALLOWED_GROUP,
            from_chat_id=STORAGE_CHANNEL,
            message_id=msg_id,
        )
    except Exception as e:
        logger.error(f"Forward failed: {e}")
        await query.message.reply_text("⚠️ Could not forward file. Contact admin.")
