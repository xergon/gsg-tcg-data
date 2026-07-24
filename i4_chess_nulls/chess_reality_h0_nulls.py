#!/usr/bin/env python3
"""
CHESS REALITY-SIDE h0 — NULL CONTROLS (C4 scramble + random-successor).
Schrodinger's Cat (physics lane), staged 2026-06-30. STATUS: NOT EXECUTED — runnable on explicit C4 go.

WHY (cross-arena prereg honesty backstop):
  The keystone reality-side de-sharpening scale h0 ~ 3.8 plies (msg 616; baseline chess_reality_h0.py)
  is the ONLY delivered cross-substrate-sharpness arena. Before it can count toward the cross-arena
  kappa-reuse comparison it must survive two pre-registered null controls already named as controls in
  CROSS_ARENA_KAPPA_REUSE_PREREGISTRATION_v0_1.md and CROSS_ARENA_QUANTUM_KAPPA_EXTRACTION_RECIPE_BLIND_v0_1.md:

    (1) SCRAMBLE null  -> shuffle the move order WITHIN each game (same multiset of move tokens,
        temporal adjacency destroyed). Predictive information I(h)=MI(M_t;M_{t+h}) must collapse to
        the chance floor for ALL h>0, so the same-side S(h) envelope goes FLAT and the fit returns
        NO finite de-sharpening scale. PRE-REGISTERED EXPECTATION: h0 -> rail (>= 1e3 plies upper
        bound) AND/OR S_inf -> 1 (no decay). A finite h0 anywhere near the keystone band (2..8 plies)
        on scrambled data would mean the keystone is an artifact of the marginal/anchoring machinery,
        NOT of temporal order -> keystone KILLED.

    (2) RANDOM-SUCCESSOR null -> keep M_t real, replace each M_{t+h} with a token drawn i.i.d. from the
        EMPIRICAL MARGINAL move distribution (preserves move-token frequencies, destroys the M_t->M_{t+h}
        dependence). I(h) -> 0 by construction, so normalized S collapses toward 0 and H_R(h) -> H_inf
        immediately. PRE-REGISTERED EXPECTATION: S(h) ~ 0 for all h>=2; no recoverable finite h0.
        A surviving keystone-band h0 here would mean the estimator manufactures structure from marginals
        alone -> keystone KILLED.

  Both controls reuse the IDENTICAL estimator as the baseline (imported by file path below -> single
  source of truth, zero estimator drift). Only the (M_t, M_{t+h}) construction is altered, exactly at
  the documented intervention point. Same horizons, same Miller-Madow correction, same same-side parity
  fit, same bootstrap-over-games CI.

FROZEN BEFORE RUN (no target to tune to):
  - horizons, MIN_PLIES, fit form, MM-correction = inherited verbatim from chess_reality_h0.py.
  - control RNG seed = 20260630 (distinct from baseline 20260629); bootstrap seed inherited.
  - KEYSTONE BAND (for the kill test) = h0 in [2, 8] plies (brackets the reported ~3.8 +/- bootstrap).
  - PASS-AS-NULL (control behaves as a null, keystone SURVIVES) requires, per control:
        scramble:          fit_primary_sameside.h0_plies >= 1000  OR  S_inf >= 0.95
        random-successor:  all same-side S(h>=2) <= 0.05  (MI collapse)
  - FAIL-AS-NULL (control reproduces keystone-band structure) => KEYSTONE KILLED, must be reported.

NO model, NO GPU, NO claim, NO fit of any physical parameter. These are estimator null controls on
public CC0 Lichess PGN. Output is ONE JSON per control for the prereg ledger. Run ONLY on explicit C4 go.

USAGE (on go):
  zstdcat lichess_db_standard_rated_YYYY-MM.pgn.zst | \
     python3 chess_reality_h0_nulls.py scramble          [MAX_GAMES] [N_BOOT] > null_scramble.json
  zstdcat ... | python3 chess_reality_h0_nulls.py random-successor [MAX_GAMES] [N_BOOT] > null_randsucc.json
  (same input stream and MAX_GAMES as the baseline keystone run for a matched comparison.)
"""
import sys, os, io, json, importlib.util
import numpy as np

# ---- import the baseline estimator as the SINGLE SOURCE OF TRUTH (no re-implementation) ----
_HERE = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.join(_HERE, "chess_reality_h0.py")
# The baseline runs its stream loop at import time, so we load it as source and exec ONLY the
# function/constant defs we need (mm_entropy, mi_from_pairs, cond_entropy, fit_series, HORIZONS,
# HMAX, MIN_PLIES, H0_ANCHOR, EVEN_H, ci). We slice the module text up to the stream loop marker.
with open(_BASE, "r") as f:
    _src = f.read()
