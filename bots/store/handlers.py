import logging
import re
from pyrogram import Client, filters
from pyrogram.types import Message

from core.config import STORAGE_CHANNEL
from worker.tasks import process_new_movie_upload
from bots.finder.bot import finder_app

logger = logging.getLogger(__name__)

def parse_caption(text: str):
    """
    Parses a caption like:
    Title: Inception
    Year: 2010
    Genre: Sci-Fi
    Quality: 1080p
    """
    title = re.search(r"Title:\s*([^\n]+)", text, re.I)
    year = re.search(r"Year:\s*(\d{4})", text, re.I)
    genre = re.search(r"Genre:\s*([^\n]+)", text, re.I)
    
    t = title.group(1).strip() if title else "Unknown Title"
    y = year.group(1).strip() if year else "Unknown Year"
    g = genre.group(1).strip() if genre else "Unknown Genre"
    
    return t, y, g

@Client.on_message(filters.channel & filters.chat(STORAGE_CHANNEL) & (filters.document | filters.video))
async def store_bot_indexer(client: Client, message: Message):
    """
    When a document or video is sent to the STORAGE_CHANNEL, queue it for processing.
    """
    file = message.document or message.video
    if not file:
        return
        
    file_id = file.file_id
    file_name = getattr(file, "file_name", "unknown_file")
    file_size = getattr(file, "file_size", 0)
    caption = message.caption or ""
    
    # Fallback to filename if title is unknown
    title, year, genre = parse_caption(caption)
    if title == "Unknown Title" and file_name != "unknown_file":
        # Extract title from filename basic heuristic
        title = file_name.replace(".", " ").replace("_", " ")
    
    try:
        # Run natively in the background (fire and forget using Pyrogram)
        # We pass the finder_app so it can send messages to users
        await process_new_movie_upload(
            app=finder_app,
            file_id=file_id,
            file_name=file_name,
            file_size=file_size,
            message_id=message.id,
            caption=caption,
            title=title,
            year=year,
            genre=genre
        )
        logger.info(f"Queued native indexing job for {file_name}")
    except Exception as e:
        logger.error(f"Failed to enqueue indexing job natively: {e}")
