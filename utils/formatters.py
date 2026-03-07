from config import CHANNEL_NAME

def get_post_text(details, media_type="movie", layout="portrait"):
    """
    Generate professional formatted text for movie/series posts.
    layout: 'portrait' (Posters) or 'landscape' (Backdrop)
    """
    title = details.get("title") or details.get("name") or "Unknown"
    date = details.get("release_date") or details.get("first_air_date") or "N/A"
    year = date.split("-")[0] if date != "N/A" else "N/A"
    status = details.get("status", "N/A")
    rating = details.get("vote_average", "N/A")
    genres = ", ".join([g["name"] for g in details.get("genres", [])[:3]])

    if media_type == "movie":
        runtime = details.get("runtime", "N/A")
        header = f"🎬 <b>{title} ({year})</b>"
        info_rows = [
            f"➥ Status: {status}",
            f"➥ Runtime: {runtime} min",
            f"➥ Ratings: {rating} IMDB",
            f"➥ Quality: 480p | 720p | 1080p",
            f"➥ Audio: Hindi + English"
        ]
    else: # TV Series
        episodes = details.get("number_of_episodes", "N/A")
        seasons = details.get("number_of_seasons", "1")
        header = f"📺 <b>{title} (Season {seasons}) ({year})</b>"
        info_rows = [
            f"➥ Status: {status}",
            f"➥ Episodes: {episodes}",
            f"➥ Ratings: {rating} IMDB",
            f"➥ Pixels: 480p | 720p | 1080p",
            f"➥ Audio: Hindi & English (Esub)"
        ]

    # Different stylistic separators for layout
    if layout == "landscape":
        top_border = "┏" + "━"*25
        mid_border = "┣" + "━"*25
        bot_border = "┗" + "━"*25
    else:
        top_border = "╭────────────────────"
        mid_border = "├────────────────────"
        bot_border = "╰────────────────────"

    rows_text = "\n".join(info_rows)
    
    post = (
        f"{header}\n\n"
        f"{top_border}\n"
        f"{rows_text}\n"
        f"{mid_border}\n"
        f"➥ Genres: {genres}\n"
        f"{bot_border}\n\n"
        f"‣ {CHANNEL_NAME}"
    )
    return post
