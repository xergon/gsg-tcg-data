#!/usr/bin/env python3
"""Build the three tier-A tables (SPARC / LITTLE THINGS-12 / THINGS-4) for the
Phase-23 locked-vector transfer diagnostic.  NO model changes, NO fitting.
"""
from __future__ import annotations
import sys, os, json
import numpy as np
import pandas as pd

REPO = "/Users/resorb/Documents/Claude Sessions/Transaction Calculus"
LANES = "/Users/resorb/Documents/My Papers/Research Program Management/implementation_lanes"
EVAL_DIR = os.path.join(LANES, "phase23_locked_evaluator_spec_2026_07_22")
SCRATCH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, EVAL_DIR)
sys.path.insert(0, os.path.join(REPO, "src"))

import phase23_locked_evaluator as EV   # noqa: E402

KPC_M = EV.KPC_IN_M
KMS = 1.0e3
Y_DISK = 0.5
Y_BULGE = 0.7


def gobs_from_v(V_kms, R_kpc):
    return (np.asarray(V_kms, float) * KMS) ** 2 / (np.asarray(R_kpc, float) * KPC_M)


def e_gobs_from_v(V_kms, eV_kms, R_kpc):
    # d/dV of V^2/R  ->  2 V eV / R   (SPARC data.py convention)
    return 2.0 * np.abs(np.asarray(V_kms, float)) * np.asarray(eV_kms, float) * KMS**2 / (
        np.asarray(R_kpc, float) * KPC_M)


# ---------------------------------------------------------------- SPARC
def build_sparc():
    from tcg.data import load_galaxies, load_massmodels, build_rar_table, MLPriors
    g = load_galaxies()
    mm = load_massmodels()
    rar = build_rar_table(mm, MLPriors(), quality_max=2, galaxies=g)
    t = rar[["Galaxy", "R", "gbar", "gobs", "e_gobs", "Vobs", "e_Vobs",
             "Vgas", "Vdisk", "Vbul", "D"]].copy()
    t["sample"] = "sparc"
    return t, g


# ---------------------------------------------------------- LITTLE THINGS 12
LT_EXCLUDE = {"WLM", "IC_1613", "DDO_126", "DDO_154", "DDO_168", "DDO_50",
              "DDO_87", "NGC_2366"}


def build_lt12(yaml_path, star_scale="as_published"):
    import yaml
    d = yaml.safe_load(open(yaml_path))
    rows = []
    meta = {}
    for name in sorted(d):
        if name in LT_EXCLUDE:
            continue
        gg = d[name]
        R = np.asarray(gg["r"], float)
        vg = np.asarray(gg["v_gas"], float)
        vs = np.asarray(gg["v_stars"], float)
        vo = np.asarray(gg["v_obs"], float)
        ev = np.asarray(gg["err_v_obs"], float)
        yf = float(gg["y_fit"])
        if star_scale == "Y0p5_via_yfit":
            vs = vs * np.sqrt(Y_DISK / yf)
        vb2 = np.abs(vg) * vg + np.abs(vs) * vs
        for i in range(len(R)):
            rows.append(dict(Galaxy=name, R=R[i], Vgas=vg[i], Vdisk=vs[i],
                             Vbul=0.0, Vobs=vo[i], e_Vobs=ev[i], Vb2=vb2[i],
                             D=float(gg["distance"])))
        meta[name] = dict(distance_Mpc=float(gg["distance"]),
                          e_distance_Mpc=float(gg["err_distance"]),
                          inc_deg=float(gg["inc"]), e_inc_deg=float(gg["err_inc"]),
                          m_gas_Msun=float(gg["m_gas"]), m_stars_Msun=float(gg["m_stars"]),
                          y_fit=yf, n_rings_raw=len(R))
    t = pd.DataFrame(rows)
    t["gbar"] = t["Vb2"] * KMS**2 / (t["R"] * KPC_M)
    t["gobs"] = gobs_from_v(t["Vobs"], t["R"])
    t["e_gobs"] = e_gobs_from_v(t["Vobs"], t["e_Vobs"], t["R"])
    t["sample"] = "little_things_12"
    return t, meta


# ---------------------------------------------------------------- THINGS 4
THINGS4 = ["NGC925", "NGC3031", "NGC3621", "NGC4736"]