_cut = _src.index("# ---- stream + collect")           # everything below is the baseline's own run
_defs = _src[:_cut]
# strip the argv-driven constants we re-declare here; keep pure defs + estimator constants
_ns = {"np": np, "math": __import__("math"), "sys": sys}
# Provide stub argv so the baseline header constants resolve without consuming our argv
_save_argv = sys.argv
sys.argv = ["baseline"]
exec(compile(_defs, _BASE, "exec"), _ns)
sys.argv = _save_argv
# Pull curve_fit-based fit_series + EVEN_H/H0_ANCHOR from the lower half too (defined after the loop)
_post = _src[_src.index("from scipy.optimize import curve_fit"):_src.index("colmap = {")]
exec(compile(_post, _BASE, "exec"), _ns)

mm_entropy   = _ns["mm_entropy"]
mi_from_pairs= _ns["mi_from_pairs"]
cond_entropy = _ns["cond_entropy"]
fit_series   = _ns["fit_series"]
HORIZONS     = _ns["HORIZONS"]
HMAX         = _ns["HMAX"]
EVEN_H       = _ns["EVEN_H"]
H0_ANCHOR    = _ns["H0_ANCHOR"]

MIN_PLIES = HMAX + 4
MODE      = sys.argv[1] if len(sys.argv) > 1 else ""
MAX_GAMES = int(sys.argv[2]) if len(sys.argv) > 2 else 25000
N_BOOT    = int(sys.argv[3]) if len(sys.argv) > 3 else 120
CTRL_RNG  = np.random.default_rng(20260630)
BOOT_RNG  = np.random.default_rng(20260629)   # matched to baseline bootstrap

if MODE not in ("scramble", "random-successor"):
    sys.stderr.write("usage: chess_reality_h0_nulls.py {scramble|random-successor} [MAX_GAMES] [N_BOOT]\n")
    sys.exit(2)

try:
    import chess, chess.pgn
except Exception as e:
    sys.stderr.write("python-chess missing: %r\n" % e); sys.exit(2)

# ---- stream games; build per-game move token lists (identical parse to baseline) ----
raw_games = []
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
    try:
        for mv in g.mainline_moves():
            moves.append(mv.from_square * 64 + mv.to_square)
    except Exception:
        continue
    if len(moves) < MIN_PLIES:
        continue
    raw_games.append(np.asarray(moves, dtype=np.int64))
    n_games += 1

if n_games < 50:
    print(json.dumps({"error": "too few games parsed", "n_games": n_games, "n_parsed": n_parsed, "mode": MODE}))
    sys.exit(1)

# ---- apply the control intervention, then build anchored columns EXACTLY as baseline ----
def anchored_cols(mv):
    L = len(mv); last_anchor = L - HMAX
    if last_anchor < 4: return None
    cols = [mv[0:last_anchor]]
    for h in HORIZONS:
        cols.append(mv[h:last_anchor + h])
    return np.stack(cols, axis=1)

games = []
if MODE == "scramble":
    # destroy temporal order within each game (same multiset of tokens)
    for mv in raw_games:
        perm = CTRL_RNG.permutation(len(mv))
        arr = anchored_cols(mv[perm])
        if arr is not None: games.append(arr)
else:  # random-successor: real M_t, marginal-drawn successors
    # build empirical marginal over ALL move tokens first
    pool = np.concatenate(raw_games)
    for mv in raw_games:
        arr = anchored_cols(mv)
        if arr is None: continue
        # replace every successor column (cols 1..) with marginal i.i.d. draws; keep M_t (col 0)
        nrow = arr.shape[0]
        for j in range(1, arr.shape[1]):
            arr[:, j] = pool[CTRL_RNG.integers(0, pool.size, size=nrow)]
        games.append(arr)

allarr = np.concatenate(games, axis=0)
Ntot = allarr.shape[0]
uniq = np.unique(allarr)
remap = {int(v): i for i, v in enumerate(uniq.tolist())}
dense = np.vectorize(lambda v: remap[int(v)])(allarr).astype(np.int64)
Kmoves = uniq.size

M_t = dense[:, 0]
H_inf = mm_entropy(np.bincount(M_t, minlength=Kmoves))
I = {}; HR = {}
for j, h in enumerate(HORIZONS):
    M_th = dense[:, j + 1]
    I[h] = mi_from_pairs(M_t, M_th)
    HR[h] = cond_entropy(M_t, M_th)
