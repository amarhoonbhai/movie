from config import CHANNEL_NAME

def format_movie_post(movie_details):
    title = movie_details.get("title", movie_details.get("name", "Unknown Title"))
    release_date = movie_details.get("release_date", "N/A")
    year = release_date.split("-")[0] if release_date != "N/A" else "N/A"
    status = movie_details.get("status", "Unknown")
    runtime = movie_details.get("runtime", "N/A")
    rating = movie_details.get("vote_average", "N/A")
    genres = ", ".join([g["name"] for g in movie_details.get("genres", [])])

    post = (
        f"<b>{title} ({year})</b>\n\n"
        f"╭───────────────────\n"
        f"➥ Status: {status}\n"
        f"➥ Runtime: {runtime} min\n"
        f"➥ Ratings: {rating} IMDB\n"
        f"➥ Quality: 480p | 720p | 1080p\n"
        f"➥ Audio: Hindi + English\n"
        f"├───────────────────\n"
        f"➥ Genres: {genres}\n"
        f"╰───────────────────\n\n"
        f"‣ {CHANNEL_NAME}"
    )
    return post

def format_series_post(series_details):
    title = series_details.get("name", series_details.get("title", "Unknown Title"))
    first_air_date = series_details.get("first_air_date", "N/A")
    year = first_air_date.split("-")[0] if first_air_date != "N/A" else "N/A"
    status = series_details.get("status", "Unknown")
    episodes = series_details.get("number_of_episodes", "N/A")
    rating = series_details.get("vote_average", "N/A")
    genres = ", ".join([g["name"] for g in series_details.get("genres", [])])
    
    # Assuming season 01 for now as per requirement format
    post = (
        f"<b>{title} (Season 01) ({year})</b>\n\n"
        f"╭───────────────────\n"
        f"➥ Status: {status}\n"
        f"➥ Episodes: {episodes}\n"
        f"➥ Ratings: {rating} IMDB\n"
        f"➥ Pixels: 480p | 720p | 1080p\n"
        f"➥ Audio: Hindi & English (Esub)\n"
        f"├───────────────────\n"
        f"➥ Genres: {genres}\n"
        f"╰───────────────────\n\n"
        f"‣ {CHANNEL_NAME}"
    )
    return post
