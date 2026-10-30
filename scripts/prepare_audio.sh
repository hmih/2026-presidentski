#!/bin/sh
# Fetch the debate and build the ASR input: 16 kHz mono, 08:00 trimmed, loudness-normalised.
# Usage: scripts/prepare_audio.sh [video_id]
set -e
ID=${1:-vZzeuZMG8yo}
cd "$(dirname "$0")/.."

.venv/bin/yt-dlp --js-runtimes node -f bestaudio \
  -o "data/raw/debate.%(ext)s" --write-info-json --no-playlist \
  "https://www.youtube.com/watch?v=$ID"

# -ss 480: the first 8:20 is an intro montage (YouTube captions start at 08:20 too)
ffmpeg -v error -y -ss 480 -i data/raw/debate.webm -vn -ac 1 -ar 16000 \
  -af "highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11" \
  -c:a pcm_s16le data/raw/debate.ff.16k.wav

ffprobe -v quiet -show_entries format=duration -of csv=p=0 data/raw/debate.ff.16k.wav
