from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def img2link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🖼️ Send an image to get its direct link.")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # Custom thumbnail flow
    pending = context.user_data.get("pending_post")
    if pending:
        photo = await message.photo[-1].get_file()
        await message.reply_photo(
            photo=photo.file_id,
            caption=pending["text"],
            parse_mode="HTML",
        )
        context.user_data.pop("pending_post", None)
        return

    # Regular img2link
    photo = await message.photo[-1].get_file()
    await message.reply_text(f"📎 Direct URL (expires in 1h):\n{photo.file_path}")


async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    referral_link = f"https://t.me/{context.bot.username}?start=ref_{user_id}"

    await update.effective_message.reply_text(
        "🎁 <b>Referral System</b>\n\n"
        f"Your Referral Link:\n<code>{referral_link}</code>\n\n"
        "Invite 10 friends to unlock Premium benefits for free!",
        parse_mode="HTML",
    )


async def plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plans_text = (
        "👑 <b>Premium Benefits:</b>\n\n"
        "➥ No need to open links\n"
        "➥ Direct files\n"
        "➥ Ad free\n"
        "➥ High speed downloads\n"
        "➥ Unlimited movies\n"
        "➥ Admin support\n\n"
        "Contact admin to subscribe!"
    )
    keyboard = [
        [InlineKeyboardButton("❌ Close", callback_data="close_plan")],
    ]
    await update.effective_message.reply_text(
        plans_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )
