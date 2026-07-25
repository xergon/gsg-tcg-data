#!/usr/bin/env python3
"""Parse the three longtables of Ruiz-Garcia et al. 2024 (A&A, arXiv:2410.13353)
from the arXiv LaTeX source into machine-readable CSV."""
import re, csv, sys, os

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'AAmain.tex')
OUT = os.path.dirname(os.path.abspath(__file__))
lines = open(SRC, encoding='utf-8', errors='replace').read().split('\n')


def body(start_lineno):
    """Return the data body of the longtable beginning at 1-based start_lineno:
    everything after \\endlastfoot up to \\end{longtable}."""
    i = start_lineno - 1
    assert lines[i].startswith('\\begin{longtable}'), lines[i]
    j = i
    while '\\endlastfoot' not in lines[j]:
        j += 1
    k = j
    while '\\end{longtable}' not in lines[k]:
        k += 1
    return '\n'.join(lines[j + 1:k])


def strip_comments(txt):
    out = []
    for ln in txt.split('\n'):
        m = re.search(r'(?<!\\)%', ln)
        if m:
            ln = ln[:m.start()]
        out.append(ln)
    return '\n'.join(out)


def clean(c):
    c = c.strip()
    c = c.replace('\\,', ' ').replace('\\ ', ' ').replace('~', ' ')
    c = re.sub(r'\\rm\b', '', c)
    c = re.sub(r'\\mathrm', '', c)
    # asymmetric errors: x_{-a}^{+b} or x^{+b}_{-a}  ->  x ASYM a b
    c = re.sub(r'\$?\_\{?\-([^}$\s]+)\}?\^\{?\+([^}$\s]+)\}?',
               lambda m: ' ASYM %s %s' % (m.group(1), m.group(2)), c)
    c = re.sub(r'\$?\^\{?\+([^}$\s]+)\}?\_\{?\-([^}$\s]+)\}?',
               lambda m: ' ASYM %s %s' % (m.group(2), m.group(1)), c)
    c = c.replace('$', '').replace('{', '').replace('}', '')
    c = c.replace('\\dots', '').replace('\\ldots', '')
    c = c.replace('\\dagger', 'dagger').replace('\\ddagger', 'ddagger')
    c = c.replace('\\pm', '+/-')
    c = re.sub(r'\s+', ' ', c).strip()
    return c


def rows(start_lineno, ncols):
    txt = strip_comments(body(start_lineno))
    out = []
    for raw in txt.split('\\\\'):
        if not raw.strip() or raw.strip() == '\\hline':
            continue
        raw = raw.replace('\\hline', '').replace('\\noalign{\\smallskip}', '')
        if not raw.strip():
            continue
        cells = [clean(c) for c in raw.split('&')]
        if len(cells) != ncols:
            sys.stderr.write('SKIP (%d cols, want %d): %r\n' % (len(cells), ncols, raw[:120]))
            continue
        out.append(cells)
    return out


def split_val_err(s):
    """Return (value, err_lo, err_hi). Symmetric errors give err_lo == err_hi.
    '5.2+/-0.2' -> ('5.2','0.2','0.2');  '5.9 ASYM 1.2 0.1' -> ('5.9','1.2','0.1')"""
    if not s:
        return '', '', ''
    if 'ASYM' in s:
        head, rest = s.split('ASYM', 1)
        parts = rest.split()
        lo = parts[0] if len(parts) > 0 else ''
        hi = parts[1] if len(parts) > 1 else ''
        return head.strip(), lo, hi
    if '+/-' in s:
        a, b = s.split('+/-', 1)
        return a.strip(), b.strip(), b.strip()
    return s.strip(), '', ''


# ---- Table A.1: full PHANGS sample -------------------------------------
t1 = rows(774, 11)
with open(os.path.join(OUT, 'ruizgarcia2024_tableA1_phangs_sample.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['object', 'ra_deg', 'dec_deg', 'PA_deg', 'PA_err_deg', 'incl_deg',
                'incl_err_deg', 'dist_Mpc', 'dist_err_Mpc', 'rotation_sense',
                'bar_flag', 'R_100pct_CO_kpc', 'R_50pct_CO_kpc', 'R_endCO_kpc', 'parse_note'])
    for r in t1:
        pa, pae, _ = split_val_err(r[3]); inc, ince, _ = split_val_err(r[4]); d, de, _ = split_val_err(r[5])
        note = ''
        # Published source typo: NGC 1566 PA cell reads '214.{$\\pm 4.1$} 7'
        # (the trailing digit of 214.7 sits outside the error brace).
        if r[0] == 'NGC 1566' and pa.replace(' ', '') in ('214.7', '214.'):
            pa, pae = '214.7', pae.split()[0] if pae else pae
            note = 'PA reassembled from source typo: raw cell was 214.{pm 4.1} 7'
        w.writerow([r[0], r[1], r[2], pa, pae, inc, ince, d, de, r[6], r[7], r[8], r[9], r[10], note])
print('tableA1 rows:', len(t1))

# ---- Table A.2: R_CR / R_bar / R / QF -----------------------------------
t2 = rows(962, 12)
cr = []
for r in t2:
    for half in (r[0:6], r[6:12]):
        if not half[0]:
            continue
        v, elo, ehi = split_val_err(half[1])
        cr.append([half[0], v, elo, ehi, half[2], half[3], half[4], half[5]])
with open(os.path.join(OUT, 'ruizgarcia2024_tableA2_corotation.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['object', 'R_CR_kpc', 'R_CR_err_lo_kpc', 'R_CR_err_hi_kpc', 'R_bar_kpc',
                'Rratio_CR_over_bar', 'QF', 'nominal_map'])
    w.writerows(cr)
print('tableA2 galaxies:', len(cr), '| with R_CR:', sum(1 for r in cr if r[1]))

# ---- Table A.3: pattern speed + Lindblad resonances ---------------------
t3 = rows(1068, 10)
res = []
for r in t3:
    for half in (r[0:5], r[5:10]):
        if not half[0]:
            continue
        op, oplo, ophi = split_val_err(half[1])
        ii, iilo, iihi = split_val_err(half[2])
        oi, oilo, oihi = split_val_err(half[3])
        ol, ollo, olhi = split_val_err(half[4])
        res.append([half[0], op, oplo, ophi, ii, iilo, iihi, oi, oilo, oihi, ol, ollo, olhi])
with open(os.path.join(OUT, 'ruizgarcia2024_tableA3_pattern_speed_resonances.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['object', 'Omega_p_km_s_kpc', 'Omega_p_err_lo', 'Omega_p_err_hi',
                'iILR_kpc', 'iILR_err_lo', 'iILR_err_hi', 'oILR_kpc', 'oILR_err_lo',
                'oILR_err_hi', 'OLR_kpc', 'OLR_err_lo', 'OLR_err_hi'])
    w.writerows(res)
print('tableA3 galaxies:', len(res), '| with Omega_p:', sum(1 for r in res if r[1]))
