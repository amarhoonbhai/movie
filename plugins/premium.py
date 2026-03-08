from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID

@Client.on_message(filters.command("premium") & filters.private)
async def premium_cmd(client: Client, message: Message):
    await premium_info(client, message)

async def premium_info(client: Client, message: Message):
    text = """💎 **PhiloBots Premium Features** 💎

Experience the ultimate movie searching experience with our premium plans!

✨ **Benefits:**
• 🚀 **High-Speed** search results.
• 📁 **Direct Downloads** (No Ads).
• 🎬 **Exclusive Movie** requests.
• 🌟 **Early Access** to new uploads.
• 🚫 **Ad-Free** experience in group.

💳 **Subscription Plans:**
• 🕒 **1 Month:** ₹49
• 🕒 **3 Months:** ₹129
• 🕒 **1 Year:** ₹399

To purchase, contact our admin below!"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Buy Premium", url="https://t.me/PhiloBots")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
    ])
    
    # Check if it's a message or callback
    if hasattr(message, 'edit'):
        await message.edit(text, reply_markup=buttons)
    else:
        await message.reply_text(text, reply_markup=buttons)

@Client.on_callback_query(filters.regex("back_to_start"))
async def back_to_start(client: Client, callback_query: Message):
    from plugins.start import start_cmd
    await callback_query.message.delete()
    await start_cmd(client, callback_query.message)
