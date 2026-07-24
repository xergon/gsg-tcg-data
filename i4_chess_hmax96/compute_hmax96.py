#!/usr/bin/env python3
"""
i4 HMAX=96 rerun -- STAGE 2: the June-29 estimator family, evaluated at HMAX=96.

ESTIMATOR INHERITED VERBATIM from chess_reality_h0.py (2026-06-29):
  * Miller-Madow corrected Shannon entropy   H_MM = H_plugin + (K_observed - 1)/(2N)
  * MI  I(h) = H(M_t) + H(M_{t+h}) - H(M_t, M_{t+h}), all three MM-corrected
    (June-29 additionally clamped at 0: I = max(0, .); we report BOTH the unclamped
     MM value and the June-29 clamped value, plus the uncorrected plugin value)
  * COMMON-SUPPORT anchored panel: t in [0, L - HMAX) so every horizon is measured on the
    SAME anchor positions.  MIN_PLIES = HMAX + 4.
  * bootstrap over whole GAMES.
Only HMAX changes (32 -> 96), plus three extra conditions and three extra observables.

CONDITIONS
  REAL                                      : sequences untouched
  WITHIN_GAME_SCRAMBLE                      : uniform permutation of all plies within a game
                                              (June-29 'scramble' null)
  EXACT_TARGET_MARGINAL_PERMUTATION         : real anchor column; the target column M_{t+h}
                                              is permuted uniformly across the WHOLE pooled
                                              panel -> target marginal preserved EXACTLY,
                                              all dependence destroyed.  This measures the
                                              residual estimator bias floor at matched N and
                                              matched marginals.
  PARITY_PRESERVING_WITHIN_GAME_SCRAMBLE    : within a game, even-index plies are permuted
                                              among themselves and odd-index plies among
                                              themselves (side-to-move structure preserved)

DERIVED  T(h) := I_MM(REAL, h) - I_MM(EXACT_TARGET_MARGINAL_PERMUTATION, h)      [nats]
  i.e. bias-floor-subtracted predictive information.  (T is also reported for the other
  conditions, as cond - targetperm, as a diagnostic.)  Unclamped MM values are used so T can
  legitimately go negative.  Cat states this definition explicitly; it is NOT taken from i4.

usage: python3 compute_hmax96.py PERIOD NGAMES TAG OUTDIR NBOOT
"""
import sys, os, json, time
import numpy as np

PERIOD = sys.argv[1]
NGAMES = sys.argv[2]                 # int, or "all"
TAG    = sys.argv[3]                 # "matched" | "power"
OUTDIR = sys.argv[4]
NBOOT  = int(sys.argv[5])

HMAX = 96
HORIZONS = list(range(8, HMAX + 1, 4))          # 8,12,...,96 ; all even => same side to move
GRID_I4  = [8, 12, 16, 24, 32, 40, 48, 64, 80, 96]
CONDS = ["REAL", "WITHIN_GAME_SCRAMBLE", "EXACT_TARGET_MARGINAL_PERMUTATION",
         "PARITY_PRESERVING_WITHIN_GAME_SCRAMBLE"]
CSHORT = {"REAL": "real", "WITHIN_GAME_SCRAMBLE": "scramble",
          "EXACT_TARGET_MARGINAL_PERMUTATION": "targetperm",
          "PARITY_PRESERVING_WITHIN_GAME_SCRAMBLE": "parityscramble"}
OBS = ["fromto", "san_canon", "san_matkey", "san_statekey"]
OSHORT = {"fromto": "fromto", "san_canon": "sancanon",
          "san_matkey": "sanmatkey", "san_statekey": "sanstatekey"}
BOOT_OBS = ["fromto", "san_canon"]              # small-alphabet observables only

CTRL_RNG = np.random.default_rng(20260630)      # June-29 null-control seed
BOOT_RNG = np.random.default_rng(20260629)      # June-29 bootstrap seed

