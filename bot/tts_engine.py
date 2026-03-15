import asyncio
import edge_tts
import tempfile
import os


VOICE = "en-US-AriaNeural"


async def synthesize(text: str) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(tmp.name)
    return tmp.name


def synthesize_sync(text: str) -> str:
    return asyncio.run(synthesize(text))
