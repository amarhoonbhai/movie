from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.force_join import force_join_check
from utils.tmdb import tmdb
from utils.formatter import format_movie_caption, format_series_caption
from database import db
from config import STORAGE_CHANNEL, ALLOWED_GROUP

@Client.on_message(filters.command("search"))
async def search_cmd(client: Client, message: Message):
    import logging
    logging.info(f"Received /search from {message.from_user.id if message.from_user else 'Unknown'}")
    if not await force_join_check(client, message):
        return
    
    if len(message.command) < 2:
        await message.reply_text("❌ **Please specify a movie or series name!**\n\nExample: `/search kgf 2`")
        return
    
    query = " ".join(message.command[1:])
    await db.add_trending(query)
    
    msg = await message.reply_text(f"🔍 Searching for **{query}**... Please wait.")
    
    # ── Search in Storage Channel ─────────────────────────────────────
    try:
        results = []
        async for m in client.search_messages(STORAGE_CHANNEL, query=query):
            if m.document or m.video:
                results.append(m)
    except Exception as e:
        import traceback
        logging.error(f"Search traceback: {traceback.format_exc()}")
        await msg.edit(f"⚠️ **An error occurred during search.**\n\nError: `{str(e)}`")
        return
    
    if not results:
        await db.add_request(query, message.from_user.id)
        await msg.edit(
            f"❌ **{query}** not found in our database!\n\nWe have added it to our **request list**. Our team will upload it soon and you'll be notified.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎯 Request Support", url="https://t.me/PhiloBots")]])
        )
        return
    
    await msg.edit(f"✅ Found **{len(results)}** results! Fetching premium metadata...")
    
    # ── Fetch Metadata from TMDB ─────────────────────────────────────
    details = await tmdb.get_details(query)
    
    # ── Forward Each Result ───────────────────────────────────────────
    success_count = 0
    first_msg_id = None
    
    # Process the best result to provide a direct link
    for m in results[:1]: 
        try:
            if details:
                caption = format_movie_caption(details) if details["type"] == "movie" else format_series_caption(details)
            else:
                caption = m.caption or f"📂 **File:** `{query}`"
            
            # Premium UI Buttons for the forwarded file
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 How to Download", url="https://t.me/PhiloBots")],
                [InlineKeyboardButton("⭐️ Rate Bot", url="https://t.me/PhiloBots/1")]
            ])
            
            forwarded = await client.copy_message(
                chat_id=ALLOWED_GROUP,
                from_chat_id=STORAGE_CHANNEL,
                message_id=m.id,
                caption=caption,
                reply_markup=buttons
            )
            success_count += 1
            first_msg_id = forwarded.id
        except Exception as e:
            logger.error(f"Forward error: {e}")
            continue
    
    if success_count > 0:
        group_id_str = str(ALLOWED_GROUP).replace("-100", "")
        deep_link = f"https://t.me/c/{group_id_str}/{first_msg_id}"
        
        await msg.edit(
            f"✅ **Success!** Your movie **{query}** has been sent to our community group.\n\nClick the button below to get your file! 👇",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎬 Get Movie File", url=deep_link)]])
        )
    else:
        await msg.edit("❌ Failed to forward files. Please check if the bot has permissions in the group.")

@Client.on_message(filters.command(["trending", "mostlist"]) & filters.private)
async def trending_cmd(client: Client, message: Message):
    if not await force_join_check(client, message):
        return
    
    trending = await db.get_trending(10)
    
    text = "🔥 **Trending Movies & Series** 🔥\n\n"
    if not trending:
        text += "No trending data available yet. Start searching!"
    else:
        for i, t in enumerate(trending, 1):
            text += f"{i}. **{t['name'].title()}** — `{t['count']} searches`\n"
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ])
    
    if hasattr(message, 'edit'):
        await message.edit(text, reply_markup=buttons)
    else:
        await message.reply_text(text, reply_markup=buttons)
