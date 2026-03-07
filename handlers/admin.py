from telegram import Update
from telegram.ext import ContextTypes
from database import db
from config import OWNER_IDS, ADMIN_IDS

async def admin_cmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await db.is_admin(user_id):
        await update.message.reply_text("You are not an admin.")
        return

    admin_msg = (
        "<b>Admin Commands:</b>\n\n"
        "/stats - Get bot statistics\n"
        "/addadmin {user_id} - Add a new admin\n"
        "/removeadmin {user_id} - Remove an admin\n"
        "/broadcast - Send message to all users\n"
        "/ban {user_id} - Ban a user\n"
        "/unban {user_id} - Unban a user\n"
        "/requests - View Movie Requests"
    )
    await update.message.reply_text(admin_msg, parse_mode="HTML")

async def requests_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await db.is_admin(user_id): return
    
    requests = db._movie_requests
    if not requests:
        await update.message.reply_text("No movie requests found.")
        return
        
    text = "📥 <b>Movie Requests:</b>\n\n"
    for i, req in enumerate(requests, 1):
        text += f"{i}. {req}\n"
        
    await update.message.reply_text(text, parse_mode="HTML")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await db.is_admin(user_id): return
    
    users_count, premium_count = await db.get_stats()
    await update.message.reply_text(f"Bot Stats:\n\nTotal Users: {users_count}\nPremium Users: {premium_count}")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await db.is_admin(user_id): return
    
    # Broadcast logic
    msg_to_broadcast = " ".join(context.args)
    if not msg_to_broadcast:
        await update.message.reply_text("Please provide a message to broadcast.")
        return
        
    users = await db.get_all_users()
    count = 0
    for user in users:
        try:
            await context.bot.send_message(chat_id=user["user_id"], text=msg_to_broadcast)
            count += 1
        except Exception:
            pass
    await update.message.reply_text(f"Successfully broadcasted to {count} users.")

async def add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNER_IDS: return # Only owners can add admins
    
    if not context.args: return
    new_admin_id = int(context.args[0])
    await db.add_admin(new_admin_id)
    await update.message.reply_text(f"Successfully added admin: {new_admin_id}")

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await db.is_admin(user_id): return
    
    if not context.args: return
    target_id = int(context.args[0])
    await db.ban_user(target_id)
    await update.message.reply_text(f"Successfully banned user: {target_id}")
