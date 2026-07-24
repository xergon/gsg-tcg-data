#!/usr/bin/env python3
"""
T3 gamma-stratified held-out entropy reduction -- PASS 2.

Consumes pass-1 chunks, freezes the |gamma| tercile cut points FIRST (written to
tercile_cutpoints.json before any horizon is computed), then computes the
odd/even held-out conditional cross-entropy curves E(n), q(n) and the horizon
H_clicks = n_{1/e} - 1, per rat and pooled, per |gamma| tercile, plus the two
controls T3 named.
"""
import os, sys, json, time, glob, warnings
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)

WORK = sys.argv[1]
CHUNKS = os.path.join(WORK, "chunks")
NMAX = 20
NBIN = 2 * NMAX + 1                 # D in [-20, 20]
MIN_TRIALS_PER_RAT = 200
MIN_RATS = 30
SEED = 20260724
NBOOT = 2000
N_SHUFFLE_SEEDS = 5
INV_E = float(np.exp(-1.0))

t_start = time.time()

# ------------------------------------------------------------------ load ---
files = sorted(glob.glob(os.path.join(CHUNKS, "chunk_*.npz")))
assert files, "no chunks"
acc = {k: [] for k in ("rat", "parity", "choice", "gamma", "reward_rule",
                       "trial_idx", "D")}
for f in files:
    z = np.load(f)
    for k in acc:
        acc[k].append(z[k])
rat = np.concatenate(acc["rat"]).astype(np.int64)
parity = np.concatenate(acc["parity"]).astype(np.int64)
choice = np.concatenate(acc["choice"]).astype(np.float64)
gamma = np.concatenate(acc["gamma"])
rr = np.concatenate(acc["reward_rule"])
tidx = np.concatenate(acc["trial_idx"])
D = np.concatenate(acc["D"])
del acc
print(f"loaded {len(rat):,} qualifying trials, {time.time()-t_start:.0f}s", flush=True)

# --------------------------------------------------- rat qualification -----
n_codes = int(rat.max()) + 1
cnt_per_rat = np.bincount(rat, minlength=n_codes)
qual_rats = np.where(cnt_per_rat >= MIN_TRIALS_PER_RAT)[0]
R = len(qual_rats)
assert R >= MIN_RATS, f"only {R} qualifying rats (< {MIN_RATS})"
keep = np.isin(rat, qual_rats)
rat, parity, choice = rat[keep], parity[keep], choice[keep]
gamma, rr, tidx, D = gamma[keep], rr[keep], tidx[keep], D[keep]
remap = -np.ones(n_codes, dtype=np.int64); remap[qual_rats] = np.arange(R)
rat = remap[rat]
N = len(rat)
print(f"qualifying rats={R}  qualifying trials={N:,}", flush=True)

# ------------------- STEP A: FREEZE THE TERCILE CUT POINTS (before horizons)
absg = np.abs(gamma.astype(np.float64))
cut1, cut2 = np.quantile(absg, [1.0 / 3.0, 2.0 / 3.0])
terc = np.where(absg <= cut1, 0, np.where(absg <= cut2, 1, 2)).astype(np.int64)
tcounts = np.bincount(terc, minlength=3)
uniq, ucnt = np.unique(np.round(absg, 6), return_counts=True)
o = np.argsort(-ucnt)
cutinfo = {
    "definition": "global terciles of |gamma| over the qualifying trials of qualifying rats",
    "cut1_abs_gamma_q33": float(cut1),
    "cut2_abs_gamma_q67": float(cut2),
    "assignment_rule": "T_low: |g| <= cut1 ; T_mid: cut1 < |g| <= cut2 ; T_high: |g| > cut2",
    "tercile_trial_counts": [int(x) for x in tcounts],
    "tercile_fractions": [float(x) / N for x in tcounts],
    "abs_gamma_min": float(absg.min()), "abs_gamma_max": float(absg.max()),
    "abs_gamma_mean": float(absg.mean()), "abs_gamma_median": float(np.median(absg)),
    "n_unique_abs_gamma_6dp": int(len(uniq)),
    "top20_abs_gamma_values_by_count": [[float(uniq[i]), int(ucnt[i])] for i in o[:20]],
    "per_tercile_abs_gamma_range": [[float(absg[terc == k].min()),
                                     float(absg[terc == k].max())] for k in range(3)],
    "per_tercile_abs_gamma_mean": [float(absg[terc == k].mean()) for k in range(3)],
    "per_tercile_abs_gamma_median": [float(np.median(absg[terc == k])) for k in range(3)],
    "n_qualifying_rats": int(R), "n_qualifying_trials": int(N),
}
with open(os.path.join(WORK, "tercile_cutpoints.json"), "w") as f:
    json.dump(cutinfo, f, indent=1)
