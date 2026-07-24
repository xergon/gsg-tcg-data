#!/usr/bin/env python3
"""T3 gamma-stratified horizon -- PASS 3: assemble the deliverables. No verdict."""
import os, sys, json, csv, time, hashlib, subprocess
import numpy as np

WORK = sys.argv[1]
PEAK_LOAD = sys.argv[2] if len(sys.argv) > 2 else "n/a"
WALL = sys.argv[3] if len(sys.argv) > 3 else "n/a"
ANCHOR = (6.040, 8.093)
NMAX = 20

res = json.load(open(os.path.join(WORK, "pass2_raw_results.json")))
cuts = json.load(open(os.path.join(WORK, "tercile_cutpoints.json")))
p1 = json.load(open(os.path.join(WORK, "chunks", "pass1_meta.json")))
pr = np.load(os.path.join(WORK, "perrat_raw.npz"), allow_pickle=True)
meta = res["_meta"]
JB = res.get("_joint_bootstrap_commonrats", {})

inv = {int(v): k for k, v in p1["rat_lookup"].items()}
qcodes = pr["qual_rat_codes"]
rat_ids = [inv[int(c)] for c in qcodes]
R = len(rat_ids)

TN = ("lowgamma", "midgamma", "highgamma", "allgamma")
K = lambda v, s, t: f"{v}|{s}|{t}"


def band(h):
    if h is None or not np.isfinite(h):
        return "undefined"
    if h < ANCHOR[0]:
        return "below_anchor_band"
    if h > ANCHOR[1]:
        return "above_anchor_band"
    return "inside_anchor_band"


# ------------------------------------------------------ gamma_horizon_results
H = {t: res[K("primary", "all", t)] for t in TN}
hp = {t: H[t].get("H_pooled") for t in TN}
hm = {t: H[t].get("H_rat_median") for t in TN}
trip = np.array([hp["lowgamma"], hp["midgamma"], hp["highgamma"]], dtype=float)
trip_m = np.array([hm["lowgamma"], hm["midgamma"], hm["highgamma"]], dtype=float)


def ratios(v):
    if not np.all(np.isfinite(v)) or v.min() <= 0:
        return {"max_over_min": None, "min_over_max": None}
    return {"max_over_min": float(v.max() / v.min()),
            "min_over_max": float(v.min() / v.max())}


def ordering(v, names=("low", "mid", "high")):
    if not np.all(np.isfinite(v)):
        return {"ordering": "undefined (a tercile horizon is undefined)",
                "monotonic_decreasing_in_absgamma": None}
    o = np.argsort(-v)
    return {"ordering_descending": " > ".join(names[i] for i in o),
            "values_low_mid_high": [float(x) for x in v],
            "monotonic_decreasing_in_absgamma": bool(v[0] > v[1] > v[2]),
            "monotonic_increasing_in_absgamma": bool(v[0] < v[1] < v[2])}


