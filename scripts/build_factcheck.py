"""Merge verdicts, inline the cited evidence, and render the report."""
import json, glob, collections

ev = {f.split("/")[-1][:-5]: json.load(open(f)) for f in glob.glob("data/factcheck/evidence/*.json")}
V = json.load(open("data/factcheck/_v1.json")) + json.load(open("data/factcheck/_v2.json"))
claims = {c["id"]: c for c in json.load(open("data/claims/claims.json"))["claims"]}

def resolve(ref):
    cluster, idx = ref.split(":")
    it = ev[cluster]["items"][int(idx) - 1]
    return {"statement": it["statement"], "quote": it["quote"], "source": it["source"],
            "url": it["url"], "archive": it["archive"], "date": it["date"]}

rows = []
for row in V:
    cid, verdict, conf, steel, finding, refs, cref, deception, notes = row[:9]
    doc_quote = row[9] if len(row) > 9 else ""
    c = claims[cid]
    rows.append({"claim_id": cid, "speaker": c["speaker"], "t": c["t"], "quote_bg": c["text"],
                 "claim_en": c["claim_en"], "topic": c["topic"], "verdict": verdict,
                 "confidence": conf, "steelman": steel, "finding": finding,
                 "evidence": [resolve(r) for r in refs],
                 "counter_evidence": [resolve(r) for r in cref],
                 "deception": deception, "notes": notes, "document_quote": doc_quote})

rows.sort(key=lambda r: (r["claim_id"]))
json.dump({"count": len(rows), "claims": rows}, open("data/factcheck/verdicts.json", "w"),
          ensure_ascii=False, indent=1)

cnt = collections.Counter(r["verdict"] for r in rows)
dec = collections.Counter(r["deception"] for r in rows if r["deception"] != "none")
by_topic = collections.defaultdict(list)
for r in rows:
    by_topic[r["topic"]].append(r)

md = ["# Fact-check", "",
      f"{len(rows)} claims checked against primary sources. Method: [`docs/factcheck_method.md`](../docs/factcheck_method.md).", "",
      "| verdict | n |", "|---|---|"]
for k in ["true", "mostly_true", "mixed", "mostly_false", "false", "unverified", "partly"]:
    if cnt.get(k):
        md.append(f"| {k} | {cnt[k]} |")
md += ["", f"Deception flags: {dict(dec) if dec else 'none'}", "",
       "## Verdicts by topic", ""]
for topic in sorted(by_topic):
    md += [f"### {topic}", "", "| id | t | speaker | claim | verdict | confidence |", "|---|---|---|---|---|---|"]
    for r in by_topic[topic]:
        md.append(f"| {r['claim_id']} | {r['t']} | {r['speaker']} | {r['claim_en'][:110]} | **{r['verdict']}** | {r['confidence']} |")
    md.append("")
md += ["## Dossiers", ""]
for r in rows:
    md += [f"### {r['claim_id']} — {r['verdict']}", "",
           f"> {r['quote_bg']}", "",
           f"*{r['claim_en']}*", "",
           f"**Steelman:** {r['steelman']}", "",
           f"**Finding:** {r['finding']}", ""]
    if r.get("document_quote"):
        md += [f"**Signed text:** „{r['document_quote']}“", ""]
    for e in r["evidence"]:
        md.append(f"- {e['source']} ({e['date']}) — {e['url']}" + (f" — archived: {e['archive']}" if e["archive"] else ""))
    if r["deception"] != "none":
        md.append(f"- **Deception:** {r['deception']}")
    if r["notes"]:
        md.append(f"- *Note:* {r['notes']}")
    md.append("")
open("data/factcheck/report.md", "w").write("\n".join(md))
print(len(rows), "dossiers;", dict(cnt))
