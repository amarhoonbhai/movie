from pyrogram import Client, filters
from pyrogram.types import Message
from database import db
from config import OWNER_ID, ADMIN_IDS
import asyncio

@Client.on_message(filters.command("stats") & filters.user(ADMIN_IDS))
async def stats_cmd(client: Client, message: Message):
    users = await db.total_users_count()
    requests = await db.get_requests_count()
    trending = await db.get_trending(5)
    
    text = f"""📊 **Bot Statistics**

👤 **Total Users:** `{users}`
📥 **Total Requests:** `{requests}`

🔥 **Trending Searches:**
"""
    for i, t in enumerate(trending, 1):
        text += f"{i}. {t['name']} ({t['count']})\n"
    
    await message.reply_text(text)

@Client.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("❌ Reply to a message to broadcast it!")
        return
    
    query = await db.get_all_users()
    msg = await message.reply_text(f"⏳ Broadcast started to `{len(query)}` users...")
    
    success = 0
    failed = 0
    
    for user in query:
        try:
            await message.reply_to_message.copy(user["_id"])
            success += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05) # Rate limiting
    
    await msg.edit(f"✅ **Broadcast Completed!**\n\n🚀 Success: `{success}`\n❌ Failed: `{failed}`")
