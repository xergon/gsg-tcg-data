#!/usr/bin/env python3
"""
i2 REPAIR 2026-07-26 — Sérsic K(n) participation-area factor.

DEFECT (found by ChatGPT Pro thread i2, reproduced independently on disk):
    build_lens_table.py:213-214 computed

        df["A_IPR_kpc2_ellip"]  = np.pi * (df["Re_maj_kpc_r"] ** 2) * q
        df["A_IPR_kpc2_major"]  = np.pi * (df["Re_maj_kpc_r"] ** 2)

    i.e. HALF-LIGHT AREAS. Those are NOT participation areas: the programme's canonical
    inverse-participation statistic (LEAD_SPARC_RAR_AEFF_IPR_DISCRIMINATOR.md:129-132) is

        A_eff = (∫ s dA)^2 / (∫ s^2 dA),   R_IPR = sqrt(A_eff/pi),   X_A = log10(R_IPR/kpc)

    For a Sérsic profile  I(R) = I_e exp(-b_n[(R/Re)^(1/n) - 1])  on elliptical isophotes of
    axis ratio q (dA = 2*pi*q*R dR, R = semi-major coordinate):

        ∫ I  dA = 2*pi*q*Re^2 * I_e   * e^( b_n) * n * Gamma(2n) *   b_n **(-2n)
        ∫ I^2 dA = 2*pi*q*Re^2 * I_e^2 * e^(2b_n) * n * Gamma(2n) * (2b_n)**(-2n)

    ⇒   A_IPR = pi * q * Re_maj^2 * K(n)     with
        K(n) = 2 * n * Gamma(2n) * 4**n / b_n**(2n)

    K(1) = 2.8402 (checked analytically against the exponential disk: A_IPR = 8*pi*h^2).
    The delivered columns were therefore short by exactly the factor K(n), which is
    n-dependent and so does NOT cancel in a regression slope against log10 A_IPR.

REPAIR IS ADDITIVE. v1 columns are retained bit-for-bit and marked superseded; new
columns are added beside them. v1 parquet on disk and in the GitHub release is untouched.

b_n is solved EXACTLY (not the 2n-1/3 series, which is invalid at the low-n end of the
0.1 < GALINDEX_r < 20 cut) from  gamma_lower(2n, b_n)/Gamma(2n) = 1/2  via gammaincinv.
All K factors are evaluated in log space (Gamma(40) ~ 2e46 overflows a naive product).
"""
import os
import numpy as np
import pandas as pd
from scipy.special import gammaincinv, gammaln

B = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(B, "gama_kidslegacy_ipr_rar_inputs_v1.parquet")
OUT = os.path.join(B, "gama_kidslegacy_ipr_rar_inputs_v2.parquet")
COMPANION = os.path.join(B, "i2_A_IPR_Kn_repair_v1.parquet")


def sersic_bn(n):
    """Exact b_n: median of the Gamma(2n) distribution."""
    return gammaincinv(2.0 * np.asarray(n, dtype=np.float64), 0.5)


def log_K_ipr(n, bn):
    """ln K_IPR(n) = ln(2n) + lnGamma(2n) + n ln4 - 2n ln b_n.

    (The 4**n comes from (2 b_n)**(2n) / b_n**(4n) = 4**n * b_n**(-2n) -- an earlier draft
    wrote 4**(2n) here and was caught by the numerical-integration cross-check below.)"""
    n = np.asarray(n, dtype=np.float64)
    return np.log(2.0 * n) + gammaln(2.0 * n) + n * np.log(4.0) - 2.0 * n * np.log(bn)


def log_K_totlight(n, bn):
    """Alternative convention, NOT used for A_IPR_*_Kn: A = L_tot/I_e = pi Re^2 K_tot(n),
    K_tot(n) = 2 n Gamma(2n) e^(b_n) b_n^(-2n).  Shipped for convenience only."""
    n = np.asarray(n, dtype=np.float64)
    return np.log(2.0 * n) + gammaln(2.0 * n) + bn - 2.0 * n * np.log(bn)


