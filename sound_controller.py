import pyaudio
import struct
import math
import threading
from constants import USE_SAMPLE_PACKETS

from constants import FORMAT, CHANNELS, RATE, PACKETS_TO_COLLECT_WITH_AUDIO, PACKET_TYPE_UPDATE_RATE_TO_REQUEST


class SoundController:
    pyaudio_instance = pyaudio.PyAudio()
    playback_thread = None

    @classmethod
    def playback_start_threaded(cls, frequency: int, duration: int = None):
        if USE_SAMPLE_PACKETS:  # skip playback if using not real data
            return

        if duration is None:
            duration = int((PACKETS_TO_COLLECT_WITH_AUDIO / PACKET_TYPE_UPDATE_RATE_TO_REQUEST) + 2)

        cls.playback_thread = threading.Thread(target=cls._playback_start, kwargs={'frequency': frequency, 'duration': duration})
        cls.playback_thread.start()

    @classmethod
    def _playback_start(cls, frequency: int, duration: int):   # blocking, should be ued inside separate thread
        frames = cls._data_for_freq(frequency, duration)
        stream = cls.pyaudio_instance.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)

        print(f'Start playing sound {frequency} Hz')
        stream.write(frames)
        stream.stop_stream()
        stream.close()
        print(f'Stop playing sound {frequency} Hz')

        cls.playback_thread = None  # use it as a flag to check if thread is finished

    @staticmethod
    def _data_for_freq(frequency: float, time: float = None):
        """get frames for a fixed frequency for a specified time or
        number of frames, if frame_count is specified, the specified
        time is ignored"""
        frame_count = int(RATE * time)

        remainder_frames = frame_count % RATE
        wavedata = []

        for i in range(frame_count):
            a = RATE / frequency  # number of frames per wave
            b = i / a
            # explanation for b
            # considering one wave, what part of the wave should this be
            # if we graph the sine wave in a
            # displacement vs i graph for the particle
            # where 0 is the beginning of the sine wave and
            # 1 the end of the sine wave
            # which part is "i" is denoted by b
            # for clarity you might use
            # though this is redundant since math.sin is a looping function
            # b = b - int(b)

            c = b * (2 * math.pi)
            # explanation for c
            # now we map b to between 0 and 2*math.PI
            # since 0 - 2*PI, 2*PI - 4*PI, ...
            # are the repeating domains of the sin wave (so the decimal values will
            # also be mapped accordingly,
            # and the integral values will be multiplied
            # by 2*PI and since sin(n*2*PI) is zero where n is an integer)
            d = math.sin(c) * 32767
            e = int(d)
            wavedata.append(e)

        for i in range(remainder_frames):
            wavedata.append(0)

        number_of_bytes = str(len(wavedata))
        wavedata = struct.pack(number_of_bytes + 'h', *wavedata)

        return wavedata


if __name__ == "__main__":
    FREQUENCY = 21000
    DURATION = 5

    SoundController._playback_start(frequency=FREQUENCY, duration=DURATION)
