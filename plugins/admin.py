"""
plugins/admin.py — Admin commands: /stats, /broadcast, /requests.
Owner/admin-only guards applied.
"""
import asyncio
import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from config import OWNER_ID, ADMIN_IDS
from database import db

logger = logging.getLogger(__name__)

_admin_filter = filters.user([OWNER_ID] + ADMIN_IDS)
_owner_filter = filters.user(OWNER_ID)


# ── /stats ────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("stats") & _admin_filter)
async def stats_cmd(client: Client, message: Message):
    users_count   = await db.total_users_count()
    files_count   = await db.files_count()
    req_count     = await db.get_requests_count()
    trending_list = await db.get_trending(5)

    text = (
        "📊 <b>Bot Statistics</b>\n\n"
        f"👤 <b>Total Users:</b>        <code>{users_count}</code>\n"
        f"🎬 <b>Movies Indexed:</b>     <code>{files_count}</code>\n"
        f"📥 <b>Total Requests:</b>     <code>{req_count}</code>\n\n"
        "━━━━━━━━━━━━━━\n"
        "🔥 <b>Trending Searches:</b>\n"
    )
    if trending_list:
        for i, t in enumerate(trending_list, 1):
            text += f"  {i}. {t['query'].title()} ({t['count']})\n"
    else:
        text += "  No trending data yet.\n"

    await message.reply_text(text, parse_mode="html")


# ── /requests ─────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("requests") & _admin_filter)
async def requests_cmd(client: Client, message: Message):
    reqs = await db.get_all_requests(20)
    if not reqs:
        await message.reply_text("📭 No pending movie requests.")
        return

    text = "📥 <b>Pending Movie Requests</b>\n\n"
    for i, req in enumerate(reqs, 1):
        count = len(req.get("requested_by", []))
        text += f"{i}. <b>{req['movie'].title()}</b> — {count} user{'s' if count != 1 else ''}\n"

    await message.reply_text(text, parse_mode="html")


# ── /broadcast ────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("broadcast") & _owner_filter)
async def broadcast_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text(
            "❌ <b>Usage:</b> Reply to any message with <code>/broadcast</code> to send it to all users.",
            parse_mode="html",
        )
        return

    users = await db.get_all_users()
    total = len(users)

    status_msg = await message.reply_text(
        f"⏳ Broadcasting to <b>{total}</b> users…", parse_mode="html"
    )

    success, failed = 0, 0
    for user in users:
        uid = user.get("user_id")
        if not uid:
            continue
        try:
            await message.reply_to_message.copy(uid)
            success += 1
        except Exception:
            failed += 1
        # Rate-limit: ~20 msgs/sec
        await asyncio.sleep(0.05)

    await status_msg.edit_text(
        f"✅ <b>Broadcast Completed!</b>\n\n"
        f"🚀 Success: <code>{success}</code>\n"
        f"❌ Failed:  <code>{failed}</code>",
        parse_mode="html",
    )
