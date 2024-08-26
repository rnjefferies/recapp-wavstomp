import sounddevice as sd
import numpy as np
import wave

class AudioPlayer:
    def __init__(self, filename, end_tone_frequency=500, end_tone_duration=0.5, volume=0.4):
        self.filename = filename
        self.end_tone_frequency = end_tone_frequency
        self.end_tone_duration = end_tone_duration
        self.volume = volume

    def play(self):
        with wave.open(self.filename, 'rb') as wf:
            sample_rate = wf.getframerate()
            channels = wf.getnchannels()
            dtype = np.int16

            def callback(outdata, frames, time, status):
                data = wf.readframes(frames)
                outdata.fill(0)  # Fill the output buffer with silence (zeros)
                
                # Copy the data into the output buffer
                data_np = np.frombuffer(data, dtype=dtype)
                outdata[:len(data_np)] = data_np.reshape(-1, channels)
                
                # Stop the stream if there is no more data
                if len(data) < frames * channels * np.dtype(dtype).itemsize:
                    raise sd.CallbackStop

            with sd.OutputStream(channels=channels, samplerate=sample_rate, callback=callback, dtype=dtype):
                sd.sleep(int(wf.getnframes() / sample_rate * 1000))
        
        # Play end-of-question tone
        print("Playing end-of-question tone...")
        self.play_end_tone(sample_rate)

    def play_end_tone(self, sample_rate):
        t = np.linspace(0, self.end_tone_duration, int(sample_rate * self.end_tone_duration), False)
        tone = np.sin(2 * np.pi * self.end_tone_frequency * t) * self.volume
        tone = tone.astype(np.float32)  # Using float32 for better compatibility with sounddevice

        sd.play(tone, samplerate=sample_rate)
        sd.wait()  # Wait until the tone is played completely
        print("End-of-question tone playback complete.")
