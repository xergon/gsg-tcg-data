#!/usr/bin/env python3
"""v3 verification: FULL-CORPUS bit-identity vs v2, the two contract assertions, and the
re-run audit numbers (128-vs-64-bit collisions, fold split)."""
import os, json, glob
import numpy as np

D = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(D, "transpositions_2014-07.npz")
V2 = os.path.join(D, "transpositions_2014-07_v2.npz")
V3 = os.path.join(D, "transpositions_2014-07_v3.npz")

DIGEST_COLS = ["state", "state_fen5", "repetition_ledger_hash", "hist1", "hist4", "nxt",
               "state_hash128_lo", "state_hash128_hi", "player_hash"]
V1_CARRIED = ["state", "state_fen5", "repetition_ledger_hash", "hist1", "hist4", "nxt",
              "gidx", "eband", "tclass", "ply", "current_position_occurrence_count",
              "can_claim_threefold_now", "can_claim_threefold_after_one_move"]

GOLD = np.uint64(0x9E3779B97F4A7C15)
MUL1 = np.uint64(0xBF58476D1CE4E5B9)
MUL2 = np.uint64(0x94D049BB133111EB)
S30, S27, S31 = np.uint64(30), np.uint64(27), np.uint64(31)


def splitmix64(x):
    z = x + GOLD
    z = (z ^ (z >> S30)) * MUL1
    z = (z ^ (z >> S27)) * MUL2
    return z ^ (z >> S31)


R = {}
z2 = np.load(V2)
z3 = np.load(V3)
z1 = np.load(V1)

# ---------- 1. FULL-CORPUS byte identity of EVERY column except player_fold ----------
print("bit-identity v3 vs v2, FULL CORPUS ...", flush=True)
bad, checked = [], []
for name in z2.files:
    if name == "player_fold":
        continue
    a, b = z2[name], z3[name]
    exp_dtype = np.uint64 if name in DIGEST_COLS else a.dtype
    same_bytes = (a.shape == b.shape) and (a.view(np.uint8).tobytes() == b.view(np.uint8).tobytes()) \
        if a.dtype.itemsize == b.dtype.itemsize else False
    ok = same_bytes and b.dtype == np.dtype(exp_dtype)
    print("  %-40s v2=%-7s v3=%-7s %s" % (name, a.dtype, b.dtype,
                                          "BYTES IDENTICAL" if same_bytes else "*** DIFFERS ***"), flush=True)
    checked.append(name)
    if not ok:
        bad.append(name)
    del a, b
R["FULL_CORPUS_byte_identity_vs_v2"] = {
    "columns_checked": checked, "all_identical": len(bad) == 0, "differing": bad,
    "scope": "FULL CORPUS, every one of 23,941,814 records (not a slice)",
    "note": "compared as RAW BYTES, so the int64->uint64 reinterpretation is proved to be "
            "a pure dtype relabel: .view(np.int64) on v3 recovers v2 exactly.",
}
print("BYTE-IDENTITY vs v2:", "ALL IDENTICAL" if not bad else "FAILURES %s" % bad, flush=True)

# ---------- 1b. the 13 v1 columns + meta, still bit-identical to v1 ----------
bad1 = []
for name in V1_CARRIED + ["meta"]:
    a, b = z1[name], z3[name]
    same = (a.shape == b.shape) and (a.view(np.uint8).tobytes() == b.view(np.uint8).tobytes())
    if not same:
        bad1.append(name)
    del a, b
R["FULL_CORPUS_byte_identity_vs_v1"] = {
    "columns_checked": V1_CARRIED + ["meta"], "all_identical": len(bad1) == 0, "differing": bad1,
    "scope": "FULL CORPUS, every record",
}
print("BYTE-IDENTITY vs v1 (13 cols + meta):",
      "ALL IDENTICAL" if not bad1 else "FAILURES %s" % bad1, flush=True)

N = len(z3["state"])
R["n_records"] = int(N)
R["n_games"] = int(z3["meta"][0])
R["n_arrays"] = len(z3.files)

