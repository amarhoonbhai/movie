from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant
from config import FSUB_CHANNEL, FSUB_LINK

async def is_subscribed(client, user_id):
    try:
        member = await client.get_chat_member(FSUB_CHANNEL, user_id)
    except UserNotParticipant:
        return False
    except Exception:
        return True # Fallback for admins or some issues
    return True

async def force_join_check(client, message: Message):
    if not await is_subscribed(client, message.from_user.id):
        join_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("Join Our Channel", url=FSUB_LINK)],
            [InlineKeyboardButton("Try Again", callback_data="check_join")]
        ])
        await message.reply_text(
            "⚠️ **Access Denied!**\n\nYou must join our channel to use this bot.",
            reply_markup=join_button
        )
        return False
    return True
