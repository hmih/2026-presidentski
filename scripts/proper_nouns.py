"""List mid-sentence capitalised tokens with one context each, for manual adjudication."""
import json, re, sys, collections

turns = json.load(open(sys.argv[1]))
SENT_END = re.compile(r"[.!?…:;]$")
tok = re.compile(r"[А-ЯA-Z][\w\-’']+")
ctx = collections.defaultdict(list)
count = collections.Counter()

for t in turns:
    words = t["text"].split()
    for i, w in enumerate(words):
        core = re.sub(r"^[«„\"(]+|[»“\"),.;:!?]+$", "", w)
        for m in tok.finditer(core):
            s = m.group(0)
            if i == 0 or SENT_END.search(words[i - 1]):
                # sentence-initial: only keep if clearly a name address
                if not re.search(r"(господин|госпожо|д-р|министър|президент)\s*$", words[i - 1] if i else ""):
                    continue
            count[s] += 1
            if len(ctx[s]) < 2:
                ctx[s].append(t["text"][:160])

for s, n in sorted(count.items(), key=lambda x: (x[1], x[0])):
    print(f"{s} ({n}) | {ctx[s][0][:130]}")
