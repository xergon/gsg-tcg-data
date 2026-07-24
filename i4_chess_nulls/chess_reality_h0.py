#!/usr/bin/env python3
"""
CHESS REALITY-SIDE de-sharpening scale h0 — model-INDEPENDENT, from raw public games.
Cross-substrate sharpness law (idea #1), world-model arena, "universal chess reality" object.
Author: Schrodinger's Cat (physics lane), 2026-06-29.

FROZEN OBSERVABLE (pre-registered in this header, before seeing numbers; no target to tune to):
- Reads PGN games from stdin (streamed Lichess standard DB, public CC0).
- Move token M = from_square*64 + to_square (0..4095; promotion piece ignored).
- COMMON-SUPPORT PANEL: only ply positions t in a game with t + max(HORIZONS) < len(game)
  -> every horizon h is measured on the SAME anchored positions (fixes the support-collapse
  that broke the first WM artifact). Report N (= number of such anchored positions).
- PRIMARY sharpness observable (predictive-information decay, model-free):
    I(h) = MI( M_t ; M_{t+h} )  [mutual information between the move now and the move h plies ahead]
    S(h) = I(h) / I(1)          [normalized: S(1)=1, decays toward floor S_inf]
    fit  S(h) = S_inf + (1 - S_inf) * exp( -(h-1)/h0 ),  h0 = de-sharpening scale (plies).
  Rationale: I(h) measures how much the present actualized move constrains the future move;
  its e-folding horizon h0 is the chess analogue of Zeno tau_U / weak-meas R_U / WM latent L_corr.
- ALL entropies Miller-Madow bias-corrected:  H_MM = H_plugin + (K_obs - 1)/(2N).
- SANITY: also report H_R(h) = H(M_{t+h} | M_t) [should INCREASE toward H_inf with h; the first
  buggy WM run had it DECREASING] and H_inf = marginal move entropy H(M).
- CI: bootstrap over GAMES (resample whole games), per the spec (independent, no cross-arena coupling).
- NO model, NO GPU, NO claim. This produces ONE arena row (reality-side h0 + CI) for the prereg ledger.
"""
import sys, json, io, math
import numpy as np

try:
    import chess, chess.pgn
except Exception as e:
    sys.stderr.write("python-chess missing: %r\n" % e); sys.exit(2)

HORIZONS = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32]
HMAX = max(HORIZONS)
MAX_GAMES = int(sys.argv[1]) if len(sys.argv) > 1 else 25000
MIN_PLIES = HMAX + 4          # game must be long enough to give >=4 anchored positions
N_BOOT = int(sys.argv[2]) if len(sys.argv) > 2 else 120
RNG = np.random.default_rng(20260629)

def mm_entropy(counts):
    """Miller-Madow corrected Shannon entropy (nats) from an array of integer counts."""
    counts = counts[counts > 0]
    N = counts.sum()
    if N <= 1: return 0.0
    p = counts / N
    H = -np.sum(p * np.log(p))
    K = counts.size
    return H + (K - 1) / (2.0 * N)

def mi_from_pairs(a, b):
    """Miller-Madow corrected mutual information I(A;B) in nats from paired id arrays a,b."""
    if a.size < 2: return 0.0
    Ka = a.max() + 1; Kb = b.max() + 1
    Ha = mm_entropy(np.bincount(a, minlength=Ka))
    Hb = mm_entropy(np.bincount(b, minlength=Kb))
    joint = a.astype(np.int64) * Kb + b.astype(np.int64)
    Hab = mm_entropy(np.bincount(joint))
    return max(0.0, Ha + Hb - Hab)

def cond_entropy(a, b):
    """H(B|A) = H(A,B) - H(A), MM-corrected."""
    if a.size < 2: return 0.0
    Kb = b.max() + 1
    Ha = mm_entropy(np.bincount(a, minlength=a.max()+1))
    joint = a.astype(np.int64) * Kb + b.astype(np.int64)
    Hab = mm_entropy(np.bincount(joint))
    return Hab - Ha