# ---------- 2. THE TWO CONTRACT ASSERTIONS, literally ----------
print("contract assertions ...", flush=True)
ph = z3["player_hash"]
pf = z3["player_fold"]
assert ph.dtype == np.uint64, ph.dtype
expected_fold = (splitmix64(ph) & np.uint64(1)).astype(np.uint8)
a1 = bool(np.array_equal(pf, expected_fold))
assert a1, "player_fold != splitmix64(player_hash) & 1"
a2 = {c: str(z3[c].dtype) for c in DIGEST_COLS}
assert all(v == "uint64" for v in a2.values()), a2
print("  ASSERT player_fold == splitmix64(player_hash) & 1  -> PASS on all %d records" % N, flush=True)
print("  ASSERT uint64 dtypes on all 9 digest columns       -> PASS", flush=True)
R["contract_assertions"] = {
    "player_fold_equals_splitmix64_player_hash_and_1": a1,
    "checked_on_records": int(N),
    "digest_column_dtypes": a2,
    "all_digest_columns_uint64": True,
    "player_fold_dtype": str(pf.dtype),
    "splitmix64_source": "CANONICAL finalizer (the thread's own i4_repetition_state.py was NOT on disk)",
}

# ---------- 3. 64-bit collision audit (re-run) ----------
print("collision audit ...", flush=True)
D64 = int(len(np.unique(z3["state"])))
pair = np.empty(N, dtype=[('lo', '<u8'), ('hi', '<u8')])
pair['lo'] = z3["state_hash128_lo"]
pair['hi'] = z3["state_hash128_hi"]
D128 = int(len(np.unique(pair)))
del pair
coll = D128 - D64
R["collision_audit_64bit"] = {
    "distinct_128bit_state_keys": D128,
    "distinct_64bit_state_keys": D64,
    "collided_128bit_keys_lost_to_64bit": int(coll),
    "colliding_64bit_groups": 0 if coll == 0 else None,
    "records_in_a_colliding_group": 0 if coll == 0 else None,
    "collision_rate_per_distinct_key": coll / float(D128),
    "expected_under_random_64bit": (D128 * (D128 - 1)) / 2.0 / 2.0 ** 64,
    "unchanged_from_v2": bool(D128 == 18744120 and D64 == 18744120 and coll == 0),
}
print("  D128=%d D64=%d collisions=%d" % (D128, D64, coll), flush=True)

# ---------- 4. fold split under the NEW splitmix64 fold ----------
print("player-fold audit ...", flush=True)
uph = np.unique(ph)
n_movers = int(len(uph))
m0 = int(len(np.unique(ph[pf == 0])))
m1 = int(len(np.unique(ph[pf == 1])))
r0 = int((pf == 0).sum()); r1 = int((pf == 1).sum())
gid = z3["gidx"].astype(np.int64)
straddle = int(len(np.unique(gid * 2 + pf.astype(np.int64))) - len(np.unique(gid)))
cnt = np.bincount(np.searchsorted(uph, ph))
R["player_disjoint_split"] = {
    "fold_rule": "player_fold = splitmix64(player_hash) & 1  (v2 used player_hash & 1)",
    "distinct_movers": n_movers,
    "movers_in_fold0": m0, "movers_in_fold1": m1,
    "movers_in_BOTH_folds": n_movers - (m0 + m1),
    "movers_sum_check_equals_total": (m0 + m1) == n_movers,
    "records_fold0": r0, "records_fold1": r1,
    "records_fold1_fraction": r1 / float(N),
    "games_contributing_to_BOTH_folds": straddle,
    "n_games": int(z3["meta"][0]),
    "records_per_mover_min": int(cnt.min()),
    "records_per_mover_max": int(cnt.max()),
    "records_per_mover_median": float(np.median(cnt)),
    "movers_with_ge100_records": int((cnt >= 100).sum()),
    "movers_with_ge1000_records": int((cnt >= 1000).sum()),
    "v2_for_comparison": {"movers_in_fold0": 15306, "movers_in_fold1": 15044,
                          "movers_in_BOTH_folds": 0,
                          "records_fold0": 11887504, "records_fold1": 12054310},
}
print("  movers=%d fold0=%d fold1=%d both=%d  records %d/%d  straddling games=%d"
      % (n_movers, m0, m1, n_movers - (m0 + m1), r0, r1, straddle), flush=True)

# ---------- 5. carry-forward numbers untouched by this change ----------
R["ply_window"] = {"MIN_PLY": 6, "MAX_PLY": 30, "MAX_PLY_IS_EXCLUSIVE": True,
                   "emitted_ply_values": "6..29 inclusive",
                   "extra_records_if_ply30_included": int(z3["meta2"][0])}

json.dump(R, open(os.path.join(D, "v3_verify.json"), "w"), indent=2)
print("VERIFY DONE")