LOG = open(os.path.join(OUTDIR, "parse_log.txt"), "a", buffering=1)
def log(m):
    LOG.write("[%s][%s/%s] %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                    PERIOD, TAG, m))

# ------------------------------------------------------------------ estimator (June-29)
def mm_entropy(counts):
    """returns (H_plugin, H_MillerMadow) in nats from integer counts"""
    counts = counts[counts > 0]
    N = counts.sum()
    if N <= 1:
        return 0.0, 0.0
    p = counts / N
    H = float(-np.sum(p * np.log(p)))
    K = counts.size
    return H, H + (K - 1) / (2.0 * N)

def _joint_counts(a, b, K):
    j = a.astype(np.int64) * K + b.astype(np.int64)
    if K * K <= 20_000_000:
        return np.bincount(j, minlength=K * K)
    return np.unique(j, return_counts=True)[1]

def mi_stats(a, b, K):
    """MI and conditional entropy on dense ids in [0,K).  Returns dict."""
    ca = np.bincount(a, minlength=K)
    cb = np.bincount(b, minlength=K)
    Ha_p, Ha = mm_entropy(ca)
    Hb_p, Hb = mm_entropy(cb)
    cj = _joint_counts(a, b, K)
    Hab_p, Hab = mm_entropy(cj)
    return {"I_plugin": Ha_p + Hb_p - Hab_p,
            "I_MM": Ha + Hb - Hab,
            "I_MM_clamped_june29": max(0.0, Ha + Hb - Hab),
            "H_anchor_MM": Ha, "H_target_MM": Hb, "H_joint_MM": Hab,
            "H_R_cond_MM": Hab - Ha,
            "K_anchor_obs": int((ca > 0).sum()), "K_target_obs": int((cb > 0).sum()),
            "K_joint_obs": int((cj > 0).sum())}

def mi_MM_only(a, b, K):
    ca = np.bincount(a, minlength=K); cb = np.bincount(b, minlength=K)
    _, Ha = mm_entropy(ca); _, Hb = mm_entropy(cb)
    _, Hab = mm_entropy(_joint_counts(a, b, K))
    return Ha + Hb - Hab

# ------------------------------------------------------------------ load
t0 = time.time()
z = np.load(os.path.join(OUTDIR, "tokens_%s.npz" % PERIOD))
lengths_all = z["lengths"]; offsets_all = z["offsets"]
ng_all = lengths_all.size
ng = ng_all if NGAMES == "all" else min(int(NGAMES), ng_all)
lengths = lengths_all[:ng]
offsets = np.concatenate([[0], np.cumsum(lengths)])
total_plies = int(offsets[-1])
log("loaded ng_all=%d using ng=%d total_plies=%d" % (ng_all, ng, total_plies))

game_id = np.repeat(np.arange(ng), lengths)
pos_in_game = np.arange(total_plies) - offsets[game_id]

# anchored panel row indices (common support at HMAX)
n_anchor = lengths - HMAX
assert (n_anchor >= 4).all()
anchor_idx = (np.repeat(offsets[:-1], n_anchor)
              + (np.arange(int(n_anchor.sum())) - np.repeat(np.concatenate([[0], np.cumsum(n_anchor)[:-1]]), n_anchor)))
N_panel = anchor_idx.size
panel_game = np.repeat(np.arange(ng), n_anchor)
p_off = np.concatenate([[0], np.cumsum(n_anchor)])
log("panel rows N=%d (mean %.1f anchors/game)" % (N_panel, N_panel / ng))

# ------------------------------------------------------------------ within-game scrambles
def within_game_permutation():
    r = CTRL_RNG.random(total_plies)
    return np.lexsort((r, game_id))

def parity_preserving_permutation():
    r = CTRL_RNG.random(total_plies)
    par = (pos_in_game & 1)
    src = np.lexsort((r, par, game_id))            # random order within (game, parity)
    dst = np.lexsort((pos_in_game, par, game_id))  # slots in order within (game, parity)
    perm = np.empty(total_plies, dtype=np.int64)
    perm[dst] = src
    return perm

PERM_SCRAMBLE = within_game_permutation()
PERM_PARITY = parity_preserving_permutation()

# ------------------------------------------------------------------ main loop
results = {}     # (cond, obs) -> {h: stats}
alpha = {}
DENSE_CACHE = {}
for ob in OBS:
    raw = z[ob][:total_plies]
    uniq, dense = np.unique(raw, return_inverse=True)
    dense = dense.astype(np.int64)
    K = uniq.size
    alpha[ob] = K
    if ob in BOOT_OBS:
        DENSE_CACHE[ob] = (dense, K)
    log("observable %s: alphabet K=%d over %d plies" % (ob, K, total_plies))
    seqs = {"REAL": dense,
            "WITHIN_GAME_SCRAMBLE": dense[PERM_SCRAMBLE],
            "PARITY_PRESERVING_WITHIN_GAME_SCRAMBLE": dense[PERM_PARITY]}
    for cond in CONDS:
        res = {}
        if cond == "EXACT_TARGET_MARGINAL_PERMUTATION":
            a = dense[anchor_idx]
            for h in HORIZONS:
                b = dense[anchor_idx + h]
                b = b[CTRL_RNG.permutation(N_panel)]
                res[h] = mi_stats(a, b, K)
                res[h]["I_MM_own_targetperm_floor"] = res[h]["I_MM"]
        else:
            s = seqs[cond]
            a = s[anchor_idx]
            for h in HORIZONS:
                b = s[anchor_idx + h]
                res[h] = mi_stats(a, b, K)
                # each condition gets its OWN exact-target-marginal permutation floor,
                # because scrambling changes the anchor marginal and hence the bias floor
                res[h]["I_MM_own_targetperm_floor"] = mi_MM_only(a, b[CTRL_RNG.permutation(N_panel)], K)
        results[(cond, ob)] = res
        log("  done %s / %s  (%.1fs)" % (cond, ob, time.time() - t0))

# ------------------------------------------------------------------ bootstrap SE of T (REAL - TARGETPERM)
boot = {}
for ob in BOOT_OBS:
    dense, K = DENSE_CACHE[ob]
    Tb = {h: [] for h in HORIZONS}
    for bi in range(NBOOT):
        pick = BOOT_RNG.integers(0, ng, size=ng)
        sz = n_anchor[pick]
        tot = int(sz.sum())
        starts = p_off[pick]
        rows_local = (np.arange(tot)
                      - np.repeat(np.concatenate([[0], np.cumsum(sz)[:-1]]), sz))
        rows = np.repeat(starts, sz) + rows_local
        ai = anchor_idx[rows]
        a = dense[ai]
        pp = BOOT_RNG.permutation(tot)
        for h in HORIZONS:
            tgt = dense[ai + h]
            Tb[h].append(mi_MM_only(a, tgt, K) - mi_MM_only(a, tgt[pp], K))
        if (bi + 1) % 10 == 0:
            log("  boot %s %d/%d (%.1fs)" % (ob, bi + 1, NBOOT, time.time() - t0))
    boot[ob] = {h: (float(np.mean(v)), float(np.std(v, ddof=1))) for h, v in Tb.items()}

# ------------------------------------------------------------------ emit
meta_common = {
    "run_tag": TAG, "period": PERIOD, "HMAX": HMAX,
    "horizons_computed": HORIZONS, "horizons_requested_by_i4": GRID_I4,
    "n_games": int(ng), "n_games_available": int(ng_all),
    "N_anchored_positions": int(N_panel),
    "MIN_PLIES": HMAX + 4,
    "bias_correction_in_force": "Miller-Madow  H_MM = H_plugin + (K_observed-1)/(2N)  "
                                "(inherited verbatim from chess_reality_h0.py 2026-06-29)",
    "estimator_source": "implementation_lanes/temporal_unsharpness/chess_reality_h0_2026_06_29/chess_reality_h0.py",
    "control_rng_seed": 20260630, "bootstrap_rng_seed": 20260629, "n_boot": NBOOT,
    "T_definition_by_cat": "T(h) = I_MM(condition,h) - I_MM(EXACT_TARGET_MARGINAL_PERMUTATION,h), "
                           "unclamped Miller-Madow MI, nats. Cat's stated definition, not i4's.",
}

csv_rows = []
for ob in OBS:
    perm_res = results[("EXACT_TARGET_MARGINAL_PERMUTATION", ob)]
    for cond in CONDS:
        res = results[(cond, ob)]
        T = {h: res[h]["I_MM"] - perm_res[h]["I_MM"] for h in HORIZONS}
        Town = {h: res[h]["I_MM"] - res[h]["I_MM_own_targetperm_floor"] for h in HORIZONS}
        ratio = {}
        ratio_own = {}
        for h in HORIZONS:
            if (h + 8) in T and T[h + 8] != 0:
                ratio[h] = T[h] / T[h + 8]
            if (h + 8) in Town and Town[h + 8] != 0:
                ratio_own[h] = Town[h] / Town[h + 8]
        obj = dict(meta_common)
        obj.update({
            "condition": cond, "observable": ob,
            "observable_note": {
                "fromto": "from_square*64+to_square (June-29 original token)",
                "san_canon": "SAN content on a colour-canonical board: (piece, destination mirrored "
                             "into the mover's frame, capture, promotion, castling)",
                "san_matkey": "san_canon tensored with the COARSE canonical board-state hash "
                              "(material key: P,N,B,R,Q counts for mover and opponent)",
                "san_statekey": "san_canon tensored with the FULL canonical board-state hash "
                                "(python-chess transposition key: piece bitboards, side to move, "
                                "castling rights, en-passant)",
            }[ob],
            "alphabet_K_total": int(alpha[ob]),
            "estimates_by_horizon": {str(h): {k: (round(v, 6) if isinstance(v, float) else v)
                                              for k, v in res[h].items()} for h in HORIZONS},
            "T_by_horizon_nats": {str(h): round(T[h], 6) for h in HORIZONS},
            "T_ratio_h_over_h_plus_8": {str(h): round(ratio[h], 6) for h in sorted(ratio)},
            "T_vs_OWN_floor_by_horizon_nats": {str(h): round(Town[h], 6) for h in HORIZONS},
            "T_vs_OWN_floor_ratio_h_over_h_plus_8": {str(h): round(ratio_own[h], 6) for h in sorted(ratio_own)},
            "T_floor_note": "T_by_horizon_nats uses the REAL panel's EXACT_TARGET_MARGINAL_PERMUTATION "
                            "floor for every condition (i4's literal condition list). "
                            "T_vs_OWN_floor uses each condition's own permutation floor, which is the "
                            "correct comparison for the scrambles because scrambling changes the anchor "
                            "marginal and therefore the estimator bias floor. For REAL the two are identical.",
        })
        if cond == "REAL" and ob in boot:
            obj["T_bootstrap_over_games"] = {
                str(h): {"mean": round(boot[ob][h][0], 6), "sd": round(boot[ob][h][1], 6)}
                for h in HORIZONS}
        fn = "%s_%s_%s%s.json" % (CSHORT[cond], OSHORT[ob], PERIOD,
                                  "" if TAG == "matched" else "_power")
        with open(os.path.join(OUTDIR, fn), "w") as f:
            json.dump(obj, f, indent=2)
        for h in HORIZONS:
            r = res[h]
            csv_rows.append([TAG, PERIOD, cond, ob, h, int(h in GRID_I4), ng, N_panel,
                             alpha[ob],
                             "%.6f" % r["I_plugin"], "%.6f" % r["I_MM"],
                             "%.6f" % r["I_MM_clamped_june29"], "%.6f" % r["H_R_cond_MM"],
                             "%.6f" % T[h],
                             ("%.6f" % boot[ob][h][1]) if (cond == "REAL" and ob in boot) else "",
                             ("%.6f" % ratio[h]) if h in ratio else "",
                             "%.6f" % r["I_MM_own_targetperm_floor"], "%.6f" % Town[h],
                             ("%.6f" % ratio_own[h]) if h in ratio_own else ""])

with open(os.path.join(OUTDIR, "rows_%s_%s.csv" % (PERIOD, TAG)), "w") as f:
    f.write("run,period,condition,observable,h,in_i4_grid,n_games,N_anchored,alphabet_K,"
            "I_plugin_nats,I_MM_nats,I_MM_clamped_june29_nats,H_R_cond_MM_nats,"
            "T_vs_targetperm_nats,T_boot_sd_nats,T_ratio_h_over_h_plus_8,"
            "I_MM_own_targetperm_floor_nats,T_vs_own_floor_nats,T_own_ratio_h_over_h_plus_8\n")
    for r in csv_rows:
        f.write(",".join(str(x) for x in r) + "\n")
log("EMIT DONE wall=%.1fs" % (time.time() - t0))
print(json.dumps({"period": PERIOD, "tag": TAG, "n_games": int(ng),
                  "N_panel": int(N_panel), "wall_s": round(time.time() - t0, 1),
                  "alphabets": {k: int(v) for k, v in alpha.items()}}))
