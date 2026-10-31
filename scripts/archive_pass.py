"""Fill archive URLs in evidence clusters via the Wayback availability API."""
import json, glob, time, urllib.parse, urllib.request

def snap(url):
    api = "https://archive.org/wayback/available?url=" + urllib.parse.quote(url, safe="")
    try:
        with urllib.request.urlopen(api, timeout=12) as r:
            d = json.load(r)
        c = d.get("archived_snapshots", {}).get("closest")
        return c["url"] if c and c.get("available") else ""
    except Exception:
        return ""

for f in sorted(glob.glob("data/factcheck/evidence/*.json")):
    d = json.load(open(f))
    n = 0
    for it in d["items"]:
        if it.get("url") and not it.get("archive"):
            a = snap(it["url"])
            if a:
                it["archive"] = a; n += 1
    json.dump(d, open(f, "w"), ensure_ascii=False, indent=1)
    tot = sum(1 for i in d["items"] if i.get("archive"))
    print(f"{f.split('/')[-1]}: +{n} archived, {tot}/{len(d['items'])} total")
    time.sleep(0.3)
