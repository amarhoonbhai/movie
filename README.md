# Single-Bot Movie Indexing System

A fast and highly scalable Pyrogram-based Telegram Bot. This bot directly indexes forwarded movie files from a **Private Storage Channel** (acting as your database) and allows group/private users to search and request movies natively. 

## Features
- **Aesthetic UI**: Clean `/start` interface showing First Name, User ID, and Bio.
- **Top Metrics**: `/trending`, `/top_movie`, and `/top_users` stats.
- **Single-Bot Architecture**: No need to run a separate Store bot and Finder bot. It's all unified.
- **Background Tasks Native**: No Redis, no Arq. Everything runs async natively using Pyrogram.
- **Smart Filtering**: Automatically parses Movie Title, Year, and Quality from captions.

## Prerequisites
- Python 3.10+
- MongoDB instance (Atlas or local)

## Quick Start Guide

### 1. Configure Environment Variables
Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```
Ensure you have set:
- `BOT_TOKEN`
- `API_ID` & `API_HASH`
- `MONGO_URI`
- `STORAGE_CHANNEL` (where movies are kept)
- `FSUB_CHANNEL` (where users must join)

### 2. Install Dependencies
Set up your virtual environment and install the required packages:

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

pip install -r requirements.txt
```

### 3. Start the Bot
Run the unified bot directly:

```bash
python main.py
```

### Flow Verification
1. Forward or upload a document/video to your `STORAGE_CHANNEL`.
2. Add a caption like `Title: Inception \n Year: 2010 \n Quality: 1080p`.
3. Go to the bot (or the allowed group) and type `/search Inception`.
4. The bot will fetch the file using the message ID from the private channel and copy it to the user.
