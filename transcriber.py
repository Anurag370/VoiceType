import tempfile
import wave
from pathlib import Path

import numpy as np
from groq import Groq

from config import get_api_key


MODEL = "whisper-large-v3-turbo"


def transcribe_audio(audio: np.ndarray) -> str:
    api_key = get_api_key()

    if not api_key:
        raise RuntimeError(
            "No Groq API key is configured. "
            "Open Voice Type settings to add your key."
        )

    client = Groq(
        api_key=api_key,
        timeout=60.0,
        max_retries=2,
    )

    # Convert the in-memory recording into a temporary WAV file.
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / "recording.wav"

        with wave.open(str(audio_path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(audio.astype(np.int16).tobytes())

        with audio_path.open("rb") as audio_file:
            response = client.audio.transcriptions.create(
                file=audio_file,
                model=MODEL,
                response_format="json",
                temperature=0.0,
            )

    return response.text.strip()
