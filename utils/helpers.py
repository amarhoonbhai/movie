"""
utils/helpers.py — Utility helpers for the Movie Bot.
"""
import re
import asyncio
import logging

logger = logging.getLogger(__name__)

# ── Query Normalization ────────────────────────────────────────────────────────

def normalize_query(text: str) -> str:
    """
    Lowercase, strip special characters, collapse whitespace.
    'KGF Chapter 2 (2022) [1080p]' → 'kgf chapter 2 2022 1080p'
    """
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)   # remove punctuation
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ── Quality & Audio Extraction ─────────────────────────────────────────────────

_QUALITY_PATTERNS = [
    (r"4k|2160p",            "4K"),
    (r"1080p|1080i|fhd",     "1080p"),
    (r"720p|720i|hd",        "720p"),
    (r"480p|480i|sd",        "480p"),
    (r"360p",                "360p"),
]

def extract_quality(filename: str) -> str:
    """Extract video quality tag from a filename string."""
    fn = filename.lower()
    for pattern, label in _QUALITY_PATTERNS:
        if re.search(pattern, fn):
            return label
    return "HD"


_AUDIO_PATTERNS = [
    (r"dual[\s._-]?audio|dual",          "Dual Audio"),
    (r"hindi[\s._-]?dubbed|hindi",        "Hindi"),
    (r"english",                          "English"),
    (r"tamil",                            "Tamil"),
    (r"telugu",                           "Telugu"),
    (r"malayalam",                        "Malayalam"),
    (r"kannada",                          "Kannada"),
    (r"multi[\s._-]?audio|multi",         "Multi Audio"),
]

def extract_audio(filename: str) -> str:
    """Extract audio language tag from a filename string."""
    fn = filename.lower()
    for pattern, label in _AUDIO_PATTERNS:
        if re.search(pattern, fn):
            return label
    return "English"


# ── Human-readable file size ───────────────────────────────────────────────────

def human_size(size_bytes: int) -> str:
    if size_bytes >= 1_073_741_824:
        return f"{size_bytes / 1_073_741_824:.2f} GB"
    if size_bytes >= 1_048_576:
        return f"{size_bytes / 1_048_576:.2f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    return f"{size_bytes} B"


# ── Auto-Delete Scheduler ─────────────────────────────────────────────────────

async def schedule_delete(client, chat_id: int, delay: int, *message_ids: int):
    """
    Waits `delay` seconds, then deletes all passed message IDs.
    Runs as a fire-and-forget asyncio task.
    """
    await asyncio.sleep(delay)
    for mid in message_ids:
        try:
            await client.delete_messages(chat_id, mid)
        except Exception as e:
            logger.debug(f"Auto-delete failed for msg {mid}: {e}")
