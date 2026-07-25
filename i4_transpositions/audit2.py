#!/usr/bin/env python3
"""v2 audits: full-corpus bit-identity vs v1, 64-bit collision rate, player-fold stats."""
import numpy as np, json, os, glob, sys

D = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(D, "transpositions_2014-07.npz")
V2 = os.path.join(D, "transpositions_2014-07_v2.npz")
R = {}

CARRIED = ["state", "state_fen5", "repetition_ledger_hash", "hist1", "hist4", "nxt",
           "gidx", "eband", "tclass", "ply", "current_position_occurrence_count",
           "can_claim_threefold_now", "can_claim_threefold_after_one_move"]

# ---------- 1. FULL-CORPUS bit-identity of every v1 column ----------
z1 = np.load(V1); z2 = np.load(V2)
bad = []
for c in CARRIED + ["meta"]:
    a = z1[c]; b = z2[c]
    same = (a.dtype == b.dtype) and a.shape == b.shape and np.array_equal(a, b)
    print("  %-40s %s" % (c, "identical" if same else "*** DIFFERS ***"), flush=True)
    if not same:
        bad.append(c)
    del a, b
R["bit_identity_vs_v1"] = {"columns_checked": CARRIED + ["meta"],
                           "all_identical": len(bad) == 0, "differing": bad,
                           "scope": "FULL CORPUS, every record (not a slice)"}
print("BIT-IDENTITY:", "ALL IDENTICAL" if not bad else "FAILURES %s" % bad, flush=True)

N = len(z2["state"])
R["n_records"] = int(N)
R["n_games"] = int(z2["meta"][0])

# ---------- 2. 64-bit collision audit ----------
print("collision audit ...", flush=True)
st = z2["state"]
D64 = int(len(np.unique(st)))
del st
pair = np.empty(N, dtype=[('lo', '<i8'), ('hi', '<i8')])
pair['lo'] = z2["state_hash128_lo"]
pair['hi'] = z2["state_hash128_hi"]
u128 = np.unique(pair)
D128 = int(len(u128))
del u128
coll = D128 - D64
R["collision_audit_64bit"] = {
    "distinct_128bit_state_keys": D128,
    "distinct_64bit_state_keys": D64,
    "collided_128bit_keys_lost_to_64bit": int(coll),
    "collision_rate_per_distinct_key": coll / D128 if D128 else 0.0,
    "expected_under_random_64bit": (D128 * (D128 - 1)) / 2.0 / 2.0**64,
    "method": "equal 128-bit pair => equal input => equal 64-bit state, so "
              "D128 - D64 is exactly the number of distinct rule-complete states "
              "that a 64-bit key merges away",
}
print("  D128=%d D64=%d collisions=%d" % (D128, D64, coll), flush=True)

if coll > 0:
    order = np.lexsort((pair['hi'], pair['lo'], z2["state"]))
    s_sorted = z2["state"][order]
    p_sorted = pair[order]
    new_state = np.empty(N, dtype=bool); new_state[0] = True
    new_state[1:] = s_sorted[1:] != s_sorted[:-1]
    new_pair = np.empty(N, dtype=bool); new_pair[0] = True
    new_pair[1:] = (p_sorted['lo'][1:] != p_sorted['lo'][:-1]) | (p_sorted['hi'][1:] != p_sorted['hi'][:-1])
    gid = np.cumsum(new_state) - 1
    ndistinct = np.bincount(gid, weights=new_pair.astype(np.int64)).astype(np.int64)
    gsize = np.bincount(gid)
    badg = ndistinct > 1
    R["collision_audit_64bit"]["colliding_64bit_groups"] = int(badg.sum())
    R["collision_audit_64bit"]["records_in_a_colliding_group"] = int(gsize[badg].sum())
    del order, s_sorted, p_sorted, new_state, new_pair, gid, ndistinct, gsize
else:
    R["collision_audit_64bit"]["colliding_64bit_groups"] = 0
    R["collision_audit_64bit"]["records_in_a_colliding_group"] = 0
del pair