out = {
 "what_this_is": ("Gamma-stratified held-out (odd/even) conditional cross-entropy "
                  "reduction on the Brody Poisson-clicks corpus, following T3's frozen "
                  "procedure verbatim. NUMBERS ONLY -- the kill/survive call is T3's."),
 "step_A_tercile_cutpoints_frozen_before_any_horizon": cuts,
 "counts": {
   "n_rats_in_release": p1["rat_lookup"].__len__(),
   "n_trials_in_release": p1["n_trials_seen"],
   "n_trials_with_20_informative_clicks_and_valid_choice_gamma": p1["n_qualifying"],
   "n_trials_dropped_fewer_than_20_informative_clicks": p1["n_short"],
   "n_trials_with_simultaneous_first_pair_removed": p1["n_dropped_stereo"],
   "n_qualifying_rats_ge200_qualifying_trials": meta["n_qualifying_rats"],
   "n_qualifying_trials_in_qualifying_rats": meta["n_qualifying_trials"],
   "n_rats_with_ge200_trials_in_every_tercile": meta["n_common_rats_all_terciles"],
   "qualifying_trials_per_rat": meta["trials_per_rat_qualifying"],
   "per_tercile_trial_counts": cuts["tercile_trial_counts"],
   "per_tercile_rats_used": {t: H[t]["n_rats_used"] for t in TN},
   "per_tercile_trials_used": {t: H[t]["n_trials_used"] for t in TN},
   "min_trials_per_rat_in_tercile": {t: H[t]["min_trials_per_rat_in_cell"] for t in TN},
 },
 "horizons_pooled_primary": {
   t: {"H_clicks": hp[t], "ci95_rat_bootstrap": H[t].get("H_pooled_ci95"),
       "boot_sd": H[t].get("H_pooled_boot_sd"),
       "E1_bits": H[t].get("E1_bits"), "E20_bits": H[t].get("E20_bits"),
       "E1_minus_E20_bits": H[t].get("E1_minus_E20_bits"),
       "E_min_bits": H[t].get("E_min_bits"), "argmin_n": H[t].get("argmin_n"),
       "anchor_band_position": band(hp[t]),
       "H_trainEven_testOdd": H[t].get("H_pooled_trainEven_testOdd"),
       "H_trainOdd_testEven": H[t].get("H_pooled_trainOdd_testEven"),
       "H_allrats_in_cell": H[t].get("H_pooled_allrats_in_cell"),
       "H_supplementary_altmin_anchor": H[t].get("H_pooled_altmin_anchor")}
   for t in TN},
 "horizons_per_rat_median_primary": {
   t: {"H_clicks_median": hm[t], "ci95_rat_bootstrap": H[t].get("H_rat_median_ci95"),
       "sd_across_rats": H[t].get("H_rat_sd"), "sem": H[t].get("H_rat_sem"),
       "iqr": H[t].get("H_rat_iqr"),
       "n_rats_with_finite_H": H[t].get("n_rats_with_finite_H"),
       "frac_rats_with_finite_H": H[t].get("frac_rats_with_finite_H"),
       "anchor_band_position": band(hm[t])} for t in TN},
 "ratio_pooled": ratios(trip),
 "ratio_per_rat_median": ratios(trip_m),
 "ordering_pooled": ordering(trip),
 "ordering_per_rat_median": ordering(trip_m),
 "joint_rat_bootstrap_common_rats": JB,
 "T3_stated_thresholds_positions_as_facts": {
   "anchor_band_H_clicks": list(ANCHOR),
   "raw_record_hypothesis_expects_maxH_over_minH_le_1.5": {
       "observed_pooled": ratios(trip)["max_over_min"],
       "observed_per_rat_median": ratios(trip_m)["max_over_min"]},
   "kill_condition_stated_by_T3_maxH_over_minH_gt_3_AND_monotonic_decrease": {
       "observed_ratio_pooled": ratios(trip)["max_over_min"],
       "observed_monotonic_decrease_pooled":
           ordering(trip).get("monotonic_decreasing_in_absgamma"),
       "note": "reported as measurements; no ruling is made here"},
 },
 "sensitivity_reward_rule_1_subset": {
   t: {"H_pooled": res[K("primary", "reward_rule_1", t)].get("H_pooled"),
       "ci95": res[K("primary", "reward_rule_1", t)].get("H_pooled_ci95"),
       "n_rats_used": res[K("primary", "reward_rule_1", t)]["n_rats_used"],
       "n_trials_used": res[K("primary", "reward_rule_1", t)]["n_trials_used"]}
   for t in TN},
 "sensitivity_common_rat_subset": {
   t: {"H_pooled": res[K("primaryCOMMON", "all", t)].get("H_pooled"),
       "ci95": res[K("primaryCOMMON", "all", t)].get("H_pooled_ci95"),
       "n_rats_used": res[K("primaryCOMMON", "all", t)]["n_rats_used"]}
   for t in TN},
 "run_params": {"seed": meta["seed"], "n_bootstrap": meta["nboot"],
                "min_trials_per_rat": meta["min_trials_per_rat"],
                "n_max_clicks": NMAX, "stereo_tolerance_s": 1e-7,
                "fold_rule": "odd/even trial_idx, symmetric 2-fold (both directions), "
                             "Jeffreys (a=b=1/2) smoothing on the training half",
                "interpolation": "linear in n on q(n) at the FIRST n where q(n)<=1/e; "
                                 "H_clicks = n_{1/e} - 1",
                "entropy_units": "bits"},
}
with open(os.path.join(WORK, "gamma_horizon_results.json"), "w") as f:
    json.dump(out, f, indent=1, default=float)