# ---- stream + collect per-game anchored (M_t, M_{t+h}) observations ----
# Per game store: list over anchored positions of [M_t, M_{t+1}, M_{t+2}, ... for each horizon]
games = []          # each entry: np.array shape (n_anchor, 1+len(HORIZONS)) of move tokens [M_t, M_{t+h1}, ...]
n_games = 0; n_parsed = 0
stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="ignore")
while n_games < MAX_GAMES:
    try:
        g = chess.pgn.read_game(stdin)
    except Exception:
        break
    if g is None:
        break
    n_parsed += 1
    moves = []
    node = g
    try:
        for mv in g.mainline_moves():
            moves.append(mv.from_square * 64 + mv.to_square)
    except Exception:
        continue
    L = len(moves)
    if L < MIN_PLIES:
        continue
    mv = np.asarray(moves, dtype=np.int64)
    last_anchor = L - HMAX            # t ranges [0, last_anchor)
    if last_anchor < 4:
        continue
    cols = [mv[0:last_anchor]]                       # M_t
    for h in HORIZONS:
        cols.append(mv[h:last_anchor + h])           # M_{t+h}
    arr = np.stack(cols, axis=1)                     # (n_anchor, 1+len(HORIZONS))
    games.append(arr)
    n_games += 1

if n_games < 50:
    print(json.dumps({"error": "too few games parsed", "n_games": n_games, "n_parsed": n_parsed}))
    sys.exit(1)

allarr = np.concatenate(games, axis=0)               # (Ntot, 1+H)
Ntot = allarr.shape[0]

# Remap move tokens to DENSE ids (over all columns) for compact bincount
uniq = np.unique(allarr)
remap = {int(v): i for i, v in enumerate(uniq.tolist())}
dense = np.vectorize(lambda v: remap[int(v)])(allarr).astype(np.int64)
Kmoves = uniq.size

# point estimate
M_t = dense[:, 0]
H_inf = mm_entropy(np.bincount(M_t, minlength=Kmoves))   # marginal move entropy (max-entropy anchor)
I = {}; HR = {}
for j, h in enumerate(HORIZONS):
    M_th = dense[:, j + 1]
    I[h] = mi_from_pairs(M_t, M_th)
    HR[h] = cond_entropy(M_t, M_th)
I1 = I[1]
S = {h: (I[h] / I1 if I1 > 0 else float("nan")) for h in HORIZONS}

# PARITY: M_{t+h} for even h is the SAME side to move as M_t (own-move persistence);
# odd h is the opponent. The clean de-sharpening envelope is the same-side (even-h) series;
# the odd/even alternation is a chess nuisance with NO analogue in the quantum arenas, so the
# PRIMARY h0 is fit on the same-side envelope, anchored at the smallest same-side lag.
from scipy.optimize import curve_fit
EVEN_H = [h for h in HORIZONS if h % 2 == 0]
ODD_H  = [h for h in HORIZONS if h % 2 == 1]
H0_ANCHOR = EVEN_H[0]   # = 2

def fit_series(hlist, Svals, anchor):
    """Fit S(h)=S_inf+(1-S_inf)exp(-(h-anchor)/h0) to the given (h,S) series (S(anchor)=1)."""
    hh = np.array(hlist, float); yy = np.array(Svals, float)
    def m(h, S_inf, h0): return S_inf + (1.0 - S_inf) * np.exp(-(h - anchor) / h0)
    try:
        p, _ = curve_fit(m, hh, yy, p0=[0.3, 4.0], bounds=([0.0, 0.05], [1.0, 1e4]), maxfev=20000)
        sse = float(np.sum((yy - m(hh, *p))**2))
        return float(p[0]), float(p[1]), sse
    except Exception:
        return float("nan"), float("nan"), float("nan")

