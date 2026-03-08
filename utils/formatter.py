def format_movie_caption(details):
    template = """🎬 **{title} ({year})**

╭───────────────────
➥ 🔉 **Audio:** `{audio}`
➥ 📺 **Quality:** `480p | 720p | 1080p`
➥ 🧬 **Genres:** `{genres}`
➥ ⭐️ **Rating:** `{rating}`
╰───────────────────

━━━━━━━━━━━━━━
📢 **Powered by:** @PhiloBots
━━━━━━━━━━━━━━"""
    return template.format(**details)

def format_series_caption(details):
    template = """📺 **{title}**

╭───────────────────
➥ 📊 **Status:** `{status}`
➥ 🎬 **Episodes:** `{episodes}`
➥ ⭐️ **Ratings:** `{rating}`
➥ 📺 **Pixels:** `480p | 720p | 1080p`
➥ 🔉 **Audio:** `{audio}`
├───────────────────
➥ 🧬 **Genres:** `{genres}`
╰───────────────────

<blockquote expandable>
{plot}
</blockquote>

━━━━━━━━━━━━━━
📢 **Powered by:** @PhiloBots
━━━━━━━━━━━━━━"""
    return template.format(**details)
