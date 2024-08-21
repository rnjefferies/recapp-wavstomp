import librosa
import numpy as np
import matplotlib.pyplot as plt
import csv
import os

def detect_speech_segments(audio, sr, dynamic_range=1.5, min_silence_len=0.4, min_segment_len=0.1):
    amplitude = np.abs(audio)
    amplitude = amplitude / np.max(amplitude)

    # Calculate a dynamic threshold based on the mean and standard deviation of the amplitude
    mean_amplitude = np.mean(amplitude)
    std_amplitude = np.std(amplitude)
    dynamic_thresh = mean_amplitude + dynamic_range * std_amplitude

    speech_indices = np.where(amplitude > dynamic_thresh)[0]

    segments = []
    current_start = None
    current_end = None
    
    for i in speech_indices:
        if current_start is None:
            current_start = i
        elif i > current_end + sr * min_silence_len:
            # Check if the segment is longer than the minimum segment length
            if (current_end - current_start) / sr >= min_segment_len:
                segments.append((current_start, current_end))
            current_start = i
        current_end = i
    
    # Add the last segment if it exists and is longer than the minimum segment length
    if current_start is not None and (current_end - current_start) / sr >= min_segment_len:
        segments.append((current_start, current_end))
    
    return segments

def analyze_audio(file_path):
    audio, sr = librosa.load(file_path, sr=None)
    speech_segments = detect_speech_segments(audio, sr)
    segments = []
    
    for i, (start, end) in enumerate(speech_segments):
        segment_type = 'Question' if i % 2 == 0 else 'Answer'
        segments.append((segment_type, start / sr, end / sr))
    
    return segments, audio, sr

def save_segments_to_csv(csv_file, segments, participant_id, condition):
    event_id = 1  # Start event ID
    
    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        
        question_time = None
        
        for segment_type, start, end in segments:
            if segment_type == 'Question':
                question_time = end  # Save end time of the question
            elif segment_type == 'Answer' and question_time is not None:
                time_difference = end - question_time
                writer.writerow([participant_id, condition, f'E{event_id}', f'{question_time:.2f}', f'{end:.2f}', f'{time_difference:.2f}'])
                event_id += 1  # Increment event ID for each new Q&A pair

def plot_segments(segments, audio, sr, plot_file):
    time = np.linspace(0, len(audio) / sr, len(audio))
    plt.figure(figsize=(14, 8))
    plt.plot(time, audio, label='Waveform')

    for segment_type, start, end in segments:
        color = 'yellow' if segment_type == 'Question' else 'red'
        plt.axvspan(start, end, color=color, alpha=0.3, label=segment_type)
    
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('Waveform with Detected Segments')
    plt.legend(loc='upper right')
    plt.savefig(plot_file)
    plt.close()  # Close the plot to save memory

def extract_info_from_filename(filename):
    base_name = os.path.basename(filename)
    parts = base_name.split('_')
    participant_id = parts[1]
    condition = parts[2][1]  # Take the second character after the underscore
    return participant_id, condition

def process_directory(main_directory, output_csv):
    # Ensure the data directory exists
    data_directory = os.path.dirname(output_csv)
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    # Prepare the CSV file with a header
    with open(output_csv, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Participant ID', 'Condition', 'Event ID', 'Question Timestamp (s)', 'Answer Timestamp (s)', 'Time Difference (s)'])
    
    all_segments = []

    # Recursively walk through the directory
    for root, dirs, files in os.walk(main_directory):
        for filename in files:
            if filename.endswith('.wav'):
                file_path = os.path.join(root, filename)
                participant_id, condition = extract_info_from_filename(filename)
                
                # Analyze the audio and detect segments
                segments, audio, sr = analyze_audio(file_path)
                
                # Prepare the segments for sorting
                event_id = 1
                for segment_type, start, end in segments:
                    if segment_type == 'Question':
                        question_time = end
                    elif segment_type == 'Answer' and question_time is not None:
                        time_difference = end - question_time
                        all_segments.append([participant_id, condition, f'E{event_id}', question_time, end, time_difference])
                        event_id += 1

                # Generate and save the plot
                plot_file = os.path.join(root, f'{os.path.splitext(filename)[0]}.png')
                plot_segments(segments, audio, sr, plot_file)
                print(f"Processed {filename}, saved plot to {plot_file}")
    
    # Sort all segments by Participant ID, Condition, and Event ID
    all_segments.sort(key=lambda x: (x[0], x[1], int(x[2][1:])))  # Assuming Event ID format is 'E<number>'
    
    # Write sorted segments to the CSV
    with open(output_csv, 'a', newline='') as file:
        writer = csv.writer(file)
        for segment in all_segments:
            writer.writerow([segment[0], segment[1], segment[2], f'{segment[3]:.2f}', f'{segment[4]:.2f}', f'{segment[5]:.2f}'])

if __name__ == "__main__":
    # Calculate the absolute path to the main directory
    main_directory = os.path.abspath(os.path.join('..', 'participants'))  # Move up one directory level to reach the participants directory
    output_csv = os.path.abspath(os.path.join('..', 'data', 'main_segments.csv'))  # Save the main_segments.csv in the data subdirectory
    
    # Process all WAV files in the main directory and its subdirectories
    process_directory(main_directory, output_csv)
