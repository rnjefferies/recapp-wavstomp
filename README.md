# Recapp and Wavstomp

## Description

This project is built specifically for my PhD analyses, but the tools could be useful to other SA reserachers or adapted to something completely different. It icludes two main tools: `Recapp` and `Wavstomp`. 

- **Recapp** is a Python application for recording speech-based data collection sessions. It allows users to start and stop recordings, and to flag the end of questions and answers during the session. The recordings are saved as `.wav` files, and the flagged events are logged in a CSV file.

- **Wavstomp** is a Python script for analyzing the recorded `.wav` files. It detects speech segments in the audio files, differentiating between questions and answers using a simple system of expected Q & A alternaiton, and logs the details into a comprehensive CSV file. Additionally, it generates waveform plots with the detected segments highlighted.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Recapp](#recapp)
  - [Wavstomp](#wavstomp)
- [Project Structure](#project-structure)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/recapp-wavstomp.git

Navigate to the Project Directory:

bash

cd recapp-wavstomp

Install the Required Dependencies:

bash

    pip install -r requirements.txt

Ensure Proper Directory Structure:
    Make sure the following directories exist within your project:
        app/: Contains the recapp.py file.
        scripts/: Contains the wavstomp.py file.
        data/: For storing output CSV files.
        participants/: For storing participant-specific recordings and data.

## Usage
**Recapp**

    Start the Application:
        Navigate to the app directory and run recapp.py:

        bash

        cd app
        python recapp.py

    Recording Sessions:
        Enter the Participant ID and Condition (A, B, or C).
        Click "Start Recording" to begin the session.
        Use the "Flag Question" and "Flag Answer" buttons to mark the end of questions and answers during the session. You can also use the Q and A
        keys on your keyboard. 
        Click "Stop Recording" to save the session.

    Output:
        .wav files are saved in the participants/ directory, named according to the participant ID and condition.
        A CSV log (flagged_events.csv) is saved in the data/ directory, recording the flagged events.

**Wavstomp**

    Run the Script:
        Navigate to the scripts directory and run wavstomp.py:

        bash

        cd scripts
        python wavstomp.py

    Processing Files:
        The script will process all .wav files in the participants/ directory, analyse them to detect speech segments, and save the results.

    Output:
        A main_segments.csv file is generated in the data/ directory, summarising the detected segments across all participants.
        Waveform plots with highlighted segments are saved in the participants/ directory alongside the original .wav files.

## Project Structure

recapp-wavstomp/
│
├── app/
│   └── recapp.py          # Recording application
│
├── scripts/
│   └── wavstomp.py        # Analysis script
│
├── data/                  # Directory for output CSV files
│   ├── flagged_events.csv
│   └── main_segments.csv
│
├── participants/          # Directory for storing participant recordings and plots
│   ├── participant_1/
│   │   └── recording_1_C_A_TIMESTAMP.wav
│   └── participant_2/
│       └── recording_2_C_B_TIMESTAMP.wav
│
└── requirements.txt       # Project dependencies

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

    Thanks to the open-source community for providing the libraries and tools that made this project possible. Special thanks to Alex for being the best brother and for the most epic frontshuvits. 
