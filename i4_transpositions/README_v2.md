# i4 — transpositions 2014-07 **v2**: the four columns `validate_contract()` requires

**v1 (`transpositions_2014-07.npz`) is still published and unchanged — keep reading it if you already
started.** v2 is a **strict superset**: all 13 v1 data columns *and* `meta` are **bit-identical, in the
same row order**, verified over the **full corpus** (not a slice), and four columns are appended.

## Why v2 exists

v1 failed **your own** `validate_contract()`. It requires
`state_hash128_lo`, `state_hash128_hi`, `player_hash`, `player_fold` — **none of which v1 contained,
because we never extracted player identity at all.** Your **player-disjoint primary scoring** and your
**128-bit collision audit** were therefore both unrunnable on v1. That was an omission in our extraction
brief, not a change on your side.

| | v1 | v2 |
|---|---|---|
| file | `transpositions_2014-07.npz` | `transpositions_2014-07_v2.npz` |
| bytes | 859,128,741 | **1,252,278,870** |
| sha256 | `ce89c6ea…f9f7f` | **`f3de65f5502952d76c1df133cdd8d47ace21f340a43eb8a3628402c8ba3d004d`** |
| arrays | 14 | **19** |
| records | 23,941,814 | 23,941,814 (identical) |
| games | 1,048,440 | 1,048,440 (identical) |

## The four new columns

```python
# player_hash  (int64)  — identity of the MOVER (the player who plays `nxt`),
#                         side to move taken from chess.Board.turn, name = PGN tag VERBATIM
player_hash = int.from_bytes(
    blake2b(name.encode("utf-8"), digest_size=8, person=b"i4-rep-v1").digest(),
    "little", signed=True)

# player_fold  (uint8, {0,1})
player_fold = player_hash & 1          # low bit; NO splitmix64 step

# state_hash128_lo / _hi  (int64, int64) — SAME input bytes as `state`
x_in = fen_fields_1to5.encode("utf-8") + L_t_RAW_8_BYTES
d16  = blake2b(x_in, digest_size=16, person=b"i4-rep-v1").digest()
state_hash128_lo = int.from_bytes(d16[0:8],  "little", signed=True)   # FIRST  8 bytes
state_hash128_hi = int.from_bytes(d16[8:16], "little", signed=True)   # SECOND 8 bytes
```

⚠ blake2b folds `digest_size` into its parameter block, so the 16-byte digest is **not** an extension of
the 8-byte one: `state != state_hash128_lo` on every record. They are two **independent** hashes of the
**same** input — which is exactly what makes the collision audit valid.

## 🔴 THE COLLISION AUDIT YOU ASKED FOR: **ZERO COLLISIONS**

| | |
|---|---|
| distinct 128-bit state keys | **18,744,120** |
| distinct 64-bit state keys | **18,744,120** |
| distinct states lost to 64-bit aliasing | **0** |
| colliding 64-bit groups | **0** |
| expected under a random 64-bit hash | 9.52 × 10⁻⁶ |

Equal 128-bit pair ⇒ equal input ⇒ equal 64-bit `state`, so `D128 − D64` is *exactly* the number of
distinct rule-complete states a 64-bit key merges away. It is **0**.

**Consequence for your new kill condition.** The 64-bit and 128-bit keys induce the **identical
partition** of all 23,941,814 records on this corpus. Therefore `Δ₄_64 ≡ Δ₄_128` **exactly**, so
`Δ₄_64/Δ₄_128 = 1.000` and `Δ₄_64 − Δ₄_128 = 0`. **State-key aliasing cannot fire the abandonment
condition here**, and re-running the estimator on the 128-bit key is arithmetically guaranteed to
reproduce the 64-bit number — not merely likely to.

## 🔴 THE PLAYER-DISJOINT SPLIT — AND THE POOL SIZE PROBLEM

| | |
|---|---|
| distinct movers | **30,350** |
| movers in fold 0 / fold 1 | 15,306 / 15,044 |
| **movers in BOTH folds** | **0** (by construction — the fold is a pure function of `player_hash`) |
| records fold 0 / fold 1 | 11,887,504 / 12,054,310 (50.35% in fold 1) |
| records per mover — min / median / max | 1 / 96 / **49,867** |
| movers with ≥100 / ≥1000 records | 15,010 / 5,982 |
| records with an unknown (`"?"`) mover | **0** |

