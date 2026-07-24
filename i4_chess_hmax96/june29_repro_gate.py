#!/usr/bin/env python3
"""
REPRODUCTION GATE + bias-floor probe on the ORIGINAL June-29 configuration.

Purpose 1 (gate): re-run the June-29 setup exactly (HMAX=32, MIN_PLIES=36, first 30000
  qualifying games, fromto token) with THIS re-implementation of the estimator and check the
  I_MM(h) values against the published result_2014-07.json / result_2016-01.json.  If they do
  not reproduce, the HMAX=96 numbers are not the same estimator family and must not ship.

Purpose 2 (probe): measure the EXACT_TARGET_MARGINAL_PERMUTATION bias floor at the June-29
  horizons, so the "fraction of the tail signal that is estimator bias" can be stated for the
  earlier run (i4 quotes ~44.5%).

usage: zstdcat X.pgn.zst | python3 june29_repro_gate.py PERIOD OUTDIR
"""
import sys, os, re, json, time
import numpy as np
import chess

PERIOD, OUTDIR = sys.argv[1], sys.argv[2]
HORIZONS = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32]
HMAX = 32
MIN_PLIES = HMAX + 4
MAX_GAMES = 30000
CTRL_RNG = np.random.default_rng(20260630)

TOKCLEAN = re.compile(r"\{[^}]*\}|\$\d+|\d+\.(?:\.\.)?|[?!]+|\([^)]*\)")
RESULTS = ("1-0", "0-1", "1/2-1/2", "*")

def mm_entropy(counts):
    counts = counts[counts > 0]; N = counts.sum()
    if N <= 1: return 0.0, 0.0
    p = counts / N
    H = float(-np.sum(p * np.log(p)))
    return H, H + (counts.size - 1) / (2.0 * N)

def mi(a, b, K):
    ca = np.bincount(a, minlength=K); cb = np.bincount(b, minlength=K)
    _, Ha = mm_entropy(ca); _, Hb = mm_entropy(cb)
    _, Hab = mm_entropy(np.bincount(a * K + b, minlength=K * K))
    return Ha + Hb - Hab

t0 = time.time()
seqs = []; n_games = 0; n_scanned = 0; n_bad = 0
stdin = sys.stdin.buffer; remainder = b""; buf = []; inmv = False; done = False

def handle(gtext):
    global n_games, n_bad
    toks = [x for x in TOKCLEAN.sub(" ", gtext).split() if x not in RESULTS]
    if len(toks) < MIN_PLIES: return
    b = chess.Board(); out = np.empty(len(toks), dtype=np.int64)
    try:
        for i, s in enumerate(toks):
            mv = b.parse_san(s); out[i] = mv.from_square * 64 + mv.to_square; b.push(mv)
    except Exception:
        n_bad += 1; return
    seqs.append(out); n_games += 1

while not done:
    chunk = stdin.read(1 << 26)
    if not chunk: break
    data = (remainder + chunk).decode("utf-8", errors="ignore")
    nl = data.rfind("\n")
    if nl < 0: remainder = data.encode(); continue
    remainder = data[nl + 1:].encode("utf-8", errors="ignore")
    for ln in data[:nl].split("\n"):
        if ln.startswith("["):
            if inmv:
                n_scanned += 1; handle(" ".join(buf)); buf = []; inmv = False
                if n_games >= MAX_GAMES: done = True; break
        elif ln.strip():
            inmv = True; buf.append(ln)

lengths = np.array([s.size for s in seqs]); off = np.concatenate([[0], np.cumsum(lengths)])
flat = np.concatenate(seqs)
n_anchor = lengths - HMAX
anchor_idx = (np.repeat(off[:-1], n_anchor)
              + (np.arange(int(n_anchor.sum()))
                 - np.repeat(np.concatenate([[0], np.cumsum(n_anchor)[:-1]]), n_anchor)))
uniq, dense = np.unique(flat, return_inverse=True)
dense = dense.astype(np.int64); K = uniq.size
N = anchor_idx.size
a = dense[anchor_idx]
I_real = {}; I_perm = {}
for h in HORIZONS:
    b_ = dense[anchor_idx + h]
    I_real[h] = mi(a, b_, K)
    I_perm[h] = mi(a, b_[CTRL_RNG.permutation(N)], K)

pub = json.load(open("/Users/resorb/Documents/My Papers/Research Program Management/"
                     "implementation_lanes/temporal_unsharpness/chess_reality_h0_2026_06_29/"
                     "result_%s.json" % PERIOD.replace("-", "_")))
pubI = {int(k): v for k, v in pub["I_MI_by_horizon_nats"].items()}
out = {
    "period": PERIOD, "n_games": n_games, "n_scanned": n_scanned, "n_malformed": n_bad,
    "N_anchored": int(N), "K_alphabet": int(K),
    "published_N_anchored": pub["N_anchored_positions"],
    "published_K": pub["K_distinct_move_tokens"],
    "I_MM_reproduced": {str(h): round(I_real[h], 6) for h in HORIZONS},
    "I_MM_published_june29": {str(h): pubI[h] for h in HORIZONS},
    "max_abs_diff_vs_published": round(max(abs(I_real[h] - pubI[h]) for h in HORIZONS), 8),
    "I_MM_exact_target_marginal_permutation_biasfloor": {str(h): round(I_perm[h], 6) for h in HORIZONS},
    "bias_fraction_of_I": {str(h): round(I_perm[h] / I_real[h], 6) for h in HORIZONS},
    "T_june29_grid": {str(h): round(I_real[h] - I_perm[h], 6) for h in HORIZONS},
    "wall_s": round(time.time() - t0, 1),
}
with open(os.path.join(OUTDIR, "june29_repro_gate_%s.json" % PERIOD), "w") as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
