"""Merge per-segment speaker labels into readable turns + flag uncertain ones.

A turn = consecutive segments by the same speaker with < GAP s between them.
Turn is flagged if any member segment was low-margin, pitch-inconsistent, or very short
inside a speaker change.
"""
import sys, json, re

src, out_p = sys.argv[1], sys.argv[2]
GAP = 1.5
segs = json.load(open(src))

FIX = [  # (pattern, replacement) - conservative, names/terms only
    (r"Слатарева", "Златарева"),
    (r"Иллена|Илена|Иляна", "Илияна"),
    (r"Ятова", "Йотова"),
    (r"балутаж", "балотаж"),
    (r"КАДИДАТИТЕ", "КАНДИДАТИТЕ"),
    (r"даначна", "данъчна"),
    (r"удобрили", "одобрили"),
    (r"жреби и", "жребий"),
    (r"във къщи", "в къщи"),
    (r"господин (Дюров|Гиров|Георс|Геров|Геов|Гио|Волч|Григо|Бюров)", "господин Гюров"),
    (r"госпожо (Геров|Ятова|Йото)\b", "госпожо Йотова"),
    (r"(Илана|Елена|Илена) (Юто|Йотова)", "Илияна Йотова"),
    (r"Болотажа|Балутажа", "балотажа"),
    (r"Ботъш", "Боташ"),
    (r"Сен Василев", "Асен Василев"),
    (r"Изривове", "Взривове"),
    (r"Заговядайте", "Заповядайте"),
    (r"\bИмато\b", "Имате"),
    (r"Госпожото", "Госпожо"),
    (r"Бърс отговор", "Бърз отговор"),
    (r"Русула Фон Дерлайн", "Урсула фон дер Лайен"),
    (r"\bДова са\b", "Кои са"),
]


def fix(t):
    for a, b in FIX:
        t = re.sub(a, b, t)
    return t


turns = []
for s in segs:
    bad = s["margin"] < 0.12 or (s["speaker"] == "gyurov") != (s["f0"] < 155)
    if turns and turns[-1]["speaker"] == s["speaker"] and s["start"] - turns[-1]["end"] < GAP:
        turns[-1]["text"] += " " + fix(s["text"])
        turns[-1]["end"] = s["end"]
        turns[-1]["bad"] += bad; turns[-1]["n"] += 1
    else:
        turns.append({"speaker": s["speaker"], "start": s["start"], "end": s["end"],
                      "text": fix(s["text"]), "bad": int(bad), "n": 1})

# glue sentence fragments split across segment boundaries back onto the previous turn
glued = []
for t in turns:
    if (glued and t["start"] - glued[-1]["end"] < 1.2
            and (t["end"] - t["start"]) < 4.0
            and re.match(r"[а-я]", t["text"]) and not re.search(r"[.!?]$", glued[-1]["text"])):
        glued[-1]["text"] += " " + t["text"]
        glued[-1]["end"] = t["end"]
        glued[-1]["bad"] += t["bad"]; glued[-1]["n"] += t["n"]
    else:
        glued.append(t)
turns = glued

# manual fixes for fragments acoustics cannot resolve (see notes.md)
try:
    fixes = json.load(open("data/transcripts/label_fixes.json"))
except FileNotFoundError:
    fixes = {}
for t in turns:
    if str(int(round(t["start"]))) in fixes:
        t["speaker"] = fixes[str(int(round(t["start"])))]
        t["uncertain"] = False

for t in turns:
    t["uncertain"] = t["bad"] / t["n"] > 0.4
    t["text"] = re.sub(r"\s+", " ", t["text"]).strip()
    t["start_ts"] = f"{int(t['start']//60):02d}:{int(t['start']%60):02d}"

json.dump(turns, open(out_p + ".json", "w"), ensure_ascii=False, indent=1)
with open(out_p + ".md", "w") as f:
    f.write("# Дебат Йотова – Гюров, БНТ, 29.10.2026\n\n")
    f.write("Автоматичен транскрипт (whisper.cpp large-v3-turbo) с диаризация.\n")
    f.write("⚠ = несигурно разпознаване на говорител/текст.\n\n")
    for t in turns:
        mark = " ⚠" if t["uncertain"] else ""
        f.write(f"**{t['speaker']}** [{t['start_ts']}]{mark}\n{t['text']}\n\n")

print(f"{len(turns)} turns, {sum(t['uncertain'] for t in turns)} flagged")
for n in ("moderator", "gyurov", "iotova"):
    ss = [t for t in turns if t["speaker"] == n]
    print(f"  {n}: {len(ss)} turns, {sum(t['end']-t['start'] for t in ss)/60:.1f} min")
