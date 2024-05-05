import winsound


class Audio:
    @staticmethod
    def play_sound(frequency: int, duration: int):
        print(f'Start playing sound {frequency} Hz')
        winsound.Beep(frequency=frequency, duration=duration)
        print(f'Stop playing sound {frequency} Hz')