# ----------------------------------------------------------------- controls -
CTRLS = [k for k in ("ctrl_choice_shuffle_s0", "ctrl_choice_shuffle_s1",
                     "ctrl_choice_shuffle_s2", "ctrl_choice_shuffle_s3",
                     "ctrl_choice_shuffle_s4", "ctrl_trial_mismatch")]
ctrl = {"definitions": {
    "choice_shuffle": "C permuted uniformly at random within rat over all qualifying "
                      "trials (5 independent seeds).",
    "trial_mismatch": "D_n of trial i paired with C of the NEXT qualifying trial of the "
                      "same rat in trial_idx order (cyclic shift by 1 within rat).",
    "note": "For a control the held-out cross-entropy does not fall with n, so "
            "E(1)-E(20) is <= 0 and T3's q(n) normalisation has no positive "
            "denominator; H is then reported as undefined (null), with the sign and "
            "size of E(1)-E(20) given so the absence of any reduction is visible."},
    "target_for_comparison": {"H_pooled_allgamma": hp["allgamma"],
                              "H_pooled_lowgamma": hp["lowgamma"],
                              "H_pooled_midgamma": hp["midgamma"],
                              "H_pooled_highgamma": hp["highgamma"]},
    "runs": {}}
for c in CTRLS:
    ctrl["runs"][c] = {}
    for t in TN:
        r = res[K(c, "all", t)]
        ctrl["runs"][c][t] = {
            "H_pooled": r.get("H_pooled"),
            "E1_bits": r.get("E1_bits"), "E20_bits": r.get("E20_bits"),
            "E1_minus_E20_bits": r.get("E1_minus_E20_bits"),
            "H_rat_median_where_defined": r.get("H_rat_median"),
            "n_rats_with_finite_H": r.get("n_rats_with_finite_H"),
            "frac_rats_with_finite_H": r.get("frac_rats_with_finite_H"),
            "H_supplementary_altmin_anchor": r.get("H_pooled_altmin_anchor")}
finite_ctrl = [(c, t, ctrl["runs"][c][t]["H_pooled"]) for c in CTRLS for t in TN
               if ctrl["runs"][c][t]["H_pooled"] is not None
               and np.isfinite(ctrl["runs"][c][t]["H_pooled"] or np.nan)]
within3 = []
for c, t, h in finite_ctrl:
    tgt = hp[t]
    if tgt and np.isfinite(tgt) and h > 0:
        r_ = max(h / tgt, tgt / h)
        if r_ <= 3.0:
            within3.append({"control": c, "tercile": t, "H_control": h,
                            "H_target": tgt, "ratio": float(r_)})
ctrl["controls_with_a_defined_pooled_horizon"] = [
    {"control": c, "tercile": t, "H_pooled": h} for c, t, h in finite_ctrl]
ctrl["any_control_within_factor_three_of_target"] = bool(within3)
ctrl["controls_within_factor_three"] = within3
ctrl["entropy_reduction_comparison_bits"] = {
    "target_E1_minus_E20": {t: H[t].get("E1_minus_E20_bits") for t in TN},
    "controls_E1_minus_E20": {c: {t: ctrl["runs"][c][t]["E1_minus_E20_bits"] for t in TN}
                              for c in CTRLS}}
