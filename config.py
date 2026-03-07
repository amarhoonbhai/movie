import os
from dotenv import load_dotenv

load_dotenv()

# --- Bot Configuration ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
API_ID = int(os.getenv("API_ID", "12345"))  # Not strictly needed for python-telegram-bot but good practice
API_HASH = os.getenv("API_HASH", "your_api_hash")

# --- TMDb Configuration ---
TMDB_API_KEY = "abc0e45d572a0a9065b3498a9c8ebc24"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/original"

# --- MongoDB Configuration ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "movie_bot"

# --- Admin Configuration ---
OWNER_IDS = [1577166444, 8395808382]
ADMIN_IDS = [8395808382]

# --- UI Customization ---
CHANNEL_NAME = "@philobots"
TUTORIAL_URL = "https://t.me/your_tutorial_link"
BANNER_URL = "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?q=80&w=2070&auto=format&fit=crop"

# --- Force Subscribe ---
FSUB_CHANNEL = "@philobots"