def main():
    df = pd.read_parquet(SRC)
    n0 = len(df)
    print(f"read  {SRC}  rows={n0:,} cols={df.shape[1]}")

    n = df["GALINDEX_r"].to_numpy(dtype=np.float64)
    bn = sersic_bn(n)
    K = np.exp(log_K_ipr(n, bn))
    Ktot = np.exp(log_K_totlight(n, bn))

    df["sersic_bn_r"] = bn
    df["K_IPR_sersic_r"] = K
    df["K_totlight_sersic_r"] = Ktot

    df["A_IPR_kpc2_ellip_Kn"] = df["A_IPR_kpc2_ellip"].to_numpy() * K
    df["A_IPR_kpc2_major_Kn"] = df["A_IPR_kpc2_major"].to_numpy() * K
    df["log10_A_IPR_ellip_Kn"] = np.log10(df["A_IPR_kpc2_ellip_Kn"])
    df["log10_A_IPR_major_Kn"] = np.log10(df["A_IPR_kpc2_major_Kn"])
    df["R_IPR_kpc_ellip_Kn"] = np.sqrt(df["A_IPR_kpc2_ellip_Kn"].to_numpy() / np.pi)
    df["X_A_ellip_Kn"] = np.log10(df["R_IPR_kpc_ellip_Kn"])

    assert len(df) == n0, "row count changed"
    df.to_parquet(OUT, index=False)
    print(f"wrote {OUT}  rows={len(df):,} cols={df.shape[1]}  {os.path.getsize(OUT):,} bytes")

    cols = ["CATAID", "GALINDEX_r", "sersic_bn_r", "K_IPR_sersic_r", "K_totlight_sersic_r",
            "A_IPR_kpc2_ellip", "A_IPR_kpc2_major",
            "A_IPR_kpc2_ellip_Kn", "A_IPR_kpc2_major_Kn",
            "log10_A_IPR_ellip_Kn", "log10_A_IPR_major_Kn",
            "R_IPR_kpc_ellip_Kn", "X_A_ellip_Kn"]
    df[cols].to_parquet(COMPANION, index=False)
    print(f"wrote {COMPANION}  {os.path.getsize(COMPANION):,} bytes")

    # ---- VERIFY by re-opening what was actually written ----
    print("\n=== VERIFICATION (re-read from disk) ===")
    v = pd.read_parquet(OUT)
    print(f"rows = {len(v):,}   cols = {v.shape[1]}")
    for c in ["GALINDEX_r", "sersic_bn_r", "K_IPR_sersic_r"]:
        a = v[c].to_numpy()
        print(f"{c:22s} min={np.nanmin(a):.6g}  median={np.nanmedian(a):.6g}  max={np.nanmax(a):.6g}"
              f"  n_nonfinite={int((~np.isfinite(a)).sum())}")
    for pair in [("A_IPR_kpc2_ellip_Kn", "A_IPR_kpc2_ellip"),
                 ("A_IPR_kpc2_major_Kn", "A_IPR_kpc2_major")]:
        r = v[pair[0]].to_numpy() / v[pair[1]].to_numpy()
        print(f"ratio {pair[0]}/{pair[1]}: min={np.nanmin(r):.6g} median={np.nanmedian(r):.6g} "
              f"max={np.nanmax(r):.6g}")
    # closed-form spot checks
    for nn, ref in [(1.0, 2.8402), (4.0, 0.86287)]:
        bb = sersic_bn(nn)
        print(f"  spot K_IPR(n={nn}) = {float(np.exp(log_K_ipr(nn, bb))):.6f}  (expected ~{ref})")
    # numerical-integration check of K_IPR at three n
    for nn in [0.5, 1.0, 4.0, 10.0]:
        bb = float(sersic_bn(nn))
        R = np.logspace(-6, 3, 400001)
        I = np.exp(-bb * ((R) ** (1.0 / nn) - 1.0))
        i1 = np.trapz(I * 2 * np.pi * R, R)
        i2 = np.trapz(I ** 2 * 2 * np.pi * R, R)
        print(f"  numeric K_IPR(n={nn}) = {i1**2/i2/np.pi:.6f}   analytic = "
              f"{float(np.exp(log_K_ipr(nn, bb))):.6f}"
              f"   | numeric K_tot(n={nn}) = {i1/np.pi:.6f}"
              f"   analytic = {float(np.exp(log_K_totlight(nn, bb))):.6f}")
    # percentiles of the correction actually applied
    kk = v["K_IPR_sersic_r"].to_numpy()
    print("  K_IPR percentiles:", {f"p{p}": round(float(np.percentile(kk, p)), 6)
                                   for p in [0.1, 1, 5, 25, 50, 75, 95, 99, 99.9]})
    nn_ = v["GALINDEX_r"].to_numpy()
    print(f"  rows with GALINDEX_r > 8 (K < ~0.1): {int((nn_ > 8).sum()):,}"
          f"  |  > 15: {int((nn_ > 15).sum()):,}  |  >= 19.99: {int((nn_ >= 19.99).sum()):,}")
    # v1 columns untouched?
    o = pd.read_parquet(SRC, columns=["A_IPR_kpc2_ellip", "A_IPR_kpc2_major"])
    same = (np.array_equal(o["A_IPR_kpc2_ellip"].to_numpy(), v["A_IPR_kpc2_ellip"].to_numpy())
            and np.array_equal(o["A_IPR_kpc2_major"].to_numpy(), v["A_IPR_kpc2_major"].to_numpy()))
    print(f"v1 A_IPR_* columns bit-identical in v2: {same}")


if __name__ == "__main__":
    main()
