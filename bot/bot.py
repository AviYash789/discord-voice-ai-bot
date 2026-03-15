import os
import asyncio
import threading
import discord
from discord.ext import commands, voice_recv
from dotenv import load_dotenv

import stats
from key_rotator import KeyRotator
from ai_brain import get_ai_response
from tts_engine import synthesize
from dashboard_api import run_dashboard, set_rotator
from voice_listener import SpeechSink

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
rotator = KeyRotator()
set_rotator(rotator)

processing_users = set()


async def handle_speech(user, audio_data: bytes):
    if user.id in processing_users:
        return
    processing_users.add(user.id)
    try:
        print(f"[BOT] Processing speech from {user.display_name}...")

        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, lambda: _transcribe(audio_data))

        if not text:
            print("[BOT] No speech detected or empty transcription.")
            return

        print(f"[BOT] Transcribed: {text}")
        stats.increment_requests()

        ai_response = await loop.run_in_executor(
            None, lambda: get_ai_response(text, rotator)
        )
        print(f"[BOT] AI response: {ai_response}")

        audio_file = await synthesize(ai_response)

        voice_client = user.guild.voice_client
        if voice_client and voice_client.is_connected():
            def after_play(err):
                if err:
                    print(f"[BOT] Playback error: {err}")
                try:
                    os.remove(audio_file)
                except Exception:
                    pass

            source = discord.FFmpegPCMAudio(audio_file)
            if not voice_client.is_playing():
                voice_client.play(source, after=after_play)
    except Exception as e:
        print(f"[BOT] Error handling speech: {e}")
    finally:
        processing_users.discard(user.id)


def _transcribe(audio_data: bytes) -> str:
    from stt_engine import transcribe_audio
    return transcribe_audio(audio_data)


@bot.event
async def on_ready():
    stats.set_status("online")
    print(f"[BOT] Logged in as {bot.user} | {rotator.total()} Groq key(s) loaded")
    print(f"[BOT] Connected to {len(bot.guilds)} server(s)")


@bot.command(name="join")
async def join(ctx: commands.Context):
    if not ctx.author.voice:
        await ctx.send("You must be in a voice channel first!")
        return

    channel = ctx.author.voice.channel

    if ctx.guild.voice_client and ctx.guild.voice_client.is_connected():
        await ctx.guild.voice_client.disconnect()

    try:
        vc = await channel.connect(cls=voice_recv.VoiceRecvClient, timeout=15.0)
    except TimeoutError:
        await ctx.send(
            "⚠️ **Voice connection timed out.**\n"
            "This is a network limitation of the current hosting environment — "
            "outbound UDP (required by Discord voice) is restricted.\n\n"
            "**To fix this:** Run the bot locally or on a VPS/server with unrestricted UDP access. "
            "All other bot features (text commands, dashboard, AI) are fully working!"
        )
        print("[BOT] Voice connection timed out — UDP likely blocked by host network.")
        return
    except Exception as e:
        await ctx.send(f"❌ Failed to join voice channel: `{e}`")
        print(f"[BOT] Voice connect error: {e}")
        return

    stats.set_channel(channel.name)
    sink = SpeechSink(handle_speech)
    vc.listen(sink)

    await ctx.send(f"Joined **{channel.name}**! I'm listening — talk to me!")
    print(f"[BOT] Joined voice channel: {channel.name}")


@bot.command(name="leave")
async def leave(ctx: commands.Context):
    vc = ctx.guild.voice_client
    if vc and vc.is_connected():
        await vc.disconnect()
        stats.set_channel(None)
        await ctx.send("Left the voice channel. See you later!")
    else:
        await ctx.send("I'm not in a voice channel.")


@bot.command(name="status")
async def status_cmd(ctx: commands.Context):
    s = stats.get_stats()
    channel_name = s.get("active_channel") or "None"
    await ctx.send(
        f"**Bot Status:** {s['bot_status']}\n"
        f"**Active Channel:** {channel_name}\n"
        f"**Total Requests:** {s['total_requests']}\n"
        f"**Active API Key:** {rotator.current_masked()}"
    )


def main():
    dashboard_port = int(os.environ.get("DASHBOARD_PORT", 5050))
    dashboard_thread = threading.Thread(
        target=run_dashboard, args=(dashboard_port,), daemon=True
    )
    dashboard_thread.start()
    print(f"[BOT] Dashboard API running on port {dashboard_port}")

    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable not set.")

    bot.run(token)


if __name__ == "__main__":
    main()
