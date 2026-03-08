"""
utils/formatter.py — Caption formatting for movie/series files.
"""

def format_movie_caption(details: dict, quality: str = "HD", audio: str = "Hindi | English") -> str:
    title   = details.get("title", "Unknown")
    year    = details.get("year", "N/A")
    genres  = details.get("genres", "N/A")
    rating  = details.get("rating", "N/A")
    plot    = details.get("plot", "")

    caption = (
        f"<b>{title} ({year})</b>\n\n"
        f"➪ Audio: <code>{audio}</code>\n"
        f"➪ Quality: <code>{quality}</code>\n"
        f"➪ Genres: <code>{genres}</code>\n"
        f"➪ Rating: <code>{rating}</code>\n"
    )
    if plot:
        caption += f"\n<blockquote expandable>{plot[:300]}{'...' if len(plot) > 300 else ''}</blockquote>\n"

    caption += (
        "\n━━━━━━━━━━━━━━\n"
        "📢 Powered by: @PhiloBots\n"
        "━━━━━━━━━━━━━━"
    )
    return caption


def format_series_caption(details: dict, quality: str = "HD", audio: str = "Hindi | English") -> str:
    title    = details.get("title", "Unknown")
    year     = details.get("year", "N/A")
    status   = details.get("status", "N/A")
    episodes = details.get("episodes", "N/A")
    genres   = details.get("genres", "N/A")
    rating   = details.get("rating", "N/A")
    plot     = details.get("plot", "")

    caption = (
        f"<b>📺 {title} ({year})</b>\n\n"
        f"➪ Audio: <code>{audio}</code>\n"
        f"➪ Quality: <code>{quality}</code>\n"
        f"➪ Status: <code>{status}</code>\n"
        f"➪ Episodes: <code>{episodes}</code>\n"
        f"➪ Genres: <code>{genres}</code>\n"
        f"➪ Rating: <code>{rating}</code>\n"
    )
    if plot:
        caption += f"\n<blockquote expandable>{plot[:300]}{'...' if len(plot) > 300 else ''}</blockquote>\n"

    caption += (
        "\n━━━━━━━━━━━━━━\n"
        "📢 Powered by: @PhiloBots\n"
        "━━━━━━━━━━━━━━"
    )
    return caption