with open(os.path.join(WORK, "controls.json"), "w") as f:
    json.dump(ctrl, f, indent=1, default=float)

# ---------------------------------------------------------------- q_curves --
with open(os.path.join(WORK, "q_curves.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["n", "E_low_bits", "E_mid_bits", "E_high_bits", "E_all_bits",
                "q_low", "q_mid", "q_high", "q_all",
                "E_ctrlshuffle_all_bits", "E_ctrlmismatch_all_bits"])
    cs = res[K("ctrl_choice_shuffle_s0", "all", "allgamma")]
    cm = res[K("ctrl_trial_mismatch", "all", "allgamma")]
    for i in range(NMAX):
        row = [i + 1]
        for t in ("lowgamma", "midgamma", "highgamma", "allgamma"):
            row.append(H[t].get("E_pooled_bits", [None] * NMAX)[i])
        for t in ("lowgamma", "midgamma", "highgamma", "allgamma"):
            row.append(H[t].get("q_pooled", [None] * NMAX)[i])
        row.append(cs.get("E_pooled_bits", [None] * NMAX)[i])
        row.append(cm.get("E_pooled_bits", [None] * NMAX)[i])
        w.writerow(row)

# --------------------------------------------------------- per_rat_horizons -
def get(key, arr):
    k = key.replace("|", "__") + "__" + arr
    return pr[k] if k in pr.files else np.full(R, np.nan)


ntr_t = pr["ntr_by_terc"]; ntr_tot = pr["ntr_total"]; common = pr["common_rats"]
with open(os.path.join(WORK, "per_rat_horizons.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["rat_id", "n_qualifying_trials", "n_trials_low", "n_trials_mid",
                "n_trials_high", "has_ge200_in_all_terciles",
                "H_allgamma", "H_lowgamma", "H_midgamma", "H_highgamma",
                "H_ctrl_choice_shuffle_s0_allgamma", "H_ctrl_trial_mismatch_allgamma"])
    cols = {t: get(K("primary", "all", t), "H") for t in TN}
    c1 = get(K("ctrl_choice_shuffle_s0", "all", "allgamma"), "H")
    c2 = get(K("ctrl_trial_mismatch", "all", "allgamma"), "H")
    for i in range(R):
        w.writerow([rat_ids[i], int(ntr_tot[i]), int(ntr_t[i, 0]), int(ntr_t[i, 1]),
                    int(ntr_t[i, 2]), bool(common[i]),
                    *[("" if not np.isfinite(cols[t][i]) else f"{cols[t][i]:.6f}")
                      for t in ("allgamma", "lowgamma", "midgamma", "highgamma")],
                    "" if not np.isfinite(c1[i]) else f"{c1[i]:.6f}",
                    "" if not np.isfinite(c2[i]) else f"{c2[i]:.6f}"])

# ----------------------------------------------------------------- RESULTS.md
def fmt(x, nd=4):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "undefined"
    return f"{x:.{nd}f}"


def ci(c):
    if not c or not np.all(np.isfinite(np.array(c, dtype=float))):
        return "n/a"
    return f"[{c[0]:.4f}, {c[1]:.4f}]"


md = []
md.append("# T3 gamma-stratified held-out entropy reduction -- NUMBERS ONLY\n")
md.append("Cat is the compute arm. **No verdict is offered here; the kill/survive "
          "call is T3's.**\n")
md.append(f"Data: `brody_poisson_clicks_trials.parquet`, sha256 "
          f"`{json.load(open(os.path.join(WORK,'RELEASE_SUMMARY.json')))['parquet_sha256']}` "
          f"(verified), Zenodo 13352119, CC-BY-4.0.\n")
