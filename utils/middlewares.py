from telegram import Update
from telegram.error import BadRequest
from config import FSUB_CHANNEL, ALLOWED_GROUP, OWNER_IDS, ADMIN_IDS

async def is_subscribed(bot, user_id):
    """
    Check if a user is subscribed to the force-subscribe channel.
    Returns True if subscribed or if checking fails (to avoid blocking users on API issues).
    """
    if not FSUB_CHANNEL:
        return True
    
    # Owners and Admins are always considered subscribed for UX
    if user_id in OWNER_IDS or user_id in ADMIN_IDS:
        return True

    try:
        member = await bot.get_chat_member(chat_id=FSUB_CHANNEL, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except BadRequest as e:
        if "User not found" in str(e):
            return False
        # If bot is not admin in channel, we can't check
        return True
    except Exception:
        return True
    
    return False

async def is_allowed_chat(update: Update):
    """
    Check if the chat is the allowed group or a private chat with an admin.
    """
    chat = update.effective_chat
    user_id = update.effective_user.id
    
    if chat.id == ALLOWED_GROUP:
        return True
    
    if chat.type == "private":
        from database import db
        if await db.is_admin(user_id):
            return True
            
    return False
