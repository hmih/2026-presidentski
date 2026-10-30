"""Lightweight speaker diarization: log-mel/MFCC stats + k-means + Viterbi smoothing.

No ML deps (torch/pyannote unavailable on py3.14); adequate for a 3-voice studio debate.
Usage: diarize.py in.wav out.json [k]
"""
import sys, json, wave
import numpy as np

SR, WIN, HOP, NMEL, NCEP = 16000, 400, 160, 40, 20
WSEG, WHOP = 1.5, 0.75  # analysis window / hop, seconds


def mel_fb(nfft, nmel, sr):
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


def dct_mat(ncep, nmel):
    n = np.arange(nmel)
    return np.cos(np.pi / nmel * (n + 0.5) * np.arange(ncep)[:, None])


def frame_feats(x, fb, dct):
    n = 1 + (len(x) - WIN) // HOP
    idx = np.arange(WIN)[None, :] + HOP * np.arange(n)[:, None]
    out = np.empty((n, NCEP + 1), np.float32)
    for i in range(0, n, 4000):
        fr = x[idx[i:i + 4000]].astype(np.float32) * np.hamming(WIN)
        p = np.abs(np.fft.rfft(fr, 512)) ** 2
        out[i:i + 4000, 1:] = np.log(p @ fb.T + 1e-10) @ dct.T
        out[i:i + 4000, 0] = np.log(p.sum(1) + 1e-10)
    return out


def kmeans(X, k, iters=60, restarts=6):
    best = None
    for _ in range(restarts):
        C = [X[np.random.randint(len(X))]]
        for _ in range(1, k):
            d = np.min(((X[:, None] - np.array(C)[None]) ** 2).sum(-1), 1)
            C.append(X[np.random.choice(len(X), p=d / d.sum())])
        C = np.array(C)
        for _ in range(iters):
            d = ((X[:, None] - C[None]) ** 2).sum(-1)
            lab = d.argmin(1)
            for j in range(k):
                if (lab == j).any():
                    C[j] = X[lab == j].mean(0)
        cost = ((X - C[lab]) ** 2).sum()
        if best is None or cost < best[0]:
            best = (cost, C.copy(), lab.copy())
    return best[1], best[2]


def viterbi(dist, pen):
    n, k = dist.shape
    cost = dist[0].copy()
    bp = np.zeros((n, k), int)
    for t in range(1, n):
        cand = cost[:, None] + pen * (1 - np.eye(k))
        bp[t] = cand.argmin(0)
        cost = dist[t] + cand.min(0)
    path = [int(cost.argmin())]
    for t in range(n - 1, 0, -1):
        path.append(int(bp[t, path[-1]]))
    return np.array(path[::-1])


def main():
    src, dst = sys.argv[1], sys.argv[2]
    k = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    with wave.open(src) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    fb, dct = mel_fb(512, NMEL, SR), dct_mat(NCEP, NMEL)
    F = frame_feats(x, fb, dct)
    win, hop = int(WSEG * 100), int(WHOP * 100)
    # energy-based VAD on the log-energy column
    e = F[:, 0]
    thr = np.percentile(e, 15) + 0.5 * (np.percentile(e, 90) - np.percentile(e, 15))
    segs, feats = [], []
    for i in range(0, len(F) - win, hop):
        sl = F[i:i + win]
        m = e[i:i + win] > thr
        if m.sum() < 0.3 * win:
            continue
        segs.append((i * HOP / SR, (i + win) * HOP / SR))
        feats.append(sl[m, 1:].mean(0))
    X = np.array(feats)
    X = (X - X.mean(0)) / (X.std(0) + 1e-6)
    C, lab = kmeans(X, k)
    d = ((X[:, None] - C[None]) ** 2).sum(-1)
    path = viterbi(d / d.std(), pen=6.0)
    out, cur, start = [], int(path[0]), segs[0][0]
    for (s, e2), p in zip(segs[1:], path[1:]):
        if p != cur:
            out.append({"start": round(start, 2), "end": round(s, 2), "spk": cur})
            cur, start = int(p), s
    out.append({"start": round(start, 2), "end": round(segs[-1][1], 2), "spk": cur})
    # merge slivers
    merged = []
    for s in out:
        if merged and (s["end"] - s["start"] < 0.4):
            continue
        merged.append(s)
    json.dump({"hop": WHOP, "n": len(path), "labels": path.tolist(), "segments": merged},
              open(dst, "w"), ensure_ascii=False)
    print(f"{len(merged)} segments, k={k}, share:", np.bincount(path) / len(path))


if __name__ == "__main__":
    main()
