import os
from dotenv import load_dotenv

load_dotenv()

# Helper to require env vars
def get_env_or_raise(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise ValueError(f"Missing required environment variable: {key}")
    return val

# ── Bot Credentials ────────────────────────────────────────────────────────────
BOT_TOKEN   = get_env_or_raise("BOT_TOKEN")
API_ID      = int(get_env_or_raise("API_ID"))
API_HASH    = get_env_or_raise("API_HASH")

# ── TMDb ───────────────────────────────────────────────────────────────────────
# Optional, use default or raise if you strictly require metadata
TMDB_API_KEY       = get_env_or_raise("TMDB_API_KEY")
TMDB_IMAGE_BASE    = "https://image.tmdb.org/t/p/w500"

# ── MongoDB ────────────────────────────────────────────────────────────────────
MONGO_URI  = get_env_or_raise("MONGO_URI")
DB_NAME    = os.getenv("DB_NAME", "movie_bot")

# ── Ownership & Access ─────────────────────────────────────────────────────────
OWNER_ID      = int(get_env_or_raise("OWNER_ID"))
ADMIN_IDS     = [int(i.strip()) for i in os.getenv("ADMIN_IDS", str(OWNER_ID)).split(",") if i.strip()]
ALLOWED_GROUP = int(get_env_or_raise("ALLOWED_GROUP"))

# ── Developer & Support ────────────────────────────────────────────────────────
DEV_USERNAME    = os.getenv("DEV_USERNAME", "@kurup")
SUPPORT_GROUP   = os.getenv("SUPPORT_GROUP", "")
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "")

# ── Storage & Force-Subscribe ─────────────────────────────────────────────────
STORAGE_CHANNEL = int(get_env_or_raise("STORAGE_CHANNEL"))

# Force-join channel 1 (public) — numeric ID or @username
FSUB_CHANNEL    = get_env_or_raise("FSUB_CHANNEL")
FSUB_LINK       = get_env_or_raise("FSUB_LINK")

# ── UI ─────────────────────────────────────────────────────────────────────────
BANNER_URL = os.getenv(
    "BANNER_URL",
    "https://graph.org/file/f47a79f0a69e48a0eb5d5.jpg"
)

# ── Auto-Delete ────────────────────────────────────────────────────────────────
AUTO_DELETE_TIMER = int(os.getenv("AUTO_DELETE_TIMER", "600"))   # seconds (10 min)
