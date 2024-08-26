import sounddevice as sd
import numpy as np
import wave
import os

class AudioPlayer:
    def __init__(self, filename, end_tone_frequency=500, end_tone_duration=0.5, volume=0.4, tone_file="end_tone.wav"):
        self.filename = filename
        self.end_tone_frequency = end_tone_frequency
        self.end_tone_duration = end_tone_duration
        self.volume = volume
        self.tone_file = tone_file

        # Generate and save the tone if it doesn't already exist
        if not os.path.exists(self.tone_file):
            self.save_end_tone(self.tone_file)

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

            with sd.OutputStream(channels=channels, samplerate=sample_rate, callback=callback, dtype=dtype, blocksize=4096):
                sd.sleep(int(wf.getnframes() / sample_rate * 1000))
        
        # Play the pre-saved end-of-question tone
        print("Playing end-of-question tone...")
        self.play_saved_tone(self.tone_file)
    
    def save_end_tone(self, file_path):
        sample_rate = 44100  # Standard sample rate
        t = np.linspace(0, self.end_tone_duration, int(sample_rate * self.end_tone_duration), False)
        tone = np.sin(2 * np.pi * self.end_tone_frequency * t) * self.volume
        tone = tone.astype(np.float32)

        # Save the tone to a WAV file
        with wave.open(file_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit PCM
            wf.setframerate(sample_rate)
            wf.writeframes((tone * 32767).astype(np.int16).tobytes())
        print(f"End-of-question tone saved to {file_path}")

    def play_saved_tone(self, file_path):
        with wave.open(file_path, 'rb') as wf:
            sample_rate = wf.getframerate()
            channels = wf.getnchannels()
            dtype = np.int16

            def callback(outdata, frames, time, status):
                data = wf.readframes(frames)
                outdata.fill(0)
                data_np = np.frombuffer(data, dtype=dtype)
                outdata[:len(data_np)] = data_np.reshape(-1, channels)
                if len(data) < frames * channels * np.dtype(dtype).itemsize:
                    raise sd.CallbackStop

            with sd.OutputStream(channels=channels, samplerate=sample_rate, callback=callback, dtype=dtype, blocksize=4096):
                sd.sleep(int(wf.getnframes() / sample_rate * 1000))
        print("End-of-question tone playback complete.")
