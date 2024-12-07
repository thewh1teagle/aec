"""
pip install pyaec numpy soundfile
wget https://github.com/thewh1teagle/aec-rs/releases/download/audio-files/rec.wav
wget https://github.com/thewh1teagle/aec-rs/releases/download/audio-files/echo.wav
python3 wav.py rec.wav echo.wav output.wav
"""

from pyaec import Aec
import soundfile as sf
import sys
import numpy as np

rec_path, echo_path, out_path = sys.argv[1:]
frame_size = 160
filter_length = 1600
sample_rate = 16000
aec = Aec(frame_size, filter_length, sample_rate, True)

rec_samples, _ = sf.read(rec_path, dtype="int16")
echo_samples, _ = sf.read(echo_path, dtype="int16")

num_frames = len(rec_samples) // frame_size
output_frames = []
for i in range(num_frames):
    start = i * frame_size
    end = start + frame_size
    # Process each frame
    processed_frame = aec.cancel_echo(rec_samples[start:end], echo_samples[start:end])
    output_frames.append(processed_frame)

# Concatenate all processed frames
output = np.concatenate(output_frames, dtype="int16")
sf.write(out_path, output, sample_rate)
print(f"Created {out_path}")
