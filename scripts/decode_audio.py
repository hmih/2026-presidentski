"""Decode debate audio to 16 kHz mono s16le WAV (no ffmpeg CLI needed)."""
import sys, wave
import av
import numpy as np

src, dst = sys.argv[1], sys.argv[2]
res = av.AudioResampler(format="s16", layout="mono", rate=16000)
out = []
with av.open(src) as c:
    st = c.streams.audio[0]
    for fr in c.decode(st):
        for r in res.resample(fr):
            out.append(r.to_ndarray())
resampler_flush = res.resample(None)
for r in resampler_flush:
    out.append(r.to_ndarray())
pcm = np.concatenate([a.reshape(-1) for a in out])
with wave.open(dst, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
    w.writeframes(pcm.tobytes())
print(f"{dst}: {len(pcm)/16000:.1f}s")
