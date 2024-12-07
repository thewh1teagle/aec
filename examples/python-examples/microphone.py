"""
pip install pyaec PyAudio soundfile numpy
wget https://github.com/thewh1teagle/aec-rs/releases/download/audio-files/song.wav
python microphone.py song.wav off.wav off
python microphone.py song.wav on.wav on
"""

import soundfile as sf
import numpy as np
import sys
import pyaudio
from pyaec import Aec
import time

# Parameters
frame_size = 160
filter_length = 1600
sample_rate = 16000
aec = Aec(frame_size, filter_length, sample_rate, True)

# Input and output paths from command line arguments
song_path, out_path, echo_cancellation = sys.argv[1], sys.argv[2], sys.argv[3]

# Load the song
song_samples, _ = sf.read(song_path, dtype="int16")

# Initialize PyAudio instance
p = pyaudio.PyAudio()

# List to store output frames
output_frames = []

# Open the input (microphone) and output (speaker) streams
input_stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=sample_rate,
    input=True,
    frames_per_buffer=frame_size,
)

output_stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=sample_rate,
    output=True,
    frames_per_buffer=frame_size,
)


# Function to handle recording and playback for 10 seconds
def process_audio(duration=10):
    global song_samples
    start_time = time.time()

    while len(song_samples) > frame_size and (time.time() - start_time) < duration:
        # Read input (microphone) frame
        in_samples = np.frombuffer(input_stream.read(frame_size), dtype="int16")

        # Play a portion of the song
        song_frame = song_samples[:frame_size]
        song_samples = song_samples[
            frame_size:
        ]  # Get next portion of the song for playback

        # Process echo cancellation or skip it based on argument
        if echo_cancellation.lower() == "on":
            processed_frame = aec.cancel_echo(in_samples, song_frame)
        else:
            processed_frame = (
                in_samples  # No echo cancellation, just use input as output
            )

        # Append processed frame to the output frames list
        output_frames.append(processed_frame)

        # Play back the song frame through speakers
        output_stream.write(song_frame.tobytes())

    # Concatenate all processed frames and save to output file
    output = np.concatenate(output_frames, axis=0)

    # Convert output to int16 before saving to file
    output = output.astype(np.int16)

    # Write the output to the output file
    sf.write(out_path, output, sample_rate)
    print(f"Created {out_path}")


# Start processing for 10 seconds
process_audio(duration=10)

# Close the streams
input_stream.stop_stream()
input_stream.close()
output_stream.stop_stream()
output_stream.close()

# Terminate PyAudio instance
p.terminate()
