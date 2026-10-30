"""Extract flagged turns with neighbouring context for human review."""
import json, sys

turns = json.load(open(sys.argv[1]))
out = sys.argv[2]
lines = ["# Review: flagged turns", "",
         "Listen: `ffmpeg -ss <sec> -t 40 -i data/raw/debate.16k.wav -af volume=2 clip.wav`", ""]
n = 0
for i, t in enumerate(turns):
    if not t.get("uncertain"):
        continue
    n += 1
    lines.append(f"## {n}. [{t['start_ts']}] {t['speaker']}  (sec {int(t['start'])})")
    if i:
        lines.append(f"- prev **{turns[i-1]['speaker']}**: {turns[i-1]['text'][-160:]}")
    lines.append(f"- **{t['speaker']}**: {t['text']}")
    if i + 1 < len(turns):
        lines.append(f"- next **{turns[i+1]['speaker']}**: {turns[i+1]['text'][:160]}")
    lines.append("")
open(out, "w").write("\n".join(lines))
print(f"{n} flagged turns -> {out}")
