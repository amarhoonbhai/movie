from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import BANNER_URL, TUTORIAL_URL
from database import db

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.add_user(user.id, user.username, user.full_name)
    
    keyboard = [
        [
            InlineKeyboardButton("SPECIAL", callback_data="special"),
            InlineKeyboardButton("ABOUT", callback_data="about")
        ],
        [
            InlineKeyboardButton("Click Here to See Tutorial", url=TUTORIAL_URL)
        ],
        [
            InlineKeyboardButton("REFER", callback_data="refer"),
            InlineKeyboardButton("SHARE ME", switch_inline_query="Check this awesome movie bot!")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = (
        f"Hi {user.first_name}!\n\n"
        "Welcome to the Professional Movie & Series Bot. "
        "Search your favorite movies and web series by name."
    )
    
    await update.message.reply_photo(
        photo=BANNER_URL,
        caption=welcome_msg,
        reply_markup=reply_markup
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("MOST SEARCH", callback_data="most_searched"),
            InlineKeyboardButton("TOP TRENDING", callback_data="trending")
        ],
        [
            InlineKeyboardButton("IMAGE TO LINK", callback_data="img2link_info"),
            InlineKeyboardButton("HOME", callback_data="home")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Main Menu:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "home":
        await query.edit_message_text("Welcome Home! Use /start to see the main banner or /menu for options.")
    elif query.data == "special":
        await query.edit_message_text("SPECIAL feature: Stay tuned for updates!")
    elif query.data == "about":
        await query.edit_message_text("This bot allows you to search for movies and series using TMDb API.")
    elif query.data == "img2link_info":
        await query.edit_message_text("Use the /img2link command and send an image to get a direct URL.")
