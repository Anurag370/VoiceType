import threading

import numpy as np
import sounddevice as sd


SAMPLE_RATE = 16000
CHANNELS = 1


class AudioRecorder:
    def __init__(self):
        self.chunks = []
        self.lock = threading.Lock()
        self.stream = None
        self.level = 0.0
        self.recording = False

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            print("Audio warning:", status)

        chunk = indata.copy()

        with self.lock:
            self.chunks.append(chunk)

        samples = chunk.astype(np.float32) / 32768.0
        self.level = float(np.sqrt(np.mean(samples ** 2)))

    def start(self):
        if self.recording:
            return

        with self.lock:
            self.chunks = []

        self.level = 0.0

        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            callback=self._audio_callback,
        )

        try:
            stream.start()
        except Exception:
            stream.close()
            raise

        self.stream = stream
        self.recording = True

    def stop(self):
        if not self.recording or self.stream is None:
            return None

        stream = self.stream
        self.recording = False
        self.stream = None

        try:
            stream.stop()
        finally:
            stream.close()

        with self.lock:
            chunks = list(self.chunks)
            self.chunks = []

        self.level = 0.0

        if not chunks:
            return None

        audio = np.concatenate(chunks, axis=0)

        if len(audio) < SAMPLE_RATE // 4:
            return None

        return audio
