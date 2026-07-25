#!/usr/bin/env python3
"""Stream the 17.7 GB KiDS DR4.1 SOM-gold WL catalogue over HTTP and keep only
sources within R_MAX of a SAMI DR3 GAMA-region galaxy.  Nothing is derived --
this is a spatial row selection plus a column subset.  No shear product computed."""
import os, sys, csv, math, time, urllib.request, numpy as np

URL   = "https://kids.strw.leidenuniv.nl/DR4/data_files/KiDS_DR4.1_ugriZYJHKs_SOM_gold_WL_cat.fits"
BASE  = os.path.dirname(os.path.abspath(__file__))
OUT   = os.path.join(BASE, "kids1000_sami_aperture_sources.npy")
LOG   = os.path.join(BASE, "stream_filter.log")
R_MAX = 15.0/60.0          # deg  -- generous local-aperture radius
DATA_OFFSET = 169920
ROWLEN      = 833
NROWS       = 21262011
CELL        = 0.01         # deg, coarse pre-filter grid

def log(*a):
    with open(LOG, "a") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%SZ ", time.gmtime()) + " ".join(str(x) for x in a) + "\n")

# ---- column layout, byte offsets computed from the FITS header TFORMs ----
COLS = [   # (name, byte_offset, numpy big-endian dtype) -- derived from the FITS header
    ("SeqNr", 0, ">i4"),
    ("MAG_AUTO", 45, ">f4"),
    ("RAJ2000", 89, ">f8"),
    ("DECJ2000", 97, ">f8"),
    ("Flag", 145, ">i2"),
    ("MAG_GAAP_r", 395, ">f4"),
    ("MAGERR_GAAP_r", 399, ">f4"),
    ("Z_B", 565, ">f8"),
    ("Z_B_MIN", 573, ">f8"),
    ("Z_B_MAX", 581, ">f8"),
    ("T_B", 589, ">f8"),
    ("ODDS", 597, ">f8"),
    ("SG_FLAG", 661, ">f4"),
    ("MASK", 665, ">i4"),
    ("fitclass", 685, ">i2"),
    ("bias_corrected_scalelength_pixels", 687, ">f4"),
    ("pixel_SNratio", 699, ">f4"),
    ("model_SNratio", 703, ">f4"),
    ("PSF_e1", 711, ">f4"),
    ("PSF_e2", 715, ">f4"),
    ("PSF_Q11", 723, ">f4"),
    ("PSF_Q22", 727, ">f4"),
    ("PSF_Q12", 731, ">f4"),
    ("THELI_INT", 819, ">i2"),
    ("e1", 821, ">f4"),
    ("e2", 825, ">f4"),
    ("weight", 829, ">f4"),
]

def build_offsets(hdrfile):
    """Recompute offsets from the real header so we never guess."""
    import re
    d = open(hdrfile, "rb").read(200000)
    off = 0
    def blk(o):
        cards = []
        while True:
            b = d[o:o+2880]; o += 2880
            for i in range(0, 2880, 80):
                c = b[i:i+80].decode("ascii", "replace")
                cards.append(c)
                if c.startswith("END     "):
                    return cards, o
    _, off = blk(0)
    cards, dataoff = blk(off)
    kv = {}
    for c in cards:
        m = re.match(r"^(\S+)\s*=\s*(.+?)\s*(/.*)?$", c)
        if m: kv.setdefault(m.group(1), m.group(2).strip())
    n = int(kv["TFIELDS"])
    sizes = {"L":1,"B":1,"I":2,"J":4,"K":8,"A":1,"E":4,"D":8}
    o = 0; layout = {}
    for i in range(1, n+1):
        nm = kv["TTYPE%d"%i].strip().strip("'").strip()
        fm = kv["TFORM%d"%i].strip().strip("'").strip()
        m = re.match(r"^(\d*)([A-Z])", fm)
        rep = int(m.group(1) or 1); code = m.group(2)
        layout[nm] = (o, code, rep)
        o += rep*sizes[code]
    return layout, dataoff, int(kv["NAXIS1"]), int(kv["NAXIS2"])

layout, dataoff, rowlen, nrows = build_offsets(os.path.join(BASE, "kids_head.bin"))
assert dataoff == DATA_OFFSET and rowlen == ROWLEN and nrows == NROWS, (dataoff, rowlen, nrows)
FITSMAP = {"E":">f4","D":">f8","J":">i4","I":">i2","K":">i8","B":">u1"}
FIELDS = []
for nm, _, _ in COLS:
    o, code, rep = layout[nm]
    FIELDS.append((nm, o, FITSMAP[code]))
