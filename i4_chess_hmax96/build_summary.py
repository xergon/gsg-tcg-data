#!/usr/bin/env python3
"""Build the combined CSV, the readable markdown table, and SUMMARY.json (with sha256s)."""
import json, os, glob, hashlib, time, sys

OUT = sys.argv[1]
PERIODS = ["2014-07", "2016-01"]
OBS = [("fromto", "fromto"), ("sancanon", "san_canon"),
       ("sanmatkey", "san_matkey"), ("sanstatekey", "san_statekey")]
CONDS = ["real", "scramble", "targetperm", "parityscramble"]
GRID_I4 = [8, 12, 16, 24, 32, 40, 48, 64, 80, 96]

def L(cond, ob, per, tag):
    fn = os.path.join(OUT, "%s_%s_%s%s.json" % (cond, ob, per, "" if tag == "matched" else "_power"))
    return json.load(open(fn)) if os.path.exists(fn) else None

# ---- combined CSV
rows = []
hdr = None
for per in PERIODS:
    for tag in ["matched", "power"]:
        fn = os.path.join(OUT, "rows_%s_%s.csv" % (per, tag))
        if not os.path.exists(fn):
            continue
        lines = open(fn).read().strip().split("\n")
        hdr = lines[0]
        rows += lines[1:]
with open(os.path.join(OUT, "hmax96_all_rows.csv"), "w") as f:
    f.write(hdr + "\n" + "\n".join(rows) + "\n")

# ---- markdown
md = []
md.append("# i4 HMAX=96 rerun of the June-29 extractor family — results\n")
md.append("Run by Cat (compute arm) 2026-07-25 (UTC). Lichess standard rated, public CC0, "
          "streamed from the Cat-published GitHub release mirror.\n")
md.append("**Bias correction in force:** Miller–Madow, `H_MM = H_plugin + (K_observed − 1)/(2N)`, "
          "inherited verbatim from `chess_reality_h0.py` (2026-06-29). Every table below reports the "
          "**unclamped** MM mutual information; the June-29 code additionally clamped MI at 0 "
          "(`I_MM_clamped_june29` in the JSONs/CSV) — the clamp never binds for REAL.\n")
md.append("**Reproduction gate:** this re-implementation reproduces the published June-29 "
          "`I_MI_by_horizon_nats` for both periods to max |Δ| = 4.5e-07 (6-dp rounding), with identical "
          "`N_anchored_positions` (1,274,769 / 1,233,924) and identical `K = 1792`. "
          "See `june29_repro_gate_*.json`.\n")
md.append("**T definition (Cat's, stated — NOT taken from i4):** "
          "`T(h) = I_MM(condition, h) − I_MM(exact-target-marginal-permutation of that same panel, h)` in nats. "
          "Two floors are reported: `T` uses the REAL panel's permutation floor for every condition "
          "(i4's literal condition list); `T_own` uses each condition's own floor, which is the correct "
          "comparison for the scrambles because scrambling changes the anchor marginal. "
          "For REAL the two are identical.\n")

