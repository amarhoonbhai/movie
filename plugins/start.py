from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.force_join import force_join_check, is_subscribed
from database import db
from config import BANNER_URL

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    if not await force_join_check(client, message):
        return
    
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()
    
    await db.add_user(message.from_user.id, first_name, last_name)
    
    text = f"""🌟 **Welcome to PhiloBots Movie Search!** 🌟

Hello **{full_name}**, I'm your high-performance movie assistant. 🚀

───────────────────────
🔹 **Search Movies & Series** instantly.
🔹 **Professional Metadata** & High Quality.
🔹 **Fast Forwarding** to our community.
───────────────────────

💡 **How to use:**
Simply type `/search movie_name` or click the button below!"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔍 Search Movie", switch_inline_query_current_chat="/search "),
            InlineKeyboardButton("🚀 Trending", callback_data="show_trending")
        ],
        [
            InlineKeyboardButton("💎 Premium Features", callback_data="show_premium"),
            InlineKeyboardButton("🛡️ Support", url="https://t.me/PhiloBots")
        ]
    ])
    
    if BANNER_URL:
        await message.reply_photo(BANNER_URL, caption=text, reply_markup=buttons)
    else:
        await message.reply_text(text, reply_markup=buttons)

@Client.on_callback_query(filters.regex("check_join"))
async def check_join_callback(client: Client, callback_query: CallbackQuery):
    if await is_subscribed(client, callback_query.from_user.id):
        await callback_query.message.delete()
        await start_cmd(client, callback_query.message)
    else:
        await callback_query.answer("❌ You still haven't joined!", show_alert=True)

@Client.on_callback_query(filters.regex("show_trending"))
async def trending_callback(client: Client, callback_query: CallbackQuery):
    # Use callback_query.answer() before doing long ops or changing message
    from plugins.search import trending_cmd
    await trending_cmd(client, callback_query.message)

@Client.on_callback_query(filters.regex("show_premium"))
async def premium_callback(client: Client, callback_query: CallbackQuery):
    from plugins.premium import premium_info
    await premium_info(client, callback_query.message)