# sanity: our hard-coded offsets must equal the header-derived ones
for (nm, o_hard, dt), (nm2, o_hdr, dt2) in zip(COLS, FIELDS):
    assert nm == nm2 and o_hard == o_hdr and dt == dt2, (nm, o_hard, o_hdr, dt, dt2)
log("column layout verified against FITS header; %d columns" % len(FIELDS))

# ---- SAMI GAMA-region galaxy positions ----
gal = []
with open(os.path.join(BASE, "sami_gama_targets.csv")) as f:
    for r in csv.DictReader(f):
        gal.append((float(r["RA_OBJ"]), float(r["DEC_OBJ"])))
gal = np.array(gal)
log("SAMI GAMA galaxies:", len(gal))

RA0, RA1 = gal[:,0].min()-1.0, gal[:,0].max()+1.0
DE0, DE1 = gal[:,1].min()-1.0, gal[:,1].max()+1.0
NX = int((RA1-RA0)/CELL)+2; NY = int((DE1-DE0)/CELL)+2
grid = np.zeros((NX, NY), dtype=bool)
pad = R_MAX + CELL*1.5
for ra, de in gal:
    cosd = math.cos(math.radians(de))
    dra = pad/max(cosd, 1e-6)
    i0 = max(0, int((ra-dra-RA0)/CELL)); i1 = min(NX-1, int((ra+dra-RA0)/CELL))
    j0 = max(0, int((de-pad-DE0)/CELL)); j1 = min(NY-1, int((de+pad-DE0)/CELL))
    grid[i0:i1+1, j0:j1+1] = True
log("coarse grid %dx%d, %d cells set (%.1f deg^2)" % (NX, NY, grid.sum(), grid.sum()*CELL*CELL))

out_dtype = np.dtype([(nm, dt.replace(">", "<")) for nm, _, dt in FIELDS])
chunks = []
kept = 0
CHUNK_ROWS = 200000
CHUNK_BYTES = CHUNK_ROWS*ROWLEN

req = urllib.request.Request(URL, headers={"User-Agent": "gsg-tcg research fetch"})
t0 = time.time()
with urllib.request.urlopen(req, timeout=120) as resp:
    # consume header
    got = 0
    while got < DATA_OFFSET:
        b = resp.read(min(65536, DATA_OFFSET-got))
        if not b: raise SystemExit("short read in header")
        got += len(b)
    residual = b""
    nread = 0
    tlast = time.time()
    while True:
        buf = resp.read(CHUNK_BYTES)
        if not buf: break
        buf = residual + buf
        n = len(buf)//ROWLEN
        residual = buf[n*ROWLEN:]
        if n == 0: continue
        raw = np.frombuffer(buf[:n*ROWLEN], dtype=np.uint8).reshape(n, ROWLEN)
        ra = raw[:, 89:97].copy().view(">f8").ravel()
        de = raw[:, 97:105].copy().view(">f8").ravel()
        m = (ra > RA0) & (ra < RA1) & (de > DE0) & (de < DE1)
        if m.any():
            idx = np.nonzero(m)[0]
            ii = ((ra[idx]-RA0)/CELL).astype(np.int32)
            jj = ((de[idx]-DE0)/CELL).astype(np.int32)
            ok = grid[np.clip(ii, 0, NX-1), np.clip(jj, 0, NY-1)]
            idx = idx[ok]
            if len(idx):
                sub = raw[idx]
                rec = np.empty(len(idx), dtype=out_dtype)
                for nm, off, dt in FIELDS:
                    w = int(dt[2:])
                    rec[nm] = sub[:, off:off+w].copy().view(dt).ravel()
                chunks.append(rec)
                kept += len(idx)
        nread += n
        if time.time()-tlast > 120:
            tlast = time.time()
            el = time.time()-t0
            log("rows %d/%d (%.1f%%) kept %d  %.1f MB/s  eta %.0f min" %
                (nread, NROWS, 100.0*nread/NROWS, kept,
                 nread*ROWLEN/1e6/el, (NROWS-nread)*ROWLEN/1e6/max(nread*ROWLEN/1e6/el, 1e-9)/60))

log("DONE read rows", nread, "kept", kept, "elapsed %.0f s" % (time.time()-t0))
res = np.concatenate(chunks) if chunks else np.empty(0, dtype=out_dtype)
np.save(OUT, res)
log("wrote", OUT, os.path.getsize(OUT), "bytes")
