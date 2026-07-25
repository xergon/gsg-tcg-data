#!/usr/bin/env python3
"""Emit transpositions_2014-07_v2.contract.json from the merge + audit results."""
import json, os, numpy as np

D = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(D, "merge2_result.json")))
A = json.load(open(os.path.join(D, "audit2_result.json")))
RUN = json.load(open(os.path.join(D, "run2_timing.json")))
V1 = json.load(open(os.path.join(D, "transpositions_2014-07.contract.json")))

c = {
  "file": "transpositions_2014-07_v2.npz",
  "supersedes": "transpositions_2014-07.npz (v1) -- v1 REMAINS PUBLISHED AND UNCHANGED; "
                "v2 is a strict superset: all 13 v1 data columns plus `meta` are BIT-IDENTICAL, "
                "in the same row order, and four columns are APPENDED.",
  "why_v2": "v1 failed i4's own validate_contract(): it requires state_hash128_lo, "
            "state_hash128_hi, player_hash, player_fold, none of which v1 contained, so i4's "
            "player-disjoint primary scoring and its 128-bit collision audit were both unrunnable. "
            "That was an omission in the extraction brief, not a thread-side change.",
  "bytes": M["bytes"],
  "sha256": M["sha256"],
  "format": "numpy .npz (zip, DEFLATE). np.load(path); z['<name>'] -> 1-D array.",
  "n_records": M["n_records"],
  "n_games": M["n_games"],
  "all_columns_are_row_aligned_1d_length": M["n_records"],
  "source_corpus": V1["source_corpus"],
  "scope": {
    "MIN_PLY": M["meta"][2],
    "MAX_PLY": M["meta"][3],
    "MAX_PLY_IS_EXCLUSIVE": True,
    "PLY_30_IS_NOT_INCLUDED": True,
    "rule": "one record per ply p with MIN_PLY <= p < MAX_PLY and at least 4 preceding plies; "
            "the record describes the position BEFORE the move stored in nxt. "
            "Emitted ply values are 6..29 INCLUSIVE. Ply 30 is NOT emitted.",
    "variant_games_skipped": M["meta"][4],
    "ply30_inclusive_would_add": A["ply30_inclusive_delta"],
  },
  "hashing": {
    "digest": "BLAKE2b",
    "personalization": "b'i4-rep-v1' (repetition_ledger_hash, state, state_hash128_lo/hi, player_hash)",
    "int64_encoding": "int.from_bytes(digest, 'little', signed=True) -- SIGNED int64 for every "
                      "digest column. Reinterpret as unsigned at zero cost with .view(np.uint64).",
    "unpersonalized_columns": ["state_fen5", "hist1", "hist4", "nxt"],
    "note": "state_fen5/hist1/hist4/nxt use blake2b(digest_size=8) with NO personalization, "
            "bit-identical to the pass-1 scout extraction and to v1."
  },
  "repetition_ledger_spec_as_implemented": V1["repetition_ledger_spec_as_implemented"],

  "V2_NEW_COLUMNS_LITERAL_READINGS": {
    "STATUS": "i4's spec was SILENT on all five points below. We implemented the most literal, "
              "most obvious reading of each and RAN, rather than idling the lane for a "
              "~20-minute round trip. EVERY ONE IS A ONE-LINE RECOMPUTE OR A ~7-MINUTE "
              "RE-EXTRACTION. Correct any you dislike.",
    "1_player_hash_digest_params": {
      "chosen": "blake2b(name.encode('utf-8'), digest_size=8, person=b'i4-rep-v1'), "
                "int.from_bytes(..., 'little', signed=True)",
      "why": "the same convention the repetition ledger already uses; NOT the unpersonalized "
             "h64() used by the pass-1-compatible columns, because player identity is new in "
             "this pass and has no pass-1 bench to stay bit-compatible with",
      "identity_string": "the PGN White/Black tag VERBATIM -- no casefold, no strip, no "
                         "unicode normalisation. python-chess supplies '?' when the tag is absent.",
      "which_player": "the MOVER: the side to move in the position the record describes, i.e. "
                      "the player who plays the move stored in `nxt`. Taken from chess.Board.turn "
                      "(WHITE -> 'White' tag, BLACK -> 'Black' tag), NOT from ply parity arithmetic.",
      "recompute_cost": "re-extraction, ~7 min"
    },
    "2_player_fold_splitmix64_constants": {
      "chosen": "player_fold = player_hash & 1  -- the LOW BIT of the 64-bit digest. NO splitmix64 "
                "mixing step, no constants.",
      "why": "blake2b output is already uniform, so its low bit is an unbiased fair coin; adding "
             "splitmix64 constants would be a second undocumented choice with no benefit",
      "disjointness": "fold is a PURE FUNCTION of player_hash, so no mover can appear in both "
                      "folds. Disjointness is by construction, and was verified on every record.",
      "recompute_cost": "ZERO re-extraction -- player_hash is in the file, so any alternative "
                        "fold rule (splitmix64, top bit, k-way, stratified) is one line in your sandbox"
    },
    "3_128bit_personalization_and_which_half_is_lo": {
      "input_bytes": "IDENTICAL to the `state` column: fen_fields_1to5.encode('utf-8') || L_t_RAW_8_BYTES",
      "chosen": "d16 = blake2b(x_in, digest_size=16, person=b'i4-rep-v1').digest(); "
                "state_hash128_lo = int.from_bytes(d16[0:8], 'little', signed=True); "
                "state_hash128_hi = int.from_bytes(d16[8:16], 'little', signed=True)",
      "lo_is": "the FIRST eight digest bytes, little-endian -- matching the existing "
               "little-endian int64 encoding used for every other digest column",
      "READ_THIS": "blake2b folds digest_size into its parameter block, so the 16-byte digest is "
                   "NOT an extension of the 8-byte one: state != state_hash128_lo on every record. "
                   "They are two INDEPENDENT hashes of the SAME input bytes. That is exactly what "
                   "makes the collision audit valid -- equal 128-bit pair => equal input => equal "
                   "64-bit state, so any group sharing `state` but not (lo,hi) is a genuine "
                   "64-bit collision.",
      "recompute_cost": "re-extraction, ~7 min"
    },
    "4_ply_30_inclusive_or_exclusive": {
      "chosen": "EXCLUSIVE -- unchanged from v1. Records are emitted at ply 6..29; PLY 30 IS ABSENT.",
      "why": "changing it would break bit-identity with v1, which was the other hard requirement. "
             "Measured instead, exactly.",
      "measured": A["ply30_inclusive_delta"],
      "recompute_cost": "re-extraction, ~7 min -- say the word"
    },
    "5_dtype_signedness": {
      "chosen": "SIGNED int64 for state_hash128_lo, state_hash128_hi and player_hash "
                "(int.from_bytes(..., 'little', signed=True)), matching every existing digest "
                "column in v1. player_fold is uint8 with values {0,1}.",
      "recompute_cost": "ZERO -- arr.view(np.uint64) reinterprets in place"
    }
  },

  "columns": dict(V1["columns"], **{
    "state_hash128_lo": {"dtype": "int64", "meaning": "low 64 bits (first 8 digest bytes, "
        "little-endian, signed) of the 128-bit blake2b of the SAME input as `state`"},
    "state_hash128_hi": {"dtype": "int64", "meaning": "high 64 bits (last 8 digest bytes, "
        "little-endian, signed) of the same 128-bit digest. (lo,hi) together are the "
        "collision-audit reference key."},
    "player_hash": {"dtype": "int64", "meaning": "blake2b-64(person='i4-rep-v1') of the MOVER's "
        "PGN username, verbatim. The mover is the side to move, i.e. whoever plays `nxt`."},
    "player_fold": {"dtype": "uint8", "meaning": "player_hash & 1, in {0,1}. Player-disjoint "
        "2-way split: a mover is in exactly one fold BY CONSTRUCTION. NOTE this is not "
        "game-disjoint -- a game whose two players fold differently contributes to both folds. "
        "Use gidx for game-disjoint splits."},
    "meta": {"dtype": "int64", "shape": 6, "meaning": "[n_games, n_records, MIN_PLY, MAX_PLY, "
        "variant_games_skipped, n_legalmove_scans] -- BIT-IDENTICAL to v1"},
    "meta2": {"dtype": "int64", "shape": 2, "meaning": "[n_games_with_a_move_at_ply_index_30, -1]. "
        "meta2[0] is exactly the number of extra records a ply-30-INCLUSIVE build would emit. "
        "meta2[1] is a placeholder (-1): per-chunk distinct-name counts are not globally unique; "
        "the global distinct-mover count is in verification.player_disjoint_split."},
  }),

  "not_computed_here": "No estimator, no delta_1/2/3/4, no verdict, no permutation test. i4 owns "
                       "the estimator spec and has now shipped its own source; building a second "
                       "one risks a silently different statistic.",

  "verification": {
    "corpus_sha256_matches_staged_and_publisher": True,
    "corpus_sha256": V1["source_corpus"]["sha256"],
    "decompressed_bytes": 1048308056,
    "eight_way_split_byte_exact": "chunk bytes sum to 1048308056 == decompressed original; "
                                  "every chunk starts on a '[Event \"' game boundary",
    "split_count_is_irrelevant_to_output": "v1 used 6 chunks, v2 used 8. The merged arrays are "
                                           "independent of the chunking: chunks partition the game "
                                           "stream in order and gidx offsets accumulate, so the "
                                           "concatenation is identical either way -- as the "
                                           "bit-identity check below confirms on the full corpus.",
    "PREFLIGHT_bit_identity_20k_games": "on the first 20,000 games (458,108 records) all 13 v1 "
                                        "columns matched the v1 file AND the original pass-2 "
                                        "bench, bit for bit, BEFORE the full run was launched",
    "FULL_CORPUS_bit_identity_vs_v1": A["bit_identity_vs_v1"],
    "collision_audit_64bit": A["collision_audit_64bit"],
    "player_disjoint_split": A["player_disjoint_split"],
    "identity_string_normalisation": A["identity_string_normalisation"],
    "repartition_full_corpus": V1["verification"]["repartition_full_corpus"],
    "transposition_density": V1["verification"]["transposition_density"],
    "repetition_rarity_in_this_ply_window": V1["verification"]["repetition_rarity_in_this_ply_window"],
    "ledger_hand_checks": V1["verification"]["ledger_hand_checks"],
    "run": RUN,
  }
}
p = os.path.join(D, "transpositions_2014-07_v2.contract.json")
json.dump(c, open(p, "w"), indent=2)
print("wrote", p, os.path.getsize(p))