I1 = I[1]
S = {h: (I[h] / I1 if I1 > 0 else float("nan")) for h in HORIZONS}

colmap = {h: dense[:, j + 1] for j, h in enumerate(HORIZONS)}
def sameside_S(mt, dcols):
    Ia = mi_from_pairs(mt, dcols[H0_ANCHOR])
    if Ia <= 0: return None, Ia
    return [mi_from_pairs(mt, dcols[h]) / Ia for h in EVEN_H], Ia
S_even_vals, Ianchor = sameside_S(M_t, colmap)
if S_even_vals is None:
    S_inf_hat, h0_hat, sse = float("nan"), float("nan"), float("nan")
else:
    S_inf_hat, h0_hat, sse = fit_series(EVEN_H, S_even_vals, H0_ANCHOR)

# bootstrap over games (matched to baseline)
boot_h0 = []; boot_Sinf = []
ng = len(games)
gsizes = np.array([g.shape[0] for g in games])
offsets = np.concatenate([[0], np.cumsum(gsizes)])
for b in range(N_BOOT):
    pick = BOOT_RNG.integers(0, ng, size=ng)
    rows = np.concatenate([np.arange(offsets[i], offsets[i+1]) for i in pick])
    d = dense[rows]; mt = d[:, 0]
    cm = {h: d[:, j + 1] for j, h in enumerate(HORIZONS)}
    sev, ia = sameside_S(mt, cm)
    if sev is None: continue
    si, h0b, _ = fit_series(EVEN_H, sev, H0_ANCHOR)
    if np.isfinite(h0b):
        boot_h0.append(h0b); boot_Sinf.append(si)

def ci(v):
    if len(v) < 5: return [float("nan"), float("nan")]
    return [float(np.percentile(v, 16)), float(np.percentile(v, 84))]

# pre-registered verdict logic
KEYSTONE_BAND = [2.0, 8.0]
if MODE == "scramble":
    behaves_as_null = (np.isfinite(h0_hat) and h0_hat >= 1000.0) or (np.isfinite(S_inf_hat) and S_inf_hat >= 0.95)
    reproduces_keystone = np.isfinite(h0_hat) and KEYSTONE_BAND[0] <= h0_hat <= KEYSTONE_BAND[1]
else:
    Smax = max([v for v in (S_even_vals or []) if np.isfinite(v)] + [float("nan")])
    behaves_as_null = np.isfinite(Smax) and Smax <= 0.05
    reproduces_keystone = np.isfinite(h0_hat) and KEYSTONE_BAND[0] <= h0_hat <= KEYSTONE_BAND[1]

out = {
    "arena": "chess world-model reality — NULL CONTROL",
    "mode": MODE,
    "source": "Lichess standard DB (public CC0), streamed sample",
    "control_rng_seed": 20260630,
    "n_games": n_games, "n_parsed": n_parsed, "N_anchored_positions": int(Ntot),
    "K_distinct_move_tokens": int(Kmoves),
    "horizons": HORIZONS, "keystone_band_plies": KEYSTONE_BAND,
    "H_inf_marginal_move_entropy_nats": round(H_inf, 6),
    "H_R_by_horizon_nats": {str(h): round(HR[h], 6) for h in HORIZONS},
    "I_MI_by_horizon_nats": {str(h): round(I[h], 6) for h in HORIZONS},
    "S_by_horizon_full": {str(h): round(S[h], 6) for h in HORIZONS},
    "S_sameside_anchored_at_%d" % H0_ANCHOR: None if S_even_vals is None else {str(h): round(v, 6) for h, v in zip(EVEN_H, S_even_vals)},
    "fit_primary_sameside": {"S_inf": S_inf_hat, "h0_plies": h0_hat, "sse": sse},
    "bootstrap_primary_sameside": {
        "n_boot_valid": len(boot_h0),
        "h0_plies_median": float(np.median(boot_h0)) if boot_h0 else float("nan"),
        "h0_plies_CI68": ci(boot_h0),
    },
    "PREREG_VERDICT": {
        "control_behaves_as_null": bool(behaves_as_null),
        "control_reproduces_keystone_band": bool(reproduces_keystone),
        "interpretation": ("KEYSTONE SURVIVES this control" if behaves_as_null and not reproduces_keystone
                           else "KEYSTONE KILLED — control reproduced keystone-band structure" if reproduces_keystone
                           else "INCONCLUSIVE — control neither cleanly nulled nor reproduced keystone; inspect S/H_R"),
    },
}
print(json.dumps(out, indent=2))
