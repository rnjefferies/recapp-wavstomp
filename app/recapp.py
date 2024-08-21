import sounddevice as sd
import numpy as np
import wave
import tkinter as tk
import time
import csv
import os
from PIL import Image, ImageTk

class AudioRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recapp: for SA Data Collection")

        # Set the application icon
        self.set_app_icon()

        self.recording = False
        self.start_time = None
        self.recorded_chunks = []
        self.event_id = 1
        self.participant_id = None
        self.condition = None

        self.question_times = {}
        self.answer_times = {}
        self.last_flagged = None

        # Ensure the participants directory exists
        self.main_directory = os.path.join('..', 'participants')
        if not os.path.exists(self.main_directory):
            os.makedirs(self.main_directory)

        # Ensure the data directory exists
        self.data_directory = os.path.join('..', 'data')
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)

        # CSV file for flagged events (save in the data directory)
        self.csv_filename = os.path.join(self.data_directory, 'flagged_events.csv')
        self.ensure_csv_file_exists()

        # Input validation
        validate_numeric_command = root.register(self.validate_numeric_input)
        validate_letter_command = root.register(self.validate_letter_condition)

        # Create a frame for the content
        self.content_frame = tk.Frame(root)
        self.content_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # UI Elements
        self.participant_id_label = tk.Label(self.content_frame, text="Participant ID:")
        self.participant_id_label.pack(pady=(10, 5))

        self.participant_id_entry = tk.Entry(self.content_frame, validate="key", validatecommand=(validate_numeric_command, '%S'))
        self.participant_id_entry.pack(pady=(0, 20))

        self.condition_label = tk.Label(self.content_frame, text="Condition (A, B, C):")
        self.condition_label.pack(pady=(10, 5))

        self.condition_entry = tk.Entry(self.content_frame, validate="key", validatecommand=(validate_letter_command, '%S'))
        self.condition_entry.pack(pady=(0, 20))

        self.start_button = tk.Button(self.content_frame, text="Start Recording", command=self.start_recording)
        self.start_button.pack(pady=(10, 5))

        self.stop_button = tk.Button(self.content_frame, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=(5, 5))

        self.flag_question_button = tk.Button(self.content_frame, text="Flag Question", command=self.flag_question, state=tk.DISABLED)
        self.flag_question_button.pack(pady=(5, 5))

        self.flag_answer_button = tk.Button(self.content_frame, text="Flag Answer", command=self.flag_answer, state=tk.DISABLED)
        self.flag_answer_button.pack(pady=(5, 10))

        self.status_label = tk.Label(self.content_frame, text="Status: Idle")
        self.status_label.pack(pady=(10, 5))

        self.recording_time_label = tk.Label(self.content_frame, text="Recording Time: 00:00")
        self.recording_time_label.pack(pady=(5, 10))

        self.event_id_label = tk.Label(self.content_frame, text="Last Completed Event ID (e.g., E1 = 1):")
        self.event_id_label.pack(pady=(10, 5))

        self.event_id_entry = tk.Entry(self.content_frame, validate="key", validatecommand=(validate_numeric_command, '%S'))
        self.event_id_entry.pack(pady=(0, 20))

        self.root.bind('<q>', self.flag_question_key)
        self.root.bind('<a>', self.flag_answer_key)

        # Audio parameters
        self.sample_rate = 44100
        self.channels = 1
        self.dtype = np.int16

        self.update_clock()

    def set_app_icon(self):
        try:
            icon_image = Image.open('icon2.png')  # Adjust path to find the icon
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.root.iconphoto(True, icon_photo)
        except Exception as e:
            print(f"Error loading application icon: {e}")

    def validate_numeric_input(self, input):
        return input.isdigit() or input == ''

    def validate_letter_condition(self, input):
        return input in {'A', 'B', 'C'} or input == ''

    def ensure_csv_file_exists(self):
        if not os.path.isfile(self.csv_filename):
            with open(self.csv_filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Participant ID', 'Condition', 'Event ID', 'Question Timestamp (s)', 'Answer Timestamp (s)', 'Time Difference (s)'])

    def start_recording(self):
        participant_id_input = self.participant_id_entry.get().strip()
        condition_input = self.condition_entry.get().strip()

        if participant_id_input == '':
            print("Participant ID cannot be empty.")
            return
        if condition_input not in {'A', 'B', 'C'}:
            print("Condition must be A, B, or C.")
            return

        # Set the participant ID and condition
        if self.participant_id != participant_id_input or self.condition != condition_input:
            self.participant_id = participant_id_input
            self.condition = condition_input
            self.event_id = 1  # Reset event ID for new participant or condition
            self.question_times = {}
            self.answer_times = {}
            self.last_flagged = None
            self.create_participant_directory()
            self.load_last_event_id()

        self.recording = True
        self.start_time = time.time()
        self.recorded_chunks = []
        self.status_label.config(text="Status: Recording...")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.flag_question_button.config(state=tk.NORMAL)
        self.flag_answer_button.config(state=tk.NORMAL)

        self.participant_id_entry.config(state=tk.DISABLED)
        self.condition_entry.config(state=tk.DISABLED)

        self.stream = sd.InputStream(
            channels=self.channels,
            samplerate=self.sample_rate,
            dtype=self.dtype,
            callback=self.audio_callback
        )
        self.stream.start()

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.status_label.config(text="Status: Idle")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.flag_question_button.config(state=tk.DISABLED)
            self.flag_answer_button.config(state=tk.DISABLED)

            self.participant_id_entry.config(state=tk.NORMAL)
            self.condition_entry.config(state=tk.NORMAL)

            self.stream.stop()
            self.stream.close()

            # Save the recorded data with participant ID and condition in filename
            filename = f"recording_{self.participant_id}_C{self.condition}_{int(time.time())}.wav"
            filepath = os.path.join(self.participant_directory, filename)
            try:
                with wave.open(filepath, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(np.iinfo(self.dtype).bits // 8)
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(b''.join(self.recorded_chunks))
                print(f"Recording saved as {filepath}")
            except Exception as e:
                print(f"Error saving recording: {e}")

            # Save the flagged events in the specified format
            self.save_flagged_events()

    def audio_callback(self, indata, frames, time, status):
        if self.recording:
            self.recorded_chunks.append(indata.tobytes())

    def flag_question(self):
        if self.recording and self.last_flagged != 'question':
            elapsed_time = time.time() - self.start_time
            self.question_times[self.event_id] = f"{elapsed_time:.2f}"
            print(f"Question flagged at {elapsed_time:.2f} seconds (Event ID: E{self.event_id})")
            self.last_flagged = 'question'
            self.flag_question_button.config(state=tk.DISABLED)
            self.flag_answer_button.config(state=tk.NORMAL)

    def flag_answer(self):
        if self.recording and self.last_flagged != 'answer':
            elapsed_time = time.time() - self.start_time
            self.answer_times[self.event_id] = f"{elapsed_time:.2f}"
            print(f"Answer flagged at {elapsed_time:.2f} seconds (Event ID: E{self.event_id})")
            self.event_id += 1
            self.last_flagged = 'answer'
            self.flag_answer_button.config(state=tk.DISABLED)
            self.flag_question_button.config(state=tk.NORMAL)

    def save_flagged_events(self):
        try:
            with open(self.csv_filename, 'a', newline='') as file:
                writer = csv.writer(file)
                for event_id in sorted(set(self.question_times.keys()).union(self.answer_times.keys())):
                    question_time = self.question_times.get(event_id, '')
                    answer_time = self.answer_times.get(event_id, '')
                    if question_time and answer_time:
                        question_time_float = float(question_time)
                        answer_time_float = float(answer_time)
                        time_difference = f"{answer_time_float - question_time_float:.2f}"
                        writer.writerow([self.participant_id, self.condition, f"E{event_id}", question_time, answer_time, time_difference])
        except Exception as e:
            print(f"Error saving flagged events: {e}")

    def flag_question_key(self, event):
        self.flag_question()

    def flag_answer_key(self, event):
        self.flag_answer()

    def load_last_event_id(self):
        """ Load the last completed event ID from the CSV file. """
        last_event_id = 0
        try:
            with open(self.csv_filename, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['Participant ID'] == self.participant_id and row['Condition'] == self.condition:
                        event_id = int(row['Event ID'][1:])
                        last_event_id = max(last_event_id, event_id)
        except Exception as e:
            print(f"Error loading last event ID: {e}")
        # Set the event ID based on the last event ID
        self.event_id = last_event_id + 1

    def create_participant_directory(self):
        """ Create a directory for the participant if it doesn't exist. """
        self.participant_directory = os.path.join(self.main_directory, f"participant_{self.participant_id}")
        if not os.path.exists(self.participant_directory):
            os.makedirs(self.participant_directory)

    def update_clock(self):
        if self.recording:
            elapsed_time = int(time.time() - self.start_time)
            minutes, seconds = divmod(elapsed_time, 60)
            self.recording_time_label.config(text=f"Recording Time: {minutes:02}:{seconds:02}")
        self.root.after(1000, self.update_clock)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioRecorderApp(root)
    root.mainloop()