md.append("\n## 1. Tercile cut points (frozen BEFORE any horizon was computed)\n")
md.append(f"- `|gamma|` 33.3 pct cut = **{cuts['cut1_abs_gamma_q33']:.6f}**")
md.append(f"- `|gamma|` 66.7 pct cut = **{cuts['cut2_abs_gamma_q67']:.6f}**")
md.append(f"- assignment: {cuts['assignment_rule']}")
md.append(f"- tercile trial counts: {cuts['tercile_trial_counts']} "
          f"(fractions {[round(x,4) for x in cuts['tercile_fractions']]})")
md.append(f"- per-tercile |gamma| range: {cuts['per_tercile_abs_gamma_range']}")
md.append(f"- per-tercile |gamma| mean: {[round(x,4) for x in cuts['per_tercile_abs_gamma_mean']]}")
md.append(f"- distinct |gamma| values in the corpus: {cuts['n_unique_abs_gamma_6dp']}")
md.append("\n## 2. Sample\n")
c_ = out["counts"]
for k, v in c_.items():
    md.append(f"- `{k}`: {v}")
md.append("\n## 3. Horizons (pooled across rats, symmetric odd/even 2-fold)\n")
md.append("| stratum | H_clicks | 95% CI (rat bootstrap) | E(1) bits | E(20) bits | "
          "E(1)-E(20) | argmin_n | anchor band |")
md.append("|---|---|---|---|---|---|---|---|")
for t in ("lowgamma", "midgamma", "highgamma", "allgamma"):
    d = out["horizons_pooled_primary"][t]
    md.append(f"| {t} | {fmt(d['H_clicks'])} | {ci(d['ci95_rat_bootstrap'])} | "
              f"{fmt(d['E1_bits'],6)} | {fmt(d['E20_bits'],6)} | "
              f"{fmt(d['E1_minus_E20_bits'],6)} | {d['argmin_n']} | "
              f"{d['anchor_band_position']} |")
md.append("\n### Per-rat median horizons\n")
md.append("| stratum | median H | 95% CI | IQR | SD across rats | rats with finite H |")
md.append("|---|---|---|---|---|---|")
for t in ("lowgamma", "midgamma", "highgamma", "allgamma"):
    d = out["horizons_per_rat_median_primary"][t]
    md.append(f"| {t} | {fmt(d['H_clicks_median'])} | {ci(d['ci95_rat_bootstrap'])} | "
              f"{ci(d['iqr'])} | {fmt(d['sd_across_rats'])} | "
              f"{d['n_rats_with_finite_H']} ({fmt(d['frac_rats_with_finite_H'],3)}) |")
md.append("\n## 4. Ratio and ordering\n")
md.append(f"- pooled maxH/minH = **{fmt(out['ratio_pooled']['max_over_min'])}**, "
          f"minH/maxH = **{fmt(out['ratio_pooled']['min_over_max'])}**")
md.append(f"- pooled ordering (descending H): "
          f"**{out['ordering_pooled'].get('ordering_descending','undefined')}**")
md.append(f"- monotonic DECREASING in |gamma| (H_low > H_mid > H_high): "
          f"**{out['ordering_pooled'].get('monotonic_decreasing_in_absgamma')}**")
md.append(f"- monotonic INCREASING in |gamma|: "
          f"**{out['ordering_pooled'].get('monotonic_increasing_in_absgamma')}**")
md.append(f"- per-rat-median maxH/minH = {fmt(out['ratio_per_rat_median']['max_over_min'])}, "
          f"ordering {out['ordering_per_rat_median'].get('ordering_descending','undefined')}")
if JB.get("ratio_max_over_min_point") is not None:
    md.append(f"- joint rat bootstrap on the {JB['n_rats_joint']} rats with >=200 trials in "
              f"every tercile: maxH/minH = {fmt(JB['ratio_max_over_min_point'])} "
              f"CI95 {ci(JB.get('ratio_max_over_min_ci95'))}; "
              f"fraction of bootstrap draws monotonically decreasing = "
              f"{fmt(JB.get('frac_boot_monotonic_decreasing_in_absgamma'),3)}")
