"""
/start command, stats, trending, and requests.
"""
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from core.config import BANNER_URL, FSUB_CHANNEL, DEV_USERNAME, SUPPORT_GROUP, SUPPORT_CHANNEL
from core.database import db
from utils.force_join import force_join_check, is_subscribed

logger = logging.getLogger(__name__)

# ── /start ─────────────────────────────────────────────────────────────────────
@Client.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    if not await force_join_check(client, message):
        return

    user = message.from_user
    await db.add_user(user_id=user.id, first_name=user.first_name, username=user.username)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔍 Search Movie", switch_inline_query_current_chat=""),
            InlineKeyboardButton("📥 Requests",     callback_data="show_requests"),
        ],
        [
            InlineKeyboardButton("📊 Stats",   callback_data="show_stats"),
            InlineKeyboardButton("🔥 Trending", callback_data="show_trending"),
        ],
        [
            InlineKeyboardButton("💬 Support Group", url=SUPPORT_GROUP) if SUPPORT_GROUP else InlineKeyboardButton("📢 Channel", url=f"https://t.me/{FSUB_CHANNEL.lstrip('@')}"),
            InlineKeyboardButton("📢 Channel", url=SUPPORT_CHANNEL) if SUPPORT_CHANNEL else InlineKeyboardButton("👨‍💻 Developer", url=f"https://t.me/{DEV_USERNAME.lstrip('@')}"),
        ],
    ])

    bio = ""
    try:
        # Fetch bio if available (requires full user object sometimes, but we try)
        full_user = await client.get_users(user.id)
        if getattr(full_user, 'bio', None):
            bio = f"\n📝 <b>Bio:</b> <i>{full_user.bio}</i>"
    except Exception:
        pass

    welcome = (
        f"🎬 <b>Welcome to Movie Finder Bot</b>\n\n"
        f"👤 <b>Name:</b> {user.first_name}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>{bio}\n\n"
        "Search and download movies directly in the group.\n\n"
        "<b>Commands:</b>\n"
        "• /search <i>movie name</i> → Search movies\n"
        "• /help → View all features\n"
        "• /trending → Top searched movies\n"
        "• /requests → View requested movies\n\n"
        "━━━━━━━━━━━━━━\n"
        f"👨‍💻 <b>Developer:</b> {DEV_USERNAME}\n"
        "━━━━━━━━━━━━━━"
    )

    try:
        await message.reply_photo(photo=BANNER_URL, caption=welcome, reply_markup=keyboard, parse_mode="html")
    except Exception:
        await message.reply_text(text=welcome, reply_markup=keyboard, parse_mode="html")

# ── /help ─────────────────────────────────────────────────────────────────────
@Client.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    if not await force_join_check(client, message):
        return

    help_text = (
        "💡 **How to use this bot:**\n\n"
        "1️⃣ **Search a Movie**\n"
        "Send `/search <Movie Name>` in the group.\n"
        "Example: `/search Avatar`\n\n"
        "2️⃣ **View Top Movies**\n"
        "`/trending`, `/top_movie`, or `/top_search` to see what everyone is looking for!\n\n"
        "3️⃣ **View Stats**\n"
        "`/stats` to see bot indexing stats and `/top_users` for user stats.\n\n"
        f"💬 **Need Help?** Join our Support Group: {SUPPORT_GROUP or 'N/A'}"
    )
    await message.reply_text(help_text, disable_web_page_preview=True)

# ── Trending / Top Movie Commands ─────────────────────────────────────────────
@Client.on_message(filters.command(["trending", "top_movie", "top_search"]))
async def top_search_cmd(client: Client, message: Message):
    if not await force_join_check(client, message):
        return

    trending_list = await db.get_trending(10)
    if not trending_list:
        await message.reply_text("No trending data yet. Start searching!")
        return

    text = "🔥 <b>Top Searched Movies</b>\n\n"
    for i, t in enumerate(trending_list, 1):
        text += f"{i}. <b>{t['query'].title()}</b> <code>({t['count']} searches)</code>\n"

    await message.reply_text(text, parse_mode="html")

# ── Top Users Command ─────────────────────────────────────────────────────────
@Client.on_message(filters.command("top_users"))
async def top_users_cmd(client: Client, message: Message):
    if not await force_join_check(client, message):
        return

    # Assuming we create a get_top_users method, or just show total users for now
    users_count = await db.total_users_count()
    await message.reply_text(f"🏆 <b>Top Users Stats:</b>\n\nWe currently have <b>{users_count}</b> amazing users!", parse_mode="html")


