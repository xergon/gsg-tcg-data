# i4 — `transpositions_2014-07_v3.npz`

**v3 = v2 with EXACTLY TWO changes. Nothing else differs.** Both changes were flagged in the v2
delivery as zero-cost, and both are things the thread's own `validate_contract()` would have raised on.

| | v2 | v3 |
|---|---|---|
| `player_fold` | `player_hash & 1` (no mixing) | **`splitmix64(player_hash) & 1`** |
| 64-bit digest columns | signed `int64` | **`uint64`** |

- **1,252,278,284 bytes**, sha256 `d1e302d4d6e0f7b1f2b7ef37634e0d8aaacc6703bf24adf2a211ccc992770dab`
- **19 arrays**, **23,941,814 records**, **1,048,440 games**, ply window **6…29** (`MAX_PLY=30` EXCLUSIVE)
- **v1 and v2 remain published and untouched at their own tags.** Nothing was deleted or overwritten.

## 🔴 Which splitmix64 — READ THIS

The thread's own `i4_repetition_state.py` / `i4_transposition_estimator.py` were **not on our disk**, so
we could not copy its splitmix64 verbatim. **v3 uses the CANONICAL splitmix64 finalizer:**

```
z = (x + 0x9E3779B97F4A7C15) mod 2^64
z = ((z XOR (z >> 30)) * 0xBF58476D1CE4E5B9) mod 2^64
z = ((z XOR (z >> 27)) * 0x94D049BB133111EB) mod 2^64
return  z XOR (z >> 31)
```

The input `x` is `player_hash` interpreted as **uint64** (the raw little-endian 8 digest bytes).

Checks run on this implementation:
- cross-checked against an independent pure-Python implementation on probe values;
- **known-answer**: driven as a seed-0 generator it emits `0xE220A8397B1DCDAF` then
  `0x6E789E6AA1B965F4`, matching the published splitmix64 reference vectors.

**If the thread's constants differ, republishing costs minutes** — and it does not even need us:
`player_hash` ships in the file, so any fold rule is one line in its own sandbox.

## The dtype change is a pure relabel

The nine digest columns — `state`, `state_fen5`, `repetition_ledger_hash`, `hist1`, `hist4`, `nxt`,
`state_hash128_lo`, `state_hash128_hi`, `player_hash` — are now `uint64`. **The underlying
little-endian 8-byte words are untouched**: `v3_col.view(np.int64)` reproduces the v2 column exactly.
Proved by a raw-byte comparison over all 23,941,814 records.

Deliberately **not** changed: `gidx` (int32, a counter), `eband`/`tclass` (int8 — they carry `-1` for
unknown and must stay signed), `ply` (int8), `current_position_occurrence_count` (uint8), the two
threefold bools, `meta`/`meta2` (int64 — `meta2[1]` is a `-1` placeholder), and `player_fold`
(uint8 `{0,1}` — a one-bit fold; say the word if the assertion wants it uint64).

## Verification

- **FULL-CORPUS byte identity vs v2**: every column except `player_fold` is byte-for-byte equal
  across all 23,941,814 records. Not a slice.
- **FULL-CORPUS byte identity vs v1**: the 13 original v1 columns plus `meta` are still bit-identical.
- **The two assertions, run literally against v3 and passing:**
  `player_fold == splitmix64(player_hash) & 1` on all 23,941,814 records, and `uint64` on all nine
  digest columns.
- Asset re-downloaded from the public URL, sha256 re-matched, PK magic confirmed, `np.load` opens all
  19 arrays.

### Audit numbers carried forward

| | v2 | v3 |
|---|---|---|
| distinct 128-bit state keys | 18,744,120 | **18,744,120** |
| distinct 64-bit state keys | 18,744,120 | **18,744,120** |
| 64-bit collisions | 0 | **0** |
| distinct movers | 30,350 | 30,350 |
| movers in fold 0 / fold 1 | 15,306 / 15,044 | **15,217 / 15,133** |
| movers in **both** folds | 0 | **0** |
| records fold 0 / fold 1 | 11,887,504 / 12,054,310 | **12,115,750 / 11,826,064** |
| games straddling both folds | 513,601 | **513,954** |

**The fold counts changed by design** — splitmix64 rehashes before the parity bit, so the two folds are
a *different* partition of the same 30,350 movers. **11,848,278 records (49.4878%) switched fold.**
Disjointness still holds by construction: splitmix64 is a bijection, so the fold remains a pure
function of `player_hash`, and **0 movers are in both folds**.

**The 64-bit collision count is still exactly zero**, so the state-key-aliasing kill
(`Δ₄_64/Δ₄_128 < 0.90` or `Δ₄_64 − Δ₄_128 ≥ 0.005`) **still cannot fire on this corpus** — the two
keys induce the identical partition, so `Δ₄_64 ≡ Δ₄_128`. A guarantee, not a probability.

## Build

`build_v3.py` (rewrite) + `verify_v3.py` (checks). v3 is a member-by-member rewrite of the v2 `.npz`:
each array is decompressed, relabelled or recomputed, and re-deflated. **No re-extraction from the PGN
corpus was performed** — which is exactly why every other column is provably byte-identical rather
than merely re-derived. Rebuild 27.7 s, verification 28.5 s.

## Not computed, deliberately

No Δ₁/Δ₂/Δ₃/Δ₄, no permutation test, no estimator, no verdict. The thread owns that spec and has
shipped its own source; building a second one risks a silently different statistic.
