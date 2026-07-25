#!/usr/bin/env python3
"""i5 cross-survey replication package: extract SNLS / PS1MD / SDSS-II from SNDATA_ROOT."""
import os, gzip, json, glob, re, sys
import numpy as np, pandas as pd
from astropy.io import fits

ROOT = "/Users/resorb/Documents/tmp_i5_sndata/SNDATA_ROOT"
OUT  = "/Users/resorb/Documents/tmp_i5_sndata/out/i5_sndata_root_xsurvey"
os.makedirs(OUT + "/derived", exist_ok=True)

HEAD_KEEP = [
    "SNID","IAUC","SUBSURVEY","RA","DEC","DECL","SNTYPE","NOBS","MWEBV","MWEBV_ERR",
    "REDSHIFT_HELIO","REDSHIFT_HELIO_ERR","REDSHIFT_FINAL","REDSHIFT_FINAL_ERR",
    "REDSHIFT_SN","REDSHIFT_SN_ERR","REDSHIFT_QUALITYFLAG","VPEC","VPEC_ERR",
    "HOSTGAL_OBJID","HOSTGAL_SPECZ","HOSTGAL_SPECZ_ERR","HOSTGAL_PHOTOZ","HOSTGAL_PHOTOZ_ERR",
    "HOSTGAL_SNSEP","HOSTGAL_LOGMASS","HOSTGAL_LOGMASS_ERR","PEAKMJD","SEARCH_TYPE","FAKE",
]
PHOT_KEEP = ["MJD","BAND","FLT","FIELD","TELESCOPE","PHOTFLAG","PHOTPROB",
             "FLUXCAL","FLUXCALERR","MAG","MAGERR","ZEROPT","ZEROPT_ERR","CCDNUM"]

summary = {}


def _native(a):
    """Return a little-endian / native-order copy of a FITS column array."""
    if a.dtype.byteorder in ('>', '<') and a.dtype.byteorder != '=':
        import sys as _s
        native = '<' if _s.byteorder == 'little' else '>'
        if a.dtype.byteorder != native:
            return a.astype(a.dtype.newbyteorder(native))
    return a

def dump_fits(tag, survey, headpath, photpath):
    with fits.open(headpath) as h:
        hd = h[1].data; hcols = [c.name for c in h[1].columns]
        keep = [c for c in HEAD_KEEP if c in hcols]
        keep += [c for c in hcols if c.startswith("HOSTGAL_SB_FLUXCAL")]
        df = pd.DataFrame({c: _native(np.asarray(hd[c])) for c in keep})
        for c in df.columns:
            if df[c].dtype == object:
                df[c] = df[c].astype(str).str.strip()
        ptr_min = np.asarray(hd["PTROBS_MIN"], dtype=np.int64)
        ptr_max = np.asarray(hd["PTROBS_MAX"], dtype=np.int64)
        snid = np.asarray(hd["SNID"]).astype(str)
        snid = np.char.strip(snid)
    if "DECL" in df.columns and "DEC" not in df.columns:
        df = df.rename(columns={"DECL": "DEC"})
    df.insert(0, "survey", survey)
    hp = f"{OUT}/derived/{tag}_HEAD.csv.gz"
    df.to_csv(hp, index=False, compression="gzip")

    with fits.open(photpath) as h:
        pd_ = h[1].data; pcols = [c.name for c in h[1].columns]
        pk = [c for c in PHOT_KEEP if c in pcols]
        arrs = {}
        for c in pk:
            arrs[c] = _native(np.asarray(pd_[c]))
        n = len(pd_)
    # map each phot row -> SNID via PTROBS (1-based inclusive)
    owner = np.full(n, "", dtype=object)
    for i in range(len(snid)):
        lo = ptr_min[i] - 1; hi = ptr_max[i]
        if lo >= 0 and hi <= n and hi > lo:
            owner[lo:hi] = snid[i]
    p = pd.DataFrame(arrs)
    for c in p.columns:
        if p[c].dtype == object:
            p[c] = p[c].astype(str).str.strip()
    p.insert(0, "SNID", owner)
    p.insert(0, "survey", survey)
    p = p[p["SNID"] != ""]
    if "FLT" in p.columns and "BAND" not in p.columns:
        p = p.rename(columns={"FLT": "band"})
    elif "BAND" in p.columns:
        p = p.rename(columns={"BAND": "band"})
    pp = f"{OUT}/derived/{tag}_PHOT.csv.gz"
    p.to_csv(pp, index=False, compression="gzip")
    summary[tag] = dict(survey=survey, n_sn=int(len(df)), n_epochs=int(len(p)),
                        head_csv=os.path.basename(hp), phot_csv=os.path.basename(pp),
                        head_bytes=os.path.getsize(hp), phot_bytes=os.path.getsize(pp),
                        head_cols=list(df.columns), phot_cols=list(p.columns),
                        native_head=headpath.replace(ROOT, "$SNDATA_ROOT"),
                        native_phot=photpath.replace(ROOT, "$SNDATA_ROOT"))
    print(f"[FITS] {tag}: {len(df)} SNe, {len(p)} epochs")
    return df, p


def parse_snana_text(path):
    """Parse a TERSE SNANA .dat light curve (OBS: rows with VARLIST)."""
    op = gzip.open if path.endswith(".gz") else open
    hdr, varlist, obs = {}, None, []
    with op(path, "rt", errors="replace") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if s.startswith("VARLIST:"):
                varlist = s.split(":", 1)[1].split()
            elif s.startswith("OBS:"):
                obs.append(s.split()[1:])
            elif s.startswith("END"):
                continue
            elif ":" in s:
                k, v = s.split(":", 1)
                hdr.setdefault(k.strip(), v.strip())
    return hdr, varlist, obs