print("=== TERCILE CUT POINTS FROZEN ===")
print(json.dumps({k: cutinfo[k] for k in
                  ("cut1_abs_gamma_q33", "cut2_abs_gamma_q67",
                   "tercile_trial_counts", "per_tercile_abs_gamma_range",
                   "per_tercile_abs_gamma_mean")}, indent=1), flush=True)

# --------------------------------------------------------------- machinery -
rr1 = (rr == 1).astype(np.int64)
fold = parity                                  # 0 = even trial_idx, 1 = odd
Dp = D.astype(np.int64) + NMAX
BASE = ((((rat * 3 + terc) * 2 + rr1) * 2 + fold) * NMAX) * NBIN
SHAPE = (R, 3, 2, 2, NMAX, NBIN)
SZ = int(np.prod(SHAPE))


def accumulate(ch):
    tot = np.zeros(SZ, dtype=np.float64)
    pos = np.zeros(SZ, dtype=np.float64)
    for n in range(NMAX):
        idx = BASE + n * NBIN + Dp[:, n]
        tot += np.bincount(idx, minlength=SZ)
        pos += np.bincount(idx, weights=ch, minlength=SZ)
    return tot.reshape(SHAPE), pos.reshape(SHAPE)


def cell(tot, pos, tsel, rsel):
    """-> t,p arrays [R, fold, n, d] for the selected terciles / reward rules."""
    t = tot[:, tsel][:, :, rsel].sum(axis=(1, 2))
    p = pos[:, tsel][:, :, rsel].sum(axis=(1, 2))
    return t, p


def ce_folds(t, p, folds):
    """Held-out cross-entropy in bits, summed over held-out trials.
    folds: iterable of held-out fold ids. Returns CE[R,n], Nho[R,n]."""
    CE = np.zeros((t.shape[0], NMAX)); NH = np.zeros((t.shape[0], NMAX))
    for f in folds:
        tr_t, tr_p = t[:, 1 - f], p[:, 1 - f]
        ho_t, ho_p = t[:, f], p[:, f]
        ph = np.clip((tr_p + 0.5) / (tr_t + 1.0), 1e-15, 1 - 1e-15)
        CE += -(ho_p * np.log2(ph) + (ho_t - ho_p) * np.log2(1.0 - ph)).sum(axis=-1)
        NH += ho_t.sum(axis=-1)
    return CE, NH


def horizon_from_E(E):
    """T3's frozen definition: q(n)=(E(n)-E(20))/(E(1)-E(20));
    H = n_{1/e} - 1 with n_{1/e} linearly interpolated at the FIRST crossing."""
    E = np.asarray(E, dtype=np.float64)
    den = E[0] - E[-1]
    if not np.isfinite(den) or den <= 0:
        return np.nan, np.full(NMAX, np.nan), float(den) if np.isfinite(den) else np.nan
    q = (E - E[-1]) / den
    for i in range(1, NMAX):
        if q[i] <= INV_E:
            q0, q1 = q[i - 1], q[i]
            frac = (q0 - INV_E) / (q0 - q1) if q0 != q1 else 0.0
            return float(i + frac - 1.0), q, float(den)
    return np.nan, q, float(den)