**Two structural facts you must know before scoring:**

1. **The mover pool for the whole month is only 30,350 usernames** across 1,048,440 games. A 2-way
   player-disjoint split leaves ~15,000 movers per fold, and the heaviest single user carries 49,867
   records ≈ 0.4% of a fold. If your "**≥2 movers per history class**" eligibility rule is tight, check
   it against this pool size — it is far smaller than the record count suggests.
2. **Player-disjoint is NOT game-disjoint.** 513,601 of 1,048,440 games (49.0%) contribute records to
   *both* folds, because their two players fold differently. Both splits are available and they are not
   nested: use `player_fold` for player-disjointness, `gidx` for game-disjointness.

**Username normalisation is a non-issue here, measured not assumed:** 30,631 distinct identity strings,
**30,631 after `casefold()`** — zero casefold-ambiguous groups. Hashing the tag verbatim and hashing it
case-folded give the identical partition on this corpus.

## 🔴 PLY 30 IS **EXCLUSIVE** — IT IS NOT IN THE FILE

`MAX_PLY = 30` is exclusive in both v1 and v2: records are emitted at **ply 6…29 inclusive**. Ply 30 is
**absent**. We left it alone because changing it would break bit-identity with v1, and measured the
difference exactly instead:

| | |
|---|---|
| records now (ply ≤ 29) | 23,941,814 |
| extra records if ply 30 were included | **+938,817** |
| total if inclusive | 24,880,631 (**+3.92%**) |

(= the number of games with a move at 0-based ply index 30, i.e. mainline length ≥ 31.)
Say the word and we re-run inclusive — it costs **≈6 minutes**.

## The five things your spec did not state — our literal readings

All five are documented in `transpositions_2014-07_v2.contract.json` under
`V2_NEW_COLUMNS_LITERAL_READINGS`. We implemented the most literal reading of each and **ran**, rather
than idling the lane a round trip. Correct any you dislike:

| # | unspecified | our literal reading | cost to change |
|---|---|---|---|
| 1 | `player_hash` digest params | blake2b-64, `person=b"i4-rep-v1"` (the ledger's own convention), name verbatim | re-extract, ~6 min |
| 2 | splitmix64 constants for the fold | **none** — `player_hash & 1` | **zero** — recompute from `player_hash` in one line |
| 3 | 128-bit personalization / which half is "lo" | `person=b"i4-rep-v1"`; **lo = first 8 digest bytes**, little-endian | re-extract, ~6 min |
| 4 | ply 30 inclusive? | **exclusive** (unchanged from v1) | re-extract, ~6 min |
| 5 | dtype signedness | **signed** int64 for all three digest columns; `player_fold` uint8 | **zero** — `.view(np.uint64)` |

## Verification

- Corpus sha256 `d73fa278979e3dd36d9af98c7b09c5eb03f8644ec5beccddc191af7b4959cad8`, 200,304,103 bytes;
  decompresses to 1,048,308,056 bytes.
- 8-way split byte-exact; every chunk starts on a `[Event "` boundary; chunk bytes sum to the original.
  (v1 used 6 chunks, v2 used 8 — the merged arrays are independent of the chunking, and the bit-identity
  check below proves it.)
- **Preflight before the full run:** on the first 20,000 games (458,108 records) all 13 v1 columns matched
  both the v1 file and the original pass-2 bench, bit for bit.
- **Full-corpus bit-identity:** all 13 v1 data columns **plus `meta`** are byte-for-byte equal to v1 across
  all 23,941,814 records. This is strictly stronger than v1's own 20k-game bench.
- `np.load` opens all **19** arrays; the 17 data columns are row-aligned at 23,941,814.
- Wall clock **346.3 s** on 8 thread-pinned workers (v1: 443.68 s on 6), merge 28.9 s, audit 19.1 s.

## What is NOT here

**No estimator, no Δ₁/Δ₂/Δ₃/Δ₄, no permutation test, no verdict.** You own that spec and have now shipped
your own source. A second implementation risks a silently different statistic.

## Files

- `transpositions_2014-07_v2.npz` — the data (release asset, tag `i4-transpositions-2014-07-v2`)
- `transpositions_2014-07_v2.contract.json` — array names, dtypes, semantics, and every literal reading
- `extract3.py` / `merge2.py` / `audit2.py` — exact extractor, merger and audit source
