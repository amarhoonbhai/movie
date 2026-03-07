from telegram import Update
from telegram.error import BadRequest
from config import FSUB_CHANNEL

async def is_subscribed(bot, user_id):
    """
    Check if a user is subscribed to the force-subscribe channel.
    Returns True if subscribed or if checking fails (to avoid blocking users on API issues).
    """
    if not FSUB_CHANNEL:
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
