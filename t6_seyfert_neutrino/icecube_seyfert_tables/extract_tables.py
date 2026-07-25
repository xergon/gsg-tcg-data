#!/usr/bin/env python3
"""Extract the published source-list / results tables from the two IceCube
Seyfert ApJL LaTeX sources into machine-readable CSV.

No approximations: every numeric cell is copied verbatim from the LaTeX;
only LaTeX markup is stripped.  Significance values that the papers print in
brackets (e.g. "6.6\,(5.0\sigmas)") are split into two columns.
"""
import csv
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "src")
OUT = os.path.join(BASE, "t6_seyfert_tables")
os.makedirs(OUT, exist_ok=True)


def clean(cell):
    s = cell.strip()
    s = s.replace(r"\phantom{$-$}", "")
    s = re.sub(r"\\rule\{[^}]*\}\{[^}]*\}", "", s)
    s = re.sub(r"\\hspace\{[^}]*\}", "", s)
    s = re.sub(r"\\multicolumn\{\d+\}\{[^}]*\}\{(.*)\}\s*$", r"\1", s.strip())
    s = re.sub(r"\\(citep|citealt|cite)\{[^}]*\}", "", s)
    s = re.sub(r"\\times\s*10\^\{?(-?\d+)\}?", r"e\1", s)
    s = s.replace(r"\,", " ").replace(r"\;", " ").replace("~", " ")
    s = s.replace(r"$-$", "-").replace(r"\sigmas", "sigma").replace(r"\sigma", "sigma")
    s = s.replace(r"\%", "%")
    s = re.sub(r"\^\{?\*\}?", "*", s)
    s = s.replace("$", "")
    s = re.sub(r"\\[a-zA-Z]+", "", s)
    s = s.replace("{", "").replace("}", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


SIG = re.compile(r"^(-?[\d.]+)\s*\((-?[\d.]+)\s*sigma\)$")
SIGP = re.compile(r"^([\d.e+-]+)\s*\((-?[\d.]+)\s*sigma\)$")


def split_sig(cells, headers):
    """Expand 'X (Ysigma)' cells into two columns.  Headers are expanded for
    EVERY column that carries a bracketed significance anywhere in the table,
    so the header always lines up with the widest row."""
    out_cells, out_heads = [], []
    for i, h in enumerate(headers):
        c = cells[i] if i < len(cells) else ""
        m = SIGP.match(c)
        if m:
            out_cells += [m.group(1), m.group(2)]
            out_heads += [h, h + "_sigma"]
        else:
            out_cells.append(c)
            out_heads.append(h)
    return out_cells, out_heads


def split_table(rows_raw, hdr):
    """Apply split_sig to a whole table, deriving one consistent header."""
    sig_cols = set()
    for r in rows_raw:
        for i in range(min(len(r), len(hdr))):
            if SIGP.match(r[i]):
                sig_cols.add(i)
    header = []
    for i, h in enumerate(hdr):
        header.append(h)
        if i in sig_cols:
            header.append(h + "_sigma")
    out = []
    for r in rows_raw:
        row = []
        for i in range(len(hdr)):
            c = r[i] if i < len(r) else ""
            if i in sig_cols:
                m = SIGP.match(c)
                if m:
                    row += [m.group(1), m.group(2)]
                else:
                    row += [c, ""]
            else:
                row.append(c)
        out.append(row)
    return header, out


def body_rows(text, start_marker, end_marker):
    i = text.index(start_marker)
    j = text.index(end_marker, i)
    return text[i + len(start_marker):j]


def parse_rows(block, ncols, name_must_be_nonempty=True):
    rows = []
    for raw in block.split("\\\\"):
        line = raw
        # drop comment lines and pure rule lines
        line = re.sub(r"(?<!\\)%.*", "", line)
        for kill in ("\\toprule", "\\midrule", "\\bottomrule", "\\hline",
                     "\\endfirsthead", "\\endhead", "\\endfoot", "\\endlastfoot",
                     "\\cmidrule"):
            if kill in line:
                line = re.sub(re.escape(kill) + r"(\{[^}]*\})?", "", line)
        if "Continued on next page" in line:
            continue
        cells = []
        for raw_cell in line.split("&"):
            span = re.search(r"\\multicolumn\{(\d+)\}", raw_cell)
            cells.append(clean(raw_cell))
            if span:  # a \multicolumn{N} cell occupies N alignment slots
                cells.extend([""] * (int(span.group(1)) - 1))
        if len(cells) < 2:
            continue
        if name_must_be_nonempty and not cells[0]:
            # keep -- some tables legitimately have a blank leading label
            pass
        if all(c == "" for c in cells):
            continue
        while len(cells) < ncols:
            cells.append("")
        rows.append(cells[:ncols])
    return rows


def write(fn, header, rows):
    p = os.path.join(OUT, fn)
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print("%-52s %4d data rows" % (fn, len(rows)))
    return p


# ---------------------------------------------------------------- 2510.13403
app = open(os.path.join(SRC, "x2510.13403", "appendix.tex"), encoding="utf-8").read()
main = open(os.path.join(SRC, "x2510.13403", "main.tex"), encoding="utf-8").read()

# --- Table: 110 gamma-ray emitters (longtable, 8 cols)
blk = app[app.index("\\label{tab:gammaray}"):]
blk = blk[blk.index("\\endlastfoot") + len("\\endlastfoot"):]
blk = blk[:blk.index("\\end{longtable*}")]
hdr = ["source_name", "ra_deg", "dec_deg", "ns_hat", "gamma_hat",
       "neglog10_p_local", "phi90_E-2", "phi90_E-3"]
raw = [r for r in parse_rows(blk, 8) if r[0]]
hdr110, rows = split_table(raw, hdr)
write("icecube_2510.13403_tab_gammaray_110sources.csv", hdr110, rows)
N110 = len(rows)

# --- Table: 47 X-ray-bright AGN (longtable, 12 cols)
blk = app[app.index("\\label{tab:xray}"):]
blk = blk[blk.index("\\endlastfoot") + len("\\endlastfoot"):]
blk = blk[:blk.index("\\end{longtable*}")]
hdr = ["source_name", "ra_deg", "dec_deg", "F_intr_20-50keV_1e-11_erg_cm2_s",
       "pl_ns_hat", "pl_gamma_hat", "pl_neglog10_p_local",
       "pl_phi90_E-2", "pl_phi90_E-3",
       "cc_ns_hat", "cc_neglog10_p_local", "cc_ns_90pct_UL"]
raw = [r for r in parse_rows(blk, 12) if r[0]]
hdr47, rows = split_table(raw, hdr)
# NGC 1068 heads this table for reference but is EXPLICITLY EXCLUDED from the
# 47-source sample (abstract: "with NGC 1068 excluded from the sample").
hdr47 = hdr47 + ["in_47_source_sample"]
for r in rows:
    r.append("0" if r[0].startswith("NGC 1068") else "1")
write("icecube_2510.13403_tab_xray_47sources.csv", hdr47, rows)
N47 = sum(1 for r in rows if r[-1] == "1")

# --- main results table (tabular, 9 cols)
blk = main[main.index("\\label{tab:results}"):]
blk = blk[blk.index("\\midrule"):]
blk = blk[:blk.index("\\end{tabular}")]
hdr = ["block", "test_type", "object", "ra_deg", "dec_deg", "ns_hat",
       "gamma_hat", "neglog10_p_local", "neglog10_p_global"]
raw = [r for r in parse_rows(blk, 9) if not all(c == "" for c in r[:3])]
hdrm, rows = split_table(raw, hdr)
write("icecube_2510.13403_tab_summary_of_results.csv", hdrm, rows)

# ---------------------------------------------------------------- 2602.10208
m2 = open(os.path.join(SRC, "x2602.10208", "main.tex"), encoding="utf-8").read()


def deluxe(label, ncols, hdr, fn):
    i = m2.index(label)
    # the \startdata for this table is BEFORE the \label in aastex deluxetable
    j = m2.rindex("\\startdata", 0, i)
    k = m2.index("\\enddata", j)
    blk = m2[j + len("\\startdata"):k]
    raw = [r for r in parse_rows(blk, ncols) if not all(c == "" for c in r)]
    hh, rows = split_table(raw, hdr)
    write(fn, hh, rows)
    return len(rows)


N14 = deluxe("\\label{tab:int_cat}", 5,
             ["source", "dec_deg", "ra_deg", "log10_L_2-10keV_intr", "n_exp"],
             "icecube_2602.10208_tab_candidate_sources_14.csv")

deluxe("\\label{tab:more_results}", 10,
       ["source", "dc_n_exp", "dc_ns_hat", "dc_neglog10_p", "dc_n_UL",
        "pl_ns_hat", "pl_gamma_hat", "pl_neglog10_p",
        "pl_phi90_E-2_1e-11", "pl_phi90_E-3_1e-11"],
       "icecube_2602.10208_tab_individual_results_14.csv")

deluxe("\\label{tab:results}", 8,
       ["row", "n_exp", "TS", "ns_hat", "gamma_hat", "p_pre", "p_post",
        "UL_90pct"],
       "icecube_2602.10208_tab_stacking_and_brightest.csv")

print("\nROW-COUNT CHECKS (must match the papers' own statements):")
print("  110 gamma-ray emitters   -> %d  %s" % (N110, "OK" if N110 == 110 else "MISMATCH"))
print("  47 X-ray-bright AGN      -> %d  %s  (table has 48 rows; NGC 1068 is row 1 and is EXCLUDED from the 47)" % (N47, "OK" if N47 == 47 else "MISMATCH"))
print("  14 southern candidates   -> %d  %s" % (N14, "OK" if N14 == 14 else "MISMATCH"))
