"""Re-transcribe selected spans with a second model and print both versions side by side.

Usage: verify_spans.py model.bin wav out_dir [pad]
Reads spans.json: [{"start": s, "end": s}, ...]
"""
import json, subprocess, sys, os

model, wav, out, pad = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4] if len(sys.argv) > 4 else 4)
os.makedirs(out, exist_ok=True)
spans = json.load(open("spans.json"))
bin = "third_party/whisper.cpp/build/bin/whisper-cli"
for i, s in enumerate(spans):
    a, b = max(0, s["start"] - pad), s["end"] + pad
    w = f"{out}/s{i}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(b - a),
                    "-i", wav, "-c", "copy", w], check=True)
    r = subprocess.run([bin, "-m", model, "-f", w, "-l", "bg", "-t", "5", "-mc", "0",
                        "-sns", "--no-prints", "--prompt",
                        "Илияна Йотова, Андрей Гюров, БНТ, ЦИК, балотаж, Ботaш"],
                       capture_output=True, text=True)
    txt = " ".join(l.split("]")[-1].strip() for l in r.stdout.splitlines() if "] " in l)
    print(f"\n[{a:7.1f}-{b:7.1f}] {s.get('note','')}\n  v3: {txt[:400]}")
