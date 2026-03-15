import asyncio
import time
import numpy as np
from discord.ext import voice_recv
import discord.opus as opus_lib

SILENCE_THRESHOLD = 500
MIN_SPEECH_DURATION = 0.5


class SpeechSink(voice_recv.AudioSink):
    def __init__(self, on_speech_callback):
        super().__init__()
        self.on_speech = on_speech_callback
        self._buffers = {}
        self._last_audio = {}
        self._decoders = {}

    def wants_opus(self) -> bool:
        return True

    def write(self, user, data: voice_recv.VoiceData):
        if user is None or user.bot:
            return
        uid = user.id
        now = time.time()

        if uid not in self._buffers:
            self._buffers[uid] = bytearray()
            self._last_audio[uid] = now
            self._decoders[uid] = opus_lib.Decoder()

        try:
            raw = data.data if data.data else getattr(data, 'opus', None)
            if not raw:
                return
            pcm = self._decoders[uid].decode(raw, fec=False)
        except Exception:
            return

        if not pcm:
            return

        audio_array = np.frombuffer(pcm, dtype=np.int16)
        amplitude = float(np.abs(audio_array).mean())

        if amplitude > SILENCE_THRESHOLD:
            self._buffers[uid].extend(pcm)
            self._last_audio[uid] = now
        else:
            if self._buffers.get(uid):
                elapsed = now - self._last_audio[uid]
                duration = len(self._buffers[uid]) / (48000 * 2 * 2)
                if elapsed > 0.8 and duration >= MIN_SPEECH_DURATION:
                    audio_data = bytes(self._buffers[uid])
                    self._buffers[uid] = bytearray()
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asyncio.ensure_future(self.on_speech(user, audio_data))
                    except Exception as e:
                        print(f"[SINK] Error dispatching speech: {e}")

    def cleanup(self):
        self._buffers.clear()
        self._last_audio.clear()
        self._decoders.clear()
