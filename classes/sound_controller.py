import threading
import time
import synthesizer
import numpy as np
import pyaudio
import scipy

from classes.logger_mixin import LoggerMixin
from constants import AUDIO_CHANNELS, AUDIO_FORMAT, AUDIO_SAMPLING_RATE


class SoundController(LoggerMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = self.pyaudio_instance.open(
            format=AUDIO_FORMAT, channels=AUDIO_CHANNELS, rate=AUDIO_SAMPLING_RATE, output=True
        )
        self.playback_thread = None
        self.synth = synthesizer.Synthesizer(rate=AUDIO_SAMPLING_RATE)
        self.amplitude = 25

    def playback_start_threaded(self, frequency: int, duration: int = None):
        frames = self.generate_audio_frames(frequency=frequency, duration=duration)

        self.playback_thread = threading.Thread(
            target=self.playback_start, kwargs={"frequency": frequency, "duration": duration, "frames": frames}
        )
        self.playback_thread.start()
        self.logger.debug("Audio playback thread started")

    def playback_start(
        self, frequency: int, duration: int, frames: np.ndarray
    ):  # blocking, should be used inside separate thread
        self.logger.info(f"Start playing sound {frequency} Hz for {duration} time")
        self.stream.write(frames.tobytes())
        self.logger.info(f"Stop playing sound {frequency} Hz")

    def bandpass_filter(self, data: np.ndarray, edges: list[float], sample_rate: float, poles: int = 5):
        sos = scipy.signal.butter(poles, edges, "bandpass", fs=sample_rate)
        filtered_data = scipy.signal.filtfilt(*sos, x=data)
        return filtered_data

    def remove_low_frequencies(self, data, sampling_rate, cutoff_frequency):
        # Design a high-pass filter
        nyquist_frequency = 0.5 * sampling_rate
        high_pass_frequency = cutoff_frequency / nyquist_frequency
        b, a = scipy.signal.butter(4, high_pass_frequency, btype="low")

        # Apply the filter to the data
        filtered_data = scipy.signal.filtfilt(b, a, data)
        return filtered_data

    def generate_audio_frames(self, frequency: float, duration: int = 1):
        self.logger.debug("Start audio data generation")

        # t = np.linspace(0, duration, int(AUDIO_SAMPLING_RATE * duration), endpoint=False)
        # wavedata = np.sin(2 * np.pi * frequency * t)

        # wavedata = self.remove_low_frequencies(wavedata, AUDIO_SAMPLING_RATE, cutoff_frequency=16000)
        # wavedata = self.bandpass_filter(wavedata, [16000, 30000], AUDIO_SAMPLING_RATE)
        # wavedata = self.bandpass_filter(wavedata, [200, 18000], AUDIO_SAMPLING_RATE)
        # wavedata = self.remove_low_frequencies(wavedata, AUDIO_SAMPLING_RATE, cutoff_frequency=7000)

        wavedata = self.synth.generate_constant_wave(frequency=frequency, length=duration)

        self.logger.debug("Finish audio data generation")
        return wavedata


if __name__ == "__main__":
    FREQUENCY = 20000
    DURATION = 1000

    import synthesizer

    synt = synthesizer.Synthesizer(rate=192000)

    wave = synt.generate_constant_wave(27000, 10)
    print('sad')

    sound_controller = SoundController()
    sound_controller.playback_start(frequency=FREQUENCY, duration=DURATION, frames=wave)