def analyse(tot, pos, tsel, rsel, label, ratmask=None):
    t, p = cell(tot, pos, tsel, rsel)
    ntr_rat = t[:, :, 0, :].sum(axis=(1, 2))          # trials per rat in this cell
    ok = ntr_rat >= MIN_TRIALS_PER_RAT
    if ratmask is not None:
        ok = ok & ratmask
    allr = ntr_rat > 0
    out = {"label": label,
           "n_rats_used": int(ok.sum()), "n_rats_any": int(allr.sum()),
           "n_trials_cell": float(ntr_rat.sum()),
           "n_trials_used": float(ntr_rat[ok].sum()),
           "min_trials_per_rat_in_cell": float(ntr_rat[allr].min()) if allr.any() else 0.0,
           "median_trials_per_rat_in_cell": float(np.median(ntr_rat[allr])) if allr.any() else 0.0}
    if ok.sum() == 0:
        out["H_pooled"] = np.nan
        return out, np.full(t.shape[0], np.nan), ok

    CE, NH = ce_folds(t, p, (0, 1))                   # symmetric 2-fold (primary)
    Ep = CE[ok].sum(axis=0) / NH[ok].sum(axis=0)
    Hp, qp, den = horizon_from_E(Ep)
    out["E_pooled_bits"] = [float(x) for x in Ep]
    out["q_pooled"] = [float(x) for x in qp]
    out["H_pooled"] = Hp
    out["E1_bits"] = float(Ep[0]); out["E20_bits"] = float(Ep[-1])
    out["E1_minus_E20_bits"] = den
    out["E_min_bits"] = float(np.nanmin(Ep)); out["argmin_n"] = int(np.nanargmin(Ep) + 1)
    # supplementary robustness variant (Cat addition, NOT T3's definition):
    # same 1/e rule but anchored on min_n E(n) instead of E(20)
    Emin = float(np.nanmin(Ep)); dena = Ep[0] - Emin
    if dena > 0:
        qa = (Ep - Emin) / dena
        Ha = np.nan
        for i in range(1, NMAX):
            if qa[i] <= INV_E:
                q0, q1 = qa[i - 1], qa[i]
                Ha = float(i + ((q0 - INV_E) / (q0 - q1) if q0 != q1 else 0.0) - 1.0)
                break
        out["H_pooled_altmin_anchor"] = Ha
    else:
        out["H_pooled_altmin_anchor"] = np.nan
    # single-direction folds
    for f, nm in ((1, "trainEven_testOdd"), (0, "trainOdd_testEven")):
        CEf, NHf = ce_folds(t, p, (f,))
        Ef = CEf[ok].sum(axis=0) / NHf[ok].sum(axis=0)
        out[f"H_pooled_{nm}"], _, d1 = horizon_from_E(Ef)
        out[f"E1_minus_E20_bits_{nm}"] = d1
    # all-rats-in-cell sensitivity (drops the >=200-in-cell rule)
    if allr.sum() and allr.sum() != ok.sum():
        Ea = CE[allr].sum(axis=0) / NH[allr].sum(axis=0)
        out["H_pooled_allrats_in_cell"], _, _ = horizon_from_E(Ea)
    else:
        out["H_pooled_allrats_in_cell"] = Hp
    # per rat
    Hr = np.full(t.shape[0], np.nan)
    for r in np.where(ok)[0]:
        Hr[r], _, _ = horizon_from_E(CE[r] / NH[r])
    valid = ok & np.isfinite(Hr)
    out["n_rats_with_finite_H"] = int(valid.sum())
    out["frac_rats_with_finite_H"] = float(valid.sum() / max(ok.sum(), 1))
    if valid.sum():
        hv = Hr[valid]
        out["H_rat_median"] = float(np.median(hv))
        out["H_rat_mean"] = float(np.mean(hv))
        out["H_rat_sd"] = float(np.std(hv, ddof=1)) if len(hv) > 1 else np.nan
        out["H_rat_sem"] = float(np.std(hv, ddof=1) / np.sqrt(len(hv))) if len(hv) > 1 else np.nan
        out["H_rat_iqr"] = [float(np.percentile(hv, 25)), float(np.percentile(hv, 75))]
    # rat-level bootstrap
    rng = np.random.default_rng(SEED)
    io = np.where(ok)[0]
    CEk, NHk, Hrk = CE[io], NH[io], Hr[io]
    bp = np.empty(NBOOT); bm = np.empty(NBOOT)
    for b in range(NBOOT):
        s = rng.integers(0, len(io), len(io))
        bp[b], _, _ = horizon_from_E(CEk[s].sum(axis=0) / NHk[s].sum(axis=0))
        hh = Hrk[s]; hh = hh[np.isfinite(hh)]
        bm[b] = np.median(hh) if len(hh) else np.nan
    out["H_pooled_ci95"] = [float(np.nanpercentile(bp, 2.5)), float(np.nanpercentile(bp, 97.5))]
    out["H_pooled_boot_sd"] = float(np.nanstd(bp))
    out["H_pooled_boot_nonfinite"] = int((~np.isfinite(bp)).sum())
    out["H_rat_median_ci95"] = [float(np.nanpercentile(bm, 2.5)), float(np.nanpercentile(bm, 97.5))]
    out["H_rat_median_boot_sd"] = float(np.nanstd(bm))
    return out, Hr, ok


