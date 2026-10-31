"""Render the comparative narrative document from the per-candidate maps."""
import json, csv, collections

G = json.load(open("data/narratives/gyurov.json"))
I = json.load(open("data/narratives/iotova.json"))
rows = list(csv.DictReader(open("data/narratives/salience.csv")))
by = collections.defaultdict(collections.Counter)
for r in rows:
    by[(int(r["bin_start_min"]), r["speaker"])][r["topic"]] += int(r["claims"])

out = ["# Narrative trajectories", "",
       "Two independent analyses (one per candidate) of the 111-minute debate, anchored in the",
       "339 claims in `data/claims/claims.json`. `salience.csv` holds the per-20-minute topic counts",
       "behind the phase table.", ""]

out += ["## Phases", "", "| window | gyurov (top topics) | iotova (top topics) |", "|---|---|---|"]
for b in sorted({k[0] for k in by}):
    g = ", ".join(f"{t} {n}" for t, n in by[(b, "gyurov")].most_common(3))
    i = ", ".join(f"{t} {n}" for t, n in by[(b, "iotova")].most_common(3))
    out.append(f"| {b:02d}–{b+20:02d} min | {g} | {i} |")
out.append("")

for d, name in ((G, "Гюров"), (I, "Йотова")):
    out += [f"## {name}", "", d["summary"], "",
            "| narrative | salience | window | shift |", "|---|---|---|---|"]
    for n in d["narratives"]:
        w = n["active_windows"][0] if n["active_windows"] else ""
        out.append(f"| **{n['label']}** | {n['salience']} | {w} | {n['shift'][:160]} |")
    out.append("")
    out += ["<details><summary>Narrative detail</summary>", ""]
    for n in d["narratives"]:
        out += [f"### {n['label']}", "",
                f"- **Problem:** {n['problem']}",
                f"- **Culprit:** {n['culprit']}",
                f"- **Remedy:** {n['remedy']}",
                f"- **Warning:** {n['warning']}",
                f"- **Claims:** {', '.join(n['evidence_claims'])}",
                f"- **Moves:** {', '.join(n['rhetorical_moves'])}",
                f"- **Trajectory:** " + "; ".join(n["active_windows"]), ""]
    out += ["</details>", ""]

out += ["## Where the narratives collide", "",
        "Each pair is stated by one candidate and answered by the other. The last line names the",
        "record that would settle it — this is the fact-check queue, not a verdict.", ""]
seen = set()
for d in (G, I):
    for c in d["collisions"]:
        k = c["topic"].lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(f"- **{c['topic']}**\n  - {c['their_claim']}\n  - {c['counter']}\n  - *resolve with:* {c['checkable']}")
out.append("")
open("data/narratives/README.md", "w").write("\n".join(out))
print("wrote data/narratives/README.md")
