"""Merge per-chunk claim files into one validated dataset + readable index."""
import json, re, glob, collections

claims = []
for i in range(1, 9):
    claims += json.load(open(f"data/claims/chunk_{i:02d}.json"))["claims"]

def secs(t):
    m, s = t.split(":")
    return int(m) * 60 + int(s)

seen_q, seen_e, out = {}, {}, []
for c in claims:
    c["text"] = re.sub(r"\s+", " ", c["quote_bg"]).strip()
    key_q = c["text"].lower()
    key_e = re.sub(r"[^a-zа-я ]", "", c["claim_en"].lower())
    if key_q in seen_q or key_e in seen_e:
        out[seen_q.get(key_q, seen_e.get(key_e))]["dupes"] = out[seen_q.get(key_q, seen_e.get(key_e))].get("dupes", 0) + 1
        continue
    seen_q[key_q] = len(out); seen_e[key_e] = len(out)
    c["sec"] = secs(c["t"])
    out.append(c)

out.sort(key=lambda c: c["sec"])
for c in out:
    c.pop("sec", None)
data = {"source": "data/transcripts/transcript.json", "count": len(out), "claims": out}
json.dump(data, open("data/claims/claims.json", "w"), ensure_ascii=False, indent=1)

by_topic = collections.defaultdict(list)
for c in out:
    by_topic[c["topic"]].append(c)
with open("data/claims/claims.md", "w") as f:
    f.write(f"# Claims — {len(out)} extracted from the BNT debate\n\n")
    f.write("Generated from `transcript.json`; every `quote_bg` is a verbatim substring of the transcript.\n\n")
    for topic in sorted(by_topic):
        cs = by_topic[topic]
        f.write(f"## {topic} ({len(cs)})\n\n")
        f.write("| id | t | speaker | type | checkable | claim |\n|---|---|---|---|---|---|\n")
        for c in cs:
            f.write(f"| {c['id']} | {c['t']} | {c['speaker']} | {c['type']} | {c['checkable']} | {c['claim_en']} |\n")
        f.write("\n")

print(f"merged {len(claims)} -> {len(out)} unique")
for k in ("speaker", "type", "checkable", "topic"):
    print(k, dict(collections.Counter(c[k] for c in out).most_common()))
print("decisions:", len({c["decision"] for c in out if c["decision"]}))