def sameside_S(mt, dcols):
    """given M_t array and dict h->M_{t+h} array, return same-side S list anchored at H0_ANCHOR."""
    Ia = mi_from_pairs(mt, dcols[H0_ANCHOR])
    if Ia <= 0: return None, Ia
    return [mi_from_pairs(mt, dcols[h]) / Ia for h in EVEN_H], Ia

colmap = {h: dense[:, j + 1] for j, h in enumerate(HORIZONS)}
S_even_vals, Ianchor = sameside_S(M_t, colmap)
S_inf_hat, h0_hat, sse = fit_series(EVEN_H, S_even_vals, H0_ANCHOR)
# full-series (secondary, parity-contaminated) for reference
S_inf_full, h0_full, sse_full = fit_series(HORIZONS, [S[h] for h in HORIZONS], 1)

# bootstrap over games on the PRIMARY same-side fit
boot_h0 = []; boot_Sinf = []
ng = len(games)
gsizes = np.array([g.shape[0] for g in games])
offsets = np.concatenate([[0], np.cumsum(gsizes)])
for b in range(N_BOOT):
    pick = RNG.integers(0, ng, size=ng)
    rows = np.concatenate([np.arange(offsets[i], offsets[i+1]) for i in pick])
    d = dense[rows]
    mt = d[:, 0]
    cm = {h: d[:, j + 1] for j, h in enumerate(HORIZONS)}
    sev, ia = sameside_S(mt, cm)
    if sev is None: continue
    si, h0b, _ = fit_series(EVEN_H, sev, H0_ANCHOR)
    if np.isfinite(h0b):
        boot_h0.append(h0b); boot_Sinf.append(si)

def ci(v):
    if len(v) < 5: return [float("nan"), float("nan")]
    return [float(np.percentile(v, 16)), float(np.percentile(v, 84))]  # 68% CI

out = {
    "arena": "chess world-model reality (universal, model-independent)",
    "source": "Lichess standard DB (public CC0), streamed sample",
    "n_games": n_games, "n_parsed": n_parsed, "N_anchored_positions": int(Ntot),
    "K_distinct_move_tokens": int(Kmoves),
    "horizons": HORIZONS,
    "H_inf_marginal_move_entropy_nats": round(H_inf, 6),
    "H_R_by_horizon_nats": {str(h): round(HR[h], 6) for h in HORIZONS},
    "H_R_monotone_increasing": bool(all(HR[HORIZONS[i]] <= HR[HORIZONS[i+1]] + 1e-9 for i in range(len(HORIZONS)-1))),
    "I_MI_by_horizon_nats": {str(h): round(I[h], 6) for h in HORIZONS},
    "S_by_horizon_full": {str(h): round(S[h], 6) for h in HORIZONS},
    "parity_note": "even h = same side to move as M_t (own-move persistence); odd h = opponent. Primary fit uses same-side envelope.",
    "even_horizons": EVEN_H,
    "S_sameside_anchored_at_%d" % H0_ANCHOR: {str(h): round(v, 6) for h, v in zip(EVEN_H, S_even_vals)},
    "fit_primary_sameside": {"S_inf": S_inf_hat, "h0_plies": h0_hat, "sse": sse,
                              "note": "h0 = same-side de-sharpening e-fold length in plies"},
    "fit_secondary_fullseries": {"S_inf": S_inf_full, "h0_plies": h0_full, "sse": sse_full,
                                  "note": "parity-contaminated; reference only"},
    "bootstrap_primary_sameside": {
        "n_boot_valid": len(boot_h0),
        "h0_plies_median": float(np.median(boot_h0)) if boot_h0 else float("nan"),
        "h0_plies_CI68": ci(boot_h0),
        "S_inf_median": float(np.median(boot_Sinf)) if boot_Sinf else float("nan"),
        "S_inf_CI68": ci(boot_Sinf),
    },
}
print(json.dumps(out, indent=2))
