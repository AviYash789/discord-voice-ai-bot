import speech_recognition as sr
import tempfile
import os
import wave


def transcribe_audio(pcm_data: bytes, sample_rate: int = 48000, channels: int = 2) -> str:
    recognizer = sr.Recognizer()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        with wave.open(tmp_path, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(pcm_data)

        with sr.AudioFile(tmp_path) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"[STT] Google STT error: {e}")
        return ""
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
