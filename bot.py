import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    InlineQueryHandler,
    filters,
)
from telegram import Update
from config import BOT_TOKEN, ALLOWED_GROUP
from handlers.start import start, menu, cmds_command, button_callback
from handlers.search import (
    search_command,
    search_details_callback,
    most_searched_command,
    search_again_callback,
    skip_thumbnail_callback,
    inline_search_handler,
)
from handlers.trending import trending_command, trending_callback
from handlers.premium import img2link_command, handle_photo, referral_command, plan_command
from handlers.admin import (
    admin_cmds,
    stats_command,
    broadcast_command,
    add_admin_command,
    ban_command,
    requests_command,
)
from handlers.groups import index_storage_handler, group_search_handler, file_selection_callback

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # ── Commands ──────────────────────────────────────────────────────────
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("cmds", cmds_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("mostlist", most_searched_command))
    application.add_handler(CommandHandler("trendlist", trending_command))
    application.add_handler(CommandHandler("img2link", img2link_command))
    application.add_handler(CommandHandler("refer", referral_command))
    application.add_handler(CommandHandler("plan", plan_command))

    # ── Admin Commands ────────────────────────────────────────────────────
    application.add_handler(CommandHandler("admin_cmds", admin_cmds))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("addadmin", add_admin_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("requests", requests_command))

    # ── Callback Queries ──────────────────────────────────────────────────
    application.add_handler(CallbackQueryHandler(search_details_callback, pattern=r"^details_"))
    application.add_handler(CallbackQueryHandler(search_again_callback, pattern=r"^search_again_"))
    application.add_handler(CallbackQueryHandler(skip_thumbnail_callback, pattern=r"^skip_thumb_"))
    application.add_handler(CallbackQueryHandler(trending_callback, pattern=r"^trending$"))
    application.add_handler(CallbackQueryHandler(file_selection_callback, pattern=r"^fwd_"))
    application.add_handler(CallbackQueryHandler(
        lambda u, c: u.callback_query.message.delete(), pattern=r"^close_post$",
    ))
    application.add_handler(InlineQueryHandler(inline_search_handler))
    application.add_handler(CallbackQueryHandler(button_callback))  # Fallback

    # ── Auto-Filter (Group & Storage Channel) ─────────────────────────────
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, index_storage_handler))
    application.add_handler(MessageHandler(
        filters.Chat(ALLOWED_GROUP) & filters.TEXT & (~filters.COMMAND),
        group_search_handler,
    ))

    # ── Message Handlers ──────────────────────────────────────────────────
    application.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, handle_photo))

    logger.info("Bot started...")
    application.run_polling(
        allowed_updates=[
            Update.MESSAGE,
            Update.CALLBACK_QUERY,
            Update.INLINE_QUERY,
            Update.CHANNEL_POST,
        ]
    )


if __name__ == "__main__":
    main()