def build_things4(with_bulge=True):
    p = os.path.join(LANES, "phase23_external_heldout_sources_2026_07_22",
                     "C_things_littlethings", "things_deblok2008_massmodels_tidy.csv")
    d = pd.read_csv(p)
    # ISO.fix.REV is the par_MD = 1.0 variant -> Vdisk is the M/L = 1 disk.
    d = d[(d.galaxy.isin(THINGS4)) & (d.variant == "ISO.fix.REV")].copy()
    vb = d["Vbulge_kms"].to_numpy(float) if with_bulge else np.zeros(len(d))
    vg = d["Vgas_kms"].to_numpy(float)
    vd = d["Vdisk_kms"].to_numpy(float)
    vb2 = np.abs(vg) * vg + Y_DISK * np.abs(vd) * vd + Y_BULGE * np.abs(vb) * vb
    t = pd.DataFrame(dict(Galaxy=d["galaxy"].to_numpy(), R=d["R_kpc"].to_numpy(float),
                          Vgas=vg, Vdisk=vd, Vbul=d["Vbulge_kms"].to_numpy(float),
                          Vobs=d["Vobs_kms"].to_numpy(float),
                          e_Vobs=d["e_Vobs_kms"].to_numpy(float), Vb2=vb2))
    t["gbar"] = t["Vb2"] * KMS**2 / (t["R"] * KPC_M)
    t["gobs"] = gobs_from_v(t["Vobs"], t["R"])
    t["e_gobs"] = e_gobs_from_v(t["Vobs"], t["e_Vobs"], t["R"])
    t["sample"] = "things_4"
    return t


# ------------------------------------------------- evidence by 1-D quadrature
# k = 1 pair: only log10 sigma_int free, uniform prior on [-3, 0]
# (BOUNDS_LOCKED_K1, phase23_locked_evaluator.py:117)
LS_LO, LS_HI = -3.0, 0.0


def _lnZ_quad(logL_fn, n=20001):
    ls = np.linspace(LS_LO, LS_HI, n)
    ll = np.array([logL_fn(x) for x in ls])
    m = ll.max()
    w = np.exp(ll - m)
    # uniform prior density 1/(hi-lo); integral over ls -> mean of w
    from numpy import trapz
    Z = np.trapz(w, ls) / (LS_HI - LS_LO)
    return m + np.log(Z), ls, ll


def _post_mean_sigma(ls, ll):
    m = ll.max()
    w = np.exp(ll - m)
    return float(np.trapz(w * (10.0 ** ls), ls) / np.trapz(w, ls))


def evidence_pair(prep):
    """Return dict with lnZ_gate, lnZ_mond, dlnB, sigma_gate, sigma_mond."""
    f_gate = EV.make_loglike_locked_k1(prep, gate=True)
    f_mond = EV.make_loglike_locked_k1(prep, gate=False)
    zg, lsg, llg = _lnZ_quad(lambda x: f_gate((x,)))
    zm, lsm, llm = _lnZ_quad(lambda x: f_mond((x,)))
    return dict(lnZ_gate=zg, lnZ_mond=zm, dlnB=zg - zm,
                sigma_int_gate=_post_mean_sigma(lsg, llg),
                sigma_int_mond=_post_mean_sigma(lsm, llm))


def per_ring_dln(prep, sig_gate, sig_mond):
    gp_g = EV.rar_screened(prep["g_bar"], prep["L_b"], EV.P120_A0_MS2,
                           EV.P120_L_STAR_M, EV.P120_Q)
    gp_m = EV.rar_mcgaugh(prep["g_bar"], EV.P120_A0_MS2)
    lo, el = prep["log_obs"], prep["e_log_obs"]

    def term(gp, s):
        d = lo - np.log10(np.maximum(gp, 1e-300))
        s2 = el**2 + s**2
        return -0.5 * (d**2 / s2 + np.log(EV.TWO_PI * s2))
    return term(gp_g, sig_gate) - term(gp_m, sig_mond), gp_g, gp_m


if __name__ == "__main__":
    os.makedirs(SCRATCH, exist_ok=True)
    sparc, sparc_gal = build_sparc()
    lt_a, lt_meta = build_lt12(os.path.join(SCRATCH, "little_things_sample.yaml"),
                               "as_published")
    lt_b, _ = build_lt12(os.path.join(SCRATCH, "little_things_sample.yaml"),
                         "Y0p5_via_yfit")
    th_wb = build_things4(with_bulge=True)
    th_nb = build_things4(with_bulge=False)

    for nm, t in [("sparc", sparc), ("lt12_as_published", lt_a),
                  ("lt12_Y0p5", lt_b), ("things4_bulge", th_wb),
                  ("things4_nobulge", th_nb)]:
        p = EV.prepare(t)
        r = evidence_pair(p)
        print(f"{nm:22s} N={p['N']:5d} ngal={p['table']['Galaxy'].nunique():4d} "
              f"dlnB={r['dlnB']:+9.4f}  sig_g={r['sigma_int_gate']:.5f} "
              f"sig_m={r['sigma_int_mond']:.5f}")
    sparc.to_pickle(os.path.join(SCRATCH, "tierA_sparc.pkl"))
    lt_a.to_pickle(os.path.join(SCRATCH, "tierA_lt12_pub.pkl"))
    lt_b.to_pickle(os.path.join(SCRATCH, "tierA_lt12_y05.pkl"))
    th_wb.to_pickle(os.path.join(SCRATCH, "tierA_things4_bulge.pkl"))
    th_nb.to_pickle(os.path.join(SCRATCH, "tierA_things4_nobulge.pkl"))
    sparc_gal.to_pickle(os.path.join(SCRATCH, "sparc_table1.pkl"))
    json.dump(lt_meta, open(os.path.join(SCRATCH, "lt_meta.json"), "w"), indent=1)
    print("saved.")
