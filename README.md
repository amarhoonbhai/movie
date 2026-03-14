# Scalable Dual-Bot Movie Indexing System

This system uses:
1. **Pyrogram** for handling the Telegram Bots.
2. **MongoDB** + Motor for primary storage of movies, users, and requests.
3. **Meilisearch** for lightning-fast, fuzzy text search.
4. **Arq + Redis** for offloading heavy tasks (broadcasting, auto-deletion, notifying users, and indexing) to background workers.

## Quick Start Guide

### 1. Start Infrastructure Services
You need Redis and Meilisearch running. A `docker-compose.yml` is provided.
```bash
docker-compose up -d
```
*(Wait a few seconds for Meilisearch to initialize).*

### 2. Configure Environment Variables
Ensure the `.env` file (or your environment variables) includes:
- `BOT_TOKEN` for `@AutoMovieFinderBot`
- `STORE_BOT_TOKEN` for `@Philostorebot`
- `API_ID` & `API_HASH`
- `MONGO_URI`
- `MEILI_URL` (usually `http://localhost:7700`)
- `REDIS_URL` (usually `redis://localhost:6379/0`)

### 3. Start the Background Worker
In one terminal window, start the `arq` worker so it can listen for Redis jobs:
```bash
arq worker.arq_worker.WorkerSettings
```

### 4. Start the Bots
In a second terminal window, run the main unified runner to start both bots simultaneously:
```bash
python start_bots.py
```

### Flow Verification
- Open your **STORAGE_CHANNEL**, upload a movie file or forward one, and include a caption like `Title: Inception`.
- You should see logs indicating the Store bot queued an indexing task, and the `arq` worker picked it up.
- Open **@AutoMovieFinderBot** inside your allowed group, type `/search Inception`. 
- You should see inline buttons to download it. Clicking download forwards the file and starts the 10-minute auto-delete countdown in the background.