# ---------- 3. player / fold statistics ----------
print("player-fold audit ...", flush=True)
ph = z2["player_hash"]; pf = z2["player_fold"]
uph = np.unique(ph)
n_movers = int(len(uph))
fold_of_mover = (uph & 1).astype(np.uint8)
consistent = bool(np.array_equal(pf.astype(np.int64), (ph & 1).astype(np.int64)))
m0 = int(len(np.unique(ph[pf == 0])))
m1 = int(len(np.unique(ph[pf == 1])))
r0 = int((pf == 0).sum()); r1 = int((pf == 1).sum())
gid = z2["gidx"].astype(np.int64)
straddle = int(len(np.unique(gid * 2 + pf.astype(np.int64))) - len(np.unique(gid)))
cnt = np.bincount(np.searchsorted(uph, ph))
R["player_disjoint_split"] = {
    "distinct_movers": n_movers,
    "movers_in_fold0": m0, "movers_in_fold1": m1,
    "movers_in_BOTH_folds": n_movers - (m0 + m1) if (m0 + m1) <= n_movers else -1,
    "movers_sum_check_equals_total": (m0 + m1) == n_movers,
    "records_fold0": r0, "records_fold1": r1,
    "records_fold1_fraction": r1 / float(N),
    "player_fold_equals_low_bit_of_player_hash_on_every_record": consistent,
    "games_contributing_to_BOTH_folds": straddle,
    "n_games": int(z2["meta"][0]),
    "records_per_mover_min": int(cnt.min()), "records_per_mover_max": int(cnt.max()),
    "records_per_mover_median": float(np.median(cnt)),
    "note": "fold is a pure function of player_hash, so a mover is in exactly one fold "
            "BY CONSTRUCTION. A GAME however contributes to both folds whenever its two "
            "players fold differently -- player-disjointness is at the MOVER level, and it "
            "is NOT game-disjoint. Both are available: gidx for game-disjoint, player_fold "
            "for player-disjoint.",
}
print("  movers=%d fold0=%d fold1=%d both=%d records %d/%d straddling games=%d"
      % (n_movers, m0, m1, n_movers - (m0 + m1), r0, r1, straddle), flush=True)
del ph, pf, uph, gid, cnt

# ---------- 4. ply-30 delta ----------
m2 = z2["meta2"]
R["ply30_inclusive_delta"] = {
    "current_build": "MAX_PLY=30 EXCLUSIVE -- records at ply 6..29 inclusive; ply 30 IS NOT INCLUDED",
    "records_now": int(N),
    "extra_records_if_ply30_included": int(m2[0]),
    "records_if_ply30_included": int(N) + int(m2[0]),
    "pct_increase": 100.0 * int(m2[0]) / float(N),
    "definition": "exactly the number of games that have a move at 0-based ply index 30 "
                  "(i.e. mainline length >= 31); each would emit one extra record",
}
print("  ply30 extra records:", int(m2[0]), flush=True)

# ---------- 5. username normalisation finding ----------
names = {}
for p in sorted(glob.glob(os.path.join(D, "names_*.tsv"))):
    with open(p, encoding="utf-8") as f:
        for line in f:
            h, _, nm = line.rstrip("\n").partition("\t")
            names[nm] = h
cf = {}
for nm in names:
    cf.setdefault(nm.casefold(), []).append(nm)
dup = {k: v for k, v in cf.items() if len(v) > 1}
R["identity_string_normalisation"] = {
    "distinct_identity_strings_hashed": len(names),
    "distinct_after_casefold": len(cf),
    "casefold_groups_with_more_than_one_spelling": len(dup),
    "extra_identities_created_by_NOT_casefolding": len(names) - len(cf),
    "unknown_player_tag_present": "?" in names,
    "choice": "PGN tag hashed VERBATIM (no casefold / strip / normalise) -- the literal reading",
    "example_casefold_groups": [v for v in list(dup.values())[:5]],
}
print("  identity strings=%d casefolded=%d ambiguous groups=%d"
      % (len(names), len(cf), len(dup)), flush=True)

json.dump(R, open(os.path.join(D, "audit2_result.json"), "w"), indent=2)
print("AUDIT DONE")