# ------------------------------------------------------ control constructs -
order = np.lexsort((tidx, rat))
rs = np.searchsorted(rat[order], np.arange(R), side="left")
re_ = np.searchsorted(rat[order], np.arange(R), side="right")


def shuffle_within_rat(seed):
    rng = np.random.default_rng(seed)
    out = np.empty_like(choice)
    tmp = choice[order].copy()
    for r in range(R):
        a, b = rs[r], re_[r]
        tmp[a:b] = rng.permutation(tmp[a:b])
    out[order] = tmp
    return out


def mismatch_within_rat():
    """D_n of trial i paired with C of the NEXT trial of the same rat in
    trial_idx order (cyclic shift by 1 within rat)."""
    out = np.empty_like(choice)
    tmp = choice[order].copy()
    for r in range(R):
        a, b = rs[r], re_[r]
        tmp[a:b] = np.roll(tmp[a:b], -1)
    out[order] = tmp
    return out


TERCS = (("allgamma", [0, 1, 2]), ("lowgamma", [0]), ("midgamma", [1]), ("highgamma", [2]))
RSELS = (("all", [0, 1]), ("reward_rule_1", [1]))

RESULTS = {}; PERRAT = {}
tot, pos = accumulate(choice)
print(f"accumulated primary, {time.time()-t_start:.0f}s", flush=True)

# common-rat set: >=200 qualifying trials in EVERY tercile
ntr_by_terc = tot[:, :, :, :, 0, :].sum(axis=(2, 3, 4))       # [R, 3]
common = (ntr_by_terc >= MIN_TRIALS_PER_RAT).all(axis=1)
print(f"rats with >=200 trials in all three terciles: {int(common.sum())} / {R}", flush=True)

for sname, rsel in RSELS:
    for tname, tsel in TERCS:
        key = f"primary|{sname}|{tname}"
        r, Hr, ok = analyse(tot, pos, tsel, rsel, key)
        RESULTS[key] = r; PERRAT[key] = (Hr, ok)
        print(f"  {key}: H_pool={r['H_pooled']} H_med={r.get('H_rat_median')} "
              f"nrats={r['n_rats_used']} ntr={r['n_trials_used']:.0f}", flush=True)
    for tname, tsel in TERCS:
        key = f"primaryCOMMON|{sname}|{tname}"
        r, Hr, ok = analyse(tot, pos, tsel, rsel, key, ratmask=common)
        RESULTS[key] = r; PERRAT[key] = (Hr, ok)
        print(f"  {key}: H_pool={r['H_pooled']} nrats={r['n_rats_used']}", flush=True)

# ---- joint rat-level bootstrap of the three tercile horizons and the ratio -
cellCE = {}
for tname, tsel in TERCS:
    t_, p_ = cell(tot, pos, tsel, [0, 1])
    cellCE[tname] = ce_folds(t_, p_, (0, 1))
