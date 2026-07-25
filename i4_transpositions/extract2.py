#!/usr/bin/env python3
"""
i4 STATE-SUFFICIENCY BREAK-HUNT -- pass 2: RULE-COMPLETE extraction.

Pass 1 keyed state on FEN fields 1-5 only. i4 rejected that as rule-incomplete: it
omits repetition rights, so it is "only a scout" and cannot establish a
state-sufficiency FAILURE. This implements i4's byte-level repetition-ledger spec.

SPEC AS IMPLEMENTED (every choice documented; see CONTRACT json emitted by merge.py)

  ledger key  k  = placement / side-to-move / castling / LEGAL en-passant
                 = python-chess  Board.epd()   [default en_passant="legal";
                   verified equal to " ".join(fen().split(" ")[:4])]
                 halfmove + fullmove counters are EXCLUDED, as specified.

  reversible segment: a new segment starts AFTER any irreversible move, where
                 irreversible == chess.Board.is_irreversible(move), evaluated on the
                 PRE-move board.  (python-chess: is_zeroing or _reduces_castling_rights
                 or has_legal_en_passant.)  On an irreversible move the count-map is
                 cleared and re-seeded with the post-move position at count 1.

  count-map  = {k: occurrences} over the current reversible segment, INCLUDING the
                 current position.  Seeded at the game's initial position with count 1.

  serialization = "\\n".join("<k>:<count>") over items sorted in LEXICOGRAPHIC KEY
                 ORDER (Python sorted() on the ASCII EPD strings == byte order),
                 encoded UTF-8.

  L_t = repetition_ledger_hash = BLAKE2b(serialization, digest_size=8, person=b"i4-rep-v1")

  X_t = state = BLAKE2b( fen1to5.encode("utf-8") || L_t_raw8 , digest_size=8,
                         person=b"i4-rep-v1")
        where L_t_raw8 are the 8 RAW digest bytes of L_t (not its hex, not its decimal).

  All 64-bit digests are exposed as int64 via int.from_bytes(d, "little", signed=True).

  hist1 / hist4 / nxt keep the pass-1 hash exactly: UNPERSONALIZED blake2b(digest_size=8),
  so those columns stay bit-identical to the pass-1 bench.

  state_fen5 = the pass-1 scout key, h64(fen fields 1-5), carried alongside so i4 can
  measure directly how much the rule-complete key re-partitions the scout key.

COMPANION FIELDS
  current_position_occurrence_count  = count-map[k_current], >= 1 (includes current).
  can_claim_threefold_now            = count >= 3 for the CURRENT position.
       NB: python-chess Board.can_claim_threefold_repetition() is NOT used -- it returns
       True also when a repetition "is reached with one of the possible legal moves",
       which is i4's OTHER field. Using it for _now would silently merge the two.
  can_claim_threefold_after_one_move = exists a legal move m such that the resulting
       position has occurred 3 times. An irreversible m resets the segment, so it can
       never qualify; and a qualifying m requires some existing key at count >= 2. That
       gives an EXACT short-circuit (max(count-map.values()) >= 2) used to avoid
       generating legal moves at >99% of records. Reported independently of _now.

No verdict, no estimator, no deltas are produced here. i4 owns the estimator.
"""
import sys, os, hashlib, argparse
from array import array
import numpy as np
import chess
import chess.pgn

MIN_PLY = int(os.environ.get("MIN_PLY", "6"))
MAX_PLY = int(os.environ.get("MAX_PLY", "30"))
PERSON = b"i4-rep-v1"
_b2b = hashlib.blake2b


def h64(s):
    """pass-1 hash, UNPERSONALIZED -- keeps hist1/hist4/nxt/state_fen5 bit-identical."""
    return int.from_bytes(_b2b(s.encode(), digest_size=8).digest(), "little", signed=True)


def d8(data):
    """personalized 64-bit blake2b, raw 8 bytes"""
    return _b2b(data, digest_size=8, person=PERSON).digest()


def to_i64(d):
    return int.from_bytes(d, "little", signed=True)


def elo_band(w, b):
    try:
        m = (int(w) + int(b)) / 2.0
    except Exception:
        return -1
    if m < 1400: return 0
    if m < 1600: return 1
    if m < 1800: return 2
    if m < 2000: return 3
    if m < 2200: return 4
    return 5