NUM = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")
def firstnum(v):
    if v is None: return np.nan
    m = NUM.search(v)
    return float(m.group()) if m else np.nan

def tok(v):
    parts = (v or "").split()
    return parts[0] if parts else ""

def znums(v):
    return [float(x) for x in NUM.findall(v or "")]


def dump_text(tag, survey, pattern):
    files = sorted(glob.glob(pattern))
    H, P = [], []
    for fp in files:
        hdr, varlist, obs = parse_snana_text(fp)
        if not varlist or not obs:
            continue
        snid = hdr.get("SNID", os.path.basename(fp)).split()[0]
        zh = znums(hdr.get("REDSHIFT_HELIO", ""))
        zf = znums(hdr.get("REDSHIFT_FINAL", ""))
        rec = dict(
            survey=survey, SNID=snid,
            IAUC=tok(hdr.get("IAUC")),
            PHOTOMETRY_VERSION=tok(hdr.get("PHOTOMETRY_VERSION")),
            RA=firstnum(hdr.get("RA")), DEC=firstnum(hdr.get("DECL") or hdr.get("DEC")),
            MWEBV=firstnum(hdr.get("MWEBV")),
            REDSHIFT_HELIO=zh[0] if zh else np.nan,
            REDSHIFT_HELIO_ERR=zh[1] if len(zh) > 1 else np.nan,
            REDSHIFT_FINAL=zf[0] if zf else np.nan,
            REDSHIFT_FINAL_ERR=zf[1] if len(zf) > 1 else np.nan,
            REDSHIFT_STATUS=(hdr.get("REDSHIFT_Status") or hdr.get("REDSHIFT_STATUS") or "").strip(),
            PEAKMJD=firstnum(hdr.get("SEARCH_PEAKMJD")),
            FILTERS=tok(hdr.get("FILTERS")),
            NOBS=len(obs),
            SNTYPE=firstnum(hdr.get("SEARCH_TYPE")) if hdr.get("SEARCH_TYPE") else np.nan,
            HOSTGAL_LOGMASS=np.nan, HOSTGAL_LOGMASS_ERR=np.nan,
        )
        H.append(rec)
        for row in obs:
            row = row[:len(varlist)]
            d = dict(zip(varlist, row))
            P.append(dict(
                survey=survey, SNID=snid,
                MJD=float(d.get("MJD", "nan")),
                band=d.get("FLT", d.get("BAND", "")),
                FIELD=d.get("FIELD", ""),
                FLUXCAL=float(d.get("FLUXCAL", "nan")),
                FLUXCALERR=float(d.get("FLUXCALERR", "nan")),
                MAG=float(d.get("MAG", "nan")), MAGERR=float(d.get("MAGERR", "nan")),
                SNR=float(d.get("SNR", "nan")) if "SNR" in d else np.nan,
                ZEROPT=float(d.get("Zpt", d.get("ZEROPT", "nan"))),
                PHOTFLAG=np.nan,
            ))
    dh = pd.DataFrame(H); dp = pd.DataFrame(P)
    hp = f"{OUT}/derived/{tag}_HEAD.csv.gz"; pp = f"{OUT}/derived/{tag}_PHOT.csv.gz"
    dh.to_csv(hp, index=False, compression="gzip")
    dp.to_csv(pp, index=False, compression="gzip")
    summary[tag] = dict(survey=survey, n_sn=int(len(dh)), n_epochs=int(len(dp)),
                        head_csv=os.path.basename(hp), phot_csv=os.path.basename(pp),
                        head_bytes=os.path.getsize(hp), phot_bytes=os.path.getsize(pp),
                        head_cols=list(dh.columns), phot_cols=list(dp.columns),
                        native_glob=pattern.replace(ROOT, "$SNDATA_ROOT"),
                        note="derived from SNANA TERSE text light curves; PHOTFLAG absent upstream")
    print(f"[TEXT] {tag}: {len(dh)} SNe, {len(dp)} epochs")
    return dh, dp


if __name__ == "__main__":
    L = ROOT + "/lcmerge"
    dump_fits("PS1MD_Jones18", "PS1MD",
              f"{L}/PS1MD_Jones18/PS1MD_Jones18_HEAD.FITS.gz",
              f"{L}/PS1MD_Jones18/PS1MD_Jones18_PHOT.FITS.gz")
    dump_fits("PS1MD_Pantheon_specIa", "PS1MD",
              f"{L}/Pantheon/Pantheon_PS1MD_FITS/Pantheon_PS1MD_FITS_HEAD.FITS.gz",
              f"{L}/Pantheon/Pantheon_PS1MD_FITS/Pantheon_PS1MD_FITS_PHOT.FITS.gz")
    dump_fits("SDSS_allCandidates_BOSS", "SDSS",
              f"{L}/SDSS_allCandidates+BOSS/SDSS_allCandidates+BOSS_HEAD.FITS.gz",
              f"{L}/SDSS_allCandidates+BOSS/SDSS_allCandidates+BOSS_PHOT.FITS.gz")
    dump_text("SNLS_SNLS3year_MEGACAM", "SNLS", f"{L}/SNLS3year/SNLS3year_MEGACAM/*.dat.gz")
    dump_text("SNLS_JLA2014", "SNLS", f"{L}/JLA2014/JLA2014_SNLS/*.dat.gz")
    dump_text("SNLS_Ast06", "SNLS", f"{L}/SNLS_Ast06/*.dat.gz")
    json.dump(summary, open(f"{OUT}/derived/_extract_summary.json", "w"), indent=2)
    print("done")