for tag in ["matched", "power"]:
    d0 = L("real", "fromto", PERIODS[0], tag)
    if d0 is None:
        continue
    md.append("\n## Run `%s` — n_games = %d per period\n" % (tag, d0["n_games"]))
    for obs_short, obs_long in OBS:
        md.append("\n### Observable `%s`\n" % obs_long)
        md.append("| period | condition | " + " | ".join("h=%d" % h for h in GRID_I4) + " |")
        md.append("|---|---|" + "---|" * len(GRID_I4))
        for per in PERIODS:
            for c in CONDS:
                d = L(c, obs_short, per, tag)
                if d is None: continue
                md.append("| %s | %s I_MM | " % (per, c)
                          + " | ".join("%.4f" % d["estimates_by_horizon"][str(h)]["I_MM"] for h in GRID_I4) + " |")
            for c in CONDS:
                d = L(c, obs_short, per, tag)
                if d is None: continue
                md.append("| %s | %s T_own | " % (per, c)
                          + " | ".join("%.4f" % d["T_vs_OWN_floor_by_horizon_nats"][str(h)] for h in GRID_I4) + " |")
        # REAL ratios
        md.append("\n**REAL — `T(h)/T(h+8)` (i4 predeclared 0.774) and its reciprocal `T(h+8)/T(h)`:**\n")
        md.append("| period | quantity | " + " | ".join("h=%d" % h for h in GRID_I4) + " |")
        md.append("|---|---|" + "---|" * len(GRID_I4))
        for per in PERIODS:
            d = L("real", obs_short, per, tag)
            if d is None: continue
            r = d["T_ratio_h_over_h_plus_8"]
            md.append("| %s | T(h)/T(h+8) | " % per
                      + " | ".join(("%.4f" % r[str(h)]) if str(h) in r else "–" for h in GRID_I4) + " |")
            md.append("| %s | T(h+8)/T(h) | " % per
                      + " | ".join(("%.4f" % (1.0 / r[str(h)])) if str(h) in r else "–" for h in GRID_I4) + " |")
    # full-grid REAL detail for the two primary observables
    for obs_short, obs_long in OBS[:2]:
        md.append("\n### REAL, `%s`, full computed grid (every h ≡ 0 mod 4 from 8 to 96)\n" % obs_long)
        md.append("| period | h | I_MM | I_plugin | perm floor | T | T boot sd | T(h)/T(h+8) | T(h+8)/T(h) |")
        md.append("|---|---|---|---|---|---|---|---|---|")
        for per in PERIODS:
            d = L("real", obs_short, per, tag); p = L("targetperm", obs_short, per, tag)
            if d is None: continue
            for h in d["horizons_computed"]:
                s = str(h); r = d["T_ratio_h_over_h_plus_8"].get(s)
                sd = d.get("T_bootstrap_over_games", {}).get(s, {}).get("sd")
                md.append("| %s | %d | %.4f | %.4f | %.4f | %.4f | %s | %s | %s |" % (
                    per, h, d["estimates_by_horizon"][s]["I_MM"], d["estimates_by_horizon"][s]["I_plugin"],
                    p["estimates_by_horizon"][s]["I_MM"], d["T_by_horizon_nats"][s],
                    ("%.4f" % sd) if sd is not None else "–",
                    ("%.4f" % r) if r else "–", ("%.4f" % (1 / r)) if r else "–"))

md.append("\n## Kill-condition inputs (numbers only — i4's call, not Cat's)\n")
md.append("| run | period | observable | T(48) | T(64) | T(80) | T(96) | first h with T<0.10 | T(64)−T(96) |")
md.append("|---|---|---|---|---|---|---|---|---|")
for tag in ["matched", "power"]:
    for per in PERIODS:
        for obs_short, obs_long in OBS:
            d = L("real", obs_short, per, tag)
            if d is None: continue
            T = {int(k): v for k, v in d["T_by_horizon_nats"].items()}
            below = [h for h in sorted(T) if T[h] < 0.10]
            md.append("| %s | %s | %s | %.4f | %.4f | %.4f | %.4f | %s | %.4f |" % (
                tag, per, obs_long, T[48], T[64], T[80], T[96],
                (str(below[0]) if below else "none ≤96"), T[64] - T[96]))

with open(os.path.join(OUT, "SUMMARY.md"), "w") as f:
    f.write("\n".join(md) + "\n")

# ---- SUMMARY.json
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

files = sorted(f for f in os.listdir(OUT)
               if f.endswith((".json", ".csv", ".md", ".txt", ".py")) and f != "SUMMARY.json")
