import os
from dotenv import load_dotenv

load_dotenv()

# --- Bot Configuration ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
API_ID = int(os.getenv("API_ID", "25662706"))
API_HASH = os.getenv("API_HASH", "8828b6a3821034c44917544073801f65")

# --- TMDb Configuration ---
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "abc0e45d572a0a9065b3498a9c8ebc24")
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/original"

# --- MongoDB Configuration ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://admin:pass@cluster.mongodb.net/movie_bot?retryWrites=true&w=majority")
DB_NAME = os.getenv("DB_NAME", "movie_bot")

# --- Admin Configuration ---
OWNER_ID = int(os.getenv("OWNER_ID", "8395808382"))
ADMIN_IDS = [int(i.strip()) for i in os.getenv("ADMIN_IDS", "8395808382").split(",") if i.strip()]

# --- UI Customization ---
CHANNEL_NAME = os.getenv("FSUB_CHANNEL", "@PhiloBots")
FSUB_LINK = os.getenv("FSUB_LINK", "https://t.me/+AxJ9AFAeGsM3ZDE1")
BANNER_URL = os.getenv("BANNER_URL", "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?q=80&w=2070&auto=format&fit=crop")

# --- Group & Storage Settings ---
ALLOWED_GROUP = int(os.getenv("ALLOWED_GROUP", "-1001548130580"))
STORAGE_CHANNEL = int(os.getenv("STORAGE_CHANNEL", "-1003661525300"))
FSUB_CHANNEL = os.getenv("FSUB_CHANNEL", "@PhiloBots")