md.append("\n### Position relative to the thresholds T3 stated (facts, not a ruling)\n")
md.append(f"- T3 raw-record expectation `maxH/minH <= 1.5`: observed pooled "
          f"{fmt(out['ratio_pooled']['max_over_min'])}")
md.append(f"- T3 kill condition `maxH/minH > 3` AND monotonic decrease: observed ratio "
          f"{fmt(out['ratio_pooled']['max_over_min'])}, monotonic decrease "
          f"{out['ordering_pooled'].get('monotonic_decreasing_in_absgamma')}")
md.append(f"- T3 anchor band `H_clicks in [{ANCHOR[0]}, {ANCHOR[1]}]`: "
          + "; ".join(f"{t}={fmt(hp[t])} ({band(hp[t])})" for t in TN))
md.append("\n## 5. Controls\n")
md.append("| control | stratum | H_pooled | E(1)-E(20) bits | rats with finite H |")
md.append("|---|---|---|---|---|")
for c in CTRLS:
    for t in ("allgamma", "lowgamma", "midgamma", "highgamma"):
        d = ctrl["runs"][c][t]
        md.append(f"| {c} | {t} | {fmt(d['H_pooled'])} | {fmt(d['E1_minus_E20_bits'],6)} | "
                  f"{d['n_rats_with_finite_H']} ({fmt(d['frac_rats_with_finite_H'],3)}) |")
md.append(f"\n- any control with a defined pooled horizon within a factor of three of the "
          f"corresponding target: **{ctrl['any_control_within_factor_three_of_target']}**")
if within3:
    md.append(f"- cases: {json.dumps(within3, default=float)}")
md.append("\n## 6. Method (as executed)\n")
md.append("- Per-trial evidence: L click s=-1, R click s=+1; if |first_L - first_R| < 1e-7 s "
          "that simultaneous pair is removed; remaining clicks sorted by time (ties broken "
          "L before R, deterministic); first 20 informative clicks retained; "
          "D_n = sum_{k<=n} s_k for n=1..20.")
md.append("- A trial qualifies if it has >=20 informative clicks after the stereo removal "
          "and has a valid `choice_R` and a finite `gamma`. Rats qualify at >=200 "
          "qualifying trials; >=30 qualifying rats required.")
md.append("- Held-out curve: trials split by odd/even `trial_idx`; "
          "p(C=1|D_n=d) = (N_{d,1}+1/2)/(N_{d,.}+1) on the training half; "
          "E(n) = held-out conditional cross-entropy of the rat's choice given D_n, in bits.")
md.append("- q(n) = (E(n)-E(20))/(E(1)-E(20)); H_clicks = n_{1/e} - 1 with n_{1/e} obtained "
          "by LINEAR interpolation in n on q at the FIRST n where q(n) <= 1/e.")
md.append("- |gamma| terciles are GLOBAL over qualifying trials of qualifying rats, and the "
          "cut points were written to `tercile_cutpoints.json` before any horizon was computed.")
md.append("\n### Cat judgement calls (T3 may overrule)\n")
md.append("1. **\"Qualifying trial\" = >=20 informative clicks** (so every D_1..D_20 exists). "
          "T3's text names a qualifying trial without defining it; requiring the full "
          "20-click prefix is the conservative reading. Trials dropped for this reason are "
          "counted above.")
md.append("2. **Fold direction.** T3 says \"training half\"/\"held-out half\" without saying "
          "which parity is which. Primary numbers use the SYMMETRIC 2-fold (train even/test "
          "odd and train odd/test even, cross-entropies summed, every trial held out exactly "
          "once). Both single directions are reported separately.")
md.append("3. **Per-rat inclusion inside a tercile** uses the same >=200-trial rule as the "
          "global cut. A no-cut variant (`H_allrats_in_cell`) and a common-rat variant "
          "(rats with >=200 trials in ALL three terciles) are both reported.")
