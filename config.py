import os
from dotenv import load_dotenv

load_dotenv()

# ── Bot Credentials ────────────────────────────────────────────────────────────
BOT_TOKEN   = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
API_ID      = int(os.getenv("API_ID", "25662706"))
API_HASH    = os.getenv("API_HASH", "8828b6a3821034c44917544073801f65")

# ── TMDb ───────────────────────────────────────────────────────────────────────
TMDB_API_KEY       = os.getenv("TMDB_API_KEY", "abc0e45d572a0a9065b3498a9c8ebc24")
TMDB_IMAGE_BASE    = "https://image.tmdb.org/t/p/w500"

# ── MongoDB ────────────────────────────────────────────────────────────────────
MONGO_URI  = os.getenv("MONGO_URI", "mongodb+srv://admin:pass@cluster.mongodb.net/movie_bot?retryWrites=true&w=majority")
DB_NAME    = os.getenv("DB_NAME", "movie_bot")

# ── Ownership & Access ─────────────────────────────────────────────────────────
OWNER_ID      = int(os.getenv("OWNER_ID", "8395808382"))
ADMIN_IDS     = [int(i.strip()) for i in os.getenv("ADMIN_IDS", "8395808382").split(",") if i.strip()]
ALLOWED_GROUP = int(os.getenv("ALLOWED_GROUP", "-1001548130580"))

# ── Storage & Force-Subscribe ─────────────────────────────────────────────────
STORAGE_CHANNEL = int(os.getenv("STORAGE_CHANNEL", "-1003661525300"))

# Force-join channel 1 (public) — numeric ID or @username
FSUB_CHANNEL    = os.getenv("FSUB_CHANNEL", "@PhiloBots")
FSUB_CHANNEL_ID = int(os.getenv("FSUB_CHANNEL_ID", "-1002036931987"))  # numeric id for get_chat_member

# Force-join channel 2 (private invite link group)
FSUB_LINK       = os.getenv("FSUB_LINK", "https://t.me/+AxJ9AFAeGsM3ZDE1")
FSUB_GROUP_ID   = int(os.getenv("FSUB_GROUP_ID", "-1001548130580"))    # group behind invite link

# ── UI ─────────────────────────────────────────────────────────────────────────
BANNER_URL = os.getenv(
    "BANNER_URL",
    "https://graph.org/file/f47a79f0a69e48a0eb5d5.jpg"
)

# ── Auto-Delete ────────────────────────────────────────────────────────────────
AUTO_DELETE_TIMER = int(os.getenv("AUTO_DELETE_TIMER", "600"))   # seconds (10 min)
