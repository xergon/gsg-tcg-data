# i4 — transposition extraction, RULE-COMPLETE state key (Lichess standard rated 2014-07)

**Discovery period.** One record per position in the ply window `6 <= ply < 30`, from all
1,048,440 standard rated games of `lichess_db_standard_rated_2014-07.pgn.zst`.

This supersedes the pass-1 "scout" extraction, which keyed state on **FEN fields 1–5 only**.
That key is **rule-incomplete**: it omits repetition rights, so it cannot establish a
state-sufficiency *failure*. The key here is rule-complete.

## The state key

| symbol | definition |
|---|---|
| `k` | ledger key = placement / side-to-move / castling / **legal** en-passant. `chess.Board.epd()` (python-chess default `en_passant="legal"`). halfmove + fullmove **excluded**. |
| segment | the current **reversible segment**; a new one starts after any move with `chess.Board.is_irreversible(move)` on the pre-move board. |
| count-map | `{k: occurrences}` over the segment, **including** the current position; seeded at the initial position with count 1. |
| serialization | `"\n".join("<k>:<count>")` in **lexicographic key order**, UTF-8. |
| `L_t` | `blake2b(serialization, digest_size=8, person=b"i4-rep-v1")` — column `repetition_ledger_hash` |
| `X_t` | `blake2b(fen_1to5.encode() + L_t_raw8, digest_size=8, person=b"i4-rep-v1")` — column `state` |

`L_t_raw8` is the **8 raw digest bytes** of `L_t`, not its hex and not its decimal.

## Files

- `transpositions_2014-07.npz` — the data (release asset)
- `transpositions_2014-07.contract.json` — **array names, dtypes and semantics**; write against this, no round-trip needed

## What is NOT here

**No estimator, no Δ₁/Δ₂/Δ₃/Δ₄, no verdict.** i4 owns the estimator spec (Jeffreys α=1/2 with
both models sharing `K_x`, singleton/backoff rules, symmetric held-out cross-entropy) and has not
released the code. A second implementation here would risk a silently different statistic.

## Verification carried out

- Corpus sha256 `d73fa278979e3dd36d9af98c7b09c5eb03f8644ec5beccddc191af7b4959cad8`, 200,304,103 bytes
  — equals lichess's published `content-length`.
- 6-way split is byte-exact (chunk bytes sum to the original; game counts sum to 1,048,440).
- All 8 columns carried over from pass 1 are **bit-identical** to the pass-1 bench on the first
  20,000 games (458,108 records).
- Ledger hand-checked: knight-shuffle threefold reaches `occurrence_count == 3` and agrees with
  `python-chess Board.is_repetition(3)`; an intervening pawn move correctly resets the segment
  (count 2, not 3); an available legal en-passant makes every move irreversible.

## Scale delivered

| | |
|---|---|
| games | 1,048,440 |
| records | 23,941,814 |
| distinct rule-complete keys `X_t` | 18,744,120 |
| records in an `X_t` group of size >= 2 | 6,190,299 (25.86%) |

## The two findings that change what can validly be computed

1. **The ledger genuinely re-partitions the scout key.** 141,797 of the 1,013,787 multi-record
   FEN-1–5 groups (13.99%) are split by the repetition ledger; 1,253,135 records (5.23%) sit in a
   group the ledger splits. So the pass-1 key really was conflating distinct rule states — but the
   effect is 5%, not 50%.
2. **🔴 Actual repetitions are near-absent in ply 6–30.** Only 4,965 records of 23,941,814 (0.021%)
   have `current_position_occurrence_count >= 2`; `can_claim_threefold_now` is true on 183 records
   and `can_claim_threefold_after_one_move` on 528. The rule-completeness fix therefore bites almost
   entirely through **segment membership** (which reversible positions preceded), not through
   realised repetitions. **The two threefold-claim columns are near-degenerate at this window.**
   If repetition *rights* are meant to be a live discriminator, `MAX_PLY` must extend well past 30.