md.append("4. **Aggregation.** Each rat keeps its own p(C|D_n); the pooled E(n) is "
          "sum_rats CE_rat(n) / sum_rats N_rat. The per-rat median is reported alongside.")
md.append("5. **Undefined horizons.** Where E(20) >= E(1) the T3 denominator is non-positive "
          "and no 1/e crossing exists; H is reported as undefined rather than forced. A "
          "supplementary variant anchored on min_n E(n) is given for information only.")
md.append("6. **Entropy in bits.** q(n) and H are unit-invariant.")
md.append("7. **Tercile tie rule.** `np.quantile` puts the 33.3/66.7 cuts exactly on the "
          "mass points |gamma| = 1.5 and 2.5. The primary numbers use inclusive upper "
          "bounds (|g| <= cut), which sends all of |gamma| = 1.5 to the low tercile and "
          "all of 2.5 to the mid tercile and makes the terciles unequal "
          "(44.7 / 24.7 / 30.7 % of trials). Section 8 reports the strict-`<` alternative "
          "and the value-by-value horizons so the choice can be inspected.")
qd_path = os.path.join(WORK, "qualification_diagnostic.json")
if os.path.exists(qd_path):
    qd = json.load(open(qd_path))
    out["qualification_diagnostic"] = qd
    md.append("\n## 7. Does the >=20-informative-click trial cut depend on |gamma|?\n")
    md.append("Computed on ALL trials in the release (scalar columns only). The exact "
              "per-trial stereo removal is not available in this cheap pass, so both "
              "bounds are given.\n")
    md.append("| tercile | all trials | qualify rate (>=20 clicks) | qualify rate "
              "(>=22 clicks) | mean stim duration s |")
    md.append("|---|---|---|---|---|")
    for i, t in enumerate(("low", "mid", "high")):
        md.append(f"| {t} | {qd['all_trials_per_tercile'][i]} | "
                  f"{fmt(qd['qualify_rate_per_tercile_optimistic_ge20_clicks'][i])} | "
                  f"{fmt(qd['qualify_rate_per_tercile_strict_ge22_clicks'][i])} | "
                  f"{fmt(qd['mean_stim_duration_s_per_tercile'][i])} |")

gr_path = os.path.join(WORK, "gamma_resolved_sensitivity.json")
if os.path.exists(gr_path):
    gr = json.load(open(gr_path))
    out["gamma_resolved_sensitivity"] = gr
    md.append("\n## 8. |gamma| is discrete and BOTH cut points land on mass points\n")
    md.append("The 33.3 and 66.7 percentiles of |gamma| are exactly 1.5 and 2.5, and "
              "|gamma| = 0.5, 1.5, 2.5, 3.5 alone carry 9.52 M of the 13.38 M qualifying "
              "trials. Tercile membership of |gamma| = 1.5 and 2.5 is therefore decided by "
              "the tie rule. Both rules and the value-by-value resolution are reported.\n")
    a = gr["alt_tie_rule_strict_lt"]
    md.append(f"**Alternative tie rule** ({a['rule']}), trial counts {a['trial_counts']}:\n")
    md.append("| tercile | H_clicks | 95% CI | rats | trials |")
    md.append("|---|---|---|---|---|")
    for t in ("lowgamma", "midgamma", "highgamma"):
        h = a["horizons"][t]
        md.append(f"| {t} | {fmt(h.get('H'))} | {ci(h.get('ci95'))} | {h['n_rats']} | "
                  f"{h['n_trials']:.0f} |")
    hv = [a["horizons"][t].get("H") for t in ("lowgamma", "midgamma", "highgamma")]
    if all(x is not None for x in hv):
        md.append(f"\n- alt-tie maxH/minH = **{fmt(max(hv)/min(hv))}**, "
                  f"monotonic decreasing = **{bool(hv[0] > hv[1] > hv[2])}**")
    md.append("\n**Horizon at each dominant single |gamma| value** (no tie question at all):\n")
    md.append("| \\|gamma\\| | H_clicks | 95% CI | rats | trials |")
    md.append("|---|---|---|---|---|")
    for k, h in gr["per_absgamma_value"]["horizons"].items():
        hh = ("not computed (<30 rats with >=200 trials)" if h.get("note")
              else fmt(h.get("H")))
        md.append(f"| {k.replace('absgamma_','')} | {hh} | "
                  f"{ci(h.get('ci95'))} | {h['n_rats']} | {h['n_trials']:.0f} |")

