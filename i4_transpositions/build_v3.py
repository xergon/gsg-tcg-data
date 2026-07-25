#!/usr/bin/env python3
"""
v3 = v2 with EXACTLY TWO changes, both previously assessed as zero-cost:

  1. player_fold = splitmix64(player_hash) & 1     (v2 shipped player_hash & 1, no mixing)
  2. every 64-bit DIGEST column is uint64          (v2 shipped signed int64)

Nothing else changes.  Every other column keeps the SAME BYTES as v2 (and therefore as
v1 for the 13 original columns).  The dtype change is a pure reinterpretation: the
underlying little-endian 8-byte words are untouched, so .view(np.int64) recovers v2
exactly.

splitmix64: the CANONICAL finalizer.  The thread's own i4_repetition_state.py was NOT
on disk, so this is the standard reference form and it is documented in the contract:
    z = (x + 0x9E3779B97F4A7C15) mod 2**64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) mod 2**64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) mod 2**64
    return z ^ (z >> 31)
"""
import io, os, sys, json, time, zipfile
import numpy as np

D = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.join(D, "transpositions_2014-07_v2.npz")
V3 = os.path.join(D, "transpositions_2014-07_v3.npz")

# columns whose 8-byte words are BLAKE2b digest material -> uint64 in v3
DIGEST_COLS = ["state", "state_fen5", "repetition_ledger_hash", "hist1", "hist4", "nxt",
               "state_hash128_lo", "state_hash128_hi", "player_hash"]

GOLD = np.uint64(0x9E3779B97F4A7C15)
MUL1 = np.uint64(0xBF58476D1CE4E5B9)
MUL2 = np.uint64(0x94D049BB133111EB)
S30, S27, S31 = np.uint64(30), np.uint64(27), np.uint64(31)


def splitmix64(x):
    """canonical splitmix64 finalizer, vectorised; x must be uint64"""
    z = x + GOLD
    z = (z ^ (z >> S30)) * MUL1
    z = (z ^ (z >> S27)) * MUL2
    return z ^ (z >> S31)


def splitmix64_ref(x):
    """independent pure-python reference, for cross-check"""
    M = (1 << 64) - 1
    z = (x + 0x9E3779B97F4A7C15) & M
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M
    return z ^ (z >> 31)


def main():
    t0 = time.time()
    zin = np.load(V2)
    order = [n[:-4] for n in zipfile.ZipFile(V2).namelist()]
    print("v2 members:", order, flush=True)

    # --- cross-check the vectorised splitmix64 against the pure-python reference
    probe = np.array([0, 1, 2, 0xFFFFFFFFFFFFFFFF, 0x123456789ABCDEF0,
                      0x9E3779B97F4A7C15], dtype=np.uint64)
    got = splitmix64(probe)
    exp = np.array([splitmix64_ref(int(v)) for v in probe], dtype=np.uint64)
    assert np.array_equal(got, exp), (got, exp)
    # known-answer probe: splitmix64 driven from seed 0 (state += GOLD then finalize)
    ka1 = int(splitmix64(np.array([0], dtype=np.uint64))[0])
    ka2 = int(splitmix64(np.array([GOLD], dtype=np.uint64))[0])
    print("splitmix64 vectorised == pure-python reference. "
          "KNOWN-ANSWER seed0 out1=0x%016X out2=0x%016X "
          "(reference: 0xE220A8397B1DCDAF, 0x6E789E6AA1B965F4)" % (ka1, ka2), flush=True)

    # --- new fold
    ph_u = zin["player_hash"].view(np.uint64)
    new_fold = (splitmix64(ph_u) & np.uint64(1)).astype(np.uint8)
    old_fold = zin["player_fold"]
    n_changed = int((new_fold != old_fold).sum())
    print("fold recomputed: %d / %d records change fold (%.4f%%)"
          % (n_changed, len(new_fold), 100.0 * n_changed / len(new_fold)), flush=True)
    del old_fold, ph_u

    # --- write v3, member by member, streaming (low memory)
    with zipfile.ZipFile(V3, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zo:
        for name in order:
            if name == "player_fold":
                arr = new_fold
            else:
                arr = zin[name]
                if name in DIGEST_COLS:
                    arr = arr.view(np.uint64)
            zi = zipfile.ZipInfo(name + ".npy", date_time=(1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            with zo.open(zi, "w", force_zip64=True) as f:
                np.lib.format.write_array(f, arr, allow_pickle=False)
            print("  wrote %-40s %s %s" % (name, arr.dtype, arr.shape), flush=True)
            del arr
    dt = time.time() - t0
    sz = os.path.getsize(V3)
    print("V3 WRITTEN %s bytes in %.1f s" % (sz, dt), flush=True)
    json.dump({"bytes": sz, "wall_s": round(dt, 2),
               "records_changing_fold": n_changed}, open(os.path.join(D, "v3_build.json"), "w"))


if __name__ == "__main__":
    main()
