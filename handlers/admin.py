from telegram import Update
from telegram.ext import ContextTypes
from database import db
from config import OWNER_IDS


async def admin_cmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await db.is_admin(user_id):
        await update.message.reply_text("You are not an admin.")
        return

    admin_msg = (
        "<b>Admin Commands:</b>\n\n"
        "/stats - Bot statistics\n"
        "/addadmin {user_id} - Add admin\n"
        "/removeadmin {user_id} - Remove admin\n"
        "/broadcast {msg} - Message all users\n"
        "/ban {user_id} - Ban user\n"
        "/requests - View movie requests"
    )
    await update.message.reply_text(admin_msg, parse_mode="HTML")


async def requests_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await db.is_admin(update.effective_user.id):
        return

    reqs = await db.get_movie_requests()
    if not reqs:
        await update.message.reply_text("No movie requests found.")
        return

    text = "📥 <b>Movie Requests:</b>\n\n"
    for i, req in enumerate(reqs, 1):
        text += f"{i}. {req}\n"

    await update.message.reply_text(text, parse_mode="HTML")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await db.is_admin(update.effective_user.id):
        return

    users_count, premium_count = await db.get_stats()
    indexed = len(db._indexed_files)
    requests_count = len(db._movie_requests)

    text = (
        "<b>📊 Bot Stats:</b>\n\n"
        f"👥 Users: {users_count}\n"
        f"👑 Premium: {premium_count}\n"
        f"📁 Indexed Files: {indexed}\n"
        f"📥 Movie Requests: {requests_count}"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await db.is_admin(update.effective_user.id):
        return

    msg_to_broadcast = " ".join(context.args) if context.args else ""
    if not msg_to_broadcast:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    users = await db.get_all_users()
    count = 0
    for user in users:
        try:
            await context.bot.send_message(chat_id=user["user_id"], text=msg_to_broadcast)
            count += 1
        except Exception:
            pass
    await update.message.reply_text(f"✅ Broadcasted to {count}/{len(users)} users.")


async def add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNER_IDS:
        return
    if not context.args:
        await update.message.reply_text("Usage: /addadmin <user_id>")
        return
    new_admin_id = int(context.args[0])
    await db.add_admin(new_admin_id)
    await update.message.reply_text(f"✅ Added admin: {new_admin_id}")


async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await db.is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /ban <user_id>")
        return
    target_id = int(context.args[0])
    await db.ban_user(target_id)
    await update.message.reply_text(f"✅ Banned user: {target_id}")