jidx = np.where(common)[0]
JB = {"n_rats_joint": int(len(jidx))}
if len(jidx) >= MIN_RATS:
    pt = {}
    for tname in ("lowgamma", "midgamma", "highgamma", "allgamma"):
        CE, NH = cellCE[tname]
        pt[tname] = horizon_from_E(CE[jidx].sum(axis=0) / NH[jidx].sum(axis=0))[0]
    JB["H_point"] = pt
    rng = np.random.default_rng(SEED + 7)
    bh = {k: np.empty(NBOOT) for k in ("lowgamma", "midgamma", "highgamma", "allgamma")}
    ratio = np.empty(NBOOT); mono = np.zeros(NBOOT, dtype=bool)
    for b in range(NBOOT):
        s = jidx[rng.integers(0, len(jidx), len(jidx))]
        hs = {}
        for tname in bh:
            CE, NH = cellCE[tname]
            hs[tname] = horizon_from_E(CE[s].sum(axis=0) / NH[s].sum(axis=0))[0]
            bh[tname][b] = hs[tname]
        v = np.array([hs["lowgamma"], hs["midgamma"], hs["highgamma"]])
        if np.all(np.isfinite(v)) and v.min() > 0:
            ratio[b] = v.max() / v.min()
            mono[b] = (v[0] > v[1] > v[2])
        else:
            ratio[b] = np.nan
    JB["H_ci95"] = {k: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]
                    for k, v in bh.items()}
    JB["H_boot_sd"] = {k: float(np.nanstd(v)) for k, v in bh.items()}
    vpt = np.array([pt["lowgamma"], pt["midgamma"], pt["highgamma"]], dtype=float)
    JB["ratio_max_over_min_point"] = float(vpt.max() / vpt.min()) if np.all(np.isfinite(vpt)) else np.nan
    JB["ratio_min_over_max_point"] = float(vpt.min() / vpt.max()) if np.all(np.isfinite(vpt)) else np.nan
    JB["ratio_max_over_min_ci95"] = [float(np.nanpercentile(ratio, 2.5)),
                                     float(np.nanpercentile(ratio, 97.5))]
    JB["frac_boot_monotonic_decreasing_in_absgamma"] = float(mono.mean())
    JB["frac_boot_all_finite"] = float(np.isfinite(ratio).mean())
RESULTS["_joint_bootstrap_commonrats"] = JB
print("joint bootstrap:", json.dumps(JB, default=float)[:600], flush=True)

del tot, pos, cellCE

# ------------------------------------------------------------- controls ----
ctrls = [(f"ctrl_choice_shuffle_s{i}", shuffle_within_rat(SEED + 1000 * i))
         for i in range(N_SHUFFLE_SEEDS)]
ctrls.append(("ctrl_trial_mismatch", mismatch_within_rat()))
for cname, ch in ctrls:
    tot, pos = accumulate(ch)
    for tname, tsel in TERCS:
        key = f"{cname}|all|{tname}"
        r, Hr, ok = analyse(tot, pos, tsel, [0, 1], key)
        RESULTS[key] = r; PERRAT[key] = (Hr, ok)
        print(f"  {key}: H_pool={r['H_pooled']} dE={r.get('E1_minus_E20_bits')} "
              f"fracfinite={r.get('frac_rats_with_finite_H')}", flush=True)
    del tot, pos
    print(f"  done {cname}, {time.time()-t_start:.0f}s", flush=True)

RESULTS["_meta"] = {
    "n_qualifying_rats": int(R), "n_qualifying_trials": int(N),
    "n_common_rats_all_terciles": int(common.sum()),
    "tercile_cutpoints": cutinfo, "seed": SEED, "nboot": NBOOT,
    "n_shuffle_seeds": N_SHUFFLE_SEEDS,
    "min_trials_per_rat": MIN_TRIALS_PER_RAT,
    "trials_per_rat_qualifying": {"min": int(np.bincount(rat, minlength=R).min()),
                                  "median": float(np.median(np.bincount(rat, minlength=R))),
                                  "max": int(np.bincount(rat, minlength=R).max())},
    "wall_seconds_pass2": time.time() - t_start,
}
np.savez(os.path.join(WORK, "perrat_raw.npz"),
         qual_rat_codes=qual_rats,
         ntr_by_terc=ntr_by_terc,
         ntr_total=np.bincount(rat, minlength=R),
         common_rats=common,
         **{k.replace("|", "__") + "__H": v[0] for k, v in PERRAT.items()},
         **{k.replace("|", "__") + "__ok": v[1] for k, v in PERRAT.items()})
with open(os.path.join(WORK, "pass2_raw_results.json"), "w") as f:
    json.dump(RESULTS, f, indent=1, default=float)
print("PASS2 DONE", f"{time.time()-t_start:.0f}s", flush=True)
