"""Merge whisper segments with diarization labels into speaker turns.

Usage: build_transcript.py asr.json diar.json out_prefix [speaker_map.json]
"""
import sys, json

asr_p, diar_p, out_p = sys.argv[1:4]
smap = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else {}

W = 1.5  # analysis window length, seconds (must match diarize.py)
segs = json.load(open(asr_p))["transcription"]
d = json.load(open(diar_p))
hop, labels = d["hop"], d["labels"]


def label_for(a, b):
    """Overlap-weighted majority of diarization windows covering [a, b] seconds."""
    i0, i1 = int(a / hop), min(len(labels), int(b / hop) + 1)
    votes = {}
    for i in range(i0, i1):
        s = min(i * hop + W, b) - max(i * hop, a)
        if s > 0:
            votes[labels[i]] = votes.get(labels[i], 0) + s
    return max(votes, key=votes.get) if votes else -1


turns = []
for s in segs:
    a, b = s["offsets"]["from"] / 1000, s["offsets"]["to"] / 1000
    txt = s["text"].strip()
    if not txt:
        continue
    spk = label_for(a, b)
    if turns and turns[-1]["spk"] == spk and a - turns[-1]["end"] < 1.0:
        turns[-1]["text"] += " " + txt
        turns[-1]["end"] = b
    else:
        turns.append({"spk": spk, "start": a, "end": b, "text": txt})

for t in turns:
    t["speaker"] = smap.get(str(t["spk"]), f"spk{t['spk']}")
    t["start_ts"] = f"{int(t['start']//60):02d}:{int(t['start']%60):02d}"
    t["end_ts"] = f"{int(t['end']//60):02d}:{int(t['end']%60):02d}"

json.dump(turns, open(out_p + ".json", "w"), ensure_ascii=False, indent=1)
with open(out_p + ".md", "w") as f:
    for t in turns:
        f.write(f"**{t['speaker']}** [{t['start_ts']}–{t['end_ts']}]\n{t['text']}\n\n")

print(f"{len(turns)} turns -> {out_p}.json/.md")
for name in sorted({t["speaker"] for t in turns}):
    tt = [t for t in turns if t["speaker"] == name]
    print(f"  {name}: {len(tt)} turns, {sum(x['end']-x['start'] for x in tt)/60:.1f} min")