# ── ✅ I Joined callback ────────────────────────────────────────────────────────
@Client.on_callback_query(filters.regex("^check_join$"))
async def check_join_callback(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if await is_subscribed(client, user_id):
        await callback.answer("✅ Verified! Welcome.", show_alert=True)
        try:
            await callback.message.delete()
        except:
            pass

        user = callback.from_user
        await db.add_user(user.id, user.first_name, user.username)

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔍 Search Movie", switch_inline_query_current_chat=""),
                InlineKeyboardButton("📥 Requests",     callback_data="show_requests"),
            ],
            [
                InlineKeyboardButton("📊 Stats",   callback_data="show_stats"),
                InlineKeyboardButton("🔥 Trending", callback_data="show_trending"),
            ],
            [
                InlineKeyboardButton("💬 Support Group", url=SUPPORT_GROUP) if SUPPORT_GROUP else InlineKeyboardButton("📢 Channel", url=f"https://t.me/{FSUB_CHANNEL.lstrip('@')}"),
            ],
        ])

        welcome = (
            f"🎬 <b>Welcome to Movie Finder Bot</b>\n\n"
            f"Hello <b>{user.first_name}</b>! 👋\n\n"
            "Search and download movies directly in the group.\n\n"
            "<b>Commands:</b>\n"
            "• /search <i>movie name</i> → Search movies\n"
            "• /help → View all features\n\n"
            "━━━━━━━━━━━━━━\n"
            f"👨‍💻 <b>Developer:</b> {DEV_USERNAME}\n"
            "━━━━━━━━━━━━━━"
        )
        try:
            await client.send_photo(chat_id=callback.message.chat.id, photo=BANNER_URL, caption=welcome, reply_markup=keyboard, parse_mode="html")
        except Exception:
            await client.send_message(chat_id=callback.message.chat.id, text=welcome, reply_markup=keyboard, parse_mode="html")
    else:
        await callback.answer("❌ You haven't joined yet! Please join both channels first.", show_alert=True)

# ── show_stats callback ───────────────────────────────────────────────────────
@Client.on_callback_query(filters.regex("^show_stats$"))
async def show_stats_callback(client: Client, callback: CallbackQuery):
    await callback.answer()
    users_count   = await db.total_users_count()
    files_count   = await db.files_count()
    req_count     = await db.get_requests_count()
    trending_list = await db.get_trending(5)

    text = (
        "📊 <b>Bot Statistics</b>\n\n"
        f"👤 <b>Total Users:</b> <code>{users_count}</code>\n"
        f"🎬 <b>Movies Indexed:</b> <code>{files_count}</code>\n"
        f"📥 <b>Total Requests:</b> <code>{req_count}</code>\n\n"
        "🔥 <b>Trending Searches:</b>\n"
    )
    for i, t in enumerate(trending_list, 1):
        text += f"  {i}. {t['query'].title()} ({t['count']})\n"

    await callback.message.reply_text(text, parse_mode="html")

# ── show_trending callback ─────────────────────────────────────────────────────
@Client.on_callback_query(filters.regex("^show_trending$"))
async def show_trending_callback(client: Client, callback: CallbackQuery):
    await callback.answer()
    trending_list = await db.get_trending(10)
    if not trending_list:
        await callback.message.reply_text("No trending data yet. Start searching!")
        return

    text = "🔥 <b>Trending Searches</b>\n\n"
    for i, t in enumerate(trending_list, 1):
        text += f"{i}. {t['query'].title()} <code>({t['count']})</code>\n"

    await callback.message.reply_text(text, parse_mode="html")

# ── show_requests callback ─────────────────────────────────────────────────────
@Client.on_callback_query(filters.regex("^show_requests$"))
async def show_requests_callback(client: Client, callback: CallbackQuery):
    await callback.answer()
    reqs = await db.get_all_requests(15)
    if not reqs:
        await callback.message.reply_text("📭 No pending movie requests.")
        return

    text = "📥 <b>Pending Movie Requests</b>\n\n"
    for i, req in enumerate(reqs, 1):
        count = len(req.get("requested_by", []))
        text += f"{i}. <b>{req['movie'].title()}</b> — {count} user{'s' if count != 1 else ''}\n"

    await callback.message.reply_text(text, parse_mode="html")