meta = json.load(open(os.path.join(OUT, "extract_meta_2014-07.json")))
meta2 = json.load(open(os.path.join(OUT, "extract_meta_2016-01.json")))
d_m = L("real", "fromto", "2014-07", "matched")
d_p = L("real", "fromto", "2014-07", "power")
summary = {
    "job": "i4 HMAX=96 rerun of the June-29 chess predictive-information extractor family",
    "run_by": "Cat (compute arm) — numbers only, no interpretation of i4's hypothesis",
    "run_date_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "months": ["2014-07", "2016-01"],
    "data_source": "Lichess standard rated PGN (public CC0), streamed from "
                   "https://github.com/xergon/gsg-tcg-data/releases/tag/i4-lichess-standard-rated",
    "HMAX": 96, "MIN_PLIES": 100,
    "horizon_grid_requested_by_i4": GRID_I4,
    "horizon_grid_computed": d_m["horizons_computed"],
    "horizon_grid_note": "every h ≡ 0 mod 4 from 8 to 96 was computed (superset of i4's grid) so that "
                         "T(h)/T(h+8) is defined at every h from 8 to 88, including across 64–96. "
                         "All computed h are even, hence all same-side-to-move (no parity nuisance).",
    "conditions": ["REAL", "WITHIN_GAME_SCRAMBLE", "EXACT_TARGET_MARGINAL_PERMUTATION",
                   "PARITY_PRESERVING_WITHIN_GAME_SCRAMBLE"],
    "observables": {
        "fromto": "from_square*64 + to_square — the June-29 original token",
        "san_canon": "SAN content on a colour-canonical board: (piece, destination mirrored into the "
                     "mover's frame, capture, promotion, castling)",
        "san_matkey": "san_canon ⊗ coarse canonical board-state hash (material key: P,N,B,R,Q counts "
                      "for mover and opponent)",
        "san_statekey": "san_canon ⊗ full canonical board-state hash (python-chess transposition key)",
    },
    "bias_correction_in_force": "Miller–Madow: H_MM = H_plugin + (K_observed − 1)/(2N). Inherited "
                                "verbatim from chess_reality_h0.py 2026-06-29. Uncorrected plugin MI is "
                                "reported alongside as I_plugin_nats; the June-29 max(0,·) clamp is "
                                "reported as I_MM_clamped_june29_nats.",
    "T_definition": "T(h) = I_MM(condition,h) − I_MM(exact-target-marginal permutation,h), nats, "
                    "unclamped. Cat's stated definition; i4 did not supply one.",
    "game_count_convention": {
        "june29_convention": "first 30000 games passing MIN_PLIES = HMAX+4",
        "matched_run": {"n_games": d_m["n_games"], "N_anchored_2014_07": d_m["N_anchored_positions"],
                        "note": "same 30000-game convention, now with MIN_PLIES = 100 because HMAX = 96"},
        "power_run": ({"n_games": d_p["n_games"], "N_anchored_2014_07": d_p["N_anchored_positions"],
                       "note": "SUPPLEMENTARY run at 4x the game count, reported explicitly as a "
                               "deviation from the June-29 convention, to test whether the large-h "
                               "estimates are sample-size limited"} if d_p else None),
    },
    "extraction": {"2014-07": meta, "2016-01": meta2},
    "malformed_games_skipped": {"2014-07": meta["n_rejected_malformed"],
                                "2016-01": meta2["n_rejected_malformed"]},
    "june29_reproduction_gate": {
        "2014-07": json.load(open(os.path.join(OUT, "june29_repro_gate_2014-07.json")))["max_abs_diff_vs_published"],
        "2016-01": json.load(open(os.path.join(OUT, "june29_repro_gate_2016-01.json")))["max_abs_diff_vs_published"],
        "note": "max |Δ| between this re-implementation and the published June-29 I_MI_by_horizon_nats",
    },
    "sha256": {f: sha(os.path.join(OUT, f)) for f in files},
}
with open(os.path.join(OUT, "SUMMARY.json"), "w") as f:
    json.dump(summary, f, indent=2)
print("summary written; %d files hashed" % len(files))
