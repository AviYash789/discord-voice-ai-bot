# Discord Voice AI Bot

A Python Discord bot that joins voice channels, listens to users, transcribes speech, generates AI responses using Groq, and speaks back using Edge-TTS.

## Features

- **Voice Listening** — Joins your Discord voice channel on `!join`
- **Free STT** — Google Speech Recognition (no API key needed)
- **AI Brain** — Groq API with Llama-3.3-70b-versatile for fast responses
- **API Key Rotation** — Auto-rotates on 429 rate limit errors
- **TTS** — Microsoft Edge-TTS (free, neural voices, low latency)
- **Audio Streaming** — Streams response audio back via FFmpeg
- **Web Dashboard** — React dashboard showing bot status, requests, active channel, and masked API key

## Bot Commands

| Command | Description |
|---------|-------------|
| `!join` | Bot joins your voice channel and starts listening |
| `!leave` | Bot leaves the voice channel |
| `!status` | Shows current bot status in chat |

## Setup & Run Locally

### 1. Install system dependencies
```bash
# Ubuntu/Debian
sudo apt install ffmpeg libopus-dev python3-dev
```

### 2. Install Python packages
```bash
pip install -r bot/requirements.txt
```

### 3. Configure environment variables
```bash
cp bot/.env.example bot/.env
# Edit bot/.env and fill in your values
```

### 4. Run the bot
```bash
cd bot && python bot.py
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DISCORD_TOKEN` | Your Discord bot token |
| `GROQ_API_KEY_1` | First Groq API key |
| `GROQ_API_KEY_2` | (Optional) Second key for rotation |
| `GROQ_API_KEY_3` | (Optional) Third key for rotation |
| `DASHBOARD_PORT` | Flask dashboard port (default: 5050) |

## Deploying on Render.com

1. **Fork/push this repo** to your GitHub account
2. Go to [render.com](https://render.com) → **New → Background Worker**
3. Connect your GitHub repo
4. Set these settings:
   - **Root Directory:** `bot`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
5. Under **Environment Variables**, add:
   - `DISCORD_TOKEN`
   - `GROQ_API_KEY_1`
   - `DASHBOARD_PORT` = `5050`
6. Click **Deploy**

> **Note:** Render's free tier may have UDP restrictions. If voice connection times out, upgrade to a paid plan or use a VPS with full UDP access (DigitalOcean, Hetzner, etc.)

## Architecture

```
User speaks → Discord voice → VoiceRecvClient → SpeechSink
→ Google Free STT → text → Groq Llama-3.3-70b → AI response
→ Edge-TTS → .mp3 → FFmpegPCMAudio → Discord voice channel
```

## Dashboard API

The bot exposes a Flask API on port 5050:

- `GET /api/bot/stats` — Returns bot status, total requests, active channel, masked API key
