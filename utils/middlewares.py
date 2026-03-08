"""
utils/middlewares.py — Force-join and chat permission checks (Pyrogram).
"""
import logging
from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, ChannelPrivate
from config import (
    FSUB_CHANNEL, FSUB_CHANNEL_ID, FSUB_LINK,
    FSUB_GROUP_ID, ALLOWED_GROUP, OWNER_ID, ADMIN_IDS,
)

logger = logging.getLogger(__name__)


async def is_subscribed(client: Client, user_id: int) -> bool:
    """
    Returns True only if the user is a member of BOTH force-join channels.
    Owners and admins always pass.
    """
    if user_id == OWNER_ID or user_id in ADMIN_IDS:
        return True

    # Check channel 1 (@PhiloBots)
    try:
        member = await client.get_chat_member(FSUB_CHANNEL, user_id)
        if member.status.value in ("left", "banned", "restricted"):
            return False
    except UserNotParticipant:
        return False
    except (ChatAdminRequired, ChannelPrivate):
        logger.warning("Bot is not admin in FSUB_CHANNEL — skipping check.")
    except Exception as e:
        logger.debug(f"FSUB check error (channel 1): {e}")

    # Check group 2 (the invite-link group)
    try:
        member2 = await client.get_chat_member(FSUB_GROUP_ID, user_id)
        if member2.status.value in ("left", "banned", "restricted"):
            return False
    except UserNotParticipant:
        return False
    except (ChatAdminRequired, ChannelPrivate):
        logger.warning("Bot is not admin in FSUB_GROUP — skipping check.")
    except Exception as e:
        logger.debug(f"FSUB check error (group 2): {e}")

    return True


async def force_join_check(client: Client, message: Message) -> bool:
    """
    Returns True if the user has joined all required channels.
    If not, sends a join-prompt message with buttons and returns False.
    """
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        return False

    if await is_subscribed(client, user_id):
        return True

    join_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FSUB_CHANNEL.lstrip('@')}"),
            InlineKeyboardButton("🔔 Join Updates", url=FSUB_LINK),
        ],
        [InlineKeyboardButton("✅ I Joined", callback_data="check_join")],
    ])

    await message.reply_text(
        "🚫 **Access Denied!**\n\n"
        "You must join our channels to use this bot.\n\n"
        "▶ Click the buttons below to join, then tap **✅ I Joined**.",
        reply_markup=join_markup,
    )
    return False
