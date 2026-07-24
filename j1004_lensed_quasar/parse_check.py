#!/usr/bin/env python3
"""Byte-offset parse + integrity check of the two J1004+4112 light-curve tables.
Offsets taken verbatim from each VizieR ReadMe (1-indexed inclusive)."""
import os

D = os.path.dirname(os.path.abspath(__file__))

def fld(line, a, b):
    s = line[a-1:b].strip()
    return s if s else None

# ---------- Munoz+ 2022, J/ApJ/937/34 table1.dat ----------
print("=== Munoz+2022  J/ApJ/937/34  table1.dat ===")
rows = open(os.path.join(D, "table1.dat")).read().splitlines()
print("records:", len(rows))
cols = {"A": (10, 15, 17, 21), "B": (23, 28, 30, 34),
        "C": (36, 41, 43, 47), "D": (49, 54, 56, 60)}
jds, counts, mjdok = [], {k: 0 for k in cols}, 0
badfmt = []
for i, ln in enumerate(rows):
    j = fld(ln, 1, 8)
    try:
        jds.append(float(j)); mjdok += 1
    except Exception:
        badfmt.append((i, "JD", j))
    for im, (ma, mb, ea, eb) in cols.items():
        m, e = fld(ln, ma, mb), fld(ln, ea, eb)
        if m is not None:
            try:
                float(m); float(e); counts[im] += 1
            except Exception:
                badfmt.append((i, im, m, e))
print("JD parsed ok:", mjdok, " bad-format fields:", len(badfmt))
print("JD-2450000 range: %.3f .. %.3f" % (min(jds), max(jds)))
print("=> MJD range: %.3f .. %.3f" % (min(jds) + 2450000 - 2400000.5,
                                      max(jds) + 2450000 - 2400000.5))
print("span (d): %.1f  = %.2f yr" % (max(jds) - min(jds), (max(jds) - min(jds)) / 365.25))
tot = 0
for im in "ABCD":
    print("  image %s: %4d magnitudes (%d missing)" % (im, counts[im], len(rows) - counts[im]))
    tot += counts[im]
print("TOTAL usable image magnitudes:", tot, "   (T8 stated 3473)")
# season / gap structure
js = sorted(jds)
gaps = [(js[i+1] - js[i], js[i], js[i+1]) for i in range(len(js) - 1)]
big = [g for g in gaps if g[0] > 60]
print("gaps >60 d:", len(big), "(seasonal); largest: %.1f d" % max(g[0] for g in gaps))
if badfmt[:5]:
    print("sample bad:", badfmt[:5])

# ---------- Fohlmeister+ 2007, J/ApJ/662/62 table1.dat ----------
p2 = os.path.join(D, "fohlmeister2007_table1.dat")
if os.path.exists(p2):
    print("\n=== Fohlmeister+2007  J/ApJ/662/62  table1.dat ===")
    r2 = open(p2).read().splitlines()
    print("records:", len(r2))
    c2 = {"A": (20, 25, 27, 31), "B": (34, 39, 41, 45),
          "C": (48, 52, 54, 58), "D": (60, 65, 67, 71)}
    h, cnt2, obs = [], {k: 0 for k in c2}, {}
    for ln in r2:
        try:
            h.append(float(fld(ln, 1, 11)))
        except Exception:
            pass
        for im, (ma, mb, ea, eb) in c2.items():
            if fld(ln, ma, mb) is not None:
                cnt2[im] += 1
        o = fld(ln, 73, 79) or "?"
        obs[o] = obs.get(o, 0) + 1
    print("HJD range: %.3f .. %.3f  (span %.1f d)" % (min(h), max(h), max(h) - min(h)))
    for im in "ABCD":
        print("  image %s: %4d magnitudes" % (im, cnt2[im]))
    print("  total mags:", sum(cnt2.values()))
    print("  epochs per observatory:", dict(sorted(obs.items(), key=lambda x: -x[1])))