md.append("\n### Provenance\n")
md.append(f"- peak 1-min load average observed during the run: {PEAK_LOAD}")
md.append(f"- wall time: {WALL}")
md.append(f"- BLAS thread pinning: OMP/OPENBLAS/MKL/VECLIB/NUMEXPR = 1; no multiprocessing.")
md.append(f"- seed {meta['seed']}, {meta['nboot']} rat-level bootstrap resamples, "
          f"{meta['n_shuffle_seeds']} choice-shuffle seeds.")
with open(os.path.join(WORK, "RESULTS.md"), "w") as f:
    f.write("\n".join(md) + "\n")
# re-dump so the JSON carries the qualification diagnostic too
with open(os.path.join(WORK, "gamma_horizon_results.json"), "w") as f:
    json.dump(out, f, indent=1, default=float)

# ------------------------------------------------------------------ SUMMARY -
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


outfiles = ["gamma_horizon_results.json", "per_rat_horizons.csv", "q_curves.csv",
            "controls.json", "RESULTS.md", "tercile_cutpoints.json",
            "qualification_diagnostic.json", "gamma_resolved_sensitivity.json",
            "pass1_extract.py", "pass2_horizons.py", "pass3_finalize.py",
            "pass4_qualdiag.py", "pass5_gamma_resolved.py",
            "selftest_pass1.py", "selftest_pass2.py", "run_all.sh"]
summary = {
 "job": "T3 gamma-stratified held-out entropy reduction (Brody Poisson clicks)",
 "produced_by": "Cat (compute arm). No verdict -- kill/survive is T3's call.",
 "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
 "input": {"file": "brody_poisson_clicks_trials.parquet",
           "sha256_expected": json.load(open(os.path.join(WORK, "RELEASE_SUMMARY.json")))["parquet_sha256"],
           "sha256_verified": json.load(open(os.path.join(WORK, "input_sha256.json")))["sha256"],
           "bytes": json.load(open(os.path.join(WORK, "input_sha256.json")))["bytes"],
           "source": "Zenodo 13352119, CC-BY-4.0"},
 "run_params": out["run_params"],
 "seeds": {"master": meta["seed"], "bootstrap": meta["seed"],
           "joint_bootstrap": meta["seed"] + 7,
           "choice_shuffle": [meta["seed"] + 1000 * i for i in range(meta["n_shuffle_seeds"])]},
 "peak_load_1min": PEAK_LOAD,
 "wall_time": WALL,
 "pass1_wall_seconds": p1["wall_seconds"],
 "pass2_wall_seconds": meta["wall_seconds_pass2"],
 "outputs_sha256": {fn: sha(os.path.join(WORK, fn)) for fn in outfiles
                    if os.path.exists(os.path.join(WORK, fn))},
 "output_bytes": {fn: os.path.getsize(os.path.join(WORK, fn)) for fn in outfiles
                  if os.path.exists(os.path.join(WORK, fn))},
}
with open(os.path.join(WORK, "SUMMARY.json"), "w") as f:
    json.dump(summary, f, indent=1, default=float)
print("PASS3 DONE")
print(json.dumps({"H_low": hp["lowgamma"], "H_mid": hp["midgamma"],
                  "H_high": hp["highgamma"], "H_all": hp["allgamma"],
                  "ratio": out["ratio_pooled"]}, indent=1, default=float))
