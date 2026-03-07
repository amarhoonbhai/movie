from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import BANNER_URL, TUTORIAL_URL, FSUB_CHANNEL
from database import db
from utils.middlewares import is_subscribed

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.add_user(user.id, user.username, user.full_name)
    
    # Handle Deep Links (from Inline Search)
    args = context.args
    if args and args[0].startswith("info_"):
        # Format: info_media-type_media-id
        _, m_type, m_id = args[0].split("_")
        from handlers.search import search_details_callback
        # We need to simulate a callback query or refactor
        # For professional approach, we call the details logic directly
        from api.tmdb import tmdb
        from utils.formatters import get_post_text
        from config import TMDB_IMAGE_BASE_URL
        
        details = await tmdb.get_details(m_type, m_id)
        post_text = get_post_text(details, m_type, "portrait")
        media_url = f"{TMDB_IMAGE_BASE_URL}{details.get('poster_path')}"
        
        keyboard = [
            [InlineKeyboardButton("📱 Portrait", callback_data=f"details_{m_type}_{m_id}_portrait")],
            [InlineKeyboardButton("🖼️ Landscape", callback_data=f"details_{m_type}_{m_id}_landscape")],
            [InlineKeyboardButton("🏠 HOME", callback_data="home")]
        ]
        
        await update.message.reply_photo(
            photo=media_url,
            caption=post_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        return

    # Force Subscribe Check
    if not await is_subscribed(context.bot, user.id):
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FSUB_CHANNEL.replace('@', '')}")],
            [InlineKeyboardButton("🔄 Verify Membership", callback_data="verify_sub")]
        ]
        await update.message.reply_text(
            f"<b>Access Denied!</b> ❌\n\n"
            f"You must join our channel {FSUB_CHANNEL} to use this bot.\n"
            "After joining, click the verify button below.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        return

    keyboard = [
        [InlineKeyboardButton("🔍 SEARCH MOVIE", switch_inline_query_current_chat="")],
        [
            InlineKeyboardButton("🔥 TRENDING", callback_data="trending"),
            InlineKeyboardButton("📊 MOST SEARCHED", callback_data="most_searched")
        ],
        [
            InlineKeyboardButton("⭐ SPECIAL", callback_data="special"),
            InlineKeyboardButton("ℹ️ ABOUT", callback_data="about")
        ],
        [InlineKeyboardButton("📖 CLICK HERE FOR TUTORIAL", url=TUTORIAL_URL)],
        [
            InlineKeyboardButton("🎁 REFER", callback_data="refer"),
            InlineKeyboardButton("👑 PREMIUM", callback_data="see_plans")
        ],
        [InlineKeyboardButton("📢 SHARE ME", switch_inline_query="Check out this professional Movie Bot!")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = (
        f"<b>Hi {user.first_name}!</b>\n\n"
        "Welcome to the most complete <b>Movie & Series Bot</b>. 🎬\n\n"
        "➥ Search movies and series instantly\n"
        "➥ Get high-quality posters and details\n"
        "➥ Access trending content daily\n\n"
        "<i>Use the buttons below to explore!</i>"
    )
    
    try:
        await update.message.reply_photo(
            photo=BANNER_URL,
            caption=welcome_msg,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    except Exception:
        await update.message.reply_text(
            text=f"{welcome_msg}\n\n(Banner image not found)",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🔍 SEARCH", switch_inline_query_current_chat=""),
            InlineKeyboardButton("🔥 TRENDING", callback_data="trending")
        ],
        [
            InlineKeyboardButton("📊 MOST LIST", callback_data="most_searched"),
            InlineKeyboardButton("🖼️ IMG2LINK", callback_data="img2link_info")
        ],
        [
            InlineKeyboardButton("🎁 REFERRAL", callback_data="refer"),
            InlineKeyboardButton("👑 PREMIUM", callback_data="see_plans")
        ],
        [
            InlineKeyboardButton("📖 HELP", callback_data="cmds_list"),
            InlineKeyboardButton("🏠 HOME", callback_data="home")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("<b>Main Menu - Explorer</b>", reply_markup=reply_markup, parse_mode="HTML")

async def cmds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmds_text = (
        "<b>Available Commands:</b>\n\n"
        "➥ /start - Start the bot\n"
        "➥ /menu - Open main menu\n"
        "➥ /search [name] - Search for a movie/series\n"
        "➥ /trendlist - View top trending content\n"
        "➥ /mostlist - View most searched terms\n"
        "➥ /img2link - Convert image to direct link\n"
        "➥ /refer - Get your referral link\n"
        "➥ /plan - View premium plans\n"
        "➥ /cmds - Show this help menu\n\n"
        "<i>For Admins:</i> /admin_cmds"
    )
    await update.message.reply_text(cmds_text, parse_mode="HTML")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == "verify_sub":
        if await is_subscribed(context.bot, user_id):
            await query.answer("Verification successful! Welcome.", show_alert=True)
            await query.message.delete()
            await start(update, context)
        else:
            await query.answer("You haven't joined yet! Please join the channel first.", show_alert=True)
        return

    await query.answer()
    
    if query.data == "home":
        await start(update, context) # Reload start menu
    elif query.data == "special":
        await query.message.reply_text("✨ <b>SPECIAL SECTION</b>\n\nStay tuned for exclusive content and features!")
    elif query.data == "about":
        await query.message.reply_text("ℹ️ <b>ABOUT THIS BOT</b>\n\nThis is a professional Movie & Series Search bot powered by TMDb API. Created for high-speed content delivery.")
    elif query.data == "img2link_info":
        await query.message.reply_text("🖼️ <b>IMAGE TO LINK TOOL</b>\n\nSend any image directly to the bot or use /img2link to get a permanent direct URL.")
    elif query.data == "cmds_list":
        await cmds_command(update, context)
    elif query.data == "refer":
        from handlers.premium import referral_command
        await referral_command(update, context)
    elif query.data == "see_plans":
        from handlers.premium import plan_command
        await plan_command(update, context)
    elif query.data == "trending":
        from handlers.trending import trending_callback
        await trending_callback(update, context)
    elif query.data == "most_searched":
        from handlers.search import most_searched_command
        # We need a callback version of this or just call the command if we handle update correctly
        # For simplicity, simulating command or creating callback logic
        await most_searched_command(update, context)
