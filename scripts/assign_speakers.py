"""Utterance-level speaker assignment.

Per ASR segment: mean/std MFCC over voiced frames -> z-scored -> nearest anchor centroid.
Anchors are long single-speaker stretches picked from the opening round; low-margin
segments are flagged for review instead of guessed.
"""
import sys, json, wave
import numpy as np

SR, WIN, HOP, NMEL, NCEP = 16000, 400, 160, 40, 20
# (label, start, end) in seconds of the trimmed audio
ANCHORS = [("moderator", 60.0, 78.0), ("gyurov", 90.0, 155.0), ("iotova", 178.0, 225.0)]


def mel_fb(nfft=512, nmel=NMEL, sr=SR):
    hz2mel = lambda f: 2595 * np.log10(1 + f / 700.0)
    mel2hz = lambda m: 700 * (10 ** (m / 2595.0) - 1)
    pts = mel2hz(np.linspace(hz2mel(50), hz2mel(sr / 2), nmel + 2))
    bins = np.floor((nfft + 1) * pts / sr).astype(int)
    fb = np.zeros((nmel, nfft // 2 + 1))
    for i in range(nmel):
        l, c, r = bins[i], bins[i + 1], bins[i + 2]
        if r <= l + 1:
            r = l + 2
        fb[i, l:c] = (np.arange(l, c) - l) / max(c - l, 1)
        fb[i, c:r] = (r - np.arange(c, r)) / max(r - c, 1)
    return fb


def dct_mat(ncep=NCEP, nmel=NMEL):
    n = np.arange(nmel)
    return np.cos(np.pi / nmel * (n + 0.5) * np.arange(ncep)[:, None])


FB, DCT = mel_fb(), dct_mat()


def f0_med(y, sr=SR, fmin=60, fmax=400):
    """YIN f0 (median over voiced 64 ms frames)."""
    tmin, tmax = int(sr / fmax), int(sr / fmin)
    out = []
    for i in range(0, len(y) - 1024, 512):
        fr = y[i:i + 1024].astype(np.float64)
        if np.sqrt((fr ** 2).mean()) < 0.01:
            continue
        fr -= fr.mean()
        n = len(fr)
        ac = np.correlate(fr, fr, "full")[n - 1:n + tmax]
        cum = np.concatenate(([0.0], np.cumsum(fr ** 2)))
        tau = np.arange(tmax + 1)
        d = cum[n - tau] + (cum[n] - cum[tau]) - 2 * ac
        cm = d.copy(); cm[0] = 1
        cm[1:] = d[1:] / (np.cumsum(d[1:]) / tau[1:] + 1e-12)
        for t in range(tmin, tmax):
            if cm[t] < 0.15:
                while t + 1 < tmax and cm[t + 1] < cm[t]:
                    t += 1
                out.append(sr / t)
                break
    return np.median(out) if len(out) > 2 else np.nan


def seg_feat(x, a, b):
    y = x[int(a * SR):int(b * SR)].astype(np.float32)
    if len(y) < WIN * 2:
        return None
    idx = np.arange(WIN)[None, :] + HOP * np.arange(1 + (len(y) - WIN) // HOP)[:, None]
    fr = y[idx] * np.hamming(WIN)
    p = np.abs(np.fft.rfft(fr, 512)) ** 2
    e = np.log(p.sum(1) + 1e-10)
    m = e > np.percentile(e, 40)
    if m.sum() < 5:
        return None
    mfcc = (np.log(p[m] @ FB.T + 1e-10) @ DCT.T)[:, 1:]
    return np.concatenate([mfcc.mean(0), mfcc.std(0)])


def main():
    asr_p, wav_p, out_p = sys.argv[1:4]
    x = np.frombuffer(wave.open(wav_p).readframes(10**9), np.int16).astype(np.float32) / 32768
    segs = [s for s in json.load(open(asr_p))["transcription"] if s["text"].strip()]
    F, F0, keep = [], [], []
    for s in segs:
        a, b = s["offsets"]["from"] / 1000, s["offsets"]["to"] / 1000
        f = seg_feat(x, a, b)
        if f is not None:
            F.append(f); F0.append(f0_med(x[int(a * SR):int(b * SR)])); keep.append(s)
    F = np.array(F)
    F = (F - F.mean(0)) / (F.std(0) + 1e-6)
    F0 = np.array(F0)
    F0 = np.where(np.isnan(F0), np.nanmedian(F0), F0)
    F = np.concatenate([F, 3.0 * ((F0 - F0.mean()) / (F0.std() + 1e-6))[:, None]], 1)

    cent, names = [], []
    for name, a, b in ANCHORS:
        idx = [i for i, s in enumerate(keep)
               if s["offsets"]["from"] / 1000 >= a and s["offsets"]["to"] / 1000 <= b]
        cent.append(F[idx].mean(0)); names.append(name)
    C = np.array(cent)

    def dist(C):
        return np.linalg.norm(F[:, None] - C[None], axis=2)

    d = dist(C)
    lab = d.argmin(1)
    for _ in range(2):  # EM: re-estimate centroids from confident segments
        srt = np.sort(d, 1)
        conf = srt[:, 0] < 0.75 * srt[:, 1]
        for j in range(len(C)):
            m = conf & (lab == j)
            if m.sum() > 30:
                C[j] = F[m].mean(0)
        d = dist(C)
        lab = d.argmin(1)

    # pitch gate: f0 < 155 Hz is male -> gyurov; otherwise iotova vs moderator only
    g, fs = names.index("gyurov"), [names.index("iotova"), names.index("moderator")]
    allowed = np.where((F0 > 155)[:, None], np.isin(np.arange(len(names)), fs), np.arange(len(names)) == g)
    d2 = np.where(allowed, d, np.inf)
    lab = d2.argmin(1)
    srt = np.sort(d2, 1)
    margin = (srt[:, 1] - srt[:, 0]) / (srt[:, 0] + 1e-6)

    out = []
    for i in range(0, len(y) - 1024, 512):
        fr = y[i:i + 1024].astype(np.float64)
        if np.sqrt((fr ** 2).mean()) < 0.01:
            continue
        fr -= fr.mean()
        n = len(fr)
        ac = np.correlate(fr, fr, "full")[n - 1:n + tmax]
        cum = np.concatenate(([0.0], np.cumsum(fr ** 2)))
        tau = np.arange(tmax + 1)
        d = cum[n - tau] + (cum[n] - cum[tau]) - 2 * ac
        cm = d.copy(); cm[0] = 1
        cm[1:] = d[1:] / (np.cumsum(d[1:]) / tau[1:] + 1e-12)
        for t in range(tmin, tmax):
            if cm[t] < 0.15:
                while t + 1 < tmax and cm[t + 1] < cm[t]:
                    t += 1
                out.append(sr / t)
                break
    return np.median(out) if len(out) > 2 else np.nan


def seg_feat(x, a, b):
    y = x[int(a * SR):int(b * SR)].astype(np.float32)
    if len(y) < WIN * 2:
        return None
    idx = np.arange(WIN)[None, :] + HOP * np.arange(1 + (len(y) - WIN) // HOP)[:, None]
    fr = y[idx] * np.hamming(WIN)
    p = np.abs(np.fft.rfft(fr, 512)) ** 2
    e = np.log(p.sum(1) + 1e-10)
    m = e > np.percentile(e, 40)
    if m.sum() < 5:
        return None
    mfcc = (np.log(p[m] @ FB.T + 1e-10) @ DCT.T)[:, 1:]
    return np.concatenate([mfcc.mean(0), mfcc.std(0)])


def main():
    asr_p, wav_p, out_p = sys.argv[1:4]
    x = np.frombuffer(wave.open(wav_p).readframes(10**9), np.int16).astype(np.float32) / 32768
    segs = [s for s in json.load(open(asr_p))["transcription"] if s["text"].strip()]
    F, F0, keep = [], [], []
    for s in segs:
        a, b = s["offsets"]["from"] / 1000, s["offsets"]["to"] / 1000
        f = seg_feat(x, a, b)
        if f is not None:
            F.append(f); F0.append(f0_med(x[int(a * SR):int(b * SR)])); keep.append(s)
    F = np.array(F)
    F = (F - F.mean(0)) / (F.std(0) + 1e-6)
    F0 = np.array(F0)
    F0 = np.where(np.isnan(F0), np.nanmedian(F0), F0)
    F = np.concatenate([F, 3.0 * ((F0 - F0.mean()) / (F0.std() + 1e-6))[:, None]], 1)

    cent, names = [], []
    for name, a, b in ANCHORS:
        idx = [i for i, s in enumerate(keep)
               if s["offsets"]["from"] / 1000 >= a and s["offsets"]["to"] / 1000 <= b]
        cent.append(F[idx].mean(0)); names.append(name)
    C = np.array(cent)

    def nearest(C):
        d = np.linalg.norm(F[:, None] - C[None], axis=2)
        o = np.argsort(d, 1)
        return o[:, 0], d, o

    # gender gate from pitch: f0 < 150 Hz => gyurov, > 160 => iotova|moderator
    g = names.index("gyurov")
    fs = [names.index("iotova"), names.index("moderator")]

    lab, d, order = nearest(C)
    for _ in range(2):  # EM: re-estimate centroids from confident segments
        conf = (d[np.arange(len(F)), order[:, 0]] < 0.75 * d[np.arange(len(F)), order[:, 1]])
        for j in range(len(C)):
            m = conf & (lab == j)
            if m.sum() > 30:
                C[j] = F[m].mean(0)
        lab, d, order = nearest(C)

    female = F0 > 155
    lab2 = np.where(female, lab, g)
    for i in np.where(female)[0]:
        lab2[i] = fs[int(np.argmin(d[i, fs]))]
    lab = lab2
    margin = (d[np.arange(len(F)), order[:, 1]] - d[np.arange(len(F)), order[:, 0]]) / (d[np.arange(len(F)), order[:, 0]] + 1e-6)

    out = []
    for s, l, mg, f0v in zip(keep, lab, margin, F0):
        out.append({"start": s["offsets"]["from"] / 1000, "end": s["offsets"]["to"] / 1000,
                    "speaker": names[l], "f0": int(f0v), "margin": round(float(mg), 2),
                    "text": s["text"].strip()})
    json.dump(out, open(out_p + ".json", "w"), ensure_ascii=False, indent=1)
    with open(out_p + ".md", "w") as f:
        for t in out:
            flag = " ⚠" if t["margin"] < 0.15 else ""
            f.write(f"**{t['speaker']}** [{int(t['start']//60):02d}:{int(t['start']%60):02d}]{flag}\n{t['text']}\n\n")
    print(f"{len(out)} segments; low-margin: {sum(1 for t in out if t['margin'] < 0.15)}")
    for n in names:
        ss = [t for t in out if t["speaker"] == n]
        print(f"  {n}: {len(ss)} segs, {sum(t['end']-t['start'] for t in ss)/60:.1f} min")


if __name__ == "__main__":
    main()
