#!/usr/bin/env python3
"""
i4 STATE-SUFFICIENCY BREAK-HUNT -- pass 3 (v2 artifact): RULE-COMPLETE extraction
PLUS the four columns i4's own validate_contract() requires and pass 2 omitted:

    state_hash128_lo, state_hash128_hi, player_hash, player_fold

EVERYTHING ELSE IS UNCHANGED FROM extract2.py, BYTE FOR BYTE IN OUTPUT.
The 13 data columns of pass 2 are reproduced bit-identically; this file only APPENDS.

-----------------------------------------------------------------------------------
NEW COLUMNS -- LITERAL READINGS (the thread's spec was silent; every choice is
documented here and in the contract JSON, and every one is a one-line recompute)
-----------------------------------------------------------------------------------

player_hash (int64)
    Identity of the MOVER at this record -- the player to move in the position the
    record describes, i.e. the player who plays the move stored in `nxt`.
    Side to move is taken from chess.Board.turn (WHITE -> PGN "White" tag,
    BLACK -> PGN "Black" tag).  The identity STRING is the PGN tag VERBATIM, with no
    case-folding, stripping or normalisation (python-chess supplies "?" when absent).

        player_hash = int.from_bytes(
            blake2b(name.encode("utf-8"), digest_size=8, person=b"i4-rep-v1").digest(),
            "little", signed=True)

    LITERAL READING CHOSEN: the same blake2b-64 + person=b"i4-rep-v1" convention the
    ledger already uses (d8() below).  Not the unpersonalized h64() used by the
    pass-1-compatible columns, because player identity is new in this pass and has no
    pass-1 bench to stay compatible with.

player_fold (uint8, values {0,1})
    A deterministic 2-way fold of player_hash:

        player_fold = player_hash & 1          # low bit of the 64-bit digest

    LITERAL READING CHOSEN: no splitmix64 mixing step.  blake2b output is already
    uniform, so the low bit is an unbiased fair coin; adding constants would only be
    an undocumented second choice.  Because the fold is a pure function of
    player_hash, NO MOVER CAN LAND IN BOTH FOLDS -- disjointness is by construction.
    If i4 wants a different fold rule it recomputes it from player_hash in one line
    and never needs a re-extraction.

state_hash128_lo / state_hash128_hi (int64, int64)
    A 128-bit digest of EXACTLY the same input bytes as the 64-bit `state` column:

        x_in  = fen_fields_1to5.encode("utf-8") || L_t_RAW_8_BYTES     (identical to `state`)
        d16   = blake2b(x_in, digest_size=16, person=b"i4-rep-v1").digest()
        lo    = int.from_bytes(d16[0:8],  "little", signed=True)   # FIRST  8 bytes
        hi    = int.from_bytes(d16[8:16], "little", signed=True)   # SECOND 8 bytes

    LITERAL READINGS CHOSEN: same personalization b"i4-rep-v1" as `state`; "lo" is the
    FIRST eight digest bytes, matching the existing little-endian int64 encoding used
    everywhere in this file; signed int64, matching every other digest column (the
    thread can reinterpret at zero cost with .view(np.uint64)).

    NOTE, and it is the property that makes the collision audit valid: blake2b folds
    digest_size into its parameter block, so the 16-byte digest is NOT an extension of
    the 8-byte one and `state` != state_hash128_lo.  They are two INDEPENDENT hashes of
    the same input.  Equal 128-bit pair => equal input => equal 64-bit `state`;
    therefore any group that shares `state` but not (lo,hi) is a genuine 64-bit collision.

PLY WINDOW -- UNCHANGED AND FLAGGED
    MAX_PLY=30 is EXCLUSIVE, exactly as in pass 2: records are emitted at ply
    6..29 inclusive.  Ply 30 is NOT included.  Changing this would break bit-identity
    with pass 2, so it is left alone and measured instead: meta2[0] counts the games
    that have a move at ply index 30, which is exactly the number of records a
    ply-30-INCLUSIVE build would add.
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


def d16(data):
    """personalized 128-bit blake2b, raw 16 bytes"""
    return _b2b(data, digest_size=16, person=PERSON).digest()


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
    ap.add_argument("--names-out", default="",
                    help="optional: write one 'player_hash\\tname' line per DISTINCT name seen")
    ap.add_argument("--selfcheck", action="store_true",
                    help="assert epd()==fen[:4] and fen5==epd+' '+halfmove on every record")
    a = ap.parse_args()

    fh = sys.stdin if a.pgn == "-" else open(a.pgn, "r", encoding="utf-8", errors="replace")

    state = array("q"); state_fen5 = array("q"); ledhash = array("q")
    hist1 = array("q"); hist4 = array("q"); nxt = array("q")
    gidx = array("i")
    eband = array("b"); tclass = array("b"); plyv = array("b")
    occv = array("B"); claim_now = array("B"); claim_next = array("B")
    # --- v2 additions ---
    s128lo = array("q"); s128hi = array("q")
    phash = array("q"); pfold = array("B")

    namecache = {}          # name string -> (player_hash, player_fold)
    ngames = 0
    nskip_novariant = 0
    n_legalmove_scans = 0
    n_games_with_ply30 = 0  # games that HAVE a move at ply index 30 (ply-30-inclusive delta)

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

        # --- v2: mover identity, hashed ONCE per game, selected per record by board.turn
        nw = hdr.get("White", "?")
        nb = hdr.get("Black", "?")
        try:
            phw, pfw = namecache[nw]
        except KeyError:
            phw = to_i64(d8(nw.encode("utf-8"))); pfw = phw & 1
            namecache[nw] = (phw, pfw)
        try:
            phb, pfb = namecache[nb]
        except KeyError:
            phb = to_i64(d8(nb.encode("utf-8"))); pfb = phb & 1
            namecache[nb] = (phb, pfb)

        board = game.board()
        k = board.epd()
        ledger = {k: 1}
        max_count = 1

        ucis = []
        ply = 0
        for mv in game.mainline_moves():
            if ply >= MAX_PLY:
                n_games_with_ply30 += 1     # a move exists at ply index MAX_PLY
                break
            if ply >= MIN_PLY and len(ucis) >= 4:
                fen5 = k + " " + str(board.halfmove_clock)
                if a.selfcheck:
                    ff = board.fen().split(" ")
                    assert k == " ".join(ff[:4]), (k, board.fen())
                    assert fen5 == " ".join(ff[:5]), (fen5, board.fen())

                payload = "\n".join(kk + ":" + str(cc) for kk, cc in sorted(ledger.items()))
                Lraw = d8(payload.encode("utf-8"))
                x_in = fen5.encode("utf-8") + Lraw
                Xraw = d8(x_in)
                X16 = d16(x_in)

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
                # --- v2 additions ---
                s128lo.append(to_i64(X16[0:8]))
                s128hi.append(to_i64(X16[8:16]))
                if board.turn:                            # chess.WHITE is True
                    phash.append(phw); pfold.append(pfw)
                else:
                    phash.append(phb); pfold.append(pfb)

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
        state_hash128_lo=npa(s128lo, np.int64),
        state_hash128_hi=npa(s128hi, np.int64),
        player_hash=npa(phash, np.int64),
        player_fold=npa(pfold, np.uint8),
        meta=np.array([ngames, len(state), MIN_PLY, MAX_PLY, nskip_novariant,
                       n_legalmove_scans], dtype=np.int64),
        meta2=np.array([n_games_with_ply30, len(namecache)], dtype=np.int64),
    )
    if a.names_out:
        with open(a.names_out, "w", encoding="utf-8") as f:
            for nm, (ph, _pf) in namecache.items():
                f.write("%d\t%s\n" % (ph, nm.replace("\t", " ").replace("\n", " ")))
    print(f"DONE games={ngames:,} records={len(state):,} skipped_variant={nskip_novariant:,} "
          f"legalmove_scans={n_legalmove_scans:,} names={len(namecache):,} "
          f"games_with_ply30={n_games_with_ply30:,} -> {a.out}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
