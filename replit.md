# Workspace

## Overview

Discord Voice AI Bot + Web Dashboard. A Python Discord bot with voice listening, free STT (Google Speech Recognition), Groq AI (Llama-3.3-70b), Edge-TTS, and a React web dashboard.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5 (Node.js proxy for bot stats)
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Python version**: 3.11
- **Discord library**: discord.py 2.7.1 + discord-ext-voice-recv
- **STT**: Google Speech Recognition (free, via SpeechRecognition library)
- **TTS**: Edge-TTS (free, Microsoft neural voices)
- **AI**: Groq API (llama-3.3-70b-versatile)
- **Bot dashboard API**: Flask on port 5050
- **Frontend**: React + Vite (dark Discord-themed)

## Structure

```text
artifacts-monorepo/
├── artifacts/
│   ├── api-server/         # Express API server (proxies /api/bot/stats to Flask)
│   └── dashboard/          # React Vite frontend dashboard
├── bot/                    # Python Discord bot
│   ├── bot.py              # Main bot entry point
│   ├── key_rotator.py      # Groq API key rotation
│   ├── ai_brain.py         # Groq LLM integration
│   ├── tts_engine.py       # Edge-TTS synthesis
│   ├── stt_engine.py       # Google free STT
│   ├── voice_listener.py   # Discord voice audio sink
│   ├── dashboard_api.py    # Flask API for bot stats
│   ├── stats.py            # In-memory stats store
│   └── requirements.txt    # Python dependencies
├── lib/                    # Shared libraries
│   ├── api-spec/           # OpenAPI spec + Orval codegen
│   ├── api-client-react/   # Generated React Query hooks
│   ├── api-zod/            # Generated Zod schemas
│   └── db/                 # Drizzle ORM schema + DB connection
```

## Workflows

- **Discord Bot** — `cd bot && python bot.py` (console)
- **artifacts/api-server: API Server** — Express server (proxies bot stats)
- **artifacts/dashboard: web** — React Vite dashboard

## Environment Variables / Secrets

- `DISCORD_TOKEN` — Discord bot token
- `GROQ_API_KEY_1` — First Groq API key (add _2, _3 etc. for rotation)
- `DASHBOARD_PORT` — Flask dashboard port (default 5050)

## Bot Commands

- `!join` — Bot joins your voice channel and starts listening
- `!leave` — Bot leaves the voice channel
- `!status` — Shows bot status in chat

## API Keys for Groq Rotation

Add multiple keys as: `GROQ_API_KEY_1`, `GROQ_API_KEY_2`, `GROQ_API_KEY_3`, etc.
The bot auto-rotates on 429 rate limit errors.

## Architecture

```
User speaks → Discord voice → VoiceRecvClient → SpeechSink
→ Google Free STT → text → Groq Llama-3.3-70b → AI response text
→ Edge-TTS → .mp3 file → FFmpegPCMAudio → Discord voice channel
```

Dashboard flow:
```
React frontend → /api/bot/stats (Express) → proxy to Flask :5050 → in-memory stats
```
