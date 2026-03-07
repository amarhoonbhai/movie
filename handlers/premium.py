import requests
from telegram import Update
from telegram.ext import ContextTypes

async def img2link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send an image to get its direct link.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = update.effective_user.id
    
    # Check if user is in "pending_post" state for custom thumbnail
    pending = context.user_data.get("pending_post")
    if pending:
        photo = await message.photo[-1].get_file()
        photo_url = photo.file_path # This is a temporary URL from Telegram
        
        # In a real bot, we'd upload this to a persistent host or just use the Telegram file_id
        # For professional UI, we'll use the uploaded photo directly.
        await message.reply_photo(
            photo=photo.file_id,
            caption=pending["text"],
            parse_mode="HTML"
        )
        context.user_data.pop("pending_post", None)
        return

    # Regular img2link logic
    photo = await message.photo[-1].get_file()
    # Ideally upload to telegra.ph here
    # For now, providing the Telegram file path (note: expires in 1 hour)
    await message.reply_text(f"Direct Image URL (expires in 1h):\n{photo.file_path}")

async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    referral_link = f"https://t.me/{context.bot.username}?start=ref_{user_id}"
    message = update.effective_message
    
    await message.reply_text(
        "🎁 <b>Referral System</b>\n\n"
        f"Your Referral Link: {referral_link}\n\n"
        "Invite 10 friends to unlock Premium benefits for free!",
        parse_mode="HTML"
    )

async def plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    plans_text = (
        "👑 <b>Premium Benefits:</b>\n\n"
        "➥ No need to open links\n"
        "➥ Direct files\n"
        "➥ Ad free\n"
        "➥ High speed downloads\n"
        "➥ Unlimited movies\n"
        "➥ Admin support\n\n"
        "Choose a plan below:"
    )
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = [
        [InlineKeyboardButton("See Plans", callback_data="see_plans")],
        [InlineKeyboardButton("Close", callback_data="close_plan")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text(plans_text, reply_markup=reply_markup, parse_mode="HTML")