def tc_class(tc):
    try:
        base, inc = tc.split("+")
        est = int(base) + 40 * int(inc)
    except Exception:
        return -1
    if est < 179: return 0
    if est < 479: return 1
    if est < 1499: return 2
    return 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--pgn", default="-")
    ap.add_argument("--max-games", type=int, default=0)
    ap.add_argument("--progress-every", type=int, default=100000)
    ap.add_argument("--selfcheck", action="store_true",
                    help="assert epd()==fen[:4] and fen5==epd+' '+halfmove on every record")
    a = ap.parse_args()

    fh = sys.stdin if a.pgn == "-" else open(a.pgn, "r", encoding="utf-8", errors="replace")

    state = array("q"); state_fen5 = array("q"); ledhash = array("q")
    hist1 = array("q"); hist4 = array("q"); nxt = array("q")
    gidx = array("i")
    eband = array("b"); tclass = array("b"); plyv = array("b")
    occv = array("B"); claim_now = array("B"); claim_next = array("B")

    ngames = 0
    nskip_novariant = 0
    n_legalmove_scans = 0

    while True:
        try:
            game = chess.pgn.read_game(fh)
        except Exception:
            continue
        if game is None:
            break
        hdr = game.headers
        if hdr.get("Variant", "Standard") != "Standard":
            nskip_novariant += 1
            continue
        eb = elo_band(hdr.get("WhiteElo", ""), hdr.get("BlackElo", ""))
        tc = tc_class(hdr.get("TimeControl", ""))

        board = game.board()
        k = board.epd()
        ledger = {k: 1}
        max_count = 1

        ucis = []
        ply = 0
        for mv in game.mainline_moves():
            if ply >= MAX_PLY:
                break
            if ply >= MIN_PLY and len(ucis) >= 4:
                fen5 = k + " " + str(board.halfmove_clock)
                if a.selfcheck:
                    ff = board.fen().split(" ")
                    assert k == " ".join(ff[:4]), (k, board.fen())
                    assert fen5 == " ".join(ff[:5]), (fen5, board.fen())

                payload = "\n".join(kk + ":" + str(cc) for kk, cc in sorted(ledger.items()))
                Lraw = d8(payload.encode("utf-8"))
                Xraw = d8(fen5.encode("utf-8") + Lraw)

                occ = ledger[k]
                cnow = 1 if occ >= 3 else 0
                cnext = 0
                if max_count >= 2:                       # EXACT short-circuit
                    n_legalmove_scans += 1
                    for m2 in board.legal_moves:
                        if board.is_irreversible(m2):
                            continue
                        board.push(m2)
                        c2 = ledger.get(board.epd(), 0) + 1
                        board.pop()
                        if c2 >= 3:
                            cnext = 1
                            break

                state.append(to_i64(Xraw))
                ledhash.append(to_i64(Lraw))
                state_fen5.append(h64(fen5))
                hist1.append(h64(ucis[-1]))
                hist4.append(h64(" ".join(ucis[-4:])))
                nxt.append(h64(mv.uci()))
                gidx.append(ngames)
                eband.append(eb)
                tclass.append(tc)
                plyv.append(ply)
                occv.append(255 if occ > 255 else occ)
                claim_now.append(cnow)
                claim_next.append(cnext)

            try:
                irrev = board.is_irreversible(mv)
                board.push(mv)
            except Exception:
                break
            k = board.epd()
            if irrev:
                ledger = {k: 1}
                max_count = 1
            else:
                c = ledger.get(k, 0) + 1
                ledger[k] = c
                if c > max_count:
                    max_count = c
            ucis.append(mv.uci())
            ply += 1

        ngames += 1
        if a.progress_every and ngames % a.progress_every == 0:
            print(f"  games={ngames:,} records={len(state):,}", file=sys.stderr, flush=True)
        if a.max_games and ngames >= a.max_games:
            break

    def npa(arr, dt):
        return np.frombuffer(arr, dtype=dt)

    np.savez_compressed(
        a.out,
        state=npa(state, np.int64),
        state_fen5=npa(state_fen5, np.int64),
        repetition_ledger_hash=npa(ledhash, np.int64),
        hist1=npa(hist1, np.int64),
        hist4=npa(hist4, np.int64),
        nxt=npa(nxt, np.int64),
        gidx=npa(gidx, np.int32),
        eband=npa(eband, np.int8),
        tclass=npa(tclass, np.int8),
        ply=npa(plyv, np.int8),
        current_position_occurrence_count=npa(occv, np.uint8),
        can_claim_threefold_now=npa(claim_now, np.uint8).astype(bool),
        can_claim_threefold_after_one_move=npa(claim_next, np.uint8).astype(bool),
        meta=np.array([ngames, len(state), MIN_PLY, MAX_PLY, nskip_novariant,
                       n_legalmove_scans], dtype=np.int64),
    )
    print(f"DONE games={ngames:,} records={len(state):,} skipped_variant={nskip_novariant:,} "
          f"legalmove_scans={n_legalmove_scans:,} -> {a.out}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
