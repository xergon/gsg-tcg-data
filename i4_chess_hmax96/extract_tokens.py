#!/usr/bin/env python3
"""
i4 HMAX=96 rerun -- STAGE 1: stream Lichess PGN from stdin, emit per-game token sequences.

EXTENDS (does not replace) the June-29 extractor family
  implementation_lanes/temporal_unsharpness/chess_reality_h0_2026_06_29/chess_reality_h0.py
The estimator itself (Miller-Madow entropy, MI, common-support anchored panel) is inherited
verbatim in stage 2 (compute_hmax96.py). This stage only widens the horizon reach to HMAX=96
and adds the second observable family requested by i4 (SAN conditioned on a canonical
board-state hash). One streaming pass per period produces every observable at once.

OBSERVABLES emitted per ply t (before the move is played):
  A  fromto      : from_square*64 + to_square              [June-29 original, verbatim]
  B  san_canon   : SAN-equivalent token on a COLOR-CANONICAL board:
                   (piece_type, destination square mirrored to the mover's frame,
                    capture flag, promotion piece, castling flag) packed to 15 bits.
                   This is the SAN content (SAN = piece + destination + capture + promo,
                   modulo disambiguation and check suffixes) with the black/white frame
                   collapsed, i.e. the move as the side to move sees it.
  C  san_matkey  : B tensored with a COARSE canonical board-state hash = the material key
                   (piece counts P,N,B,R,Q for mover and opponent).
  D  san_statekey: B tensored with the FULL canonical board-state hash =
                   python-chess Board._transposition_key() (piece bitboards + side to move
                   + castling rights + en-passant file). This is the standard
                   transposition-invariant canonical position key.

usage: zstdcat X.pgn.zst | python3 extract_tokens.py PERIOD MAX_GAMES OUTDIR
"""
import sys, os, re, time, json
import numpy as np
import chess

PERIOD = sys.argv[1]
MAX_GAMES = int(sys.argv[2])
OUTDIR = sys.argv[3]
HMAX = 96
MIN_PLIES = HMAX + 4          # June-29 convention: HMAX + 4  (>=4 anchored positions)

LOG = open(os.path.join(OUTDIR, "parse_log.txt"), "a", buffering=1)
def log(msg):
    LOG.write("[%s][%s] %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), PERIOD, msg))

TOKCLEAN = re.compile(r"\{[^}]*\}|\$\d+|\d+\.(?:\.\.)?|[?!]+|\([^)]*\)")
RESULTS = ("1-0", "0-1", "1/2-1/2", "*")
PT_ORDER = (chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN)

def material_key(b):
    """Coarse canonical board-state hash: piece counts for (mover, opponent)."""
    k = 0
    me, opp = b.turn, not b.turn
    for c in (me, opp):
        for pt in PT_ORDER:
            n = chess.popcount(b.pieces_mask(pt, c))
            if n > 10:
                n = 10
            k = k * 11 + n
    return k

t_start = time.time()
log("START extract HMAX=%d MIN_PLIES=%d MAX_GAMES=%d" % (HMAX, MIN_PLIES, MAX_GAMES))

# ---------------- stream games ----------------
seq_fromto = []; seq_san = []; seq_mat = []; seq_state = []
lengths = []
n_games = 0          # qualifying games kept
n_scanned = 0        # games seen in the stream
n_short = 0          # rejected: len(moves) < MIN_PLIES
n_malformed = 0      # rejected: SAN replay failure

stdin = sys.stdin.buffer
remainder = b""
buf = []; inmv = False
done = False

def handle_game(gtext):
    """returns 0 ok/kept, 1 short, 2 malformed"""
    global n_games
    toks = [x for x in TOKCLEAN.sub(" ", gtext).split() if x not in RESULTS]
    if len(toks) < MIN_PLIES:
        return 1
    b = chess.Board()
    ft = np.empty(len(toks), dtype=np.int16)
    sn = np.empty(len(toks), dtype=np.int16)
    mk = np.empty(len(toks), dtype=np.int64)
    st = np.empty(len(toks), dtype=np.int64)
    try:
        for i, s in enumerate(toks):
            mv = b.parse_san(s)
            frm, to = mv.from_square, mv.to_square
            ft[i] = frm * 64 + to
            pt = b.piece_type_at(frm)
            to_c = to if b.turn == chess.WHITE else chess.square_mirror(to)
            cap = 1 if b.is_capture(mv) else 0
            promo = mv.promotion or 0
            if b.is_castling(mv):
                castle = 1 if chess.square_file(to) > chess.square_file(frm) else 2
            else:
                castle = 0
            sn[i] = ((((pt << 6) | to_c) << 1 | cap) << 3 | promo) << 2 | castle
            mk[i] = material_key(b)
            st[i] = hash(b._transposition_key()) & 0x7FFFFFFFFFFFFFF
            b.push(mv)
    except Exception:
        return 2
    seq_fromto.append(ft); seq_san.append(sn); seq_mat.append(mk); seq_state.append(st)
    lengths.append(len(toks))
    n_games += 1
    return 0

while not done:
    chunk = stdin.read(1 << 26)
    if not chunk:
        break
    data = (remainder + chunk).decode("utf-8", errors="ignore")
    nl = data.rfind("\n")
    if nl < 0:
        remainder = data.encode("utf-8", errors="ignore"); continue
    remainder = data[nl + 1:].encode("utf-8", errors="ignore")
    for ln in data[:nl].split("\n"):
        if ln.startswith("["):
            if inmv:
                n_scanned += 1
                r = handle_game(" ".join(buf))
                if r == 1: n_short += 1
                elif r == 2: n_malformed += 1
                buf = []; inmv = False
                if n_games >= MAX_GAMES:
                    done = True; break
                if n_scanned % 100000 == 0:
                    log("scanned=%d kept=%d short=%d malformed=%d elapsed=%.1fs"
                        % (n_scanned, n_games, n_short, n_malformed, time.time() - t_start))
        elif ln.strip():
            inmv = True; buf.append(ln)
if buf and not done:
    n_scanned += 1
    r = handle_game(" ".join(buf))
    if r == 1: n_short += 1
    elif r == 2: n_malformed += 1

log("STREAM DONE scanned=%d kept=%d short=%d malformed=%d elapsed=%.1fs"
    % (n_scanned, n_games, n_short, n_malformed, time.time() - t_start))

if n_games < 50:
    log("FATAL too few games")
    sys.exit(1)

lengths = np.asarray(lengths, dtype=np.int64)
offsets = np.concatenate([[0], np.cumsum(lengths)])
out = os.path.join(OUTDIR, "tokens_%s.npz" % PERIOD)
np.savez(out,
         fromto=np.concatenate(seq_fromto),
         san_canon=np.concatenate(seq_san),
         san_matkey=np.concatenate(seq_mat),
         san_statekey=np.concatenate(seq_state),
         lengths=lengths, offsets=offsets)
meta = {"period": PERIOD, "HMAX": HMAX, "MIN_PLIES": MIN_PLIES,
        "n_games_kept": int(n_games), "n_games_scanned": int(n_scanned),
        "n_rejected_short": int(n_short), "n_rejected_malformed": int(n_malformed),
        "total_plies": int(lengths.sum()), "mean_game_plies": float(lengths.mean()),
        "extract_wall_s": round(time.time() - t_start, 1)}
with open(os.path.join(OUTDIR, "extract_meta_%s.json" % PERIOD), "w") as f:
    json.dump(meta, f, indent=2)
log("WROTE %s  %s" % (out, json.dumps(meta)))
